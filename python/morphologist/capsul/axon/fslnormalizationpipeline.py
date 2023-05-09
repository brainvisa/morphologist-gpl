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


class FSLnormalizationPipeline(Pipeline):
    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        self._autoexport_nodes_parameters = autoexport_nodes_parameters
        super(FSLnormalizationPipeline, self).__init__(False, **kwargs)
        del self._autoexport_nodes_parameters
#        if autoexport_nodes_parameters:
#            self.autoexport_nodes_parameters()

    def pipeline_definition(self):
        # nodes section
        self.add_process(
            'NormalizeFSL', 'morphologist.capsul.axon.normalization_fsl_reinit.Normalization_FSL_reinit')
        self.add_process('ConvertFSLnormalizationToAIMS',
                         'morphologist.capsul.axon.fslnormalizationtoaims.FSLnormalizationToAims')
        self.add_process(
            'ReorientAnatomy', 'morphologist.capsul.axon.reorientanatomy.ReorientAnatomy')

        # exports section
        # export input parameter
        self.export_parameter('NormalizeFSL', 'anatomy_data', 't1mri')
        # export output parameter
        self.export_parameter(
            'ReorientAnatomy', 'output_transformation', 'transformation')
        # export input parameter
        self.export_parameter(
            'NormalizeFSL', 'anatomical_template', 'template')
        # export input parameter
        self.export_parameter('NormalizeFSL', 'Alignment', 'alignment')
        # export input parameter
        self.export_parameter('ConvertFSLnormalizationToAIMS',
                              'set_transformation_in_source_volume', 'set_transformation_in_source_volume')
        # export input parameter
        self.export_parameter(
            'ReorientAnatomy', 'allow_flip_initial_MRI', 'allow_flip_initial_MRI')
        # export input parameter
        self.export_parameter(
            'NormalizeFSL', 'allow_retry_initialization', 'allow_retry_initialization')
        # export output parameter
        self.export_parameter(
            'ReorientAnatomy', 'output_t1mri', 'reoriented_t1mri')

        # links section
        self.add_link('t1mri->ConvertFSLnormalizationToAIMS.source_volume')
        self.add_link('t1mri->ReorientAnatomy.t1mri')
        self.add_link(
            'template->ConvertFSLnormalizationToAIMS.registered_volume')
        self.add_link(
            'NormalizeFSL.transformation_matrix->ConvertFSLnormalizationToAIMS.read')
        self.add_link(
            'ConvertFSLnormalizationToAIMS.write->ReorientAnatomy.transformation')

        # initialization section
        self.nodes_activation.ReorientAnatomy = False
        # export orphan parameters
        if not hasattr(self, '_autoexport_nodes_parameters') \
                or self._autoexport_nodes_parameters:
            self.autoexport_nodes_parameters()

    def autoexport_nodes_parameters(self):
        '''export orphan and internal output parameters'''
        for node_name, node in self.nodes.items():
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
