# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class ImportT1MRI(Process):
    def __init__(self, **kwargs):
        super(ImportT1MRI, self).__init__(**kwargs)
        self.add_trait('input', File(allowed_extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz']))
        self.add_trait('output', File(allowed_extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], output=True))
        self.add_trait('referential', File(output=True, optional=True))
        self.add_trait('output_database', Enum('/volatile/riviere/basetests-3.1.0', optional=True))
        self.add_trait('attributes_merging', Enum('BrainVisa', 'header', 'selected_from_header', optional=True))
        self.add_trait('selected_attributes_from_header', List(optional=True))


        # initialization section
        self.output_database = '/volatile/riviere/basetests-3.1.0'
        self.attributes_merging = 'BrainVisa'
        self.selected_attributes_from_header = []

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
        context.runProcess('ImportT1MRI', **kwargs)
