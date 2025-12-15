# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class ScalpMesh(Process):
    def __init__(self, **kwargs):
        super(ScalpMesh, self).__init__(**kwargs)
        self.add_field('t1mri_nobias', File, read=True, extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz'])
        self.add_field('histo_analysis', File, read=True, extensions=['.han'], optional=True)
        self.add_field('head_mesh', File, write=True, extensions=['.gii', '.mesh', '.obj', '.ply', '.tri'])
        self.add_field('head_mask', File, write=True, extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], optional=True)
        self.add_field('keep_head_mask', bool)
        self.add_field('remove_mask', File, read=True, extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz'], optional=True, dataset=None)
        self.add_field('first_slice', int, optional=True)
        self.add_field('threshold', int, optional=True)
        self.add_field('closing', float, optional=True)
        self.add_field('threshold_mode', Literal['auto', 'abs', 'grey'])


        # initialization section
        self.keep_head_mask = False
        self.first_slice = undefined
        self.threshold = undefined
        self.closing = undefined
        self.threshold_mode = 'auto'

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
        context.runProcess('headMesh', **kwargs)
