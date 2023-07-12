# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process


class SulciGraph(Process):
    def __init__(self, **kwargs):
        super(SulciGraph, self).__init__(**kwargs)
        self.add_field('skeleton', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('roots', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('grey_white', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('hemi_cortex', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('split_brain', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg',
                       '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'], optional=True)
        self.add_field('white_mesh', File, read=True, allowed_extensions=[
                       '.gii', '.mesh', '.obj', '.ply', '.tri'])
        self.add_field('pial_mesh', File, read=True, allowed_extensions=[
                       '.gii', '.mesh', '.obj', '.ply', '.tri'])
        self.add_field('commissure_coordinates', File, read=True,
                       allowed_extensions=['.APC'], optional=True)
        self.add_field('talairach_transform', File,
                       read=True, allowed_extensions=['.trm'])
        self.add_field('compute_fold_meshes', bool)
        self.add_field('allow_multithreading', bool)
        self.add_field('graph_version', Literal['3.0', '3.1', '3.2'])
        self.add_field('graph', File, write=True,
                       allowed_extensions=['.arg', '.data'])
        self.add_field('sulci_voronoi', File, write=True, allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim',
                       '.jpg', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('write_cortex_mid_interface', bool)
        self.add_field('cortex_mid_interface', File, write=True, allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg',
                       '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'], optional=True)

        # initialization section
        self.compute_fold_meshes = True
        self.allow_multithreading = True
        self.graph_version = '3.1'
        self.write_cortex_mid_interface = False

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
        context.runProcess('corticalfoldsgraph', **kwargs)
