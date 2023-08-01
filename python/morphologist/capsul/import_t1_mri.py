
from capsul.process.process import Process
from soma.controller import File


class ImportT1Mri(Process):

    def __init__(self, **kwargs):
        super(ImportT1Mri, self).__init__(**kwargs)
        self.add_field(
            'input', File,
            extensions=['.nii.gz', '.img', '.hdr', '.v', '.i', '.mnc',
                        '.mnc.gz', '.nii', '.jpg', '.gif', '.png',
                        '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm',
                        '.xpm', '.tiff', '.tif', '.ima', '.dim',
                        '.vimg', '.vinfo', '.vhdr', ''],
            output=False)
        self.add_field(
            'output', File,
            extensions=['.nii.gz', '.img', '.hdr', '.v', '.i', '.mnc',
                        '.mnc.gz', '.nii', '.jpg', '.gif', '.png',
                        '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm',
                        '.xpm', '.tiff', '.tif', '.ima', '.dim',
                        '.vimg', '.vinfo', '.vhdr', ''],
            output=True)
        self.add_field(
            'referential', File,
            extensions=['.referential'], output=True, optional=True)

    def execute(self, context=None):
        from brainvisa.tools.data_management.image_importation import Importer
        Importer.import_t1mri(self.input, self.output, self.referential)
