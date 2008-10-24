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
from brainvisa import shelltools
import registration

name = '5 - Compute Grey white Interface'
userLevel = 2

# Argument declaration
signature = Signature(
  'Side', Choice("Both","Left","Right"),
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected', 'GIS Image'),
  'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'split_mask', ReadDiskItem( "Voronoi Diagram", 'GIS Image' ),
  'Use_ridges', Boolean(),
  'white_ridges', ReadDiskItem( "T1 MRI White Matter Ridges", 'GIS Image' ),
  'LGW_interface', WriteDiskItem( 'Left Grey White Mask', 'GIS Image' ),
  'RGW_interface', WriteDiskItem( 'Right Grey White Mask', 'GIS Image' ),
  'Compute_mesh', Boolean(),
  'left_white_mesh', WriteDiskItem( 'Left Hemisphere White Mesh', 'MESH mesh' ),
  'right_white_mesh', WriteDiskItem( 'Right Hemisphere White Mesh', 'MESH mesh' ),
  'pressure', Choice("0","25","50","75","100","125","150"),
  'iterations', Integer(), 
  'rate', Float(),
 ) 
# Default values
def initialization( self ):
  self.linkParameters( 'histo_analysis', 'mri_corrected' )
  self.linkParameters( 'LGW_interface', 'mri_corrected' )
  self.linkParameters( 'RGW_interface', 'mri_corrected' )
  self.linkParameters( 'split_mask', 'mri_corrected' )
  self.linkParameters( 'white_ridges', 'mri_corrected' )
  self.linkParameters( 'left_white_mesh', 'mri_corrected' )
  self.linkParameters( 'right_white_mesh', 'mri_corrected' )
  self.Use_ridges = "True"
  self.setOptional('white_ridges')
  self.Side = "Both"
  self.compute_mesh = "True"
  self.pressure = "0"
  self.iterations = 10
  self.rate = 0.2
#

def execution( self, context ):
  context.write( "Masking Bias corrected image with hemisphere masks...")
  Lbraing = context.temporary( 'GIS Image' )
  context.system( 'VipMask', '-i', self.mri_corrected.fullName(), "-m", 
                  self.split_mask.fullName(), "-o", Lbraing.fullName(), "-w",
                  "t", "-l", "2" )
  Rbraing = context.temporary( 'GIS Image' )
  context.system( "VipMask", "-i", self.mri_corrected.fullName(), "-m",
                  self.split_mask.fullName(), "-o", Rbraing.fullName(),
                  "-w", "t", "-l", "1" )
  tm=registration.getTransformationManager()
  if self.Side in ('Left','Both'):
       
      if os.path.exists(self.LGW_interface.fullName() + '.loc'):
        context.write( "Left grey/white locked")
      else:
        context.write( "Detecting left grey/white interface..." )
        if self.Use_ridges:
          context.system( "VipHomotopicSnake", "-i", Lbraing.fullName(), "-h",
                        self.histo_analysis.fullName(), "-o", 
                        self.LGW_interface.fullName(), "-R",  self.white_ridges.fullName(), "-w", "t" )
        else:
          context.system( "VipHomotopicSnake", "-i", Lbraing.fullName(), "-h",
                        self.histo_analysis.fullName(), "-o", 
                        self.LGW_interface.fullName(), "-w", "t" )
        tm.copyReferential(self.mri_corrected, self.LGW_interface)
      if self.Compute_mesh:
          if os.path.exists(self.left_white_mesh.fullName() + '.loc'):
            context.write( "Left Hemisphere White Mesh Locked")
          else:
            context.write("Reconstructing left hemisphere white surface...")
            white = context.temporary( 'GIS Image' )  
            context.system( "VipSingleThreshold", "-i", self.LGW_interface.fullName(), 
                      "-o", white.fullName(), "-t", "0", "-c", "b", "-m",
                      "ne", "-w", "t" )
            context.system( "AimsMeshWhite", "-i", white.fullPath(), "-o", 
                      self.left_white_mesh.fullPath() )
            del white
      
            context.write( "Smoothing mesh..." )
            context.runProcess( 'meshSmooth', mesh=self.left_white_mesh,
                                iterations=self.iterations,rate=self.rate )
            tm.copyReferential(self.mri_corrected, self.left_white_mesh)
       
  if self.Side in ('Right','Both'):
       
      if os.path.exists(self.RGW_interface.fullName() + '.loc'):
        context.write( "Right grey/white locked")
      else:
        context.write( "Detecting right grey/white interface..." )
        if self.Use_ridges:
          context.system( "VipHomotopicSnake", "-i", Rbraing.fullName(), "-h",
                        self.histo_analysis.fullName(), "-o", 
                        self.RGW_interface.fullName(), "-R",  self.white_ridges.fullName(), "-w", "t" )
        else:
          context.system( "VipHomotopicSnake", "-i", Rbraing.fullName(), "-h",
                        self.histo_analysis.fullName(), "-o", 
                        self.RGW_interface.fullName(), "-w", "t" )
          tm.copyReferential(self.mri_corrected, self.LGW_interface)
          
      if self.Compute_mesh:
        if os.path.exists(self.right_white_mesh.fullName() + '.loc'):
            context.write( "Right Hemisphere White Mesh Locked")
        else:
            context.write("Reconstructing right hemisphere white surface...")
            white = context.temporary( 'GIS Image' )  
            context.system( "VipSingleThreshold", "-i", self.RGW_interface.fullName(), 
                      "-o", white.fullName(), "-t", "0", "-c", "b", "-m",
                      "ne", "-w", "t" )
            context.system( "AimsMeshWhite", "-i", white.fullPath(), "-o", 
                      self.right_white_mesh.fullPath() )
            del white
      
            context.write( "Smoothing mesh..." )
            context.runProcess( 'meshSmooth', mesh=self.right_white_mesh,
                                iterations=self.iterations,rate=self.rate )
            tm.copyReferential(self.mri_corrected, self.right_white_mesh)

         
  del Lbraing
  del Rbraing
