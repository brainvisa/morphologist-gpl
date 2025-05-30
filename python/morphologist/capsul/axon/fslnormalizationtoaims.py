# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

from capsul.api import Process
import six


class FSLnormalizationToAims(Process):
    def __init__(self, **kwargs):
        super(FSLnormalizationToAims, self).__init__(**kwargs)
        self.add_trait('read', File(allowed_extensions=['.mat']))
        self.add_trait('source_volume', File(allowed_extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz']))
        self.add_trait('write', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('registered_volume', File(allowed_extensions=['.nii', '.nii.gz']))
        self.add_trait('standard_template', Enum(0, 1, 2))
        self.add_trait('set_transformation_in_source_volume', Bool())


        # initialization section
        self.standard_template = 0
        self.set_transformation_in_source_volume = True

    def _run_process(self):
        from brainvisa import axon
        from brainvisa.configuration import neuroConfig
        import brainvisa.processes

        neuroConfig.gui = False
        neuroConfig.fastStart = True
        neuroConfig.logFileName = ''


        axon.initializeProcesses()

        kwargs = {}
        for name in self.user_traits():
            value = getattr(self, name)
            if value is Undefined:
                continue
            if isinstance(self.trait(name).trait_type, File) and value != '':
                kwargs[name] = value
            elif isinstance(self.trait(name).trait_type, List):
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('FSLnormalizationToAims', **kwargs)
