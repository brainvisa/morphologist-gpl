# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class preparesubject(Process):
    def __init__(self, **kwargs):
        super(preparesubject, self).__init__()
        self.add_trait('T1mri', File(allowed_extensions=['.nii.gz', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.mnc', '.mnc.gz', '.nii', '']))
        self.add_trait('commissure_coordinates', File(allowed_extensions=['.APC'], output=True))
        self.add_trait('Normalised', Enum('No', 'MNI from SPM', 'MNI from Mritotal', 'Marseille from SPM'))
        self.add_trait('Anterior_Commissure', List(trait=Float(), minlen=3, maxlen=3, value=[0, 0, 0], optional=True))
        self.add_trait('Posterior_Commissure', List(trait=Float(), minlen=3, maxlen=3, value=[0, 0, 0], optional=True))
        self.add_trait('Interhemispheric_Point', List(trait=Float(), minlen=3, maxlen=3, value=[0, 0, 0], optional=True))
        self.add_trait('Left_Hemisphere_Point', List(trait=Float(), minlen=3, maxlen=3, value=[0, 0, 0], optional=True))
        self.add_trait('allow_flip_initial_MRI', Bool())
        self.add_trait('remove_older_MNI_normalization', Bool())
        self.add_trait('older_MNI_normalization', File(allowed_extensions=['.trm'], optional=True))


        # initialization section
        self.Normalised = 'No'
        self.allow_flip_initial_MRI = False
        self.remove_older_MNI_normalization = True

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
