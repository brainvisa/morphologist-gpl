#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
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

import shfjGlobals, registration

from neuroProcesses import *
name = '3 - Compute Brain Mask'
userLevel = 2

signature = Signature(
  'mri_corrected', ReadDiskItem( "T1 MRI Bias Corrected",
      shfjGlobals.vipVolumeFormats ),
  'brain_mask', WriteDiskItem( 'T1 Brain Mask',
      shfjGlobals.aimsWriteVolumeFormats ),
  'variant', Choice("2005 based on white ridge",
                    "Standard + (iterative erosion)",
                    "Standard + (selected erosion)",
                    "Standard + (iterative erosion) without regularisation",
                    "Robust + (iterative erosion)",
                    "Robust + (selected erosion)",
                    "Robust + (iterative erosion) without regularisation",
                    "Fast (selected erosion)",
                    "2010" ),
  'erosion_size', OpenChoice( 1, 1.5, 1.8, 2, 2.5, 3, 3.5 ,4 ),
  'visu', Choice("No","Yes"),
  'white_ridges', ReadDiskItem( "T1 MRI White Matter Ridges",
      shfjGlobals.aimsVolumeFormats ),
  'Commissure_coordinates', ReadDiskItem( 'Commissure coordinates',
      'Commissure coordinates'),
  'variance', ReadDiskItem( "T1 MRI Variance", shfjGlobals.aimsVolumeFormats ),
  'edges', ReadDiskItem( "T1 MRI Edges", shfjGlobals.aimsVolumeFormats ),
  'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'lesion_mask', ReadDiskItem( 'Lesion Mask', shfjGlobals.vipVolumeFormats ),
  'layer', Choice("0","1","2","3","4","5"),
  'first_slice', Integer(),
  'last_slice', Integer(),
)

def initialization( self ):
  self.linkParameters( 'mri_corrected', 'mri_corrected' )
  self.linkParameters( 'histo_analysis', 'mri_corrected' )
  self.linkParameters( 'brain_mask', 'mri_corrected' )
  self.linkParameters( 'white_ridges', 'mri_corrected' )
  self.linkParameters( 'variance', 'mri_corrected' )
  self.linkParameters( 'edges', 'mri_corrected' )
  self.erosion_size = 1.8
  self.first_slice = 0
  self.last_slice = 0
  self.setOptional('white_ridges')
  self.setOptional('lesion_mask')
  self.setOptional('Commissure_coordinates')
  self.linkParameters( 'Commissure_coordinates', 'mri_corrected' )
  self.variant = "2010"
  self.visu = "No"
  self.layer = "0"
 
def execution( self, context ):
  if os.path.exists(self.brain_mask.fullName() + '.loc'):
      context.write(self.brain_mask.fullName(), ' has been locked')
      context.write('Remove',self.brain_mask.fullName(),'.loc if you want to trigger a new segmentation')
  else:
      option_list = []
      constant_list = ['VipGetBrain','-berosion',self.erosion_size,'-i',self.mri_corrected.fullPath(),'-analyse', 'r', '-hname',  self.histo_analysis.fullPath(),'-bname', self.brain_mask.fullPath(),'-First',self.first_slice,'-Last', self.last_slice, '-layer', self.layer]
      if self.Commissure_coordinates is not None:
        option_list += ['-Points', self.Commissure_coordinates.fullPath()]
      if self.lesion_mask is not None:
        option_list += ['-patho', self.lesion_mask.fullPath()]
      if self.variant == "2005 based on white ridge":
        call_list = ['-m', "5", '-Ridge',self.white_ridges.fullPath()]
      elif self.variant == "Standard + (iterative erosion)":
        call_list = ['-m', "Standard"]
      elif self.variant == "Standard + (selected erosion)":
        call_list = ['-m', "standard"]
      elif self.variant == "Standard + (iterative erosion) without regularisation":
        call_list = ['-m', "Standard",'-niter', 0]
      elif self.variant == "Robust + (iterative erosion)":
        call_list = ['-m', "Robust"]
      elif self.variant == "Robust + (selected erosion)":
        call_list = ['-m', "robust"]
      elif self.variant == "Robust + (iterative erosion) without regularisation":
        call_list = ['-m', "Robust",'-niter', 0]
      elif self.variant == "Fast (selected erosion)":
        call_list = ['-m', "fast"]
      elif self.variant == "2010":
        call_list = [ '-m', "V"]
        constant_list += [ '-Variancename', self.variance.fullPath(), '-Edgesname', self.edges.fullPath(), '-Ridge', self.white_ridges.fullPath()]
      else:
        raise RuntimeError( _t_( 'Variant <em>%s</em> not implemented' ) % self.variant )
      result = []
      apply( context.system, constant_list+option_list+call_list )

      # manage referentials
      tm = registration.getTransformationManager()
      tm.copyReferential(self.mri_corrected, self.brain_mask)

      if self.visu == "Yes":
        result.append(context.runProcess('AnatomistShowBrainMask',
          self.brain_mask,self.mri_corrected))
      return result
