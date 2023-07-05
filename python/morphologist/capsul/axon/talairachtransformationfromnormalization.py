# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process


class TalairachTransformationFromNormalization(Process):
    def __init__(self, **kwargs):
        super(TalairachTransformationFromNormalization, self).__init__(**kwargs)
        self.add_field('normalization_transformation', File,
                       read=True, allowed_extensions=['.trm'])
        self.add_field('Talairach_transform', File,
                       write=True, allowed_extensions=['.trm'])
        self.add_field('commissure_coordinates', File, write=True,
                       allowed_extensions=['.APC'], optional=True)
        self.add_field('t1mri', File, read=True, allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'], optional=True)
        self.add_field('source_referential', File, read=True)
        self.add_field('normalized_referential', File, read=True)
        self.add_field('transform_chain_ACPC_to_Normalized', list)
        self.add_field('acpc_referential', File, read=True, optional=True)

        # initialization section
        self.transform_chain_ACPC_to_Normalized = []
        self.acpc_referential = '/casa/host/build/share/brainvisa-share-5.2/registration/Talairach-AC_PC-Anatomist.referential'

    def execution(self, context=None):
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
            if is_path(field) and value != '':
                kwargs[name] = value
            elif is_list(field):
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess(
            'TalairachTransformationFromNormalization', **kwargs)
