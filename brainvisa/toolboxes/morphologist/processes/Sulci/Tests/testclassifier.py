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

name = 'Classifier tests'
userLevel = 2


signature = Signature(
  'input_data', ReadDiskItem( '2D image', shfjGlobals.aimsVolumeFormats ),
  'classifier', WriteDiskItem( 'Classifier',
                               [ 'SVM classifier', 'MLP classifier' ] ), 
  'output_image', WriteDiskItem( 'Elevation map',
                                 shfjGlobals.aimsVolumeFormats ),
  )

def initialization( self ):
  self.input_data = '/tmp/gauss9.ima'
  self.classifier = '/tmp/gogo.svm'
  self.output_image = '/tmp/plop.ima'

  eNode = SelectionExecutionNode( self.name, parameterized=self )
  eNode.addChild( 'SVM', 
                  ProcessExecutionNode( 'classifiersvm', selected = 1 ) )
  eNode.addChild( 'MLP', 
                  ProcessExecutionNode( 'classifiermlp', selected = 0 ) )

  eNode.addLink( 'input_data', 'SVM.input_data' )
  eNode.addLink( 'SVM.input_data', 'input_data' )
  eNode.addLink( 'input_data', 'MLP.input_data' )
  eNode.addLink( 'MLP.input_data', 'input_data' )
  eNode.addLink( 'classifier', 'SVM.classifier' )
  eNode.addLink( 'SVM.classifier', 'classifier' )
  eNode.addLink( 'classifier', 'MLP.classifier' )
  eNode.addLink( 'MLP.classifier', 'classifier' )
  eNode.addLink( 'output_image', 'SVM.output_image' )
  eNode.addLink( 'SVM.output_image', 'output_image' )
  eNode.addLink( 'output_image', 'MLP.output_image' )
  eNode.addLink( 'MLP.output_image', 'output_image' )

  self.setExecutionNode( eNode )

