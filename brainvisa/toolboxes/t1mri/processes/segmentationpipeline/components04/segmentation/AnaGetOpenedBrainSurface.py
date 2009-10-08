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

from neuroProcesses import *

#
# VipGetOpenedBrainSurface process declaration
#

name = 'Ana Get Opened Whole Brain Surface'
userLevel = 0

# Argument declaration
signature = Signature(
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected', 'GIS Image'),
  'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'brain_mask', ReadDiskItem( 'T1 Brain Mask', 'GIS Image' ),
  'cortex', WriteDiskItem( 'Both CSF+GREY Mask', 'GIS Image' ),
  'brain_mesh', WriteDiskItem( "Brain Mesh", 'MESH mesh' ),
) 
# Default values
def initialization( self ):
  self.linkParameters( 'histo_analysis', 'mri_corrected' )
  self.linkParameters( 'brain_mask', 'mri_corrected' )
  self.linkParameters( 'cortex', 'mri_corrected' )
  self.linkParameters( 'brain_mesh', 'mri_corrected' )
#
# VipGetOpenedBrainSurface process declaration
#

def execution( self, context ):
  if os.path.exists(self.brain_mesh.fullName() + '.loc'):
    context.write( "Whole Brain Mesh locked")
  else:
    context.write( "Computing whole brain surface...")
    braing = context.temporary( 'GIS Image' )
    context.system( "VipMask", "-i", self.mri_corrected.fullPath(),
                    "-m", self.brain_mask.fullPath(), "-o",
                    braing.fullPath(), "-w", "t" )
    if os.path.exists(self.cortex.fullPath() + '.loc'):
      context.write( "grey/white interface detection locked")
    else:
      context.write( "Detecting Grey/White Interface..." )
      context.system( "VipHomotopicSnake", "-i", braing.fullPath(), "-h",
                      self.histo_analysis.fullPath(), "-o",
                      self.cortex.fullPath(), "-w", "t" )

      context.write("Reconstructing brain surface...")
      white = context.temporary( 'GIS Image' )  
      context.system( "VipSingleThreshold", "-i", self.cortex.fullPath(),
                      "-o", white.fullPath(), "-t", "0", "-c", "b", "-m",
                      "eq", "-w", "t" )
      openbrain = context.temporary( 'GIS Image' )  
      context.system( "VipOpenFold", "-i", braing.fullPath(), "-s",
                      white.fullPath(), "-o", openbrain.fullPath(),
                      "-a", "i", "-w", "t" )
      del white
      del braing
  
      context.write( "Triangulation and Decimation..." )
      context.system( "AimsMeshBrain", "-i", openbrain.fullPath(), "-o", 
                      self.brain_mesh.fullPath() )
      del openbrain
