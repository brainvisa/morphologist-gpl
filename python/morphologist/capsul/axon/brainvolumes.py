# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process


class brainvolumes(Process):
    def __init__(self, **kwargs):
        super(brainvolumes, self).__init__(**kwargs)
        self.add_field('split_brain', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('left_grey_white', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms',
                       '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('right_grey_white', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms',
                       '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('left_csf', File, write=True, allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('right_csf', File, write=True, allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim',
                       '.jpg', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('left_labelled_graph', File, read=True,
                       allowed_extensions=['.arg', '.data'], optional=True)
        self.add_field('right_labelled_graph', File, read=True,
                       allowed_extensions=['.arg', '.data'], optional=True)
        self.add_field('left_gm_mesh', File, read=True, allowed_extensions=[
                       '.gii', '.mesh', '.obj', '.ply', '.tri'], optional=True)
        self.add_field('right_gm_mesh', File, read=True, allowed_extensions=[
                       '.gii', '.mesh', '.obj', '.ply', '.tri'], optional=True)
        self.add_field('left_wm_mesh', File, read=True, allowed_extensions=[
                       '.gii', '.mesh', '.obj', '.ply', '.tri'], optional=True)
        self.add_field('right_wm_mesh', File, read=True, allowed_extensions=[
                       '.gii', '.mesh', '.obj', '.ply', '.tri'], optional=True)
        self.add_field('subject', str)
        self.add_field('sulci_label_attribute', str)
        self.add_field('table_format', Literal['2023', 'old'])
        self.add_field('brain_volumes_file', File, write=True,
                       allowed_extensions=['.csv'])

        # initialization section
        self.sulci_label_attribute = 'label'
        self.table_format = '2023'

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
        context.runProcess('brainvolumes', **kwargs)
