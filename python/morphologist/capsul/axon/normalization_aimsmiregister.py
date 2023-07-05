# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process


class normalization_aimsmiregister(Process):
    def __init__(self, **kwargs):
        super(normalization_aimsmiregister, self).__init__(**kwargs)
        self.add_field('anatomy_data', File, read=True, allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima',
                       '.dim', '.jpg', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('anatomical_template', File, read=True, allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima',
                       '.dim', '.jpg', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('transformation_to_template', File,
                       write=True, allowed_extensions=['.trm'], optional=True)
        self.add_field('normalized_anatomy_data', File, write=True, allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'], optional=True)
        self.add_field('transformation_to_MNI', File, write=True,
                       allowed_extensions=['.trm'], optional=True)
        self.add_field('transformation_to_ACPC', File, write=True,
                       allowed_extensions=['.trm'], optional=True)
        self.add_field('mni_to_acpc', File, read=True,
                       allowed_extensions=['.trm'], optional=True)
        self.add_field('smoothing', float)

        # initialization section
        self.anatomical_template = '/casa/host/build/share/brainvisa-share-5.2/anatomical_templates/MNI152_T1_2mm.nii.gz'
        self.mni_to_acpc = '/casa/host/build/share/brainvisa-share-5.2/transformation/talairach_TO_spm_template_novoxels.trm'
        self.smoothing = 1.0

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
        context.runProcess('normalization_aimsmiregister', **kwargs)
