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
        self.add_trait('brain_mask', File(allowed_extensions=['.nii.gz', '', '.img', '.hdr', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif']))
        self.add_trait('t1mri_nobias', File(allowed_extensions=['.nii.gz', '', '.img', '.hdr', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif']))
        self.add_trait('histo_analysis', File(allowed_extensions=['.han']))
        self.add_trait('commissure_coordinates', File(allowed_extensions=['.APC']))
        self.add_trait('use_ridges', Bool())
        self.add_trait('white_ridges', File(allowed_extensions=['.nii.gz', '', '.img', '.hdr', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif']))
        self.add_trait('use_template', Bool())
        self.add_trait('split_template', File(allowed_extensions=['.nii.gz', '', '.img', '.hdr', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif']))
        self.add_trait('mode', Enum('Watershed (2011)', 'Voronoi'))
        self.add_trait('variant', Enum('regularized', 'GW Barycentre', 'WM Standard Deviation'))
        self.add_trait('bary_factor', Enum(0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1))
        self.add_trait('initial_erosion', Float())
        self.add_trait('cc_min_size', Int())
        self.add_trait('split_brain', File(allowed_extensions=['.nii.gz', '', '.img', '.hdr', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff'], output=True))
        self.add_trait('fix_random_seed', Bool())


        # initialization section
        self.use_ridges = True
        self.use_template = True
        self.split_template = '/volatile/riviere/brainvisa/build-trunk-release/share/brainvisa-share-4.5/hemitemplate/closedvoronoi.ima'
        self.mode = 'Watershed (2011)'
        self.variant = 'GW Barycentre'
        self.bary_factor = 0.6
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

        kwargs = dict([(name, getattr(self, name)) \
            for name in self.user_traits() \
            if getattr(self, name) is not Undefined])

        context = brainvisa.processes.defaultContext()
        context.runProcess(self.id.split('.')[-1], **kwargs)
