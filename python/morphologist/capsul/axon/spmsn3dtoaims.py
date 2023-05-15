# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process


class SPMsn3dToAims(Process):
    def __init__(self, **kwargs):
        super(SPMsn3dToAims, self).__init__(**kwargs)
        self.add_field('read', File, read=True, allowed_extensions=['.mat'])
        self.add_field('write', File, write=True, allowed_extensions=['.trm'])
        self.add_field(
            'target', Literal['MNI template', 'unspecified template', 'normalized_volume in AIMS orientation'])
        self.add_field('source_volume', File, read=True, allowed_extensions=[
                       '.nii', '.img', '.hdr'], optional=True)
        self.add_field('normalized_volume', File, read=True, allowed_extensions=[
                       '.nii', '.img', '.hdr'], optional=True)
        self.add_field('removeSource', bool)

        # initialization section
        self.target = 'MNI template'
        self.removeSource = False

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
        context.runProcess('SPMsn3dToAims', **kwargs)
