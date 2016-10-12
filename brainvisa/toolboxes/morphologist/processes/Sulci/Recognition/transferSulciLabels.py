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
from brainvisa import registration

name = 'Transfer Sulci Labels'
userLevel = 0


signature = Signature(
    'labelled_graph', ReadDiskItem( 'Labelled Cortical Folds Graph', 'Graph and data' ),
    'unlabelled_graph', ReadDiskItem( 'Cortical Folds Graph', 'Graph and data' ),
    'output_graph', WriteDiskItem( 'Labelled Cortical folds graph', 'Graph and Data',
        requiredAttributes = { 'labelled' : 'Yes' } ),
    'label_attribute', Choice( 'name', 'label' ),
    'output_labels_table', WriteDiskItem( 'Text File', 'Text File' ),
    'force_same_space', Boolean(),
)



def initialization( self ):
  def linkLabelAttribute( self, process ):
    la = None
    if self.labelled_graph:
      la = self.labelled_graph.get( 'manually_labelled', None )
      if la == 'Yes':
        la = 'name'
      else:
        la = self.labelled_graph.get( 'automatically_labelled', None )
        if la == 'Yes':
          la = 'label'
        else:
          la = None
    if not la and self.unlabelled_graph:
      la = self.unlabelled_graph.get( 'manually_labelled', None )
      if la == 'Yes':
        la = 'name'
      else:
        la = self.unlabelled_graph.get( 'automatically_labelled', None )
        if la == 'Yes':
          la = 'label'
        else:
          la = None
    if la is None:
      la = 'label'
    return la

  def linkOutputGraph( self, process ):
    manual = 'No'
    required = { 'labelled' : 'Yes' }
    if self.labelled_graph:
      manual = self.labelled_graph.get( 'manually_labelled', None )
      if manual is not None:
        required[ 'manually_labelled' ] = manual
      auto = self.labelled_graph.get( 'automatically_labelled', None )
      if auto is not None:
        required[ 'automatically_labelled' ] = auto
      session = self.labelled_graph.get( 'sulci_recognition_session', None )
      if session is not None:
        required[ 'sulci_recognition_session' ] = session
    return signature[ 'output_graph' ].findValue( self.unlabelled_graph,
      requiredAttributes=required )

  self.setOptional( 'output_labels_table' )
  self.linkParameters( 'output_graph', [ 'unlabelled_graph',
    'labelled_graph' ], linkOutputGraph )
  self.linkParameters( 'label_attribute', 'labelled_graph',
    linkLabelAttribute )
  self.force_same_space = False

def execution( self, context ):
  cmd = [ 'AimsGraphTransferLabels', '-i', self.unlabelled_graph, '-j',
    self.labelled_graph, '-o', self.output_graph, '-l', self.label_attribute ]
  if self.output_labels_table:
    cmd += [ '-m', self.output_labels_table ]
  if self.force_same_space:
    cmd.append( '-s' )
  context.system( *cmd )
  trManager = registration.getTransformationManager()
  trManager.copyReferential( self.unlabelled_graph, self.output_graph )
