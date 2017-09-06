# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.api import Process


class Normalization_Baladin(Process):
    def __init__(self, **kwargs):
        super(Normalization_Baladin, self).__init__()
        self.add_trait('anatomy_data', File(allowed_extensions=['.ima', '.dim']))
        self.add_trait('anatomical_template', File(allowed_extensions=['.ima', '.dim']))
        self.add_trait('transformation_matrix', File(allowed_extensions=['.txt'], output=True))
        self.add_trait('normalized_anatomy_data', File(allowed_extensions=['.ima', '.dim', '.nii', '.nii.gz'], output=True))


        # initialization section
        self.anatomical_template = '/usr/share/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz'

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
            if isinstance(self.trait(name).trait_type, File) and value != ''                     and value is not Undefined:
                kwargs[name] = value
            elif isinstance(self.trait(name).trait_type, List):
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('Normalization_Baladin', **kwargs)
