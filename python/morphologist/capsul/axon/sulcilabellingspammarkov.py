# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process


class SulciLabellingSPAMMarkov(Process):
    def __init__(self, **kwargs):
        super(SulciLabellingSPAMMarkov, self).__init__(**kwargs)
        self.add_field('data_graph', File, read=True,
                       allowed_extensions=['.arg', '.data'])
        self.add_field('output_graph', File, write=True,
                       allowed_extensions=['.arg', '.data'])
        self.add_field('model', File, read=True, allowed_extensions=['.dat'])
        self.add_field('posterior_probabilities', File,
                       write=True, allowed_extensions=['.csv'])
        self.add_field('labels_translation_map', File, read=True,
                       allowed_extensions=['.trl', '.def'])
        self.add_field('labels_priors', File, read=True,
                       allowed_extensions=['.dat'])
        self.add_field('segments_relations_model', File,
                       read=True, allowed_extensions=['.dat'])
        self.add_field('initial_transformation', File, read=True,
                       allowed_extensions=['.trm'], optional=True)
        self.add_field('global_transformation', File, read=True,
                       allowed_extensions=['.trm'], optional=True)
        self.add_field('fix_random_seed', bool)

        # initialization section
        self.labels_translation_map = '/casa/host/build/share/brainvisa-share-5.2/nomenclature/translation/sulci_model_2008.trl'
        self.fix_random_seed = False

    def execution(self, context=None):
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
            if is_path(field) and value != '':
                kwargs[name] = value
            elif is_list(field):
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('spam_recognitionmarkov', **kwargs)
