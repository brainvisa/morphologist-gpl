# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class ReorientAnatomy(Process):
    def __init__(self, **kwargs):
        super(ReorientAnatomy, self).__init__(**kwargs)
        self.add_field('t1mri', File, read=True, extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz'])
        self.add_field('output_t1mri', File, write=True, extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'])
        self.add_field('transformation', File, read=True, extensions=['.trm'])
        self.add_field('output_transformation', File, write=True, extensions=['.trm'])
        self.add_field('commissures_coordinates', File, read=True, extensions=['.APC'], optional=True, dataset=None)
        self.add_field('output_commissures_coordinates', File, write=True, extensions=['.APC'], optional=True)
        self.add_field('allow_flip_initial_MRI', bool)


        # initialization section
        self.allow_flip_initial_MRI = False

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
        context.runProcess('reorientAnatomy', **kwargs)
