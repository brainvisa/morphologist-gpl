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
        self.add_trait('source_volume', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '']))
        self.add_trait('write', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('registered_volume', File(allowed_extensions=['.nii.gz', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', ''], optional=True))
        self.add_trait('set_transformation_in_source_volume', Bool())


        # initialization section
        self.registered_volume = u'/i2bm/local/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
        self.set_transformation_in_source_volume = True

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
        context.runProcess('BaladinNormalizationToAims', **kwargs)
