# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

from capsul.api import Process
import six


class normalization_aimsmiregister(Process):
    def __init__(self, **kwargs):
        super(normalization_aimsmiregister, self).__init__(**kwargs)
        self.add_trait('anatomy_data', File(allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz']))
        self.add_trait('anatomical_template', File(allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz']))
        self.add_trait('transformation_to_template', File(
            allowed_extensions=['.trm'], output=True, optional=True))
        self.add_trait('normalized_anatomy_data', File(allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg', '.mnc',
                       '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'], output=True, optional=True))
        self.add_trait('transformation_to_MNI', File(
            allowed_extensions=['.trm'], output=True, optional=True))
        self.add_trait('transformation_to_ACPC', File(
            allowed_extensions=['.trm'], output=True, optional=True))
        self.add_trait('mni_to_acpc', File(
            allowed_extensions=['.trm'], optional=True))
        self.add_trait('smoothing', Float())

        # initialization section
        self.anatomical_template = '/casa/host/build/share/brainvisa-share-5.2/anatomical_templates/MNI152_T1_2mm.nii.gz'
        self.mni_to_acpc = '/casa/host/build/share/brainvisa-share-5.2/transformation/talairach_TO_spm_template_novoxels.trm'
        self.smoothing = 1.0

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
        context.runProcess('normalization_aimsmiregister', **kwargs)
