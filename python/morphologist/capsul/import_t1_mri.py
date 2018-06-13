
from __future__ import absolute_import
from capsul.process.process import Process
from traits.api import Undefined, Bool, File


class ImportT1Mri(Process):

    def __init__(self, **kwargs):
        super(ImportT1Mri, self).__init__(**kwargs)
        self.add_trait('input', File(
            allowed_extensions=['.nii.gz', '.img', '.hdr', '.v', '.i', '.mnc',
                                '.mnc.gz', '.nii', '.jpg', '.gif', '.png',
                                '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm',
                                '.xpm', '.tiff', '.tif', '.ima', '.dim',
                                '.vimg', '.vinfo', '.vhdr', ''],
            output=False))
        self.add_trait('output', File(
            allowed_extensions=['.nii.gz', '.img', '.hdr', '.v', '.i', '.mnc',
                                '.mnc.gz', '.nii', '.jpg', '.gif', '.png',
                                '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm',
                                '.xpm', '.tiff', '.tif', '.ima', '.dim',
                                '.vimg', '.vinfo', '.vhdr', ''],
            output=True))
        self.add_trait('referential', File(
            allowed_extensions=['.referential'], output=True, optional=True))

    def _run_process(self):
        from brainvisa.tools.data_management.image_importation import Importer
        Importer.import_t1mri(self.input, self.output, self.referential)
