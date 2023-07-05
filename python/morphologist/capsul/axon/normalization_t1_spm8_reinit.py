# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process


class normalization_t1_spm8_reinit(Process):
    def __init__(self, **kwargs):
        super(normalization_t1_spm8_reinit, self).__init__(**kwargs)
        self.add_field('anatomy_data', File, read=True,
                       allowed_extensions=['.nii', '.img', '.hdr'])
        self.add_field('anatomical_template', File, read=True, allowed_extensions=[
                       '.nii', '.mnc', '.img', '.hdr'], optional=True)
        self.add_field('voxel_size', Literal['[1 1 1]'])
        self.add_field('cutoff_option', int)
        self.add_field('nbiteration', int)
        self.add_field('transformations_informations', File,
                       write=True, allowed_extensions=['.mat'])
        self.add_field('normalized_anatomy_data', File, write=True,
                       allowed_extensions=['.nii', '.img', '.hdr'])
        self.add_field('allow_retry_initialization', bool)
        self.add_field('init_translation_origin', Literal[0, 1])

        # initialization section
        self.voxel_size = '[1 1 1]'
        self.cutoff_option = 25
        self.nbiteration = 16
        self.allow_retry_initialization = True
        self.init_translation_origin = 0

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
        context.runProcess('normalization_t1_spm8_reinit', **kwargs)
