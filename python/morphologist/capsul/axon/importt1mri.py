# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.api import Process


class ImportT1MRI(Process):
    def __init__(self, **kwargs):
        super(ImportT1MRI, self).__init__()
        self.add_trait('input', File(allowed_extensions=['.nii.gz', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.bif', '.nii', '.jpg', '.gif', '.png', '.mng',
                                                         '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '']))
        self.add_trait('output', File(allowed_extensions=[
                       '.nii.gz', '.nii', '.ima', '.dim'], output=True))
        self.add_trait('referential', File(output=True, optional=True))

    def _run_process(self):
        from brainvisa import axon
        from brainvisa.configuration import neuroConfig
        import brainvisa.processes

        neuroConfig.gui = False
        neuroConfig.fastStart = True
        neuroConfig.logFileName = ''

        axon.initializeProcesses()

        kwargs = dict([(name, getattr(self, name))
                       for name in self.user_traits()
                       if getattr(self, name) is not Undefined and
                       (not isinstance(self.user_traits()[name].trait_type, File)
                        or getattr(self, name) != '')])

        context = brainvisa.processes.defaultContext()
        context.runProcess('ImportT1MRI', **kwargs)
