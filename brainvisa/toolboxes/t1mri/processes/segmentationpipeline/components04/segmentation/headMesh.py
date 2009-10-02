# Copyright CEA and IFR 49 (2000-2005)
#
#  This software and supporting documentation were developed by
#      CEA/DSV/SHFJ and IFR 49
#      4 place du General Leclerc
#      91401 Orsay cedex
#      France
#
# This software is governed by the CeCILL license version 2 under 
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the 
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info". 
# 
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability. 
# 
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security. 
# 
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.

from neuroProcesses import *
import shfjGlobals
import registration

name = 'Head Mesh'
userLevel = 0

# Argument declaration
signature = Signature(
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
      'Aims readable volume formats' ),
  'head_mask', WriteDiskItem( 'Head Mask',
      'Aims writable volume formats' ),
  'head_mesh', WriteDiskItem( 'Head Mesh', 'Aims mesh formats' ),
  'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'keep_head_mask', Boolean(), 
  'first_slice', Integer(),
  'threshold', Integer(),
  'closing', Float(),
  'remove_mask', ReadDiskItem( '3D Volume', 'Aims readable volume formats' ),
)

# Default values
def initialization( self ):
  self.linkParameters( 'head_mask', 'histo_analysis' )
  self.linkParameters( 'head_mesh', 'head_mask' )
  self.linkParameters( 'histo_analysis', 'mri_corrected' )
  self.setOptional('first_slice')
  self.setOptional('threshold')
  self.setOptional('closing')
  self.setOptional('head_mask')
  self.setOptional('histo_analysis')
  self.setOptional('remove_mask')
  self.first_slice = None
  self.threshold = None
  self.closing = None
  self.keep_head_mask = 0

def execution( self, context ):
  if self.head_mask is not None and self.keep_head_mask:
    mask = self.head_mask
  else:
    mask = context.temporary( 'GIS image' )
  call_list = [ 'VipGetHead', 
                '-i', self.mri_corrected,
                '-o', mask,
                '-w', 't', '-r', 't' ]
  option_list = []
  if self.remove_mask is not None:
      option_list += [ '-h', self.remove_mask ]
  if self.histo_analysis is not None:
      option_list += [ '-hn',self.histo_analysis ]
  if self.first_slice is not None:
      option_list += [ '-n', self.first_slice ]
  if self.threshold is not None:
      option_list += [ '-t', self.threshold ]
  if self.closing is not None:
      option_list += [ '-c', self.closing ]
  apply( context.system, call_list+option_list )
  context.system( 'AimsMeshBrain', '-i', mask.fullPath(), '-o',
                  self.head_mesh.fullPath() )
  trManager = registration.getTransformationManager()
  trManager.copyReferential( self.mri_corrected, self.head_mesh )
  if self.keep_head_mask:
    trManager.copyReferential( self.mri_corrected, self.head_mask )
