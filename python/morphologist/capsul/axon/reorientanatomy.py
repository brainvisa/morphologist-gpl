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
        self.add_trait('t1mri', File(allowed_extensions=['.nii.gz', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '']))
        self.add_trait('output_t1mri', File(allowed_extensions=['.nii.gz', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', ''], output=True))
        self.add_trait('transformation', File(allowed_extensions=['.trm']))
        self.add_trait('output_transformation', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('commissures_coordinates', File(allowed_extensions=['.APC'], optional=True))
        self.add_trait('output_commissures_coordinates', File(allowed_extensions=['.APC'], output=True, optional=True))
        self.add_trait('allow_flip_initial_MRI', Bool())


        # initialization section
        self.allow_flip_initial_MRI = True

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
