# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class sulcigraphmorphometrybysubject(Process):
    def __init__(self, **kwargs):
        super(sulcigraphmorphometrybysubject, self).__init__()
        self.add_trait('left_sulci_graph', File(allowed_extensions=['.arg', '.data']))
        self.add_trait('right_sulci_graph', File(allowed_extensions=['.arg', '.data']))
        self.add_trait('sulci_file', File(allowed_extensions=['.json']))
        self.add_trait('use_attribute', Enum('label', 'name'))
        self.add_trait('sulcal_morpho_measures', File(allowed_extensions=['.csv'], output=True))


        # initialization section
        self.sulci_file = '/volatile/riviere/brainvisa/build-stable-release/share/brainvisa-share-4.5/nomenclature/translation/sulci_default_list.json'
        self.use_attribute = 'label'

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
        context.runProcess('sulcigraphmorphometrybysubject', **kwargs)
