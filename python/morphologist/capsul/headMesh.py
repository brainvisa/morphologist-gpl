# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class headMesh(Process):
    def __init__(self, **kwargs):
        super(headMesh, self).__init__()
        self.add_trait('t1mri_nobias', File(allowed_extensions=['.nii.gz', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.img', '.hdr', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '']))
        self.add_trait('histo_analysis', File(allowed_extensions=['.han'], optional=True))
        self.add_trait('head_mesh', File(allowed_extensions=['.gii', '.tri', '.mesh', '.ply', '.obj'], output=True))
        self.add_trait('head_mask', File(allowed_extensions=['.nii.gz', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.img', '.hdr', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', ''], output=True, optional=True))
        self.add_trait('keep_head_mask', Bool())
        self.add_trait('remove_mask', File(allowed_extensions=['.nii.gz', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.img', '.hdr', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', ''], optional=True))
        self.add_trait('first_slice', Int(optional=True))
        self.add_trait('threshold', Int(optional=True))
        self.add_trait('closing', Float(optional=True))


        # initialization section
        self.keep_head_mask = False
        self.first_slice = Undefined
        self.threshold = Undefined
        self.closing = Undefined

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
        context.runProcess(self.id.split('.')[-1], **kwargs)
