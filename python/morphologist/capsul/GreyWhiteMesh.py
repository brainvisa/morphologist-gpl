# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class GreyWhiteMesh(Process):
    def __init__(self, **kwargs):
        super(GreyWhiteMesh, self).__init__()
        self.add_trait('hemi_cortex', File(allowed_extensions=['.nii.gz', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif']))
        self.add_trait('white_mesh', File(allowed_extensions=['.gii', '.tri', '.mesh', '.ply', '.obj'], output=True))


    def _run_process(self):
        from brainvisa import axon
        from brainvisa.configuration import neuroConfig
        import brainvisa.processes

        neuroConfig.gui = False
        neuroConfig.fastStart = True
        neuroConfig.logFileName = ''

        axon.initializeProcesses()

        kwargs = {name : getattr(self, name) for name in self.user_traits() \
            if getattr(self, name) is not Undefined}

        context = brainvisa.processes.defaultContext()
        context.runProcess(self.id.split('.')[-1], **kwargs)