# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class hemispheremesh(Process):
    def __init__(self, **kwargs):
        super(hemispheremesh, self).__init__()
        self.add_trait('hemi_cortex', File(allowed_extensions=['.nii.gz', '', '.img', '.hdr', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif']))
        self.add_trait('grey_white', File(allowed_extensions=['.nii.gz', '', '.img', '.hdr', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif']))
        self.add_trait('t1mri_nobias', File(allowed_extensions=['.nii.gz', '', '.img', '.hdr', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif']))
        self.add_trait('skeleton', File(allowed_extensions=['.nii.gz', '', '.img', '.hdr', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif']))
        self.add_trait('pial_mesh', File(allowed_extensions=['.gii', '.tri', '.mesh', '.ply', '.obj'], output=True))
        self.add_trait('fix_random_seed', Bool())


        # initialization section
        self.fix_random_seed = False

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
            if getattr(self, name) is not Undefined])

        context = brainvisa.processes.defaultContext()
        context.runProcess(self.id.split('.')[-1], **kwargs)
