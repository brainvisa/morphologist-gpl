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

#
# Brain segmentation process declaration
#
from neuroProcesses import *
import shfjGlobals, registration

name = 'Vip Get Brain'
userLevel = 1

# Argument declaration
signature = Signature(
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
      shfjGlobals.aimsVolumeFormats ),
  'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'mode',
    Choice("standard+iterative","standard","robust+iterative","robust","fast"),
  'Commissure_coordinates', ReadDiskItem( 'Commissure coordinates',
      'Commissure coordinates'),
  'brain_mask', WriteDiskItem( "T1 Brain Mask",
      shfjGlobals.aimsWriteVolumeFormats ),
  'regularization', Boolean(),
  'erosion_size', Float(),
  'layer', Choice("0","1","2","3","4","5"),
  'first_slice', Integer(),
  'last_slice', Integer(),
  'lesion_mask', ReadDiskItem( '3D Volume', shfjGlobals.vipVolumeFormats),
)

# Default values
def initialization( self ):
  self.linkParameters( 'histo_analysis', 'mri_corrected' )
  self.linkParameters( 'brain_mask', 'mri_corrected' )
  self.mode = "standard+iterative"
  self.linkParameters( 'Commissure_coordinates', 'mri_corrected' )
  self.setOptional('Commissure_coordinates')
  self.regularization = 1
  self.erosion_size = 2.1
  self.first_slice = 1
  self.last_slice = 3
  self.setOptional('lesion_mask')
  self.layer = "0"


def execution( self, context ):
    if os.path.exists(self.brain_mask.fullName() + '.loc'):
      context.write(self.brain_mask.fullName(), ' has been locked')
      context.write('Remove',self.brain_mask.fullName(),'.loc if you want to trigger a new segmentation')
    else:
      option_list = []
      if self.Commissure_coordinates is not None:
        option_list += ['-Points', self.Commissure_coordinates.fullPath()]
      if self.lesion_mask is not None:
        option_list += ['-patho', self.lesion_mask.fullPath()]
      if self.regularization is not 1:
        option_list += ['-niter', 0]
      if self.mode=="standard+iterative":
        themode="Standard"
      elif self.mode=="standard":
        themode="standard"
      elif self.mode=="robust+iterative":
        themode="Robust"
      elif self.mode=="robust":
        themode="robust"
      elif self.mode=="fast":
        themode="fast"
      call_list = ['VipGetBrain',
                   '-m', themode,
                   '-i',self.mri_corrected.fullPath(),
                   '-analyse', 'r', '-hname',  self.histo_analysis.fullPath(),
                   '-bname', self.brain_mask.fullPath(),
                   '-berosion',self.erosion_size,
                   '-First',self.first_slice,
                   '-Last', self.last_slice,
		   '-layer', self.layer]
      apply( context.system, call_list+option_list )

      # manage referentials
      tm = registration.getTransformationManager()
      tm.copyReferential(self.mri_corrected, self.brain_mask)

