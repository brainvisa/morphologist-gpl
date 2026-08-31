from brainvisa.processes import Signature, ReadDiskItem, WriteDiskItem
from brainvisa.processing import capsul_process

name = 'Imprints to skeleton'
userLevel = 1
base_class = capsul_process.CapsulProcess
capsul_process = \
    'morphologist.capsul.foetus.imprints_skeleton.ImprintsSkeleton'

signature = Signature(
    'white_mesh', ReadDiskItem('Hemisphere white mesh', 'aims mesh formats'),
    'cortex', ReadDiskItem('CSF+Grey mask', 'aims readable volume formats'),
    'output_cortex',
    WriteDiskItem('CSF+Grey mask', 'aims writable volume formats'),
    'grey_white',
    ReadDiskItem('Morphologist Grey White Mask',
                 'aims readable volume formats'),
    'skeleton',
    WriteDiskItem('Cortex skeleton', 'aims writable volume formats'),
    'roots',
    WriteDiskItem('Cortex catchment bassins', 'aims writable volume formats'),
)
