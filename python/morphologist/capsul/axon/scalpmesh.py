# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class ScalpMesh(Process):
    def __init__(self, **kwargs):
        super(ScalpMesh, self).__init__()
        self.add_trait('t1mri_nobias', File(allowed_extensions=['.nii.gz', '.bif', '.czi', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', '.mnc.gz', '.fdf', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '']))
        self.add_trait('histo_analysis', File(allowed_extensions=['.han'], optional=True))
        self.add_trait('head_mesh', File(allowed_extensions=['.gii', '.tri', '.mesh', '.ply', '.obj'], output=True))
        self.add_trait('head_mask', File(allowed_extensions=['.nii.gz', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', ''], output=True, optional=True))
        self.add_trait('keep_head_mask', Bool())
        self.add_trait('remove_mask', File(allowed_extensions=['.nii.gz', '.bif', '.czi', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', '.mnc.gz', '.fdf', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', ''], optional=True))
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
        context.runProcess('headMesh', **kwargs)
