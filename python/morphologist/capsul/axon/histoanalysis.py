# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process


class HistoAnalysis(Process):
    def __init__(self, **kwargs):
        super(HistoAnalysis, self).__init__(**kwargs)
        self.add_field('t1mri_nobias', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('use_hfiltered', bool)
        self.add_field('hfiltered', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg',
                       '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'], optional=True)
        self.add_field('use_wridges', bool)
        self.add_field('white_ridges', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'], optional=True)
        self.add_field('undersampling',
                       Literal['2', '4', '8', '16', '32', 'auto', 'iteration'])
        self.add_field('histo_analysis', File, write=True,
                       allowed_extensions=['.han'])
        self.add_field('histo', File, write=True)
        self.add_field('fix_random_seed', bool)

        # initialization section
        self.use_hfiltered = True
        self.use_wridges = True
        self.undersampling = 'iteration'
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
        context.runProcess('NobiasHistoAnalysis', **kwargs)
