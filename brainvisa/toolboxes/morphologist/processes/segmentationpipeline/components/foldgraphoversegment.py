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

import shfjGlobals
from brainvisa.processes import *
from soma.path import find_in_path
import registration

name = 'Folds graph over-segmentation'
userLevel = 2

signature = Signature(
  'input_graph', ReadDiskItem( 'Cortical Folds Graph', 'Graph' ),
  'graph_version', OpenChoice( '3.2', ),
  'output_graph', WriteDiskItem( 'Cortical Folds Graph', 'Graph' ),
  'skeleton', ReadDiskItem( 'Cortex Skeleton', shfjGlobals.aimsVolumeFormats ),
  'pieces_length', Float(),
  'minimum_size', Integer(),
)

def initialization( self ):
  def linkGraphVersion( self, proc ):
    p = WriteDiskItem( 'Cortical folds graph', 'Graph' )
    x = p.findValue( self.input_graph,
                        requiredAttributes = {
                          'graph_version' : self.graph_version } )
    return x

  self.pieces_length = 20.
  self.minimum_size = 50
  eNode = SerialExecutionNode( self.name, parameterized = self )
  eNode.addChild( 'CorticalFoldsGraphUpgradeFromOld',
                   ProcessExecutionNode( 'CorticalFoldsGraphUpgradeFromOld' ) )

  eNode.CorticalFoldsGraphUpgradeFromOld.signature[ 'old_graph' ] \
    = ReadDiskItem( 'Cortical Folds Graph', 'Graph' )
  eNode.CorticalFoldsGraphUpgradeFromOld.FoldGraphUpgradeStructure.removeLink( 'graph',
    ( 'old_graph', 'graph_version' ) )
  eNode.CorticalFoldsGraphUpgradeFromOld.graph_version = '3.2',
  #eNode.CorticalFoldsGraphUpgradeFromOld.signature[ 'graph_version' ] \
    #= OpenChoice( '3.2', ),

  self.linkParameters( 'output_graph', ( 'input_graph', 'graph_version' ),
    linkGraphVersion )

  eNode.addLink( 'CorticalFoldsGraphUpgradeFromOld.old_graph', 'output_graph' )
  eNode.addLink( 'output_graph', 'CorticalFoldsGraphUpgradeFromOld.old_graph' )
  eNode.addLink( 'CorticalFoldsGraphUpgradeFromOld.graph', 'output_graph' )
  eNode.addLink( 'output_graph', 'CorticalFoldsGraphUpgradeFromOld.graph' )
  eNode.addLink( 'CorticalFoldsGraphUpgradeFromOld.graph_version',
    'graph_version' )
  eNode.addLink( 'graph_version',
    'CorticalFoldsGraphUpgradeFromOld.graph_version' )
  eNode.addLink( 'CorticalFoldsGraphUpgradeFromOld.skeleton', 'skeleton' )
  eNode.addLink( 'skeleton', 'CorticalFoldsGraphUpgradeFromOld.skeleton' )
  self.setExecutionNode( eNode )

def execution( self, context ):
  context.system( 'python',
    find_in_path( 'AimsFoldsGraphOverSegmentation.py' ), '-i',
    self.input_graph, '-o', self.output_graph, '-l', self.pieces_length,
    '-m', self.minimum_size )
  tm = registration.getTransformationManager()
  tm.copyReferential( self.input_graph, self.output_graph )
  self.executionNode().CorticalFoldsGraphUpgradeFromOld.run( context )
