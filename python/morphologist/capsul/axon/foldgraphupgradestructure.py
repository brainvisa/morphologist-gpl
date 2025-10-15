# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

from capsul.api import Process
import six


class foldgraphupgradestructure(Process):
    def __init__(self, **kwargs):
        super(foldgraphupgradestructure, self).__init__(**kwargs)
        self.add_trait('old_graph', File(allowed_extensions=['.arg', '.data']))
        self.add_trait('skeleton', File(allowed_extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz']))
        self.add_trait('graph_version', Str(trait=Str(), default_value='3.1'))
        self.add_trait('graph', File(allowed_extensions=['.arg', '.data'], output=True))
        self.add_trait('commissure_coordinates', File(allowed_extensions=['.APC'], optional=True))
        self.add_trait('Talairach_transform', File(allowed_extensions=['.trm']))
        self.add_trait('compute_fold_meshes', Bool())
        self.add_trait('allow_multithreading', Bool())


        # initialization section
        self.graph_version = '3.1'
        self.compute_fold_meshes = True
        self.allow_multithreading = True

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
            if isinstance(self.trait(name).trait_type, File) and value != '':
                kwargs[name] = value
            elif isinstance(self.trait(name).trait_type, List):
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('foldgraphupgradestructure', **kwargs)
