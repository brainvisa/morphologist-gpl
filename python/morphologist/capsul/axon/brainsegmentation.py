# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process


class BrainSegmentation(Process):
    def __init__(self, **kwargs):
        super(BrainSegmentation, self).__init__(**kwargs)
        self.add_field('t1mri_nobias', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('histo_analysis', File, read=True,
                       allowed_extensions=['.han'])
        self.add_field('variance', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('edges', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('white_ridges', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'], optional=True)
        self.add_field('commissure_coordinates', File, read=True,
                       allowed_extensions=['.APC'], optional=True)
        self.add_field('lesion_mask', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg',
                       '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'], optional=True)
        self.add_field('lesion_mask_mode', Literal['e', 'i'])
        self.add_field('variant', Literal['2010', '2005 based on white ridge', 'Standard + (iterative erosion)', 'Standard + (selected erosion)', 'Standard + (iterative erosion) without regularisation',
                       'Robust + (iterative erosion)', 'Robust + (selected erosion)', 'Robust + (iterative erosion) without regularisation', 'Fast (selected erosion)'])
        self.add_field('erosion_size', float, trait=float(), default_value=1)
        self.add_field('visu', Literal['No', 'Yes'])
        self.add_field('layer', Literal[0, 1, 2, 3, 4, 5])
        self.add_field('first_slice', int)
        self.add_field('last_slice', int)
        self.add_field('brain_mask', File, write=True, allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim',
                       '.jpg', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('fix_random_seed', bool)

        # initialization section
        self.lesion_mask_mode = 'e'
        self.variant = '2010'
        self.erosion_size = 1.8
        self.visu = 'No'
        self.layer = 0
        self.first_slice = 0
        self.last_slice = 0
        self.fix_random_seed = False

    def execution(self, context=None):
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
            if is_path(field) and value != '':
                kwargs[name] = value
            elif is_list(field):
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('BrainSegmentation', **kwargs)
