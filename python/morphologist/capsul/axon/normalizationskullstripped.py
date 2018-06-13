# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

from capsul.api import Process
import six
from capsul.api import Pipeline
from capsul.api import Switch


class NormalizationSkullStripped(Pipeline):
    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        self._autoexport_nodes_parameters = autoexport_nodes_parameters
        super(NormalizationSkullStripped, self).__init__(False, **kwargs)
        del self._autoexport_nodes_parameters
#        if autoexport_nodes_parameters:
#            self.autoexport_nodes_parameters()

    def pipeline_definition(self):
        # nodes section
        self.add_process(
            'SkullStripping', 'morphologist.capsul.axon.skullstripping.skullstripping')
        self.add_process(
            'Normalization', 'morphologist.capsul.axon.normalization.Normalization')
        self.add_process('TalairachFromNormalization',
                         'morphologist.capsul.talairachtransformationfromnormalization.TalairachTransformationFromNormalization')

        # exports section
        # export input parameter
        self.export_parameter('SkullStripping', 't1mri', 't1mri')
        # export input parameter
        self.export_parameter('SkullStripping', 'brain_mask', 'brain_mask')
        # export input parameter
        self.export_parameter(
            'Normalization', 'NormalizeFSL_template', 'template')
        # export output parameter
        self.export_parameter(
            'SkullStripping', 'skull_stripped', 'skull_stripped')
        # export output parameter
        self.export_parameter(
            'Normalization', 'transformation', 'transformation')
        # export output parameter
        self.export_parameter('TalairachFromNormalization',
                              'Talairach_transform', 'talairach_transformation')
        # export output parameter
        self.export_parameter('TalairachFromNormalization',
                              'commissure_coordinates', 'commissure_coordinates')
        self.do_not_export.update(
            [('Normalization', 'output_commissures_coordinates')])

        # links section
        self.add_link('t1mri->TalairachFromNormalization.t1mri')
        self.add_link('template->Normalization.NormalizeSPM_template')
        self.add_link('template->Normalization.NormalizeBaladin_template')
        self.add_link(
            'template->Normalization.Normalization_AimsMIRegister_anatomical_template')
        self.add_link('SkullStripping.skull_stripped->Normalization.t1mri')
        self.add_link(
            'Normalization.transformation->TalairachFromNormalization.normalization_transformation')

        # initialization section
        self.nodes['Normalization'].allow_flip_initial_MRI = False
        # export orphan parameters
        if not hasattr(self, '_autoexport_nodes_parameters') \
                or self._autoexport_nodes_parameters:
            self.autoexport_nodes_parameters()

    def autoexport_nodes_parameters(self):
        '''export orphan and internal output parameters'''
        for node_name, node in six.iteritems(self.nodes):
            if node_name == '':
                continue  # skip main node
            if hasattr(node, '_weak_outputs'):
                weak_outputs = node._weak_outputs
            else:
                weak_outputs = False
            for parameter_name, plug in node.plugs.items():
                if parameter_name in ('nodes_activation', 'selection_changed'):
                    continue
                if (node_name, parameter_name) not in self.do_not_export:
                    if not plug.output and plug.links_from:
                        continue
                    weak_link = False
                    if plug.output:
                        if plug.links_to:  # or plug.links_from:
                            # some links exist
                            if [True for x in plug.links_to
                                    if x[0] == '' or isinstance(x[2], Switch)] \
                                    or \
                                    [True for x in plug.links_from
                                     if x[0] == '' or isinstance(x[2], Switch)]:
                                # a link to the main pipeline or to a switch
                                # already exists
                                continue
                            # links exist but not to the pipeline: export
                            # weak_link = True
                    if weak_outputs and plug.output:
                        weak_link = True
                    self.export_parameter(node_name, parameter_name,
                                          '_'.join(
                                              (node_name, parameter_name)),
                                          weak_link=weak_link, is_optional=True)
