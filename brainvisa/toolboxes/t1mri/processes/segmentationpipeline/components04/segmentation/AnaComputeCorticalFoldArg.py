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
import  os
import registration

name = 'Cortical Fold Arg (3.0)'
userLevel = 0

# Argument declaration
signature = Signature(
  'Side', Choice("Both","Left","Right"),
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected', 'GIS Image'),
  'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'brain_voronoi', ReadDiskItem( 'Voronoi Diagram', 'GIS Image'),
  'left_hemi_cortex', WriteDiskItem( 'Left CSF+GREY Mask', 'GIS Image' ),
  'right_hemi_cortex', WriteDiskItem( 'Right CSF+GREY Mask', 'GIS Image' ),
  'Lskeleton', WriteDiskItem( 'Left Cortex Skeleton', 'GIS image' ),
  'Rskeleton', WriteDiskItem( 'Right Cortex Skeleton', 'GIS Image' ),
  'Lroots', WriteDiskItem( 'Left Cortex Catchment Bassins', 'GIS image' ),
  'Rroots', WriteDiskItem( 'Right Cortex Catchment Bassins', 'GIS Image' ),
  'Lgraph', WriteDiskItem( 'Left Cortical folds graph', 'Graph',
      requiredAttributes = { 'graph_version' : '3.0' } ),
  'Rgraph', WriteDiskItem( 'Right Cortical folds graph', 'Graph',
      requiredAttributes = { 'graph_version' : '3.0' } ),
   'Commissure_coordinates', ReadDiskItem( 'Commissure coordinates','Commissure coordinates'),
  'compute_fold_meshes', Choice("Yes","No")
 ) 
# Default values
def initialization( self ):
  self.linkParameters( 'histo_analysis', 'mri_corrected' )
  self.linkParameters( 'Lgraph', 'mri_corrected' )
  self.linkParameters( 'Rgraph', 'mri_corrected' )
  self.linkParameters( 'Lskeleton', 'mri_corrected' )
  self.linkParameters( 'Rskeleton', 'mri_corrected' )
  self.linkParameters( 'Lroots', 'mri_corrected' )
  self.linkParameters( 'Rroots', 'mri_corrected' )
  self.linkParameters( 'left_hemi_cortex', 'mri_corrected' )
  self.linkParameters( 'right_hemi_cortex', 'mri_corrected' )
  self.linkParameters( 'brain_voronoi', 'mri_corrected' )
  self.linkParameters( 'Commissure_coordinates', 'mri_corrected' )
  self.Side = "Both"
  self.compute_fold_meshes = "Yes"
#
#

