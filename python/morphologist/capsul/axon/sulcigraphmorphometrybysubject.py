# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class sulcigraphmorphometrybysubject(Process):
    def __init__(self, **kwargs):
        super(sulcigraphmorphometrybysubject, self).__init__(**kwargs)
        self.add_field('left_sulci_graph', File, read=True, extensions=['.arg', '.data'])
        self.add_field('right_sulci_graph', File, read=True, extensions=['.arg', '.data'])
        self.add_field('sulci_file', File, read=True, extensions=['.json'], dataset="shared")
        self.add_field('use_attribute', Literal['label', 'name'])
        self.add_field('sulcal_morpho_measures', File, write=True, extensions=['.csv'])


        # initialization section
        self.use_attribute = 'label'

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
        context.runProcess('sulcigraphmorphometrybysubject', **kwargs)
