# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

from capsul.api import Process
import six


class SulciGraph(Process):
    def __init__(self, **kwargs):
        super(SulciGraph, self).__init__()
        self.add_trait('skeleton', File(allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.mng', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz']))
        self.add_trait('roots', File(allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.mng', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz']))
        self.add_trait('grey_white', File(allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.mng', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz']))
        self.add_trait('hemi_cortex', File(allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.mng', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz']))
        self.add_trait('split_brain', File(allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.mng', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'], optional=True))
        self.add_trait('white_mesh', File(allowed_extensions=['.gii', '.mesh', '.obj', '.ply', '.tri']))
        self.add_trait('pial_mesh', File(allowed_extensions=['.gii', '.mesh', '.obj', '.ply', '.tri']))
        self.add_trait('commissure_coordinates', File(allowed_extensions=['.APC'], optional=True))
        self.add_trait('talairach_transform', File(allowed_extensions=['.trm']))
        self.add_trait('compute_fold_meshes', Bool())
        self.add_trait('allow_multithreading', Bool())
        self.add_trait('graph_version', Enum('3.0', '3.1', '3.2'))
        self.add_trait('graph', File(allowed_extensions=['.arg', '.data'], output=True))
        self.add_trait('sulci_voronoi', File(allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.gif', '.ima', '.dim', '.jpg', '.mnc', '.mng', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'], output=True))
        self.add_trait('write_cortex_mid_interface', Bool())
        self.add_trait('cortex_mid_interface', File(allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.gif', '.ima', '.dim', '.jpg', '.mnc', '.mng', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'], output=True, optional=True))


        # initialization section
        self.compute_fold_meshes = True
        self.allow_multithreading = True
        self.graph_version = '3.1'
        self.write_cortex_mid_interface = False

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
        context.runProcess('corticalfoldsgraph', **kwargs)
