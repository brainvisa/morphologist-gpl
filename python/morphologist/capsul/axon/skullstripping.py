# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process


class skullstripping(Process):
    def __init__(self, **kwargs):
        super(skullstripping, self).__init__(**kwargs)
        self.add_field('t1mri', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('brain_mask', File, read=True, allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu',
                       '.jpg', '.scn', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz'])
        self.add_field('skull_stripped', File, write=True, allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim',
                       '.jpg', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'])

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
        context.runProcess('skullstripping', **kwargs)
