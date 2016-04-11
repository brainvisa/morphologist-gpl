# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.api import Process


class SulciLabellingANN(Process):
    def __init__(self, **kwargs):
        super(SulciLabellingANN, self).__init__()
        self.add_trait('data_graph', File(allowed_extensions=['.arg', '.data']))
        self.add_trait('model', File(allowed_extensions=['.arg', '.data']))
        self.add_trait('output_graph', File(allowed_extensions=['.arg', '.data'], output=True))
        self.add_trait('model_hint', Enum(0, 1))
        self.add_trait('energy_plot_file', File(allowed_extensions=['.nrj'], output=True))
        self.add_trait('rate', Float())
        self.add_trait('stopRate', Float())
        self.add_trait('niterBelowStopProp', Int())
        self.add_trait('forbid_unknown_label', Bool())
        self.add_trait('fix_random_seed', Bool())


        # initialization section
        self.model = '/volatile/riviere/brainvisa/build-trunk-release/share/brainvisa-share-4.6/models/models_2008/discriminative_models/3.0/Lfolds_noroots/Lfolds_noroots.arg'
        self.model_hint = 0
        self.rate = 0.98
        self.stopRate = 0.05
        self.niterBelowStopProp = 1
        self.forbid_unknown_label = False
        self.fix_random_seed = False

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
        context.runProcess('recognition', **kwargs)
