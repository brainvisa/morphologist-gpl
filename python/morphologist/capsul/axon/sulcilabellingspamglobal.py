# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class SulciLabellingSPAMGlobal(Process):
    def __init__(self, **kwargs):
        super(SulciLabellingSPAMGlobal, self).__init__()
        self.add_trait('data_graph', File(allowed_extensions=['.arg', '.data']))
        self.add_trait('output_graph', File(allowed_extensions=['.arg', '.data'], output=True))
        self.add_trait('model_type', Enum('Talairach', 'Global registration'))
        self.add_trait('model', File(allowed_extensions=['.dat']))
        self.add_trait('posterior_probabilities', File(allowed_extensions=['.csv'], output=True))
        self.add_trait('labels_translation_map', File(allowed_extensions=['.trl', '.def']))
        self.add_trait('labels_priors', File(allowed_extensions=['.dat']))
        self.add_trait('output_transformation', File(allowed_extensions=['.trm'], output=True, optional=True))
        self.add_trait('initial_transformation', File(allowed_extensions=['.trm'], optional=True))
        self.add_trait('output_t1_to_global_transformation', File(allowed_extensions=['.trm'], output=True, optional=True))


        # initialization section
        self.model_type = 'Global registration'
        self.labels_translation_map = '/volatile/riviere/brainvisa/build-trunk-release/share/brainvisa-share-4.5/nomenclature/translation/sulci_model_2008.trl'

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
        context.runProcess('spam_recognitionglobal', **kwargs)