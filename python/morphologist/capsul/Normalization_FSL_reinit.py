# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class Normalization_FSL_reinit(Process):
    def __init__(self, **kwargs):
        super(Normalization_FSL_reinit, self).__init__()
        self.add_trait('anatomy_data', File(allowed_extensions=['.nii', '.nii.gz']))
        self.add_trait('anatomical_template', File(allowed_extensions=['.nii', '.nii.gz']))
        self.add_trait('Alignment', Enum('Already Virtualy Aligned', 'Not Aligned but Same Orientation', 'Incorrectly Oriented'))
        self.add_trait('transformation_matrix', File(allowed_extensions=['.mat'], output=True))
        self.add_trait('normalized_anatomy_data', File(allowed_extensions=['.nii.gz'], output=True))
        self.add_trait('cost_function', Enum('corratio', 'mutualinfo', 'normcorr', 'normmi', 'leastsq', 'labeldiff'))
        self.add_trait('search_cost_function', Enum('corratio', 'mutualinfo', 'normcorr', 'normmi', 'leastsq', 'labeldiff'))
        self.add_trait('allow_retry_initialization', Bool())
        self.add_trait('init_translation_origin', Enum(0, 1))


        # initialization section
        self.anatomical_template = u'/i2bm/local/fsl/data/standard/MNI152_T1_1mm.nii.gz'
        self.Alignment = 'Not Aligned but Same Orientation'
        self.cost_function = 'corratio'
        self.search_cost_function = 'corratio'
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

        kwargs = dict([(name, getattr(self, name)) \
            for name in self.user_traits() \
            if getattr(self, name) is not Undefined and \
                (not isinstance(self.user_traits()[name].trait_type, File) \
                    or getattr(self, name) != '')])

        context = brainvisa.processes.defaultContext()
        context.runProcess(self.id.split('.')[-1], **kwargs)
