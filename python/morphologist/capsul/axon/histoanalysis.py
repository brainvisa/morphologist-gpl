# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.api import Process


class HistoAnalysis(Process):
    def __init__(self, **kwargs):
        super(HistoAnalysis, self).__init__()
        self.add_trait('t1mri_nobias', File(allowed_extensions=['.nii.gz', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.bif', '.czi', '.mnc.gz', '.fdf', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', '']))
        self.add_trait('use_hfiltered', Bool())
        self.add_trait('hfiltered', File(allowed_extensions=['.nii.gz', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.bif', '.czi', '.mnc.gz', '.fdf', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', ''], optional=True))
        self.add_trait('use_wridges', Bool())
        self.add_trait('white_ridges', File(allowed_extensions=['.nii.gz', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.bif', '.czi', '.mnc.gz', '.fdf', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', ''], optional=True))
        self.add_trait('undersampling', Enum('2', '4', '8', '16', '32', 'auto', 'iteration'))
        self.add_trait('histo_analysis', File(allowed_extensions=['.han'], output=True))
        self.add_trait('histo', File(output=True))
        self.add_trait('fix_random_seed', Bool())


        # initialization section
        self.use_hfiltered = True
        self.use_wridges = True
        self.undersampling = 'iteration'
        self.fix_random_seed = False

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
        context.runProcess('NobiasHistoAnalysis', **kwargs)
