# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class BrainSegmentation(Process):
    def __init__(self, **kwargs):
        super(BrainSegmentation, self).__init__()
        self.add_trait('t1mri_nobias', File(allowed_extensions=['.nii.gz', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.jpg', '.gif', '.png', '.mng', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '']))
        self.add_trait('histo_analysis', File(allowed_extensions=['.han']))
        self.add_trait('variance', File(allowed_extensions=['.nii.gz', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.jpg', '.gif', '.png', '.mng', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '']))
        self.add_trait('edges', File(allowed_extensions=['.nii.gz', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.jpg', '.gif', '.png', '.mng', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '']))
        self.add_trait('white_ridges', File(allowed_extensions=['.nii.gz', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.jpg', '.gif', '.png', '.mng', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', ''], optional=True))
        self.add_trait('commissure_coordinates', File(allowed_extensions=['.APC'], optional=True))
        self.add_trait('lesion_mask', File(allowed_extensions=['.nii.gz', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.jpg', '.gif', '.png', '.mng', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', ''], optional=True))
        self.add_trait('variant', Enum('2010', '2005 based on white ridge', 'Standard + (iterative erosion)', 'Standard + (selected erosion)', 'Standard + (iterative erosion) without regularisation', 'Robust + (iterative erosion)', 'Robust + (selected erosion)', 'Robust + (iterative erosion) without regularisation', 'Fast (selected erosion)'))
        self.add_trait('erosion_size', Float(trait=Float(), default_value=1))
        self.add_trait('visu', Enum('No', 'Yes'))
        self.add_trait('layer', Enum(0, 1, 2, 3, 4, 5))
        self.add_trait('first_slice', Int())
        self.add_trait('last_slice', Int())
        self.add_trait('brain_mask', File(allowed_extensions=['.nii.gz', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.jpg', '.gif', '.png', '.mng', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', ''], output=True))
        self.add_trait('fix_random_seed', Bool())


        # initialization section
        self.variant = '2010'
        self.erosion_size = 1.8
        self.visu = 'No'
        self.layer = 0
        self.first_slice = 0
        self.last_slice = 0
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
