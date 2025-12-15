# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class AcpcOrientation(Process):
    def __init__(self, **kwargs):
        super(AcpcOrientation, self).__init__(**kwargs)
        self.add_field('T1mri', File, read=True, extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz'])
        self.add_field('commissure_coordinates', File, write=True, extensions=['.APC'])
        self.add_field('Normalised', Literal['No', 'MNI from SPM', 'MNI from Mritotal', 'Marseille from SPM'])
        self.add_field('Anterior_Commissure', conlist(float, min_items=3, max_items=3), default_factory=lambda: [0, 0, 0], optional=True)
        self.add_field('Posterior_Commissure', conlist(float, min_items=3, max_items=3), default_factory=lambda: [0, 0, 0], optional=True)
        self.add_field('Interhemispheric_Point', conlist(float, min_items=3, max_items=3), default_factory=lambda: [0, 0, 0], optional=True)
        self.add_field('Left_Hemisphere_Point', conlist(float, min_items=3, max_items=3), default_factory=lambda: [0, 0, 0], optional=True)
        self.add_field('allow_flip_initial_MRI', bool)
        self.add_field('reoriented_t1mri', File, write=True, extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'])
        self.add_field('remove_older_MNI_normalization', bool)
        self.add_field('older_MNI_normalization', File, read=True, extensions=['.trm'], optional=True, dataset=None)


        # initialization section
        self.Normalised = 'No'
        self.allow_flip_initial_MRI = False
        self.remove_older_MNI_normalization = True

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
        context.runProcess('preparesubject', **kwargs)
