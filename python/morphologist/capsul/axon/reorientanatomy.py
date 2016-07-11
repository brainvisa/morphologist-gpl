# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class ReorientAnatomy(Process):
    def __init__(self, **kwargs):
        super(ReorientAnatomy, self).__init__()
        self.add_trait('t1mri', File(allowed_extensions=['.nii.gz', '.bif', '.czi', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', '.mnc.gz', '.fdf', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '']))
        self.add_trait('output_t1mri', File(allowed_extensions=['.nii.gz', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', ''], output=True))
        self.add_trait('transformation', File(allowed_extensions=['.trm']))
        self.add_trait('output_transformation', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('commissures_coordinates', File(allowed_extensions=['.APC'], optional=True))
        self.add_trait('output_commissures_coordinates', File(allowed_extensions=['.APC'], output=True, optional=True))
        self.add_trait('allow_flip_initial_MRI', Bool())


        # initialization section
        self.allow_flip_initial_MRI = False

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
        context.runProcess('reorientAnatomy', **kwargs)
