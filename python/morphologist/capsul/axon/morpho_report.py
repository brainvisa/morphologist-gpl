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
        self.add_trait('t1mri', File(allowed_extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz']))
        self.add_trait('left_grey_white', File(allowed_extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz'], optional=True))
        self.add_trait('right_grey_white', File(allowed_extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz'], optional=True))
        self.add_trait('left_gm_mesh', File(allowed_extensions=['.gii', '.mesh', '.obj', '.ply', '.tri'], optional=True))
        self.add_trait('right_gm_mesh', File(allowed_extensions=['.gii', '.mesh', '.obj', '.ply', '.tri'], optional=True))
        self.add_trait('left_wm_mesh', File(allowed_extensions=['.gii', '.mesh', '.obj', '.ply', '.tri'], optional=True))
        self.add_trait('right_wm_mesh', File(allowed_extensions=['.gii', '.mesh', '.obj', '.ply', '.tri'], optional=True))
        self.add_trait('left_labelled_graph', File(allowed_extensions=['.arg', '.data'], optional=True))
        self.add_trait('right_labelled_graph', File(allowed_extensions=['.arg', '.data'], optional=True))
        self.add_trait('talairach_transform', File(allowed_extensions=['.trm'], optional=True))
        self.add_trait('brain_volumes_file', File(allowed_extensions=['.csv'], optional=True))
        self.add_trait('normative_brain_stats', File(allowed_extensions=['.json'], optional=True))
        self.add_trait('report', File(allowed_extensions=['.pdf'], output=True))
        self.add_trait('subject', Str())

    def execute(self, context=None):
        from brainvisa import axon
        from brainvisa.configuration import neuroConfig
        import brainvisa.processes

        neuroConfig.gui = False
        neuroConfig.fastStart = True
        neuroConfig.logFileName = ''

        from soma.qt_gui import qt_backend
        qt_backend.set_headless(True, needs_opengl=True)

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
