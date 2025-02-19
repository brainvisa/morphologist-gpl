# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class morphologistProcess(Process):
    def __init__(self, **kwargs):
        super(morphologistProcess, self).__init__(**kwargs)
        self.add_field('t1mri', File, read=True, extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('perform_segmentation', bool)
        self.add_field('perform_bias_correction', bool)
        self.add_field(
            'method_ACPC', Literal['Manually', 'With SPM12 Normalization', 'Already done'])
        self.add_field('commissure_coordinates', File,
                       write=True, extensions=['.APC'])
        self.add_field('anterior_commissure', conlist(
            float, min_items=3, max_items=3), default_factory=lambda: [0, 0, 0], optional=True)
        self.add_field('posterior_commissure', conlist(
            float, min_items=3, max_items=3), default_factory=lambda: [0, 0, 0], optional=True)
        self.add_field('interhemispheric_point', conlist(
            float, min_items=3, max_items=3), default_factory=lambda: [0, 0, 0], optional=True)
        self.add_field('left_hemisphere_point', conlist(
            float, min_items=3, max_items=3), default_factory=lambda: [0, 0, 0], optional=True)
        self.add_field('older_MNI_normalization', File,
                       read=True, extensions=['.trm'], optional=True)
        self.add_field('anatomical_template', File, read=True, extensions=[
                       '.nii', '.mnc', '.img', '.hdr'], optional=True)
        self.add_field('transformations_information', File,
                       write=True, extensions=['.mat'])
        self.add_field('normalized_t1mri', File, write=True, extensions=[
                       '.nii', '.img', '.hdr'], optional=True)
        self.add_field('talairach_MNI_transform', File,
                       write=True, extensions=['.trm'])
        self.add_field('source_referential', File, read=True, optional=True)
        self.add_field('normalized_referential', File, read=True)
        self.add_field('tal_to_normalized_transform', list)
        self.add_field('t1mri_nobias', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('hfiltered', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('white_ridges', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('variance', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('edges', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('b_field', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('meancurvature', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('histo_analysis', File, write=True, extensions=['.han'])
        self.add_field('histo', File, write=True)
        self.add_field('brain_mask', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('skull_stripped', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('anatomical_template_skull_stripped', File, read=True, extensions=[
                       '.nii', '.mnc', '.img', '.hdr'], optional=True)
        self.add_field('split_brain', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('split_template', File, read=True, extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('talairach_ACPC_transform', File,
                       write=True, extensions=['.trm'])
        self.add_field('left_grey_white', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('right_grey_white', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('perform_meshes_and_graphs', bool)
        self.add_field('left_hemi_cortex', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('right_hemi_cortex', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim',
                       '.jpg', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('left_white_mesh', File, write=True, extensions=[
                       '.gii', '.mesh', '.obj', '.ply', '.tri'])
        self.add_field('right_white_mesh', File, write=True, extensions=[
                       '.gii', '.mesh', '.obj', '.ply', '.tri'])
        self.add_field('left_skeleton', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('left_roots', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('right_skeleton', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('right_roots', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('left_pial_mesh', File, write=True, extensions=[
                       '.gii', '.mesh', '.obj', '.ply', '.tri'])
        self.add_field('right_pial_mesh', File, write=True, extensions=[
                       '.gii', '.mesh', '.obj', '.ply', '.tri'])
        self.add_field('left_graph', File, write=True,
                       extensions=['.arg', '.data'])
        self.add_field('left_sulci_voronoi', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim',
                       '.jpg', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('left_cortex_mid_interface', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim',
                       '.jpg', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('right_graph', File, write=True,
                       extensions=['.arg', '.data'])
        self.add_field('right_sulci_voronoi', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim',
                       '.jpg', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('right_cortex_mid_interface', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim',
                       '.jpg', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('perform_sulci_recognition',
                       Literal['No', 'SPAM', 'DeepCNN'])
        self.add_field('labels_translation_map', File,
                       read=True, extensions=['.trl', '.def'])
        self.add_field('left_labelled_graph', File, write=True,
                       extensions=['.arg', '.data'])
        self.add_field('left_posterior_probabilities', File,
                       write=True, extensions=['.csv'])
        self.add_field('left_labels_priors', File,
                       read=True, extensions=['.dat'])
        self.add_field('left_model_file', File,
                       read=True, extensions=['.mdsm'])
        self.add_field('left_param_file', File,
                       read=True, extensions=['.json'])
        self.add_field('left_global_model', File,
                       read=True, extensions=['.dat'])
        self.add_field('left_tal_to_global_transform', File,
                       write=True, extensions=['.trm'])
        self.add_field('left_t1_to_global_transform', File,
                       write=True, extensions=['.trm'])
        self.add_field('left_local_model', File,
                       read=True, extensions=['.dat'])
        self.add_field('left_local_referentials', File,
                       read=True, extensions=['.dat'])
        self.add_field('left_direction_priors', File,
                       read=True, extensions=['.dat'])
        self.add_field('left_angle_priors', File,
                       read=True, extensions=['.dat'])
        self.add_field('left_translation_priors', File,
                       read=True, extensions=['.dat'])
        self.add_field('left_global_to_local_transforms',
                       Directory, write=True, extensions=[''])
        self.add_field('right_labelled_graph', File,
                       write=True, extensions=['.arg', '.data'])
        self.add_field('right_posterior_probabilities',
                       File, write=True, extensions=['.csv'])
        self.add_field('right_labels_priors', File,
                       read=True, extensions=['.dat'])
        self.add_field('right_model_file', File,
                       read=True, extensions=['.mdsm'])
        self.add_field('right_param_file', File,
                       read=True, extensions=['.json'])
        self.add_field('right_global_model', File,
                       read=True, extensions=['.dat'])
        self.add_field('right_tal_to_global_transform',
                       File, write=True, extensions=['.trm'])
        self.add_field('right_t1_to_global_transform', File,
                       write=True, extensions=['.trm'])
        self.add_field('right_local_model', File,
                       read=True, extensions=['.dat'])
        self.add_field('right_local_referentials', File,
                       read=True, extensions=['.dat'])
        self.add_field('right_direction_priors', File,
                       read=True, extensions=['.dat'])
        self.add_field('right_angle_priors', File,
                       read=True, extensions=['.dat'])
        self.add_field('right_translation_priors', File,
                       read=True, extensions=['.dat'])
        self.add_field('right_global_to_local_transforms',
                       Directory, write=True, extensions=[''])
        self.add_field('sulci_file', File, read=True, extensions=['.json'])
        self.add_field('sulcal_morpho_measures', File,
                       write=True, extensions=['.csv'])
        self.add_field('left_csf', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('right_csf', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('subject', str)
        self.add_field('sulci_label_attribute', str)
        self.add_field('brain_volumes_file', File,
                       write=True, extensions=['.csv'])
        self.add_field('report', File, write=True, extensions=['.pdf'])

        # initialization section
        self.perform_segmentation = True
        self.perform_bias_correction = True
        self.method_ACPC = 'With SPM12 Normalization'
        self.anatomical_template = '/volatile/local/spm12-standalone/spm12_mcr/spm12/spm12/toolbox/OldNorm/T1.nii'
        self.tal_to_normalized_transform = []
        self.anatomical_template_skull_stripped = '/volatile/riviere/casa-distro/conda/brainvisa-6.0/build/share/brainvisa-share-5.2/anatomical_templates/MNI152_T1_2mm_brain.nii'
        self.split_template = '/volatile/riviere/casa-distro/conda/brainvisa-6.0/build/share/brainvisa-share-5.2/hemitemplate/closedvoronoi.ima'
        self.perform_meshes_and_graphs = True
        self.perform_sulci_recognition = 'No'
        self.labels_translation_map = '/casa/host/build/share/brainvisa-share-5.2/nomenclature/translation/sulci_model_2008.trl'
        self.left_model_file = '/casa/host/build/share/brainvisa-share-5.2/models/models_2019/cnn_models/sulci_unet_model_left.mdsm'
        self.left_param_file = '/casa/host/build/share/brainvisa-share-5.2/models/models_2019/cnn_models/sulci_unet_model_params_left.json'
        self.left_global_model = '/casa/host/build/share/brainvisa-share-5.2/models/models_2008/descriptive_models/segments/global_registered_spam_left/spam_distribs.dat'
        self.left_local_model = '/casa/host/build/share/brainvisa-share-5.2/models/models_2008/descriptive_models/segments/locally_from_global_registred_spam_left/spam_distribs.dat'
        self.right_model_file = '/casa/host/build/share/brainvisa-share-5.2/models/models_2019/cnn_models/sulci_unet_model_right.mdsm'
        self.right_param_file = '/casa/host/build/share/brainvisa-share-5.2/models/models_2019/cnn_models/sulci_unet_model_params_right.json'
        self.right_global_model = '/casa/host/build/share/brainvisa-share-5.2/models/models_2008/descriptive_models/segments/global_registered_spam_right/spam_distribs.dat'
        self.right_local_model = '/casa/host/build/share/brainvisa-share-5.2/models/models_2008/descriptive_models/segments/locally_from_global_registred_spam_right/spam_distribs.dat'
        self.sulci_file = '/casa/host/build/share/brainvisa-share-5.2/nomenclature/translation/sulci_default_list.json'

    def execute(self, context=None):
        from brainvisa import axon
        from brainvisa.configuration import neuroConfig
        import brainvisa.processes

        neuroConfig.gui = False
        neuroConfig.fastStart = True
        neuroConfig.logFileName = ''


        axon.initializeProcesses()

        kwargs = {}
        for field in self.fields():
            name = field.name
            value = getattr(self, name)
            if value is undefined:
                continue
            # patch forbidden field name "field"
            if name == 'b_field':
                name = 'field'
            if field.path_type and value != '':
                kwargs[name] = value
            elif field.is_list():
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('morphologistProcess', **kwargs)
