# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class TalairachTransformation(Process):
    def __init__(self, **kwargs):
        super(TalairachTransformation, self).__init__()
        self.add_trait('split_mask', File(allowed_extensions=['.nii.gz', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '']))
        self.add_trait('commissure_coordinates', File(allowed_extensions=['.APC']))
        self.add_trait('Talairach_transform', File(allowed_extensions=['.trm'], output=True))


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
        context.runProcess('TalairachTransformation', **kwargs)