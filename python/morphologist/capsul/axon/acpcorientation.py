# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process


class AcpcOrientation(Process):
    def __init__(self, **kwargs):
        super(AcpcOrientation, self).__init__()
        self.add_trait('T1mri', File(allowed_extensions=['.nii.gz', '.bif', '.czi', '.ppm', '.xbm', '.xpm', '.tiff', '.tif', '.ima', '.dim', '.svs', '.vms', '.vmu', '.ndpi', '.scn', '.svslide', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', '.mnc.gz', '.fdf', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', '']))
        self.add_trait('commissure_coordinates', File(allowed_extensions=['.APC'], output=True))
        self.add_trait('Normalised', Enum('No', 'MNI from SPM', 'MNI from Mritotal', 'Marseille from SPM'))
        self.add_trait('Anterior_Commissure', List(trait=Float(), minlen=3, maxlen=3, value=[0, 0, 0], optional=True))
        self.add_trait('Posterior_Commissure', List(trait=Float(), minlen=3, maxlen=3, value=[0, 0, 0], optional=True))
        self.add_trait('Interhemispheric_Point', List(trait=Float(), minlen=3, maxlen=3, value=[0, 0, 0], optional=True))
        self.add_trait('Left_Hemisphere_Point', List(trait=Float(), minlen=3, maxlen=3, value=[0, 0, 0], optional=True))
        self.add_trait('allow_flip_initial_MRI', Bool())
        self.add_trait('reoriented_t1mri', File(allowed_extensions=['.nii.gz', '.ppm', '.xbm', '.xpm', '.tiff', '.ima', '.dim', '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.v', '.i', '.dcm', '.mnc', '.mnc.gz', '.nii', '.jpg', '.gif', '.png', '.mng', '.bmp', '.pbm', '.pgm', ''], output=True))
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
        context.runProcess('preparesubject', **kwargs)
