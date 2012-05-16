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
name = 'Sulci Recognition with SPAM'
userLevel = 0
import registration


signature = Signature(
  'data_graph', ReadDiskItem( 'Cortical folds graph', 'Graph and data' ),
  'output_graph',
    WriteDiskItem( 'Labelled Cortical folds graph', 'Graph and data',
                   requiredAttributes = { 'labelled' : 'Yes',
                                          'automatically_labelled' \
                                          : 'Yes' } ),
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
    spammodels.next()
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
  eNode.addChild( 'local_or_markovian', eNode1 )

  self.setExecutionNode( eNode )

  self.addLink( 'data_graph', 'global_recognition.data_graph' )
  self.addLink( 'global_recognition.data_graph', 'data_graph' )
  eNode.global_recognition.removeLink( 'output_graph', 'data_graph' )
  self.linkParameters( 'output_graph', 'data_graph' )
  self.addLink( 'output_graph', 'global_recognition.output_graph' )
  self.addLink( 'global_recognition.output_graph', 'output_graph' )

  self.addLink( 'output_graph',
    'local_or_markovian.local_recognition.data_graph' )
  self.addLink( 'local_or_markovian.local_recognition.data_graph',
    'output_graph' )
  self.addLink( 'global_recognition.labels_translation_map',
    'local_or_markovian.local_recognition.labels_translation_map' )
  self.addLink( 'local_or_markovian.local_recognition.labels_translation_map',
    'global_recognition.labels_translation_map' )
  eNode1.local_recognition.removeLink( 'labels_priors', 'data_graph' )
  self.addLink( 'global_recognition.labels_priors',
    'local_or_markovian.local_recognition.labels_priors' )
  self.addLink( 'local_or_markovian.local_recognition.labels_priors',
    'global_recognition.labels_priors' )
  self.addLink( 'global_recognition.initial_transformation',
    'local_or_markovian.local_recognition.initial_transformation' )
  self.addLink( 'local_or_markovian.local_recognition.initial_transformation',
    'global_recognition.initial_transformation' )
  eNode1.local_recognition.removeLink( 'global_transformation', 'data_graph' )
  self.addLink( 'global_recognition.output_transformation',
    'local_or_markovian.local_recognition.global_transformation' )
  self.addLink( 'local_or_markovian.local_recognition.global_transformation',
    'global_recognition.output_transformation' )

  self.addLink( 'output_graph',
    'local_or_markovian.markovian_recognition.data_graph' )
  self.addLink( 'local_or_markovian.markovian_recognition.data_graph',
    'output_graph' )
  self.addLink( 'global_recognition.labels_translation_map',
    'local_or_markovian.markovian_recognition.labels_translation_map' )
  self.addLink( \
    'local_or_markovian.markovian_recognition.labels_translation_map',
    'global_recognition.labels_translation_map' )
  eNode1.markovian_recognition.removeLink( 'labels_priors', 'data_graph' )
  self.addLink( 'global_recognition.labels_priors',
    'local_or_markovian.markovian_recognition.labels_priors' )
  self.addLink( 'local_or_markovian.markovian_recognition.labels_priors',
    'global_recognition.labels_priors' )
  self.addLink( 'global_recognition.initial_transformation',
    'local_or_markovian.markovian_recognition.initial_transformation' )
  self.addLink( \
    'local_or_markovian.markovian_recognition.initial_transformation',
    'global_recognition.initial_transformation' )
  eNode1.markovian_recognition.removeLink( 'global_transformation',
    'data_graph' )
  self.addLink( 'global_recognition.output_transformation',
    'local_or_markovian.markovian_recognition.global_transformation' )
  self.addLink( \
    'local_or_markovian.markovian_recognition.global_transformation',
    'global_recognition.output_transformation' )

