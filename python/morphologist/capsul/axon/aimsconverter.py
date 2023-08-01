# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process


class AimsConverter(Process):
    def __init__(self, **kwargs):
        super(AimsConverter, self).__init__(**kwargs)
        self.add_field('read', File, read=True, extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg',
                       '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('write', File, write=True, extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('preferredFormat', Literal[None, 'gz compressed NIFTI-1 image', 'NIFTI-1 image', 'GIS image', 'MINC image', 'gz compressed MINC image', 'SPM image', 'ECAT v image', 'ECAT i image', 'JPEG image',
                       'GIF image', 'PNG image', 'BMP image', 'PBM image', 'PGM image', 'PPM image', 'XBM image', 'XPM image', 'TIFF image', 'TIFF(.tif) image', 'DICOM image', 'Directory', 'FDF image', 'VIDA image'], optional=True)
        self.add_field('removeSource', bool)
        self.add_field('ascii', bool)
        self.add_field('voxelType', Literal[None, 'U8', 'S8', 'U16', 'S16',
                       'U32', 'S32', 'FLOAT', 'DOUBLE', 'RGB', 'RGBA', 'HSV'], optional=True)
        self.add_field('rescaleDynamic', bool)
        self.add_field('useInputTypeLimits', bool)
        self.add_field('inputDynamicMin', float, optional=True)
        self.add_field('inputDynamicMax', float, optional=True)
        self.add_field('outputDynamicMin', float, optional=True)
        self.add_field('outputDynamicMax', float, optional=True)

        # initialization section
        self.removeSource = False
        self.ascii = False
        self.rescaleDynamic = False
        self.useInputTypeLimits = False
        self.inputDynamicMin = undefined
        self.inputDynamicMax = undefined
        self.outputDynamicMin = undefined
        self.outputDynamicMax = undefined

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
        context.runProcess('AimsConverter', **kwargs)
