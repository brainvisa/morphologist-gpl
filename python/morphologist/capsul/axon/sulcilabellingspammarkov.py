# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

from capsul.api import Process
import six


class SulciLabellingSPAMMarkov(Process):
    def __init__(self, **kwargs):
        super(SulciLabellingSPAMMarkov, self).__init__(**kwargs)
        self.add_trait('data_graph', File(allowed_extensions=['.arg', '.data']))
        self.add_trait('output_graph', File(allowed_extensions=['.arg', '.data'], output=True))
        self.add_trait('model', File(allowed_extensions=['.dat']))
        self.add_trait('posterior_probabilities', File(allowed_extensions=['.csv'], output=True))
        self.add_trait('labels_translation_map', File(allowed_extensions=['.trl', '.def']))
        self.add_trait('labels_priors', File(allowed_extensions=['.dat']))
        self.add_trait('segments_relations_model', File(allowed_extensions=['.dat']))
        self.add_trait('initial_transformation', File(allowed_extensions=['.trm'], optional=True))
        self.add_trait('global_transformation', File(allowed_extensions=['.trm'], optional=True))
        self.add_trait('fix_random_seed', Bool())


        # initialization section
        self.labels_translation_map = '/volatile/home/dr144257/casa_distro/condadev/brainvisa-6.0/build/share/brainvisa-share-5.2/nomenclature/translation/sulci_model_2008.trl'
        self.fix_random_seed = False

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
            if isinstance(self.trait(name).trait_type, File) and value != '':
                kwargs[name] = value
            elif isinstance(self.trait(name).trait_type, List):
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('spam_recognitionmarkov', **kwargs)
