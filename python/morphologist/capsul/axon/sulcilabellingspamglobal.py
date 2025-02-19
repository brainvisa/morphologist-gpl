# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class SulciLabellingSPAMGlobal(Process):
    def __init__(self, **kwargs):
        super(SulciLabellingSPAMGlobal, self).__init__(**kwargs)
        self.add_field('data_graph', File, read=True,
                       extensions=['.arg', '.data'])
        self.add_field('output_graph', File, write=True,
                       extensions=['.arg', '.data'])
        self.add_field(
            'model_type', Literal['Talairach', 'Global registration'])
        self.add_field('model', File, read=True, extensions=[
                       '.dat'], dataset="shared")
        self.add_field('posterior_probabilities', File,
                       write=True, extensions=['.csv'])
        self.add_field('labels_translation_map', File, read=True,
                       extensions=['.trl', '.def'], dataset="shared")
        self.add_field('labels_priors', File, read=True,
                       extensions=['.dat'], dataset="shared")
        self.add_field('output_transformation', File, write=True,
                       extensions=['.trm'], optional=True)
        self.add_field('initial_transformation', File, read=True,
                       extensions=['.trm'], optional=True, dataset=None)
        self.add_field('output_t1_to_global_transformation', File,
                       write=True, extensions=['.trm'], optional=True)

        # initialization section
        self.model_type = 'Global registration'
        self.labels_translation_map = '/volatile/riviere/casa-distro/conda/brainvisa-6.0/build/share/brainvisa-share-5.2/nomenclature/translation/sulci_model_2008.trl'

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
        context.runProcess('spam_recognitionglobal', **kwargs)
