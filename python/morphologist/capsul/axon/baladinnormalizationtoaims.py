# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class BaladinNormalizationToAims(Process):
    def __init__(self, **kwargs):
        super(BaladinNormalizationToAims, self).__init__()
        self.add_trait('read', File(allowed_extensions=['.txt']))
        self.add_trait('source_volume', File(allowed_extensions=['.nii.gz', '.bif', '.czi', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', '.mnc.gz', '.fdf', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '']))
        self.add_trait('write', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('registered_volume', File(allowed_extensions=['.nii.gz', '.bif', '.czi', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', '.mnc.gz', '.fdf', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', ''], optional=True))
        self.add_trait('set_transformation_in_source_volume', Bool())


        # initialization section
        self.registered_volume = u'/i2bm/local/fsl/data/standard/MNI152_T1_1mm.nii.gz'
        self.set_transformation_in_source_volume = True

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
            if isinstance(self.trait(name).trait_type, File) and value != ''                     and value is not Undefined:
                kwargs[name] = value
            elif isinstance(self.trait(name).trait_type, List):
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('BaladinNormalizationToAims', **kwargs)
