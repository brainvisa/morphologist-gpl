from brainvisa.processes import *
from brainvisa import registration
from soma import aims


signature = Signature(
    'talairach_transform',
    ReadDiskItem('Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
                 'Transformation matrix'),
    'mni_transform',
    WriteDiskItem('Transform Raw T1 MRI to Talairach-MNI template-SPM',
                  'Transformation matrix'),
    'tal_to_mni',
    ReadDiskItem('Transformation matrix', 'Transformation matrix'),
)


def initialization(self):
    trManager = registration.getTransformationManager()
    mniToACPCpaths = trManager.findPaths(
        registration.talairachACPCReferentialId,
        registration.talairachMNIReferentialId)
    for x in mniToACPCpaths:
        self.tal_to_mni = x[0]
        break
    self.linkParameters('mni_transform', 'talairach_transform')


def execution(self, context):
    s_to_tal = aims.read(self.talairach_transform.fullPath())
    tal_to_mni = aims.read(self.tal_to_mni.fullPath())
    s_to_mni = tal_to_mni * s_to_tal
    aims.write(s_to_mni, self.mni_transform.fullPath())
