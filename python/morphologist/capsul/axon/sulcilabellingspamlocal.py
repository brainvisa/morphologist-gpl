# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.api import Process


class SulciLabellingSPAMLocal(Process):
    def __init__(self, **kwargs):
        super(SulciLabellingSPAMLocal, self).__init__()
        self.add_trait('data_graph', File(allowed_extensions=['.arg', '.data']))
        self.add_trait('output_graph', File(allowed_extensions=['.arg', '.data'], output=True))
        self.add_trait('model', File(allowed_extensions=['.dat']))
        self.add_trait('posterior_probabilities', File(allowed_extensions=['.csv'], output=True))
        self.add_trait('labels_translation_map', File(allowed_extensions=['.trl', '.def']))
        self.add_trait('labels_priors', File(allowed_extensions=['.dat']))
        self.add_trait('local_referentials', File(allowed_extensions=['.dat']))
        self.add_trait('direction_priors', File(allowed_extensions=['.dat']))
        self.add_trait('angle_priors', File(allowed_extensions=['.dat']))
        self.add_trait('translation_priors', File(allowed_extensions=['.dat']))
        self.add_trait('output_local_transformations', Directory(allowed_extensions=[''], output=True, optional=True))
        self.add_trait('initial_transformation', File(allowed_extensions=['.trm'], optional=True))
        self.add_trait('global_transformation', File(allowed_extensions=['.trm'], optional=True))


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
        context.runProcess('spam_recognitionlocal', **kwargs)
