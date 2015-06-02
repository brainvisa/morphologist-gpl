# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class Normalization_Baladin(Process):
    def __init__(self, **kwargs):
        super(Normalization_Baladin, self).__init__()
        self.add_trait('anatomy_data', File(allowed_extensions=['.ima', '.dim']))
        self.add_trait('anatomical_template', File(allowed_extensions=['.ima', '.dim']))
        self.add_trait('transformation_matrix', File(allowed_extensions=['.txt'], output=True))
        self.add_trait('normalized_anatomy_data', File(allowed_extensions=['.ima', '.dim', '.nii', '.nii.gz'], output=True))


    def _run_process(self):
        from brainvisa import axon
        from brainvisa.configuration import neuroConfig
        import brainvisa.processes

        neuroConfig.gui = False
        neuroConfig.fastStart = True
        neuroConfig.logFileName = ''

        axon.initializeProcesses()

        kwargs = dict([(name, getattr(self, name)) \
            for name in self.user_traits() \
            if getattr(self, name) is not Undefined and \
                (not isinstance(self.user_traits()[name].trait_type, File) \
                    or getattr(self, name) != '')])

        context = brainvisa.processes.defaultContext()
        context.runProcess(self.id.split('.')[-1], **kwargs)
