# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class normalization_aimsmiregister(Process):
    def __init__(self, **kwargs):
        super(normalization_aimsmiregister, self).__init__(**kwargs)
        self.add_field('anatomy_data', File, read=True, extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz'])
        self.add_field('anatomical_template', File, read=True, extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz'], dataset="shared")
        self.add_field('transformation_to_template', File, write=True, extensions=['.trm'], optional=True)
        self.add_field('normalized_anatomy_data', File, write=True, extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], optional=True)
        self.add_field('transformation_to_MNI', File, write=True, extensions=['.trm'], optional=True)
        self.add_field('transformation_to_ACPC', File, write=True, extensions=['.trm'], optional=True)
        self.add_field('mni_to_acpc', File, read=True, extensions=['.trm'], optional=True, dataset="shared")
        self.add_field('smoothing', float)


        # initialization section
        self.anatomical_template = '/home_local/a-sac-ns-brainvisa/bbi-daily/soma-env-0.1/.pixi/envs/default/spm12/spm12_mcr/spm/spm12/toolbox/OldNorm/T1.nii'
        self.smoothing = 1.0

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
        context.runProcess('normalization_aimsmiregister', **kwargs)
