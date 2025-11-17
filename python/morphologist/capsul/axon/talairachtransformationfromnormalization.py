# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

from capsul.api import Process
import six


class TalairachTransformationFromNormalization(Process):
    def __init__(self, **kwargs):
        super(TalairachTransformationFromNormalization, self).__init__(**kwargs)
        self.add_trait('normalization_transformation', File(allowed_extensions=['.trm']))
        self.add_trait('Talairach_transform', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('commissure_coordinates', File(allowed_extensions=['.APC'], output=True, optional=True))
        self.add_trait('t1mri', File(allowed_extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz'], optional=True))
        self.add_trait('source_referential', File())
        self.add_trait('normalized_referential', File())
        self.add_trait('transform_chain_ACPC_to_Normalized', List())
        self.add_trait('acpc_referential', File(optional=True))


        # initialization section
        self.transform_chain_ACPC_to_Normalized = []
        self.acpc_referential = '/volatile/home/dr144257/brainvisa-sf-master/build/share/brainvisa-share-5.2/registration/Talairach-AC_PC-Anatomist.referential'

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
        context.runProcess('TalairachTransformationFromNormalization', **kwargs)
