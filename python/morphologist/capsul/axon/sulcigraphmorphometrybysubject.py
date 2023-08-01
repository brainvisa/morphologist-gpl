# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process


class sulcigraphmorphometrybysubject(Process):
    def __init__(self, **kwargs):
        super(sulcigraphmorphometrybysubject, self).__init__(**kwargs)
        self.add_field('left_sulci_graph', File, read=True,
                       extensions=['.arg', '.data'])
        self.add_field('right_sulci_graph', File, read=True,
                       extensions=['.arg', '.data'])
        self.add_field('sulci_file', File, read=True, extensions=['.json'])
        self.add_field('use_attribute', Literal['label', 'name'])
        self.add_field('sulcal_morpho_measures', File,
                       write=True, extensions=['.csv'])

        # initialization section
        self.sulci_file = '/casa/host/build/share/brainvisa-share-5.2/nomenclature/translation/sulci_default_list.json'
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
