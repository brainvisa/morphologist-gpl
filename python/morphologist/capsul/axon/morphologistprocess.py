# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class morphologistProcess(Process):
    def __init__(self, **kwargs):
        super(morphologistProcess, self).__init__()
        self.add_trait('t1mri', File(allowed_extensions=['.nii.gz', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.bif', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '']))
        self.add_trait('perform_segmentation', Bool())
        self.add_trait('method_ACPC', Enum('Manually', 'With SPM Normalization', 'Already done'))
        self.add_trait('commissure_coordinates', File(allowed_extensions=['.APC'], output=True))
        self.add_trait('anterior_commissure', List(trait=Float(), minlen=3, maxlen=3, value=[0, 0, 0], optional=True))
        self.add_trait('posterior_commissure', List(trait=Float(), minlen=3, maxlen=3, value=[0, 0, 0], optional=True))
        self.add_trait('interhemispheric_point', List(trait=Float(), minlen=3, maxlen=3, value=[0, 0, 0], optional=True))
        self.add_trait('left_hemisphere_point', List(trait=Float(), minlen=3, maxlen=3, value=[0, 0, 0], optional=True))
        self.add_trait('older_MNI_normalization', File(allowed_extensions=['.trm'], optional=True))
        self.add_trait('anatomical_template', File(allowed_extensions=['.nii', '.mnc', '.img', '.hdr'], optional=True))
        self.add_trait('job_file', File(allowed_extensions=['.mat'], output=True, optional=True))
        self.add_trait('transformations_information', File(allowed_extensions=['.mat'], output=True))
        self.add_trait('normalized_t1mri', File(allowed_extensions=['.nii', '.img', '.hdr'], output=True))
        self.add_trait('talairach_MNI_transform', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('source_referential', File())
        self.add_trait('normalized_referential', File())
        self.add_trait('tal_to_normalized_transform', List())
        self.add_trait('t1mri_nobias', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('hfiltered', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('white_ridges', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('variance', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('edges', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('field', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('meancurvature', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('histo_analysis', File(allowed_extensions=['.han'], output=True))
        self.add_trait('histo', File(output=True))
        self.add_trait('brain_mask', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('skull_stripped', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('anatomical_template_skull_stripped', File(allowed_extensions=['.nii', '.mnc', '.img', '.hdr'], optional=True))
        self.add_trait('split_brain', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('split_template', File(allowed_extensions=['.nii.gz', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.bif', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '']))
        self.add_trait('talairach_ACPC_transform', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('left_grey_white', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('right_grey_white', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('perform_meshes_and_graphs', Bool())
        self.add_trait('left_hemi_cortex', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('right_hemi_cortex', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('left_white_mesh', File(allowed_extensions=['.gii', '.tri', '.mesh', '.ply', '.obj'], output=True))
        self.add_trait('right_white_mesh', File(allowed_extensions=['.gii', '.tri', '.mesh', '.ply', '.obj'], output=True))
        self.add_trait('left_skeleton', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('left_roots', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('right_skeleton', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('right_roots', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('left_pial_mesh', File(allowed_extensions=['.gii', '.tri', '.mesh', '.ply', '.obj'], output=True))
        self.add_trait('right_pial_mesh', File(allowed_extensions=['.gii', '.tri', '.mesh', '.ply', '.obj'], output=True))
        self.add_trait('left_graph', File(allowed_extensions=['.arg', '.data'], output=True))
        self.add_trait('left_sulci_voronoi', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('left_cortex_mid_interface', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('right_graph', File(allowed_extensions=['.arg', '.data'], output=True))
        self.add_trait('right_sulci_voronoi', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('right_cortex_mid_interface', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], output=True))
        self.add_trait('perform_sulci_SPAM_recognition', Bool())
        self.add_trait('labels_translation_map', File(allowed_extensions=['.trl', '.def']))
        self.add_trait('left_labelled_graph', File(allowed_extensions=['.arg', '.data'], output=True))
        self.add_trait('left_posterior_probabilities', File(allowed_extensions=['.csv'], output=True))
        self.add_trait('left_labels_priors', File(allowed_extensions=['.dat']))
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


        # initialization section
        self.perform_segmentation = True
        self.method_ACPC = 'Manually'
        self.anatomical_template = u'/i2bm/local/spm8-standalone/spm8_mcr/spm8/templates/T1.nii'
        self.tal_to_normalized_transform = []
        self.split_template = '/volatile/riviere/brainvisa/build-stable-release/share/brainvisa-share-4.5/hemitemplate/closedvoronoi.ima'
        self.perform_meshes_and_graphs = True
        self.perform_sulci_SPAM_recognition = False
        self.labels_translation_map = '/volatile/riviere/brainvisa/build-stable-release/share/brainvisa-share-4.5/nomenclature/translation/sulci_model_2008.trl'
        self.left_global_model = '/volatile/riviere/brainvisa/build-stable-release/share/brainvisa-share-4.5/models/models_2008/descriptive_models/segments/global_registered_spam_left/spam_distribs.dat'
        self.left_local_model = '/volatile/riviere/brainvisa/build-stable-release/share/brainvisa-share-4.5/models/models_2008/descriptive_models/segments/locally_from_global_registred_spam_left/spam_distribs.dat'
        self.right_global_model = '/volatile/riviere/brainvisa/build-stable-release/share/brainvisa-share-4.5/models/models_2008/descriptive_models/segments/global_registered_spam_right/spam_distribs.dat'
        self.right_local_model = '/volatile/riviere/brainvisa/build-stable-release/share/brainvisa-share-4.5/models/models_2008/descriptive_models/segments/locally_from_global_registred_spam_right/spam_distribs.dat'
        self.sulci_file = '/volatile/riviere/brainvisa/build-stable-release/share/brainvisa-share-4.5/nomenclature/translation/sulci_default_list.json'

    def _run_process(self):
        from brainvisa import axon
        from brainvisa.configuration import neuroConfig
        import brainvisa.processes

        neuroConfig.gui = False
        neuroConfig.fastStart = True
        neuroConfig.logFileName = ''

        axon.initializeProcesses()

        kwargs = dict([(name, getattr(self, name)) \
            for name in self.user_traits() \
            if getattr(self, name) is not Undefined and \
                (not isinstance(self.user_traits()[name].trait_type, File) \
                    or getattr(self, name) != '')])

        context = brainvisa.processes.defaultContext()
        context.runProcess('morphologistProcess', **kwargs)
