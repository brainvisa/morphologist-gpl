# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process
from capsul.api import Pipeline
from capsul.api import Switch


class Normalization(Pipeline):
    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        self._autoexport_nodes_parameters = autoexport_nodes_parameters
        super(Normalization, self).__init__(False, **kwargs)
        del self._autoexport_nodes_parameters
#        if autoexport_nodes_parameters:
#            self.autoexport_nodes_parameters()


    def pipeline_definition(self):
        # nodes section
        self.add_process('NormalizeFSL', 'morphologist.capsul.fslnormalization.FSLNormalization')
        self.nodes['NormalizeFSL']._weak_outputs = True
        self.add_process('NormalizeSPM', 'morphologist.capsul.spmnormalization.SPMNormalization')
        self.nodes['NormalizeSPM']._weak_outputs = True
        self.add_process('NormalizeBaladin', 'morphologist.capsul.axon.baladinnormalizationpipeline.BaladinNormalizationPipeline')
        self.nodes['NormalizeBaladin']._weak_outputs = True
        self.add_process('Normalization_AimsMIRegister', 'morphologist.capsul.axon.normalization_aimsmiregister.normalization_aimsmiregister')
        self.nodes['Normalization_AimsMIRegister']._weak_outputs = True

        # switches section
        self.add_switch('select_Normalization_pipeline', ['NormalizeFSL', 'NormalizeSPM', 'NormalizeBaladin', 'Normalization_AimsMIRegister'], ['transformation', 'normalized', 'reoriented_t1mri'], output_types=[field(type_=File, write=True, optional=True, allowed_extensions=['.trm']), field(type_=File, write=True, optional=True, allowed_extensions=['.nii.gz', '.nii', '.img', '.hdr', '.ima', '.dim', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.jpg', '.mnc', '.pbm', '.pgm', '.png', '.ppm', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz']), field(type_=File, write=True, read=True, allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz', '.svs', '.mgh', '.mgz', '.ndpi', '.vms', '.vmu', '.scn', '.svslide', '.bif', '.czi'])])

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
        self.export_parameter('select_Normalization_pipeline', 'reoriented_t1mri', 'reoriented_t1mri')
        # export output parameter
        self.export_parameter('NormalizeFSL', 'ReorientAnatomy_output_commissures_coordinates', 'output_commissures_coordinates')
        # export input parameter
        self.export_parameter('NormalizeFSL', 'NormalizeFSL_init_translation_origin', 'init_translation_origin')
        # export output parameter
        self.export_parameter('select_Normalization_pipeline', 'normalized', 'normalized')
        self.do_not_export.update([('NormalizeFSL', 'ConvertFSLnormalizationToAIMS_write'), ('NormalizeBaladin', 'ConvertBaladinNormalizationToAIMS_write')])

        # links section
        self.add_link('t1mri->NormalizeSPM.t1mri')
        self.add_link('t1mri->NormalizeBaladin.t1mri')
        self.add_link('t1mri->Normalization_AimsMIRegister.anatomy_data')
        self.add_link('allow_flip_initial_MRI->NormalizeSPM.allow_flip_initial_MRI')
        self.add_link('allow_flip_initial_MRI->NormalizeBaladin.allow_flip_initial_MRI')
        self.add_link('commissures_coordinates->NormalizeSPM.ReorientAnatomy_commissures_coordinates')
        self.add_link('commissures_coordinates->NormalizeBaladin.ReorientAnatomy_commissures_coordinates')
        self.add_link('NormalizeSPM.ReorientAnatomy_output_commissures_coordinates->output_commissures_coordinates')
        self.add_link('NormalizeBaladin.ReorientAnatomy_output_commissures_coordinates->output_commissures_coordinates')
        self.add_link('init_translation_origin->NormalizeSPM.init_translation_origin')
        self.add_link('NormalizeFSL.transformation->select_Normalization_pipeline.NormalizeFSL_switch_transformation')
        self.add_link('NormalizeFSL.NormalizeFSL_normalized_anatomy_data->select_Normalization_pipeline.NormalizeFSL_switch_normalized')
        self.add_link('NormalizeFSL.reoriented_t1mri->select_Normalization_pipeline.NormalizeFSL_switch_reoriented_t1mri')
        self.add_link('NormalizeSPM.transformation->select_Normalization_pipeline.NormalizeSPM_switch_transformation')
        self.add_link('NormalizeSPM.normalized_t1mri->select_Normalization_pipeline.NormalizeSPM_switch_normalized')
        self.add_link('NormalizeSPM.reoriented_t1mri->select_Normalization_pipeline.NormalizeSPM_switch_reoriented_t1mri')
        self.add_link('NormalizeBaladin.transformation->select_Normalization_pipeline.NormalizeBaladin_switch_transformation')
        self.add_link('NormalizeBaladin.NormalizeBaladin_normalized_anatomy_data->select_Normalization_pipeline.NormalizeBaladin_switch_normalized')
        self.add_link('NormalizeBaladin.reoriented_t1mri->select_Normalization_pipeline.NormalizeBaladin_switch_reoriented_t1mri')
        self.add_link('Normalization_AimsMIRegister.transformation_to_MNI->select_Normalization_pipeline.Normalization_AimsMIRegister_switch_transformation')
        self.add_link('Normalization_AimsMIRegister.normalized_anatomy_data->select_Normalization_pipeline.Normalization_AimsMIRegister_switch_normalized')
        self.add_link('t1mri->select_Normalization_pipeline.Normalization_AimsMIRegister_switch_reoriented_t1mri')

        # initialization section
        if 'NormalizeSPM' in self.nodes:
            self.nodes['select_Normalization_pipeline'].switch = 'NormalizeSPM'
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