def execution( self, context ):
  context.write( "Masking Bias corrected image with hemisphere masks...")
  Lbraing = context.temporary( 'GIS Image' )
  context.system( 'VipMask', '-i', self.mri_corrected.fullName(), "-m", 
                  self.brain_voronoi.fullName(), "-o", Lbraing.fullName(), "-w",
                  "t", "-l", "2" )
  Rbraing = context.temporary( 'GIS Image' )
  context.system( "VipMask", "-i", self.mri_corrected.fullName(), "-m",
                  self.brain_voronoi.fullName(), "-o", Rbraing.fullName(),
                  "-w", "t", "-l", "1" )

  trManager = registration.getTransformationManager()
  if self.Side in ('Left','Both'):

      if os.path.exists(self.left_hemi_cortex.fullName() + '.loc'):
        context.write( "Left grey/white locked")
      else:
        context.write( "Detecting left grey/white interface..." )
        context.system( "VipHomotopicSnake", "-i", Lbraing.fullName(), "-h",
                        self.histo_analysis.fullName(), "-o", 
                        self.left_hemi_cortex.fullName(), "-w", "t" )
      trManager.copyReferential( self.brain_voronoi, self.left_hemi_cortex )

      context.write("Computing skeleton and buried gyrus watershed...")
      context.system( "VipSkeleton", "-i", self.left_hemi_cortex.fullName(),
                      "-so", self.Lskeleton.fullName(), "-vo", 
                      self.Lroots.fullName(), "-g", Lbraing.fullName(), "-w",
                      "t" )
      trManager.copyReferential( self.brain_voronoi, self.Lroots )
      trManager.copyReferential( self.brain_voronoi, self.Lskeleton )


      context.write("Building Attributed Relational Graph...")
      context.system( "VipFoldArg", "-i", self.Lskeleton.fullName(), "-v", 
                      self.Lroots.fullName(), "-o", self.Lgraph.fullName() )
      if self.compute_fold_meshes == "Yes":
        context.system( "VipFoldArgAtt", "-i", self.Lskeleton.fullName(), "-lh",
                        Lbraing.fullName(), "-rh", Rbraing.fullName(), "-a",
                        self.Lgraph.fullName(), "-P", 
                        self.Commissure_coordinates.fullName(), "-t", "y" )

      else :
        context.system( "VipFoldArgAtt", "-i", self.Lskeleton.fullName(), "-lh",
                        Lbraing.fullName(), "-rh", Rbraing.fullName(), "-a",
                        self.Lgraph.fullName(), "-P", 
                        self.Commissure_coordinates.fullName(), "-t", "n" )

      context.system( "VipFoldArg", "-a", self.Lgraph.fullName(), "-o",
                      self.Lgraph.fullName() + "local", "-w", "g" )
      context.system( "AimsGraphConvert", "-i",
                      self.Lgraph.fullName() + "local.arg", "-o",
                      self.Lgraph.fullPath( 0 ) , "-b",
                      os.path.basename( self.Lgraph.fullName() ) + '.data', "-g" )
      trManager.copyReferential( self.brain_voronoi, self.Lgraph )
      context.write( 'computing additional attributes' )
      context.system( 'AimsGraphComplete', '-i', self.Lgraph.fullPath(),
                      '--dversion', '3.0', '--mversion', '3.0' )
      shelltools.rm( self.Lgraph.fullName() + "local*")
      shelltools.rm( self.Lgraph.fullName() + ".data/Tmtk")
      shelltools.rm( self.Lgraph.fullName() + "*.Vip")

  if self.Side in ('Right','Both'):

      if os.path.exists(self.right_hemi_cortex.fullName() + '.loc'):
        context.write( "Right grey/white locked")
      else:
        context.write( "Detecting right grey/white interface..." )
        context.system( "VipHomotopicSnake", "-i", Rbraing.fullName(), "-h",
                        self.histo_analysis.fullName(), "-o", 
                        self.right_hemi_cortex.fullName(), "-w", "t" )
      trManager.copyReferential( self.brain_voronoi, self.right_hemi_cortex )

      context.write("Computing skeleton and buried gyrus watershed...")
      context.system( "VipSkeleton", "-i", self.right_hemi_cortex.fullName(),
                      "-so", self.Rskeleton.fullName(), "-vo",
                      self.Rroots.fullName(), "-g", Rbraing.fullName(), 
                      "-w", "t" )
      trManager.copyReferential( self.brain_voronoi, self.Rroots )
      trManager.copyReferential( self.brain_voronoi, self.Rskeleton )

      context.write("Building Attributed Relational Graph...")
      context.system( "VipFoldArg", "-i", self.Rskeleton.fullName(), "-v",
                      self.Rroots.fullName(), "-o", self.Rgraph.fullName() ) 
      if self.compute_fold_meshes == "Yes":
        context.system( "VipFoldArgAtt", "-i", self.Rskeleton.fullName(),
                        "-lh", Lbraing.fullName(), "-rh", Rbraing.fullName(),
                        "-a", self.Rgraph.fullName(), "-P", 
                        self.Commissure_coordinates.fullName(), "-t", "y" )
      else :
        context.system( "VipFoldArgAtt", "-i", self.Rskeleton.fullName(), "-lh",
                        Lbraing.fullName(), "-rh", Rbraing.fullName(), "-a",
                        self.Rgraph.fullName(), "-P", 
                        self.Commissure_coordinates.fullName(), "-t", "n" )

      context.system( "VipFoldArg", "-a", self.Rgraph.fullName(), "-o",
                      self.Rgraph.fullName() + "local", "-w", "g" ) 
      context.system( "AimsGraphConvert", "-i", 
                      self.Rgraph.fullName() + "local.arg", "-o",
                      self.Rgraph.fullPath( 0 ), "-b",
                      os.path.basename( self.Rgraph.fullName() ) + ".data", "-g" )
      trManager.copyReferential( self.brain_voronoi, self.Rgraph )
      context.write( 'computing additional attributes' )
      context.system( 'AimsGraphComplete', '-i', self.Rgraph.fullPath(),
                      '--dversion', '3.0', '--mversion', '3.0' )
      shelltools.rm( self.Rgraph.fullName()+ "local*" )
      shelltools.rm( self.Rgraph.fullName()+ ".data/Tmtk" )
      shelltools.rm( self.Rgraph.fullName()+ "*.Vip" )

  del Lbraing
  del Rbraing
