# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class SplitBrain(Process):
    def __init__(self, **kwargs):
        super(SplitBrain, self).__init__(**kwargs)
        self.add_field('brain_mask', File, read=True, extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('t1mri_nobias', File, read=True, extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('histo_analysis', File, read=True, extensions=['.han'])
        self.add_field('commissure_coordinates', File, read=True,
                       extensions=['.APC'], optional=True)
        self.add_field('use_ridges', bool)
        self.add_field('white_ridges', File, read=True, extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('use_template', bool)
        self.add_field('split_template', File, read=True, extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('mode', Literal['Watershed (2011)', 'Voronoi'])
        self.add_field(
            'variant', Literal['regularized', 'GW Barycentre', 'WM Standard Deviation'])
        self.add_field(
            'bary_factor', Literal[0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1])
        self.add_field(
            'mult_factor', Literal[0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4], optional=True)
        self.add_field('initial_erosion', float)
        self.add_field('cc_min_size', int)
        self.add_field('split_brain', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('fix_random_seed', bool)

        # initialization section
        self.use_ridges = True
        self.use_template = True
        self.split_template = '/casa/host/build/share/brainvisa-share-5.2/hemitemplate/closedvoronoi.ima'
        self.mode = 'Watershed (2011)'
        self.variant = 'GW Barycentre'
        self.bary_factor = 0.6
        self.mult_factor = 2
        self.initial_erosion = 2.0
        self.cc_min_size = 500
        self.fix_random_seed = False

    def execute(self, context=None):
        from brainvisa import axon
        from brainvisa.configuration import neuroConfig
        import brainvisa.processes

        neuroConfig.gui = False
        neuroConfig.fastStart = True
        neuroConfig.logFileName = ''

        axon.initializeProcesses()

        kwargs = {}
        for field in self.fields():
            name = field.name
            value = getattr(self, name)
            if value is undefined:
                continue
            if field.path_type and value != '':
                kwargs[name] = value
            elif field.is_list():
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('SplitBrain', **kwargs)
