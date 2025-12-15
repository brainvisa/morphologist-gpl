# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process


class foldgraphupgradestructure(Process):
    def __init__(self, **kwargs):
        super(foldgraphupgradestructure, self).__init__(**kwargs)
        self.add_field('old_graph', File, read=True, extensions=['.arg', '.data'])
        self.add_field('skeleton', File, read=True, extensions=['.nii.gz', '.svs', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg', '.scn', '.mnc', '.nii', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.bif', '.czi', '.mnc.gz'])
        self.add_field('graph_version', str, trait=str(), default_value='3.1')
        self.add_field('graph', File, write=True, extensions=['.arg', '.data'])
        self.add_field('commissure_coordinates', File, read=True, extensions=['.APC'], optional=True)
        self.add_field('Talairach_transform', File, read=True, extensions=['.trm'])
        self.add_field('compute_fold_meshes', bool)
        self.add_field('allow_multithreading', bool)


        # initialization section
        self.graph_version = '3.1'
        self.compute_fold_meshes = True
        self.allow_multithreading = True

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
        context.runProcess('foldgraphupgradestructure', **kwargs)
