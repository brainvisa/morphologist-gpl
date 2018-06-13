# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

from capsul.api import Process
import six


class SPMsn3dToAims(Process):
    def __init__(self, **kwargs):
        super(SPMsn3dToAims, self).__init__()
        self.add_trait('read', File(allowed_extensions=['.mat']))
        self.add_trait('write', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('target', Enum(
            'MNI template', 'unspecified template', 'normalized_volume in AIMS orientation'))
        self.add_trait('source_volume', File(allowed_extensions=[
                       '.nii', '.img', '.hdr'], optional=True))
        self.add_trait('normalized_volume', File(
            allowed_extensions=['.nii', '.img', '.hdr'], optional=True))
        self.add_trait('removeSource', Bool())

        # initialization section
        self.target = 'MNI template'
        self.removeSource = False

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
            if isinstance(self.trait(name).trait_type, File) and value != '' and value is not Undefined:
                kwargs[name] = value
            elif isinstance(self.trait(name).trait_type, List):
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('SPMsn3dToAims', **kwargs)
