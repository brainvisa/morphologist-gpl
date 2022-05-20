# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process
from capsul.api import Pipeline
from capsul.api import Switch


class SPMnormalizationPipeline(Pipeline):
    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        self._autoexport_nodes_parameters = autoexport_nodes_parameters
        super(SPMnormalizationPipeline, self).__init__(False, **kwargs)
        del self._autoexport_nodes_parameters
#        if autoexport_nodes_parameters:
#            self.autoexport_nodes_parameters()


    def pipeline_definition(self):
        # nodes section
        self.add_process('ConvertSPMnormalizationToAIMS', 'morphologist.capsul.axon.spmsn3dtoaims.SPMsn3dToAims')
        self.add_process('ReorientAnatomy', 'morphologist.capsul.axon.reorientanatomy.ReorientAnatomy')
        self.add_process('normalization_t1_spm12_reinit', 'morphologist.capsul.axon.normalization_t1_spm12_reinit.normalization_t1_spm12_reinit')
        self.nodes['normalization_t1_spm12_reinit']._weak_outputs = True
        self.add_process('normalization_t1_spm8_reinit', 'morphologist.capsul.axon.normalization_t1_spm8_reinit.normalization_t1_spm8_reinit')
        self.nodes['normalization_t1_spm8_reinit']._weak_outputs = True

        # switches section
        self.add_switch('NormalizeSPM', ['normalization_t1_spm12_reinit', 'normalization_t1_spm8_reinit'], ['spm_transformation', 'normalized_t1mri'], output_types=[field(type_=File, write=True, allowed_extensions=['.mat']), field(type_=File, write=True, allowed_extensions=['.nii', '.img', '.hdr'])])

        # exports section
        # export input parameter
        self.export_parameter('normalization_t1_spm12_reinit', 'anatomy_data', 't1mri')
        # export output parameter
        self.export_parameter('ReorientAnatomy', 'output_transformation', 'transformation')
        # export output parameter
        self.export_parameter('NormalizeSPM', 'spm_transformation', 'spm_transformation')
        # export output parameter
        self.export_parameter('NormalizeSPM', 'normalized_t1mri', 'normalized_t1mri')
        # export input parameter
        self.export_parameter('normalization_t1_spm12_reinit', 'anatomical_template', 'template')
        # export input parameter
        self.export_parameter('ReorientAnatomy', 'allow_flip_initial_MRI', 'allow_flip_initial_MRI')
        # export input parameter
        self.export_parameter('normalization_t1_spm12_reinit', 'allow_retry_initialization', 'allow_retry_initialization')
        # export output parameter
        self.export_parameter('ReorientAnatomy', 'output_t1mri', 'reoriented_t1mri')
        # export input parameter
        self.export_parameter('normalization_t1_spm12_reinit', 'init_translation_origin', 'init_translation_origin')
        # export input parameter
        self.export_parameter('normalization_t1_spm12_reinit', 'voxel_size', 'voxel_size')
        # export input parameter
        self.export_parameter('normalization_t1_spm12_reinit', 'cutoff_option', 'cutoff_option')
        # export input parameter
        self.export_parameter('normalization_t1_spm12_reinit', 'nbiteration', 'nbiteration')
        self.do_not_export.update([('ConvertSPMnormalizationToAIMS', 'write')])

        # links section
        self.add_link('t1mri->normalization_t1_spm8_reinit.anatomy_data')
        self.add_link('t1mri->ConvertSPMnormalizationToAIMS.source_volume')
        self.add_link('t1mri->ReorientAnatomy.t1mri')
        self.add_link('allow_retry_initialization->normalization_t1_spm8_reinit.allow_retry_initialization')
        self.add_link('template->normalization_t1_spm8_reinit.anatomical_template')
        self.add_link('init_translation_origin->normalization_t1_spm8_reinit.init_translation_origin')
        self.add_link('cutoff_option->normalization_t1_spm8_reinit.cutoff_option')
        self.add_link('nbiteration->normalization_t1_spm8_reinit.nbiteration')
        self.add_link('voxel_size->normalization_t1_spm8_reinit.voxel_size')
        self.add_link('normalization_t1_spm12_reinit.transformations_informations->NormalizeSPM.normalization_t1_spm12_reinit_switch_spm_transformation')
        self.add_link('normalization_t1_spm12_reinit.normalized_anatomy_data->NormalizeSPM.normalization_t1_spm12_reinit_switch_normalized_t1mri')
        self.add_link('normalization_t1_spm8_reinit.transformations_informations->NormalizeSPM.normalization_t1_spm8_reinit_switch_spm_transformation')
        self.add_link('normalization_t1_spm8_reinit.normalized_anatomy_data->NormalizeSPM.normalization_t1_spm8_reinit_switch_normalized_t1mri')
        self.add_link('normalization_t1_spm12_reinit.transformations_informations->ConvertSPMnormalizationToAIMS.read')
        self.add_link('ConvertSPMnormalizationToAIMS.write->ReorientAnatomy.transformation')

        # initialization section
        if 'normalization_t1_spm12_reinit' in self.nodes:
            self.dispatch_value(self, 'NormalizeSPM', 'normalization_t1_spm12_reinit')
        self.nodes['ReorientAnatomy'].allow_flip_initial_MRI = False
        self.nodes_activation.ReorientAnatomy = False
        # export orphan parameters
        if not hasattr(self, '_autoexport_nodes_parameters') \
                or self._autoexport_nodes_parameters:
            self.autoexport_nodes_parameters()


    def autoexport_nodes_parameters(self):
        '''export orphan and internal output parameters'''
        for node_name, node in self.nodes.items():
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

