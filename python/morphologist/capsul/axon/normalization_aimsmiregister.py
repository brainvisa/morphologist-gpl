# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class normalization_aimsmiregister(Process):
    def __init__(self, **kwargs):
        super(normalization_aimsmiregister, self).__init__()
        self.add_trait('anatomy_data', File(allowed_extensions=['.nii.gz', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.bif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '']))
        self.add_trait('anatomical_template', File(allowed_extensions=['.nii.gz', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.bif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '']))
        self.add_trait('transformation_to_template', File(allowed_extensions=['.trm'], output=True, optional=True))
        self.add_trait('normalized_anatomy_data', File(allowed_extensions=['.nii.gz', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', ''], output=True, optional=True))
        self.add_trait('transformation_to_MNI', File(allowed_extensions=['.trm'], output=True, optional=True))
        self.add_trait('transformation_to_ACPC', File(allowed_extensions=['.trm'], output=True, optional=True))
        self.add_trait('mni_to_acpc', File(allowed_extensions=['.trm'], optional=True))
        self.add_trait('smoothing', Float())


        # initialization section
        self.anatomical_template = u'/i2bm/local/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
        self.mni_to_acpc = '/volatile/riviere/brainvisa/build-stable-release/share/brainvisa-share-4.5/transformation/talairach_TO_spm_template_novoxels.trm'
        self.smoothing = 1.0

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
        context.runProcess('normalization_aimsmiregister', **kwargs)
