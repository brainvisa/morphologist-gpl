# -*- coding: utf-8 -*-
from __future__ import absolute_import
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

from capsul.api import Process
import six


class ImportT1MRI(Process):
    def __init__(self, **kwargs):
        super(ImportT1MRI, self).__init__()
        self.add_trait('input', File(allowed_extensions=['.nii.gz', '.svs', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.mgh', '.mgz', '.gif', '.ima', '.dim', '.ndpi', '.vms', '.vmu', '.jpg',
                                                         '.scn', '.mnc', '.mng', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.svslide', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.bif', '.xbm', '.xpm', '.czi', '.mnc.gz']))
        self.add_trait('output', File(allowed_extensions=['.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg', '.mnc', '.mng',
                                                          '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz'], output=True))
        self.add_trait('referential', File(output=True, optional=True))
        self.add_trait('output_database', Enum(
            u'/neurospin/lnao/PClean/database_learnclean', u'/volatile/riviere/basetests-3.1.0'))
        self.add_trait('attributes_merging', Enum(
            'BrainVisa', 'header', 'selected_from_header'))
        self.add_trait('selected_attributes_from_header', List())

        # initialization section
        self.output_database = u'/neurospin/lnao/PClean/database_learnclean'
        self.attributes_merging = 'BrainVisa'
        self.selected_attributes_from_header = []

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
            if isinstance(self.trait(name).trait_type, File) and value != '' and value is not Undefined:
                kwargs[name] = value
            elif isinstance(self.trait(name).trait_type, List):
                kwargs[name] = list(value)
            else:
                kwargs[name] = value

        context = brainvisa.processes.defaultContext()
        context.runProcess('ImportT1MRI', **kwargs)
