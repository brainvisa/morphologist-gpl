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


class normalizationPipeline(Pipeline):
    def __init__(self, autoexport_node_parameters=True, **kwargs):
        super(normalizationPipeline, self).__init__(False, **kwargs)
        if autoexport_node_parameters:
            self.export_internal_parameters()


    def pipeline_definition(self):
        # nodes section
        self.add_switch('select_Normalization_pipeline', ['NormalizeFSL', 'NormalizeSPM', 'Normalization_AimsMIRegister'], ['transformation', 'normalized'])
        self.add_process('NormalizeFSL', 'morphologist.capsul.FSLnormalizationPipeline.FSLnormalizationPipeline')
        self.nodes['NormalizeFSL']._weak_outputs = True
        self.add_process('NormalizeSPM', 'morphologist.capsul.SPMnormalizationPipeline.SPMnormalizationPipeline')
        self.nodes['NormalizeSPM']._weak_outputs = True
        self.add_process('Normalization_AimsMIRegister', 'morphologist.capsul.normalization_aimsmiregister.normalization_aimsmiregister')
        self.nodes['Normalization_AimsMIRegister']._weak_outputs = True

        # exports section
        # export input parameter
        self.export_parameter('NormalizeFSL', 't1mri', 't1mri')
        # export output parameter
        self.export_parameter('select_Normalization_pipeline', 'transformation', 'transformation')
        # export input parameter
        self.export_parameter('NormalizeFSL', 'allow_flip_initial_MRI', 'allow_flip_initial_MRI')
        # export input parameter
        self.export_parameter('NormalizeFSL', 'ReorientAnatomy_commissures_coordinates', 'commissures_coordinates')
        # export output parameter
        self.export_parameter('select_Normalization_pipeline', 'normalized', 'normalized')

        # links section
        self.add_link('t1mri->NormalizeSPM.t1mri')
        self.add_link('t1mri->Normalization_AimsMIRegister.anatomy_data')
        self.add_link('commissures_coordinates->NormalizeSPM.ReorientAnatomy_commissures_coordinates')
        self.add_link('allow_flip_initial_MRI->NormalizeSPM.allow_flip_initial_MRI')
        self.add_link('NormalizeFSL.transformation->select_Normalization_pipeline.NormalizeFSL_switch_transformation')
        self.add_link('NormalizeFSL.NormalizeFSL_normalized_anatomy_data->select_Normalization_pipeline.NormalizeFSL_switch_normalized')
        self.add_link('NormalizeSPM.transformation->select_Normalization_pipeline.NormalizeSPM_switch_transformation')
        self.add_link('NormalizeSPM.normalized_t1mri->select_Normalization_pipeline.NormalizeSPM_switch_normalized')
        self.add_link('Normalization_AimsMIRegister.transformation_to_MNI->select_Normalization_pipeline.Normalization_AimsMIRegister_switch_transformation')
        self.add_link('Normalization_AimsMIRegister.normalized_anatomy_data->select_Normalization_pipeline.Normalization_AimsMIRegister_switch_normalized')

        # initialization section
        self.nodes['select_Normalization_pipeline'].switch = 'NormalizeSPM'


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

