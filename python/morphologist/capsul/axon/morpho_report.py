# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class morpho_report(Process):
    def __init__(self, **kwargs):
        super(morpho_report, self).__init__(**kwargs)
        self.add_field('t1mri', File, read=True, extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('left_grey_white', File, read=True, extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg',
                       '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'], optional=True)
        self.add_field('right_grey_white', File, read=True, extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg',
                       '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'], optional=True)
        self.add_field('left_gm_mesh', File, read=True, extensions=[
                       '.gii', '.mesh', '.obj', '.ply', '.tri'], optional=True)
        self.add_field('right_gm_mesh', File, read=True, extensions=[
                       '.gii', '.mesh', '.obj', '.ply', '.tri'], optional=True)
        self.add_field('left_wm_mesh', File, read=True, extensions=[
                       '.gii', '.mesh', '.obj', '.ply', '.tri'], optional=True)
        self.add_field('right_wm_mesh', File, read=True, extensions=[
                       '.gii', '.mesh', '.obj', '.ply', '.tri'], optional=True)
        self.add_field('left_labelled_graph', File, read=True,
                       extensions=['.arg', '.data'], optional=True)
        self.add_field('right_labelled_graph', File, read=True,
                       extensions=['.arg', '.data'], optional=True)
        self.add_field('talairach_transform', File, read=True,
                       extensions=['.trm'], optional=True)
        self.add_field('brain_volumes_file', File, read=True,
                       extensions=['.csv'], optional=True)
        self.add_field('normative_brain_stats', File, read=True,
                       extensions=['.json'], optional=True)
        self.add_field('report', File, write=True, extensions=['.pdf'])
        self.add_field('subject', str)

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
        context.runProcess('morpho_report', **kwargs)
