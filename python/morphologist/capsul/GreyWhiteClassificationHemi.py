# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class GreyWhiteClassificationHemi(Process):
    def __init__(self, **kwargs):
        super(GreyWhiteClassificationHemi, self).__init__()
        self.add_trait('side', Enum('left', 'right'))
        self.add_trait('t1mri_nobias', File(allowed_extensions=['.nii.gz', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '']))
        self.add_trait('histo_analysis', File(allowed_extensions=['.han']))
        self.add_trait('split_brain', File(allowed_extensions=['.nii.gz', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '']))
        self.add_trait('edges', File(allowed_extensions=['.nii.gz', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '']))
        self.add_trait('commissure_coordinates', File(allowed_extensions=['.APC']))
        self.add_trait('grey_white', File(allowed_extensions=['.nii.gz', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', ''], output=True))
        self.add_trait('fix_random_seed', Bool())


        # initialization section
        self.side = 'left'
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
            if getattr(self, name) is not Undefined and \
                (not isinstance(self.user_traits()[name].trait_type, File) \
                    or getattr(self, name) != '')])

        context = brainvisa.processes.defaultContext()
        context.runProcess(self.id.split('.')[-1], **kwargs)
