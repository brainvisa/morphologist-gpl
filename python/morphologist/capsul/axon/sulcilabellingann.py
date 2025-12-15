# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class SulciLabellingANN(Process):
    def __init__(self, **kwargs):
        super(SulciLabellingANN, self).__init__(**kwargs)
        self.add_field('data_graph', File, read=True, extensions=['.arg', '.data'])
        self.add_field('model', File, read=True, extensions=['.arg', '.data'], dataset="shared")
        self.add_field('output_graph', File, write=True, extensions=['.arg', '.data'])
        self.add_field('model_hint', Literal[0, 1])
        self.add_field('energy_plot_file', File, write=True, extensions=['.nrj'])
        self.add_field('rate', float)
        self.add_field('stopRate', float)
        self.add_field('niterBelowStopProp', int)
        self.add_field('forbid_unknown_label', bool)
        self.add_field('fix_random_seed', bool)


        # initialization section
        self.model_hint = 0
        self.rate = 0.98
        self.stopRate = 0.05
        self.niterBelowStopProp = 1
        self.forbid_unknown_label = False
        self.fix_random_seed = False

    def execute(self, context=None):
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
            if field.path_type and value != '':
                kwargs[name] = value
            elif field.is_list():
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('recognition', **kwargs)
