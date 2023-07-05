# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process


class Normalization_FSL_reinit(Process):
    def __init__(self, **kwargs):
        super(Normalization_FSL_reinit, self).__init__(**kwargs)
        self.add_field('anatomy_data', File, read=True,
                       allowed_extensions=['.nii', '.nii.gz'])
        self.add_field('anatomical_template', File, read=True,
                       allowed_extensions=['.nii', '.nii.gz'])
        self.add_field('Alignment', Literal['Already Virtually Aligned',
                       'Not Aligned but Same Orientation', 'Incorrectly Oriented'])
        self.add_field('transformation_matrix', File,
                       write=True, allowed_extensions=['.mat'])
        self.add_field('normalized_anatomy_data', File, write=True,
                       allowed_extensions=['.nii.gz', '.nii'])
        self.add_field(
            'cost_function', Literal['corratio', 'mutualinfo', 'normcorr', 'normmi', 'leastsq', 'labeldiff'])
        self.add_field('search_cost_function',
                       Literal['corratio', 'mutualinfo', 'normcorr', 'normmi', 'leastsq', 'labeldiff'])
        self.add_field('allow_retry_initialization', bool)
        self.add_field('init_translation_origin', Literal[0, 1])

        # initialization section
        self.Alignment = 'Not Aligned but Same Orientation'
        self.cost_function = 'corratio'
        self.search_cost_function = 'corratio'
        self.allow_retry_initialization = True
        self.init_translation_origin = 0

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
        context.runProcess('Normalization_FSL_reinit', **kwargs)
