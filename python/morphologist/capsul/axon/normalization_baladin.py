# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process


class Normalization_Baladin(Process):
    def __init__(self, **kwargs):
        super(Normalization_Baladin, self).__init__(**kwargs)
        self.add_field('anatomy_data', File, read=True, allowed_extensions=['.ima', '.dim'])
        self.add_field('anatomical_template', File, read=True, allowed_extensions=['.ima', '.dim'])
        self.add_field('transformation_matrix', File, write=True, allowed_extensions=['.txt'])
        self.add_field('normalized_anatomy_data', File, write=True, allowed_extensions=['.ima', '.dim', '.nii', '.nii.gz'])


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
        context.runProcess('Normalization_Baladin', **kwargs)
