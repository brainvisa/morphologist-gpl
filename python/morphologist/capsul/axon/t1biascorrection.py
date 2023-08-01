# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process


class T1BiasCorrection(Process):
    def __init__(self, **kwargs):
        super(T1BiasCorrection, self).__init__(**kwargs)
        self.add_field('t1mri', File, read=True, extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('commissure_coordinates', File, read=True,
                       extensions=['.APC'], optional=True)
        self.add_field('sampling', float)
        self.add_field('field_rigidity', float)
        self.add_field('zdir_multiply_regul', float)
        self.add_field('wridges_weight', float)
        self.add_field('ngrid', int)
        self.add_field('background_threshold_auto',
                       Literal['no', 'corners', 'otsu'])
        self.add_field('delete_last_n_slices', str, trait=str(),
                       default_value='auto (AC/PC Points needed)')
        self.add_field('t1mri_nobias', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('mode', Literal['write_minimal', 'write_all',
                       'delete_useless', 'write_minimal without correction'])
        self.add_field('write_field', Literal['yes', 'no'])
        self.add_field('b_field', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg', '.mnc',
                       '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'], optional=True)
        self.add_field('write_hfiltered', Literal['yes', 'no'])
        self.add_field('hfiltered', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('write_wridges', Literal['yes', 'no', 'read'])
        self.add_field('white_ridges', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('variance_fraction', int)
        self.add_field('write_variance', Literal['yes', 'no'])
        self.add_field('variance', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('edge_mask', Literal['yes', 'no'])
        self.add_field('write_edges', Literal['yes', 'no'])
        self.add_field('edges', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('write_meancurvature', Literal['yes', 'no'])
        self.add_field('meancurvature', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg', '.mnc',
                       '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'], optional=True)
        self.add_field('fix_random_seed', bool)
        self.add_field('modality', Literal['T1', 'T2'])
        self.add_field('use_existing_ridges', bool)

        # initialization section
        self.sampling = 16.0
        self.field_rigidity = 20.0
        self.zdir_multiply_regul = 0.5
        self.wridges_weight = 20.0
        self.ngrid = 2
        self.background_threshold_auto = 'corners'
        self.delete_last_n_slices = 'auto (AC/PC Points needed)'
        self.mode = 'write_minimal'
        self.write_field = 'no'
        self.write_hfiltered = 'yes'
        self.write_wridges = 'yes'
        self.variance_fraction = 75
        self.write_variance = 'yes'
        self.edge_mask = 'yes'
        self.write_edges = 'yes'
        self.write_meancurvature = 'no'
        self.fix_random_seed = False
        self.modality = 'T1'
        self.use_existing_ridges = False

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
            # patch forbidden field name "field"
            if name == 'b_field':
                name = 'field'
            if field.path_type and value != '':
                kwargs[name] = value
            elif field.is_list():
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('T1BiasCorrection', **kwargs)
