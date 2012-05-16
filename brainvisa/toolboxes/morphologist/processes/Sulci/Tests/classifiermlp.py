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
import shfjGlobals

name = 'Classifier MLP'
userLevel = 2


signature = Signature(
  'input_data', ReadDiskItem( '2D image', shfjGlobals.aimsVolumeFormats ),
  'classifier', WriteDiskItem( 'Classifier', [ 'MLP classifier' ] ), 
  'output_image', WriteDiskItem( 'Elevation map',
                                 shfjGlobals.aimsVolumeFormats ),
  )

def initialization( self ):
  self.input_data = '/tmp/gauss9.ima'
  self.classifier = '/tmp/gogo.net'
  self.output_image = '/tmp/plop.ima'

  eNode = SerialExecutionNode( self.name, parameterized=self )
  eNode.addChild( 'createClassifier', 
                  ProcessExecutionNode( 'createmlp', optional = 1,
                                        selected = 1 ) )
  eNode.addChild( 'trainClassifier',
                  ProcessExecutionNode( 'trainmlp', optional = 1,
                                        selected = 1 ) )
  eNode.addChild( 'testClassifier',
                  ProcessExecutionNode( 'testclassifier3', optional = 1,
                                        selected = 1 ) )
  eNode.addChild( 'view',
                  ProcessExecutionNode( 'AnatomistShowElevationMap',
                                        optional = 1, selected = 1 ) )

  eNode.addLink( 'input_data', 'trainClassifier.input_data' )
  eNode.addLink( 'trainClassifier.input_data', 'input_data' )
  eNode.addLink( 'input_data', 'testClassifier.input_data' )
  eNode.addLink( 'testClassifier.input_data', 'input_data' )
  eNode.addLink( 'classifier', 'createClassifier.classifier' )
  eNode.addLink( 'createClassifier.classifier', 'classifier' )
  eNode.addLink( 'classifier', 'trainClassifier.classifier' )
  eNode.addLink( 'trainClassifier.classifier', 'classifier' )
  eNode.addLink( 'testClassifier.classifier',
                 'trainClassifier.output_classifier' )
  eNode.addLink( 'trainClassifier.output_classifier',
                 'testClassifier.classifier' )
  eNode.addLink( 'output_image', 'testClassifier.output_image' )
  eNode.addLink( 'testClassifier.output_image', 'output_image' )
  eNode.addLink( 'output_image', 'view.read' )
  eNode.addLink( 'view.read', 'output_image' )

  self.setExecutionNode( eNode )


def execution( self, context ):
  enode = self.executionNode()
  if enode.createClassifier._selected:
    enode.createClassifier.execution( context )
  if enode.trainClassifier._selected:
    enode.trainClassifier.execution( context )
  if enode.testClassifier._selected:
    scales = enode.testClassifier.execution( context )
    context.write( 'test result: ', scales )
  if enode.view._selected:
    scales = self.output_image.get( 'volume_dimension' )[ 0:2 ]
    vs = self.output_image.get( 'voxel_size' )[ 0:2 ]
    scales[0] *= vs[0]
    scales[1] *= vs[1]
    scale = 0.5 * max( scales )
    enode.view.scale = scale
    return enode.view.execution( context )

