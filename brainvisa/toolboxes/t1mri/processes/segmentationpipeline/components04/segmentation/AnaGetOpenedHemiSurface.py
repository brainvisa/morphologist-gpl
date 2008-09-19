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
import registration

#
# VipGetOpenedHemiSurface process declaration
#

name = 'Ana Get Opened Hemi Surface'
userLevel = 0

# Argument declaration
signature = Signature(
  'Side', Choice("Both","Left","Right"),
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected', 'GIS Image'),
  'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'brain_voronoi', ReadDiskItem( 'Voronoi Diagram', 'GIS Image' ),
  'left_hemi_cortex', WriteDiskItem( 'Left CSF+GREY Mask', 'GIS Image' ),
  'right_hemi_cortex', WriteDiskItem( 'Right CSF+GREY Mask', 'GIS Image' ),
  'left_hemi_mesh', WriteDiskItem( 'Left Hemisphere Mesh', 'MESH mesh' ),
  'right_hemi_mesh', WriteDiskItem( 'Right Hemisphere Mesh', 'MESH mesh' ),
) 
# Default values
def initialization( self ):
  self.linkParameters( 'histo_analysis', 'mri_corrected' )
  self.linkParameters( 'left_hemi_mesh', 'mri_corrected' )
  self.linkParameters( 'right_hemi_mesh', 'mri_corrected' )
  self.linkParameters( 'left_hemi_cortex', 'mri_corrected' )
  self.linkParameters( 'right_hemi_cortex', 'mri_corrected' )
  self.linkParameters( 'brain_voronoi', 'mri_corrected' )
  self.Side = "Both"


def execution( self, context ):
  trManager = registration.getTransformationManager()
  if self.Side in ('Left','Both'):
    if os.path.exists(self.left_hemi_mesh.fullName() + '.loc'):
      context.write( "Left Hemisphere Mesh locked")
    else:  
      context.write( "Masking Bias corrected image with left hemisphere mask...")
      braing = context.temporary( 'GIS Image' )
      context.system( "VipMask", "-i", self.mri_corrected.fullName(), "-m",
                      self.brain_voronoi.fullName(), "-o", 
                      braing.fullName(), "-w", "t", "-l", "2" )
      
      if os.path.exists(self.left_hemi_cortex.fullName() + '.loc'):
        context.write( "Left grey/white locked")
      else:
        context.write( "Detecting left grey/white interface..." )
        context.system( "VipHomotopicSnake", "-i", braing.fullName(), "-h", 
                        self.histo_analysis.fullName(), "-o", 
                        self.left_hemi_cortex.fullName(), "-w", "t" )
      trManager.copyReferential( self.mri_corrected, self.left_hemi_cortex )
    
      context.write("Reconstructing left hemisphere surface...")
      white = context.temporary( 'GIS Image' )  
      context.system( "VipSingleThreshold", "-i", 
                      self.left_hemi_cortex.fullName(), "-o", 
                      white.fullName(), "-t", "0", "-c", "b", "-m", "eq",
                      "-w", "t" )
      openbrain = context.temporary( 'GIS Image' )  
      context.system( "VipOpenFold", "-i", braing.fullName(), "-s", 
                      white.fullName(), "-o", openbrain.fullName(), 
                      "-a", "i", "-w", "t", "-n", "5" )
      del braing
      del white
    
      context.write( "Triangulation and Decimation..." )
      context.system( "AimsMeshBrain", "-i", openbrain.fullPath(), "-o", 
                      self.left_hemi_mesh.fullPath() )
      trManager.copyReferential( self.mri_corrected, self.left_hemi_mesh )
      del openbrain
    
  if self.Side in ('Right','Both'):
    if os.path.exists(self.right_hemi_mesh.fullName() + '.loc'):
      context.write( "Right Hemisphere locked")
    else:  
      context.write( "Masking Bias corrected image with right hemisphere mask...")
      braing = context.temporary( 'GIS Image' )
      context.system( "VipMask", "-i", self.mri_corrected.fullName(), "-m", 
                      self.brain_voronoi.fullName(), "-o", 
                      braing.fullName(), "-w", "t", "-l", "1" )
      
      if os.path.exists(self.right_hemi_cortex.fullName() + '.loc'):
        context.write( "Right grey/white interface locked")
      else:
        context.write( "Detecting right grey/white interface...")
        context.system( "VipHomotopicSnake", "-i", braing.fullName(), "-h", 
                        self.histo_analysis.fullName(), "-o", 
                        self.right_hemi_cortex.fullName(), "-w", "t" )
      trManager.copyReferential( self.mri_corrected, self.right_hemi_cortex )

      context.write("Reconstructing right hemisphere surface...")
      white = context.temporary( 'GIS Image' )  
      context.system( "VipSingleThreshold", "-i", 
                      self.right_hemi_cortex.fullName(), "-o", 
                      white.fullName(), "-t", "0", "-c", "b", "-m", "eq",
                      "-w", "t" )
      openbrain = context.temporary( 'GIS Image' )  
      context.system( "VipOpenFold", "-i", braing.fullName(), "-s", 
                      white.fullName(), "-o", openbrain.fullName(), 
                      "-a", "i", "-w", "t" )
      del braing
      del white
  
      context.write( "Triangulation and Decimation..." )
      context.system( "AimsMeshBrain", "-i", openbrain.fullPath(), "-o", 
                      self.right_hemi_mesh.fullPath() )
      trManager.copyReferential( self.mri_corrected, self.right_hemi_mesh )
      del openbrain
