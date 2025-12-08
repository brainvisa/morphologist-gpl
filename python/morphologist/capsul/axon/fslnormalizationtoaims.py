# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class FSLnormalizationToAims(Process):
    def __init__(self, **kwargs):
        super(FSLnormalizationToAims, self).__init__(**kwargs)
        self.add_trait('read', File(allowed_extensions=['.mat']))
        self.add_trait('source_volume', File(allowed_extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz']))
        self.add_trait('write', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('registered_volume', File(allowed_extensions=['.nii', '.nii.gz']))
        self.add_trait('standard_template', Enum(0))
        self.add_trait('set_transformation_in_source_volume', Bool())


        # initialization section
        self.registered_volume = '/volatile/riviere/casa-distro/conda/brainvisa-6.0/build/share/brainvisa-share-5.2/anatomical_templates/MNI152_T1_2mm_brain.nii'
        self.standard_template = 0
        self.set_transformation_in_source_volume = True

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
        context.runProcess('FSLnormalizationToAims', **kwargs)
