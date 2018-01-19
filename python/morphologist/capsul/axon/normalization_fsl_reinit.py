# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

from capsul.api import Process
import six


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
        self.anatomical_template = '/usr/share/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'
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

        kwargs = {}
        for name in self.user_traits():
            value = getattr(self, name)
            if value is Undefined:
                continue
            if isinstance(self.trait(name).trait_type, File) and value != ''                     and value is not Undefined:
                kwargs[name] = value
            elif isinstance(self.trait(name).trait_type, List):
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('Normalization_FSL_reinit', **kwargs)
