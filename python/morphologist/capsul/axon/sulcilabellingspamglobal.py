# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

from capsul.api import Process
import six


class SulciLabellingSPAMGlobal(Process):
    def __init__(self, **kwargs):
        super(SulciLabellingSPAMGlobal, self).__init__()
        self.add_trait('data_graph', File(
            allowed_extensions=['.arg', '.data']))
        self.add_trait('output_graph', File(
            allowed_extensions=['.arg', '.data'], output=True))
        self.add_trait('model_type', Enum('Talairach', 'Global registration'))
        self.add_trait('model', File(allowed_extensions=['.dat']))
        self.add_trait('posterior_probabilities', File(
            allowed_extensions=['.csv'], output=True))
        self.add_trait('labels_translation_map', File(
            allowed_extensions=['.trl', '.def']))
        self.add_trait('labels_priors', File(allowed_extensions=['.dat']))
        self.add_trait('output_transformation', File(
            allowed_extensions=['.trm'], output=True, optional=True))
        self.add_trait('initial_transformation', File(
            allowed_extensions=['.trm'], optional=True))
        self.add_trait('output_t1_to_global_transformation', File(
            allowed_extensions=['.trm'], output=True, optional=True))

        # initialization section
        self.model_type = 'Global registration'
        self.labels_translation_map = '/home/riviere/build-current64/share/brainvisa-share-4.6/nomenclature/translation/sulci_model_2008.trl'

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
            if isinstance(self.trait(name).trait_type, File) and value != '' and value is not Undefined:
                kwargs[name] = value
            elif isinstance(self.trait(name).trait_type, List):
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('spam_recognitionglobal', **kwargs)
