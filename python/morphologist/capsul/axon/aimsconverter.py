# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

from capsul.api import Process
import six


class AimsConverter(Process):
    def __init__(self, **kwargs):
        super(AimsConverter, self).__init__()
        self.add_trait('read', File(allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg',
                                                        '.scn', '.mnc', '.mng', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz']))
        self.add_trait('write', File(allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg', '.mnc', '.mng',
                                                         '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'], output=True))
        self.add_trait('preferredFormat', Enum(None, 'gz compressed NIFTI-1 image', 'NIFTI-1 image', 'GIS image', 'MINC image', 'gz compressed MINC image', 'SPM image', 'ECAT v image', 'ECAT i image', 'JPEG image', 'GIF image',
                                               'PNG image', 'MNG image', 'BMP image', 'PBM image', 'PGM image', 'PPM image', 'XBM image', 'XPM image', 'TIFF image', 'TIFF(.tif) image', 'DICOM image', 'Directory', 'FDF image', 'VIDA image', optional=True))
        self.add_trait('removeSource', Bool())
        self.add_trait('ascii', Bool())
        self.add_trait('voxelType', Enum(None, 'U8', 'S8', 'U16', 'S16', 'U32',
                                         'S32', 'FLOAT', 'DOUBLE', 'RGB', 'RGBA', 'HSV', optional=True))
        self.add_trait('rescaleDynamic', Bool())
        self.add_trait('useInputTypeLimits', Bool())
        self.add_trait('inputDynamicMin', Float(optional=True))
        self.add_trait('inputDynamicMax', Float(optional=True))
        self.add_trait('outputDynamicMin', Float(optional=True))
        self.add_trait('outputDynamicMax', Float(optional=True))

        # initialization section
        self.removeSource = False
        self.ascii = False
        self.rescaleDynamic = False
        self.useInputTypeLimits = False
        self.inputDynamicMin = Undefined
        self.inputDynamicMax = Undefined
        self.outputDynamicMin = Undefined
        self.outputDynamicMax = Undefined

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
            if isinstance(self.trait(name).trait_type, File) and value != '' and value is not Undefined:
                kwargs[name] = value
            elif isinstance(self.trait(name).trait_type, List):
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('AimsConverter', **kwargs)
