# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process


class FSLnormalizationToAims(Process):
    def __init__(self, **kwargs):
        super(FSLnormalizationToAims, self).__init__(**kwargs)
        self.add_field('read', File, read=True, allowed_extensions=['.mat'])
        self.add_field('source_volume', File, read=True, allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima',
                       '.dim', '.jpg', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])
        self.add_field('write', File, write=True, allowed_extensions=['.trm'])
        self.add_field('registered_volume', File, read=True,
                       allowed_extensions=['.nii', '.nii.gz'])
        self.add_field('standard_template', Literal[0, 1, 2])
        self.add_field('set_transformation_in_source_volume', bool)

        # initialization section
        self.standard_template = 0
        self.set_transformation_in_source_volume = True

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
        context.runProcess('FSLnormalizationToAims', **kwargs)
