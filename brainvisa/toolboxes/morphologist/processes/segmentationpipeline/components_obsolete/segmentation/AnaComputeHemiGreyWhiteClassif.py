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

from brainvisa.processes import *
import registration

name = 'Ana Compute Hemi Grey White Classification'
userLevel = 0

# Argument declaration
signature = Signature(
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
      'Aims readable volume formats' ),
  'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'brain_voronoi', ReadDiskItem( 'Voronoi Diagram',
      'Aims readable volume formats' ),
  'Side', Choice("Both","Left","Right"),
  'left_grey_white', WriteDiskItem( 'Left Grey White Mask',
      'Aims writable volume formats' ),
  'right_grey_white', WriteDiskItem( 'Right Grey White Mask',
      'Aims writable volume formats' ),
 ) 
# Default values
def initialization( self ):
  self.linkParameters( 'histo_analysis', 'mri_corrected' )
  self.linkParameters( 'left_grey_white', 'mri_corrected' )
  self.linkParameters( 'right_grey_white', 'mri_corrected' )
  self.linkParameters( 'brain_voronoi', 'mri_corrected' )
  self.Side = "Both"
#
#

def execution( self, context ):
  tm=registration.getTransformationManager()
  if self.Side in ('Left','Both'):
       
      if os.path.exists(self.left_grey_white.fullName() + '.loc'):
        context.write( "Left grey-white locked")
      else:
        context.write( "Computing left hemisphere grey-white classification..." )
        context.system( "VipGreyWhiteClassif", "-i",
                        self.mri_corrected, "-h",
                        self.histo_analysis, "-m",
                        self.brain_voronoi, "-o",
                        self.left_grey_white, "-l", "2", "-w", "t", "-a", "R")
        tm.copyReferential(self.mri_corrected, self.left_grey_white)
  if self.Side in ('Right','Both'):
       
      if os.path.exists(self.right_grey_white.fullName() + '.loc'):
        context.write( "Right grey-white locked")
      else:
        context.write( "Computing right hemisphere grey-white classification..." )
        context.system( "VipGreyWhiteClassif", "-i",
                        self.mri_corrected, "-h",
                        self.histo_analysis, "-m",
                        self.brain_voronoi, "-o",
                        self.right_grey_white, "-l", "1", "-w",
                        "t", "-a", "R")
        tm.copyReferential(self.mri_corrected, self.right_grey_white)
