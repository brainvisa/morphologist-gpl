# -*- coding: utf-8 -*-
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
import sys

if sys.version_info[0] >= 3:
    def next(iterator):
        return iterator.__next__()
else:
    def next(iterator):
        return iterator.next()

name = 'Sulci Recognition with SPAM'
userLevel = 0


signature = Signature(
  'data_graph', ReadDiskItem( 'Cortical folds graph', 'Graph and data' ),
  'output_graph',
    WriteDiskItem( 'Labelled Cortical folds graph', 'Graph and data',
                   requiredAttributes = { 'labelled' : 'Yes',
                                          'automatically_labelled' \
                                          : 'Yes' } ),
  'fix_random_seed', Boolean(),
)

def initialization( self ):
  eNode = SerialExecutionNode( self.name, parameterized = self )
  eNode.addChild( 'global_recognition',
                   ProcessExecutionNode( 'spam_recognitionglobal',
                   selected = 1, optional=1 ) )
  # detect if SPAM models are here. If not, ANN is the default method
  # otherwise use SPAMs by default
  spammodels = ReadDiskItem( 'Sulci Segments Model', 'Text Data Table' \
    )._findValues( selection = { 'sulci_segments_model_type' : \
      'locally_from_global_registred_spam' },
      requiredAttributes = None, write = False )
  try:
    next(spammodels)
    uselocalspam = 1
  except StopIteration:
    uselocalspam = 0
  eNode1 = SelectionExecutionNode( 'Local or Markovian', selected=uselocalspam,
    optional=1 )
  eNode1.addChild( 'local_recognition',
                   ProcessExecutionNode( 'spam_recognitionlocal',
                   selected = 1 ) )
  eNode1.addChild( 'markovian_recognition',
                   ProcessExecutionNode( 'spam_recognitionmarkov',
                   selected = 0 ) )
  eNode1.selection_outputs = [ 'output_graph', 'output_graph' ]
  eNode1.switch_output = 'output_graph'
  eNode.addChild( 'local_or_markovian', eNode1 )

  self.setExecutionNode( eNode )

  self.addDoubleLink( 'data_graph', 'global_recognition.data_graph' )
  eNode.global_recognition.removeLink( 'output_graph', 'data_graph' )
  self.linkParameters( 'output_graph', 'data_graph' )
  # this link makes soma-pipeline output ambiguous
  self.addDoubleLink( 'output_graph', 'global_recognition.output_graph' )

  self.addDoubleLink( 'global_recognition.output_graph',
    'local_or_markovian.local_recognition.data_graph' )
  self.addDoubleLink( 'global_recognition.labels_translation_map',
    'local_or_markovian.local_recognition.labels_translation_map' )
  eNode1.local_recognition.removeLink( 'labels_priors', 'data_graph' )
  self.addDoubleLink( 'global_recognition.labels_priors',
    'local_or_markovian.local_recognition.labels_priors' )
  self.addDoubleLink( 'global_recognition.initial_transformation',
    'local_or_markovian.local_recognition.initial_transformation' )
  eNode1.local_recognition.removeLink( 'global_transformation', 'data_graph' )
  self.addDoubleLink( 'global_recognition.output_transformation',
    'local_or_markovian.local_recognition.global_transformation' )

  self.addDoubleLink( 'global_recognition.output_graph',
    'local_or_markovian.markovian_recognition.data_graph' )
  self.addDoubleLink( 'global_recognition.labels_translation_map',
    'local_or_markovian.markovian_recognition.labels_translation_map' )
  eNode1.markovian_recognition.removeLink( 'labels_priors', 'data_graph' )
  self.addDoubleLink( 'global_recognition.labels_priors',
    'local_or_markovian.markovian_recognition.labels_priors' )
  self.addDoubleLink( 'global_recognition.initial_transformation',
    'local_or_markovian.markovian_recognition.initial_transformation' )
  eNode1.markovian_recognition.removeLink( 'global_transformation',
    'data_graph' )
  self.addDoubleLink( 'global_recognition.output_transformation',
    'local_or_markovian.markovian_recognition.global_transformation' )

  self.addDoubleLink(
      'fix_random_seed',
      'local_or_markovian.markovian_recognition.fix_random_seed')
  self.signature['fix_random_seed'].userLevel = 3
  self.fix_random_seed = False

