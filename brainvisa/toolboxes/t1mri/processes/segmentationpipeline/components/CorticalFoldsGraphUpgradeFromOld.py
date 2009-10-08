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
import shfjGlobals
import registration

name = 'Compute Cortical Fold Graph Upgrade From Old'
userLevel = 2

# Argument declaration
signature = Signature(
  'old_graph', ReadDiskItem( 'Cortical folds graph', 'Graph' ),
  'skeleton', ReadDiskItem( 'Cortex Skeleton', shfjGlobals.aimsVolumeFormats ),
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
  def linkGraphVersion( self, proc ):
    p = WriteDiskItem( 'Cortical folds graph', 'Graph' )
    return p.findValue( self.old_graph,
                        requiredAttributes = {
                          'graph_version' : self.graph_version } )

  self.linkParameters( 'skeleton', 'old_graph' )
  self.linkParameters( 'graph', ( 'old_graph', 'graph_version' ),
    linkGraphVersion )
  self.compute_fold_meshes = True
  self.linkParameters( 'commissure_coordinates', 'old_graph' )
  self.linkParameters( 'Talairach_transform', 'old_graph' )
  self.setOptional( 'commissure_coordinates' )

  eNode = SerialExecutionNode( self.name, parameterized = self )
  eNode.addChild( 'CorticalFoldsGraphThickness',
                   ProcessExecutionNode( 'CorticalFoldsGraphThickness',
                   optional = 1 ) )
  eNode.CorticalFoldsGraphThickness.clearLinksTo( 'output_graph' )
  eNode.addLink( 'CorticalFoldsGraphThickness.graph', 'graph' )
  eNode.addLink( 'graph', 'CorticalFoldsGraphThickness.graph' )
  eNode.addLink( 'CorticalFoldsGraphThickness.output_graph', 'graph' )
  eNode.addLink( 'graph', 'CorticalFoldsGraphThickness.output_graph' )
  self.setExecutionNode( eNode )

def execution( self, context ):
  attp = [ 'AimsFoldArgAtt', '-i', self.skeleton.fullPath(), '-g',
           self.old_graph.fullPath(), '-o', self.graph.fullPath(),
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
  trManager.copyReferential( self.old_graph, self.graph )

  self.executionNode().CorticalFoldsGraphThickness.run( context )
