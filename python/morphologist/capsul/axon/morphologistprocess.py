# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

from capsul.api import Process
import six


class morphologistProcess(Process):
    def __init__(self, **kwargs):
        super(morphologistProcess, self).__init__(**kwargs)
        self.add_trait('t1mri', File(allowed_extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz']))
        self.add_trait('perform_segmentation', Bool())
        self.add_trait('perform_bias_correction', Bool())
        self.add_trait('method_ACPC', Enum('Manually', 'With SPM12 Normalization', 'Already done'))
        self.add_trait('commissure_coordinates', File(allowed_extensions=['.APC'], output=True))
        self.add_trait('anterior_commissure', List(trait=Float(), minlen=3, maxlen=3, value=[0, 0, 0], optional=True))
        self.add_trait('posterior_commissure', List(trait=Float(), minlen=3, maxlen=3, value=[0, 0, 0], optional=True))
        self.add_trait('interhemispheric_point', List(trait=Float(), minlen=3, maxlen=3, value=[0, 0, 0], optional=True))
        self.add_trait('left_hemisphere_point', List(trait=Float(), minlen=3, maxlen=3, value=[0, 0, 0], optional=True))
        self.add_trait('older_MNI_normalization', File(allowed_extensions=['.trm'], optional=True))
        self.add_trait('anatomical_template', File(allowed_extensions=['.nii', '.mnc', '.img', '.hdr'], optional=True))
        self.add_trait('transformations_information', File(allowed_extensions=['.mat'], output=True))
        self.add_trait('normalized_t1mri', File(allowed_extensions=['.nii', '.img', '.hdr'], output=True, optional=True))
        self.add_trait('talairach_MNI_transform', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('source_referential', File(optional=True))
        self.add_trait('normalized_referential', File())
        self.add_trait('tal_to_normalized_transform', List())
        self.add_trait('t1mri_nobias', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('hfiltered', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('white_ridges', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('variance', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('edges', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('field', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('meancurvature', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('histo_analysis', File(allowed_extensions=['.han'], output=True))
        self.add_trait('histo', File(output=True))
        self.add_trait('brain_mask', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('skull_stripped', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('anatomical_template_skull_stripped', File(allowed_extensions=['.nii', '.mnc', '.img', '.hdr'], optional=True))
        self.add_trait('split_brain', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('split_template', File(allowed_extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz']))
        self.add_trait('talairach_ACPC_transform', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('left_grey_white', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('right_grey_white', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('perform_meshes_and_graphs', Bool())
        self.add_trait('left_hemi_cortex', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('right_hemi_cortex', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('left_white_mesh', File(allowed_extensions=['.gii', '.mesh', '.obj', '.ply', '.tri'], output=True))
        self.add_trait('right_white_mesh', File(allowed_extensions=['.gii', '.mesh', '.obj', '.ply', '.tri'], output=True))
        self.add_trait('left_skeleton', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('left_roots', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('right_skeleton', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('right_roots', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('left_pial_mesh', File(allowed_extensions=['.gii', '.mesh', '.obj', '.ply', '.tri'], output=True))
        self.add_trait('right_pial_mesh', File(allowed_extensions=['.gii', '.mesh', '.obj', '.ply', '.tri'], output=True))
        self.add_trait('left_graph', File(allowed_extensions=['.arg', '.data'], output=True))
        self.add_trait('left_sulci_voronoi', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('left_cortex_mid_interface', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('right_graph', File(allowed_extensions=['.arg', '.data'], output=True))
        self.add_trait('right_sulci_voronoi', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('right_cortex_mid_interface', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('perform_sulci_recognition', Enum('No', 'SPAM', 'DeepCNN'))
        self.add_trait('labels_translation_map', File(allowed_extensions=['.trl', '.def']))
        self.add_trait('left_labelled_graph', File(allowed_extensions=['.arg', '.data'], output=True))
        self.add_trait('left_posterior_probabilities', File(allowed_extensions=['.csv'], output=True))
        self.add_trait('left_labels_priors', File(allowed_extensions=['.dat']))
        self.add_trait('left_model_file', File(allowed_extensions=['.mdsm']))
        self.add_trait('left_param_file', File(allowed_extensions=['.json']))
        self.add_trait('left_global_model', File(allowed_extensions=['.dat']))
        self.add_trait('left_tal_to_global_transform', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('left_t1_to_global_transform', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('left_local_model', File(allowed_extensions=['.dat']))
        self.add_trait('left_local_referentials', File(allowed_extensions=['.dat']))
        self.add_trait('left_direction_priors', File(allowed_extensions=['.dat']))
        self.add_trait('left_angle_priors', File(allowed_extensions=['.dat']))
        self.add_trait('left_translation_priors', File(allowed_extensions=['.dat']))
        self.add_trait('left_global_to_local_transforms', Directory(allowed_extensions=[''], output=True))
        self.add_trait('right_labelled_graph', File(allowed_extensions=['.arg', '.data'], output=True))
        self.add_trait('right_posterior_probabilities', File(allowed_extensions=['.csv'], output=True))
        self.add_trait('right_labels_priors', File(allowed_extensions=['.dat']))
        self.add_trait('right_model_file', File(allowed_extensions=['.mdsm']))
        self.add_trait('right_param_file', File(allowed_extensions=['.json']))
        self.add_trait('right_global_model', File(allowed_extensions=['.dat']))
        self.add_trait('right_tal_to_global_transform', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('right_t1_to_global_transform', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('right_local_model', File(allowed_extensions=['.dat']))
        self.add_trait('right_local_referentials', File(allowed_extensions=['.dat']))
        self.add_trait('right_direction_priors', File(allowed_extensions=['.dat']))
        self.add_trait('right_angle_priors', File(allowed_extensions=['.dat']))
        self.add_trait('right_translation_priors', File(allowed_extensions=['.dat']))
        self.add_trait('right_global_to_local_transforms', Directory(allowed_extensions=[''], output=True))
        self.add_trait('sulci_file', File(allowed_extensions=['.json']))
        self.add_trait('sulcal_morpho_measures', File(allowed_extensions=['.csv'], output=True))
        self.add_trait('left_csf', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('right_csf', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('subject', Str())
        self.add_trait('sulci_label_attribute', Str())
        self.add_trait('brain_volumes_file', File(allowed_extensions=['.csv'], output=True))
        self.add_trait('report', File(allowed_extensions=['.pdf'], output=True))


        # initialization section
        self.perform_segmentation = True
        self.perform_bias_correction = True
        self.method_ACPC = 'With SPM12 Normalization'
        self.anatomical_template = '/volatile/local/spm12-standalone/spm12_mcr/spm12/spm12/toolbox/OldNorm/T1.nii'
        self.tal_to_normalized_transform = []
        self.anatomical_template_skull_stripped = '/volatile/home/dr144257/casa_distro/condadev/brainvisa-6.0/build/share/brainvisa-share-5.2/anatomical_templates/MNI152_T1_2mm_brain.nii'
        self.split_template = '/volatile/home/dr144257/casa_distro/condadev/brainvisa-6.0/build/share/brainvisa-share-5.2/hemitemplate/closedvoronoi.ima'
        self.perform_meshes_and_graphs = True
        self.perform_sulci_recognition = 'No'
        self.labels_translation_map = '/volatile/home/dr144257/casa_distro/condadev/brainvisa-6.0/build/share/brainvisa-share-5.2/nomenclature/translation/sulci_model_2008.trl'
        self.left_model_file = '/volatile/home/dr144257/casa_distro/condadev/brainvisa-6.0/build/share/brainvisa-share-5.2/models/models_2019/cnn_models/sulci_unet_model_left.mdsm'
        self.left_param_file = '/volatile/home/dr144257/casa_distro/condadev/brainvisa-6.0/build/share/brainvisa-share-5.2/models/models_2019/cnn_models/sulci_unet_model_params_left.json'
        self.right_model_file = '/volatile/home/dr144257/casa_distro/condadev/brainvisa-6.0/build/share/brainvisa-share-5.2/models/models_2019/cnn_models/sulci_unet_model_right.mdsm'
        self.right_param_file = '/volatile/home/dr144257/casa_distro/condadev/brainvisa-6.0/build/share/brainvisa-share-5.2/models/models_2019/cnn_models/sulci_unet_model_params_right.json'
        self.sulci_file = '/volatile/home/dr144257/casa_distro/condadev/brainvisa-6.0/build/share/brainvisa-share-5.2/nomenclature/translation/sulci_default_list.json'

    def _run_process(self):
        from brainvisa import axon
        from brainvisa.configuration import neuroConfig
        import brainvisa.processes

        neuroConfig.gui = False
        neuroConfig.fastStart = True
        neuroConfig.logFileName = ''


        axon.initializeProcesses()

        kwargs = {}
        for name in self.user_traits():
            value = getattr(self, name)
            if value is Undefined:
                continue
            if isinstance(self.trait(name).trait_type, File) and value != '':
                kwargs[name] = value
            elif isinstance(self.trait(name).trait_type, List):
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('morphologistProcess', **kwargs)
