# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class Normalization_SPM_reinit(Process):
    def __init__(self, **kwargs):
        super(Normalization_SPM_reinit, self).__init__()
        self.add_trait('anatomy_data', File(allowed_extensions=['.nii', '.img', '.hdr']))
        self.add_trait('anatomical_template', File(allowed_extensions=['.nii', '.img', '.hdr', '.mnc'], optional=True))
        self.add_trait('job_file', File(allowed_extensions=['.mat'], output=True, optional=True))
        self.add_trait('voxel_size', Enum('[1 1 1]'))
        self.add_trait('cutoff_option', Int())
        self.add_trait('nbiteration', Int())
        self.add_trait('transformations_informations', File(allowed_extensions=['.mat'], output=True))
        self.add_trait('normalized_anatomy_data', File(allowed_extensions=['.nii', '.img', '.hdr'], output=True))
        self.add_trait('allow_retry_initialization', Bool())
        self.add_trait('init_translation_origin', Enum(0, 1))


        # initialization section
        self.anatomical_template = u'/usr/local/spm8-standalone/spm8_mcr/spm8/templates/T1.nii'
        self.voxel_size = '[1 1 1]'
        self.cutoff_option = 25
        self.nbiteration = 16
        self.allow_retry_initialization = True
        self.init_translation_origin = 0

    def _run_process(self):
        from brainvisa import axon
        from brainvisa.configuration import neuroConfig
        import brainvisa.processes

        neuroConfig.gui = False
        neuroConfig.fastStart = True
        neuroConfig.logFileName = ''

        axon.initializeProcesses()

        kwargs = {name : getattr(self, name) for name in self.user_traits() \
            if getattr(self, name) is not Undefined}

        context = brainvisa.processes.defaultContext()
        context.runProcess(self.id.split('.')[-1], **kwargs)
