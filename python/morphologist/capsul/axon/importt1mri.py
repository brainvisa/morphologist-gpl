# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class ImportT1MRI(Process):
    def __init__(self, **kwargs):
        super(ImportT1MRI, self).__init__(**kwargs)
        self.add_field('input', File, read=True, extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('output', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('referential', File, write=True, optional=True)
        self.add_field('output_database', Literal['/host/home/dr144257/data/baseessai', '/casa/home/data/baseessai-bids',
                       '/home/dr144257/data/archi-sulci', '/home/dr144257/data/archi-sulci-sulpat/archi-sulci-2023', '/tmp/morpho-bv/derivative'], optional=True)
        self.add_field('attributes_merging',
                       Literal['BrainVisa', 'header', 'selected_from_header'], optional=True)
        self.add_field('selected_attributes_from_header', list, optional=True)

        # initialization section
        self.output_database = '/host/home/dr144257/data/baseessai'
        self.attributes_merging = 'BrainVisa'
        self.selected_attributes_from_header = []

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
        context.runProcess('ImportT1MRI', **kwargs)
