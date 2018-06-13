# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

from capsul.api import Process
import six


class ScalpMesh(Process):
    def __init__(self, **kwargs):
        super(ScalpMesh, self).__init__()
        self.add_trait('t1mri_nobias', File(allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn',
                                                                '.mnc', '.mng', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz']))
        self.add_trait('histo_analysis', File(
            allowed_extensions=['.han'], optional=True))
        self.add_trait('head_mesh', File(allowed_extensions=[
                       '.gii', '.mesh', '.obj', '.ply', '.tri'], output=True))
        self.add_trait('head_mask', File(allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.gif', '.ima', '.dim', '.jpg', '.mnc', '.mng', '.nii',
                                                             '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'], output=True, optional=True))
        self.add_trait('keep_head_mask', Bool())
        self.add_trait('remove_mask', File(allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc',
                                                               '.mng', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'], optional=True))
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
            if isinstance(self.trait(name).trait_type, File) and value != '' and value is not Undefined:
                kwargs[name] = value
            elif isinstance(self.trait(name).trait_type, List):
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('headMesh', **kwargs)
