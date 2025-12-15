# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class brainvolumes(Process):
    def __init__(self, **kwargs):
        super(brainvolumes, self).__init__(**kwargs)
        self.add_field('split_brain', File, read=True, extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz'])
        self.add_field('left_grey_white', File, read=True, extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz'])
        self.add_field('right_grey_white', File, read=True, extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz'])
        self.add_field('left_csf', File, write=True, extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'])
        self.add_field('right_csf', File, write=True, extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'])
        self.add_field('left_labelled_graph', File, read=True, extensions=['.arg', '.data'], optional=True)
        self.add_field('right_labelled_graph', File, read=True, extensions=['.arg', '.data'], optional=True)
        self.add_field('left_gm_mesh', File, read=True, extensions=['.gii', '.mesh', '.obj', '.ply', '.tri'], optional=True)
        self.add_field('right_gm_mesh', File, read=True, extensions=['.gii', '.mesh', '.obj', '.ply', '.tri'], optional=True)
        self.add_field('left_wm_mesh', File, read=True, extensions=['.gii', '.mesh', '.obj', '.ply', '.tri'], optional=True)
        self.add_field('right_wm_mesh', File, read=True, extensions=['.gii', '.mesh', '.obj', '.ply', '.tri'], optional=True)
        self.add_field('subject', str, dataset="output")
        self.add_field('sulci_label_attribute', str)
        self.add_field('table_format', Literal['2023', 'old'])
        self.add_field('brain_volumes_file', File, write=True, extensions=['.csv'])


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
