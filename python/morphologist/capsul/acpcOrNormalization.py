# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process
from capsul.pipeline import Pipeline
from capsul.pipeline import Switch


class acpcOrNormalization(Pipeline):
    def __init__(self, autoexport_node_parameters=True, **kwargs):
        super(acpcOrNormalization, self).__init__(False, **kwargs)
        if autoexport_node_parameters:
            self.export_internal_parameters()


    def pipeline_definition(self):
        # nodes section
        self.add_switch('select_AC_PC_Or_Normalization', ['StandardACPC', 'Normalization'], ['commissure_coordinates'])
        self.add_process('StandardACPC', 'morphologist.capsul.preparesubject.preparesubject')
        self.nodes['StandardACPC']._weak_outputs = True
        self.add_process('Normalization', 'morphologist.capsul.normalizationPipeline.normalizationPipeline')
        self.nodes['Normalization']._weak_outputs = True
        self.add_process('TalairachFromNormalization', 'morphologist.process.customized.TalairachTransformationFromNormalization.TalairachTransformationFromNormalization')
        self.nodes['TalairachFromNormalization']._weak_outputs = True

        # exports section
        # export input parameter
        self.export_parameter('StandardACPC', 'T1mri', 'T1mri')
        # export output parameter
        self.export_parameter('select_AC_PC_Or_Normalization', 'commissure_coordinates', 'commissure_coordinates')
        # export input parameter
        self.export_parameter('StandardACPC', 'allow_flip_initial_MRI', 'allow_flip_initial_MRI')

        # links section
        self.add_link('T1mri->Normalization.t1mri')
        self.add_link('T1mri->TalairachFromNormalization.t1mri')
        self.add_link('allow_flip_initial_MRI->Normalization.allow_flip_initial_MRI')
        self.add_link('StandardACPC.commissure_coordinates->select_AC_PC_Or_Normalization.StandardACPC_switch_commissure_coordinates')
        self.add_link('TalairachFromNormalization.commissure_coordinates->select_AC_PC_Or_Normalization.Normalization_switch_commissure_coordinates')
        self.add_link('Normalization.transformation->TalairachFromNormalization.normalization_transformation')

        # initialization section
        self.nodes['select_AC_PC_Or_Normalization'].switch = 'Normalization'


    def export_internal_parameters(self):
        '''export orphan and internal output parameters'''
        for node_name, node in self.nodes.iteritems():
            if node_name == '':
                continue # skip main node
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
                        if plug.links_to or plug.links_from:
                            # some links exist
                            if [True for x in plug.links_to \
                                    if x[0]=='' or isinstance(x[2], Switch)] \
                                    or \
                                    [True for x in plug.links_from \
                                    if x[0]=='' or isinstance(x[2], Switch)]:
                                # a link to the main pipeline or to a switch
                                # already exists
                                continue
                            # links exist but not to the pipeline: export
                            # weak_link = True
                    if weak_outputs and plug.output:
                        weak_link = True
                    self.export_parameter(node_name, parameter_name,
                        '_'.join((node_name, parameter_name)),
                        weak_link=weak_link, is_optional=True)

