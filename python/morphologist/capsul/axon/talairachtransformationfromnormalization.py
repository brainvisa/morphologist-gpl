# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class TalairachTransformationFromNormalization(Process):
    def __init__(self, **kwargs):
        super(TalairachTransformationFromNormalization, self).__init__()
        self.add_trait('normalization_transformation', File(allowed_extensions=['.trm']))
        self.add_trait('Talairach_transform', File(allowed_extensions=['.trm'], output=True))
        self.add_trait('commissure_coordinates', File(allowed_extensions=['.APC'], output=True, optional=True))
        self.add_trait('t1mri', File(allowed_extensions=['.nii.gz', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', ''], optional=True))
        self.add_trait('source_referential', File())
        self.add_trait('normalized_referential', File())
        self.add_trait('transform_chain_ACPC_to_Normalized', List())
        self.add_trait('acpc_referential', File(optional=True))


        # initialization section
        self.transform_chain_ACPC_to_Normalized = []
        self.acpc_referential = '/volatile/riviere/brainvisa/build-trunk-release/share/brainvisa-share-4.5/registration/Talairach-AC_PC-Anatomist.referential'

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
        context.runProcess('TalairachTransformationFromNormalization', **kwargs)
