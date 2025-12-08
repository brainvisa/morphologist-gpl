# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class TalairachTransformationFromNormalization(Process):
    def __init__(self, **kwargs):
        super(TalairachTransformationFromNormalization, self).__init__(**kwargs)
        self.add_field('normalization_transformation',
                       File, read=True, extensions=['.trm'])
        self.add_field('Talairach_transform', File,
                       write=True, extensions=['.trm'])
        self.add_field('commissure_coordinates', File,
                       write=True, extensions=['.APC'], optional=True)
        self.add_field('t1mri', File, read=True, extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg',
                       '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'], optional=True)
        self.add_field('source_referential', File, read=True)
        self.add_field('normalized_referential', File,
                       read=True, dataset="shared")
        self.add_field('transform_chain_ACPC_to_Normalized',
                       list, dataset="shared")
        self.add_field('acpc_referential', File, read=True,
                       optional=True, dataset="shared")


        # initialization section
        self.transform_chain_ACPC_to_Normalized = []
        self.acpc_referential = '/volatile/home/dr144257/casa_distro/condadev/brainvisa-6.0/build/share/brainvisa-share-5.2/registration/Talairach-AC_PC-Anatomist.referential'

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
        context.runProcess('TalairachTransformationFromNormalization', **kwargs)
