# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.api import Process


class GreyWhiteMesh(Process):
    def __init__(self, **kwargs):
        super(GreyWhiteMesh, self).__init__()
        self.add_trait('hemi_cortex', File(allowed_extensions=['.nii.gz', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.bif', '.czi', '.mnc.gz', '.fdf', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', '']))
        self.add_trait('white_mesh', File(allowed_extensions=['.gii', '.tri', '.mesh', '.ply', '.obj'], output=True))


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
        context.runProcess('GreyWhiteMesh', **kwargs)
