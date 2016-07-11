# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class SplitBrain(Process):
    def __init__(self, **kwargs):
        super(SplitBrain, self).__init__()
        self.add_trait('brain_mask', File(allowed_extensions=['.nii.gz', '.bif', '.czi', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', '.mnc.gz', '.fdf', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '']))
        self.add_trait('t1mri_nobias', File(allowed_extensions=['.nii.gz', '.bif', '.czi', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', '.mnc.gz', '.fdf', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '']))
        self.add_trait('histo_analysis', File(allowed_extensions=['.han']))
        self.add_trait('commissure_coordinates', File(allowed_extensions=['.APC'], optional=True))
        self.add_trait('use_ridges', Bool())
        self.add_trait('white_ridges', File(allowed_extensions=['.nii.gz', '.bif', '.czi', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', '.mnc.gz', '.fdf', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '']))
        self.add_trait('use_template', Bool())
        self.add_trait('split_template', File(allowed_extensions=['.nii.gz', '.bif', '.czi', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', '.mnc.gz', '.fdf', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '']))
        self.add_trait('mode', Enum('Watershed (2011)', 'Voronoi'))
        self.add_trait('variant', Enum('regularized', 'GW Barycentre', 'WM Standard Deviation'))
        self.add_trait('bary_factor', Enum(0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1))
        self.add_trait('mult_factor', Enum(0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, optional=True))
        self.add_trait('initial_erosion', Float())
        self.add_trait('cc_min_size', Int())
        self.add_trait('split_brain', File(allowed_extensions=['.nii.gz', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', ''], output=True))
        self.add_trait('fix_random_seed', Bool())


        # initialization section
        self.use_ridges = True
        self.use_template = True
        self.split_template = '/volatile/riviere/brainvisa/build-stable-release/share/brainvisa-share-4.5/hemitemplate/closedvoronoi.ima'
        self.mode = 'Watershed (2011)'
        self.variant = 'GW Barycentre'
        self.bary_factor = 0.6
        self.mult_factor = 2
        self.initial_erosion = 2.0
        self.cc_min_size = 500
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
        context.runProcess('SplitBrain', **kwargs)
