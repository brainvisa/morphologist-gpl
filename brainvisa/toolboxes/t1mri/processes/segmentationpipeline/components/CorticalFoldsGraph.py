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

name = 'Cortical Fold Graph (3.1+)'
userLevel = 2

# Argument declaration
signature = Signature(
  'side', Choice( 'Left', 'Right' ), 
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
      'Aims readable volume formats' ),
  'split_mask', ReadDiskItem( 'Voronoi Diagram',
      'Aims readable volume formats' ),
  'hemi_cortex', ReadDiskItem( 'CSF+GREY Mask',
      'Aims readable volume formats' ),
  'skeleton', WriteDiskItem( 'Cortex Skeleton',
      'Aims writable volume formats' ),
  'roots', WriteDiskItem( 'Cortex Catchment Bassins',
      'Aims writable volume formats' ),
  'graph_version', OpenChoice( '3.1', '3.2' ),
  'graph', WriteDiskItem( 'Cortical folds graph', 'Graph' ),
  'commissure_coordinates', ReadDiskItem( 'Commissure coordinates',
                                          'Commissure coordinates'),
  'Talairach_transform',
  ReadDiskItem( 'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
                'Transformation matrix' ), 
  'compute_fold_meshes', Boolean(),
  'allow_multithreading', Boolean(),
 )


# Default values
def initialization( self ):
  def linkSide( self, proc ):
    p = ReadDiskItem( 'CSF+GREY Mask', 'GIS image' )
    return p.findValue( self.mri_corrected,
                        requiredAttributes = { 'side' : self.side.lower() } )

  def linkGraphVersion( self, proc ):
    p = WriteDiskItem( 'Cortical folds graph', 'Graph' )
    return p.findValue( self.hemi_cortex,
                        requiredAttributes = { 'labelled' : 'No',
                        'graph_version' : self.graph_version } )

  self.linkParameters( 'split_mask', 'mri_corrected' )
  self.linkParameters( 'hemi_cortex', ( 'mri_corrected', 'side' ), linkSide )
  self.linkParameters( 'skeleton', 'hemi_cortex' )
  self.linkParameters( 'graph', ( 'hemi_cortex', 'graph_version' ),
    linkGraphVersion )
  self.linkParameters( 'roots', 'hemi_cortex' )
  self.linkParameters( 'commissure_coordinates', 'mri_corrected' )
  self.linkParameters( 'Talairach_transform', 'mri_corrected' )
  self.compute_fold_meshes = True
  self.setOptional( 'commissure_coordinates' )

  eNode = SerialExecutionNode( self.name, parameterized = self )
  eNode.addChild( 'CorticalFoldsGraphThickness',
                   ProcessExecutionNode( 'CorticalFoldsGraphThickness',
                   optional = 1 ) )
  #self.clearLinksTo( eNode.parseParameterString( 'CorticalFoldsGraphThickness.hemi_cortex' ) )
  #self.clearLinksTo( eNode.parseParameterString( 'CorticalFoldsGraphThickness.output_graph' ) )
  eNode.CorticalFoldsGraphThickness.clearLinksTo( 'hemi_cortex' )
  eNode.CorticalFoldsGraphThickness.clearLinksTo( 'output_graph' )
  eNode.addLink( 'CorticalFoldsGraphThickness.graph', 'graph' )
  eNode.addLink( 'graph', 'CorticalFoldsGraphThickness.graph' )
  eNode.addLink( 'CorticalFoldsGraphThickness.hemi_cortex', 'hemi_cortex' )
  eNode.addLink( 'hemi_cortex', 'CorticalFoldsGraphThickness.hemi_cortex' )
  eNode.addLink( 'CorticalFoldsGraphThickness.output_graph', 'graph' )
  eNode.addLink( 'graph', 'CorticalFoldsGraphThickness.output_graph' )
  self.setExecutionNode( eNode )

def execution( self, context ):
  context.write( "Masking Bias corrected image with hemisphere masks...")
  braing = context.temporary( 'GIS Image' )
  if self.side == 'Left':
    masklabel = '2'
  else:
    masklabel = '1'
  context.system( 'VipMask', '-i', self.mri_corrected, "-m",
                  self.split_mask, "-o", braing,
                  "-w", "t", "-l", masklabel )

  context.write("Computing skeleton and buried gyrus watershed...")
  context.system( "VipSkeleton", "-i", self.hemi_cortex,
                  "-so", self.skeleton, "-vo",
                  self.roots, "-g", braing, "-w", "t" )

  context.write("Building Attributed Relational Graph...")
  graphd = context.temporary( 'Directory' )
  graph = os.path.join( graphd.fullPath(), 'foldgraph' )
  context.system( "VipFoldArg", "-i", self.skeleton, "-v",
                  self.roots, "-o", graph, "-w", "g" )

  attp = [ 'AimsFoldArgAtt', '-i', self.skeleton.fullPath(), '-g',
           graph + '.arg', '-o', self.graph.fullPath(),
           '-m', self.Talairach_transform, '--graphversion',
           self.graph_version ]
  if not self.compute_fold_meshes:
    attp.append( '-n' )
  if self.commissure_coordinates:
    attp += [ '--apc', self.commissure_coordinates ]
  if not self.allow_multithreading:
    attp += [ '--threads', '1' ]
  context.system( *attp )
  trManager = registration.getTransformationManager()
  trManager.copyReferential( self.mri_corrected, self.skeleton )
  trManager.copyReferential( self.mri_corrected, self.roots )
  trManager.copyReferential( self.mri_corrected, self.graph )

  self.executionNode().CorticalFoldsGraphThickness.run( context )

