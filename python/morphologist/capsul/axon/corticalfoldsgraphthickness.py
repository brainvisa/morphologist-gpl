# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class CorticalFoldsGraphThickness(Process):
    def __init__(self, **kwargs):
        super(CorticalFoldsGraphThickness, self).__init__(**kwargs)
        self.add_field('graph', File, read=True, extensions=['.arg', '.data'])
        self.add_field('hemi_cortex', File, read=True, extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz'])
        self.add_field('GW_interface', File, read=True, extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz'])
        self.add_field('white_mesh', File, read=True, extensions=['.gii', '.mesh', '.obj', '.ply', '.tri'])
        self.add_field('hemi_mesh', File, read=True, extensions=['.gii', '.mesh', '.obj', '.ply', '.tri'])
        self.add_field('output_graph', File, write=True, extensions=['.arg', '.data'])
        self.add_field('write_mid_interface', bool)
        self.add_field('output_mid_interface', File, write=True, extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], optional=True)
        self.add_field('sulci_voronoi', File, read=True, extensions=['.nii.gz', '.dcm', '', '.i', '.v', '.fdf', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.img', '.hdr', '.tiff', '.tif', '.mnc.gz'], optional=True)


        # initialization section
        self.write_mid_interface = False

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
        context.runProcess('CorticalFoldsGraphThickness', **kwargs)
