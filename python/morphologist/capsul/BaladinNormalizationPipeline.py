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


class BaladinNormalizationPipeline(Pipeline):
    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        self._autoexport_nodes_parameters = autoexport_nodes_parameters
        super(BaladinNormalizationPipeline, self).__init__(False, **kwargs)
        del self._autoexport_nodes_parameters
#        if autoexport_nodes_parameters:
#            self.autoexport_nodes_parameters()


    def pipeline_definition(self):
        # nodes section
        self.add_process('NormalizeBaladin', 'morphologist.capsul.Normalization_Baladin.Normalization_Baladin')
        self.add_process('ConvertBaladinNormalizationToAIMS', 'morphologist.capsul.BaladinNormalizationToAims.BaladinNormalizationToAims')
        self.add_process('ReorientAnatomy', 'morphologist.capsul.reorientAnatomy.reorientAnatomy')

        # exports section
        # export input parameter
        self.export_parameter('NormalizeBaladin', 'anatomy_data', 't1mri')
        # export output parameter
        self.export_parameter('ConvertBaladinNormalizationToAIMS', 'write', 'transformation')
        # export input parameter
        self.export_parameter('NormalizeBaladin', 'anatomical_template', 'template')
        # export input parameter
        self.export_parameter('ConvertBaladinNormalizationToAIMS', 'set_transformation_in_source_volume', 'set_transformation_in_source_volume')
        # export input parameter
        self.export_parameter('ReorientAnatomy', 'allow_flip_initial_MRI', 'allow_flip_initial_MRI')

        # links section
        self.add_link('t1mri->ConvertBaladinNormalizationToAIMS.source_volume')
        self.add_link('t1mri->ReorientAnatomy.t1mri')
        self.add_link('ConvertBaladinNormalizationToAIMS.write->ReorientAnatomy.transformation')
        self.add_link('template->ConvertBaladinNormalizationToAIMS.registered_volume')
        self.add_link('NormalizeBaladin.transformation_matrix->ConvertBaladinNormalizationToAIMS.read')

        # initialization section
        self.nodes_activation.ReorientAnatomy = False
        # export orphan parameters
        if not hasattr(self, '_autoexport_nodes_parameters') \
                or self._autoexport_nodes_parameters:
            self.autoexport_nodes_parameters()


    def autoexport_nodes_parameters(self):
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
                        if plug.links_to: # or plug.links_from:
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

