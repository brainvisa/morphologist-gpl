# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

from capsul.api import Process
import six


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
        self.add_trait('report_json', File(allowed_extensions=['.json'], output=True, optional=True))
        self.add_trait('inter_subject_qc_table', File(allowed_extensions=['.tsv'], output=True, optional=True))
        self.add_trait('subject', Str())
        self.add_trait('bids', Str())


    def _run_process(self):
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
        for name in self.user_traits():
            value = getattr(self, name)
            if value is Undefined:
                continue
            if isinstance(self.trait(name).trait_type, File) and value != '':
                kwargs[name] = value
            elif isinstance(self.trait(name).trait_type, List):
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('morpho_report', **kwargs)
