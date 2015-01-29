# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class T1BiasCorrection(Process):
    def __init__(self, **kwargs):
        super(T1BiasCorrection, self).__init__()
        self.add_trait('t1mri', File(allowed_extensions=['.nii.gz', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '']))
        self.add_trait('commissure_coordinates', File(allowed_extensions=['.APC'], optional=True))
        self.add_trait('sampling', Float())
        self.add_trait('field_rigidity', Float())
        self.add_trait('zdir_multiply_regul', Float())
        self.add_trait('wridges_weight', Float())
        self.add_trait('ngrid', Int())
        self.add_trait('delete_last_n_slices', Str(trait=Str(), default_value='auto (AC/PC Points needed)'))
        self.add_trait('t1mri_nobias', File(allowed_extensions=['.nii.gz', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', ''], output=True))
        self.add_trait('mode', Enum('write_minimal', 'write_all', 'delete_useless', 'write_minimal without correction'))
        self.add_trait('write_field', Enum('yes', 'no'))
        self.add_trait('field', File(allowed_extensions=['.nii.gz', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', ''], output=True))
        self.add_trait('write_hfiltered', Enum('yes', 'no'))
        self.add_trait('hfiltered', File(allowed_extensions=['.nii.gz', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', ''], output=True))
        self.add_trait('write_wridges', Enum('yes', 'no', 'read'))
        self.add_trait('white_ridges', File(allowed_extensions=['.nii.gz', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', ''], output=True))
        self.add_trait('variance_fraction', Int())
        self.add_trait('write_variance', Enum('yes', 'no'))
        self.add_trait('variance', File(allowed_extensions=['.nii.gz', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', ''], output=True))
        self.add_trait('edge_mask', Enum('yes', 'no'))
        self.add_trait('write_edges', Enum('yes', 'no'))
        self.add_trait('edges', File(allowed_extensions=['.nii.gz', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', ''], output=True))
        self.add_trait('write_meancurvature', Enum('yes', 'no'))
        self.add_trait('meancurvature', File(allowed_extensions=['.nii.gz', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', ''], output=True))
        self.add_trait('fix_random_seed', Bool())


        # initialization section
        self.sampling = 16.0
        self.field_rigidity = 20.0
        self.zdir_multiply_regul = 0.5
        self.wridges_weight = 20.0
        self.ngrid = 2
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
