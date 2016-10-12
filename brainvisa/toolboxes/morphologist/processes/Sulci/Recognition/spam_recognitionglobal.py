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

name = 'SPAM recognition, global registration'
userLevel = 1


signature = Signature(
  'data_graph', ReadDiskItem( 'Cortical folds graph', 'Graph and data' ),
  'output_graph',
    WriteDiskItem( 'Labelled Cortical folds graph', 'Graph and data',
                   requiredAttributes = { 'labelled' : 'Yes',
                                          'automatically_labelled' \
                                          : 'Yes' } ),
  'model_type', Choice( 'Talairach', 'Global registration' ),
  'model', ReadDiskItem( 'Sulci Segments Model', 'Text Data Table' ),
  'posterior_probabilities',
    WriteDiskItem( 'Sulci Labels Segmentwise Posterior Probabilities',
        'CSV file' ),
  'labels_translation_map',
    ReadDiskItem( 'Label Translation',
                  [ 'Label Translation', 'DEF Label translation' ] ),
  'labels_priors', ReadDiskItem( 'Sulci Labels Priors', 'Text Data Table' ),
  'output_transformation',
      WriteDiskItem( 'Sulci Talairach to Global SPAM transformation',
          'Transformation matrix' ),
  'initial_transformation', ReadDiskItem( 'Transformation matrix',
    'Transformation matrix' ), # FIXME
  'output_t1_to_global_transformation',
      WriteDiskItem( 'Raw T1 to Global SPAM transformation',
          'Transformation matrix' ),
)

def initialization( self ):
  def linkModelType( proc, dummy ):
    di = ReadDiskItem( 'Sulci Segments Model', 'Text Data Table' )
    if proc.model_type == 'Talairach':
      di.requiredAttributes[ 'sulci_segments_model_type' ] = 'talairach_spam'
    elif proc.model_type == 'Global registration':
      di.requiredAttributes[ 'sulci_segments_model_type' ] \
        = 'global_registered_spam'
    x = di.findValue( proc.data_graph )
    return x
  def linkOutputTrans( proc, dummy ):
    if proc.model_type == 'Talairach':
      return None
    return proc.signature[ 'output_transformation' ].findValue( \
      proc.output_graph )
  def linkOutputT1Trans( proc, dummy ):
    if proc.model_type == 'Talairach':
      return None
    return proc.signature[ 'output_t1_to_global_transformation' ].findValue( \
      proc.output_graph )

  self.linkParameters( 'output_graph', 'data_graph' )
  self.linkParameters( 'posterior_probabilities', 'output_graph' )
  self.linkParameters( 'labels_priors', 'data_graph' )
  self.labels_translation_map = \
    self.signature[ 'labels_translation_map' ].findValue(
      { 'filename_variable' : 'sulci_model_2008' } )
  self.linkParameters( 'model', [ 'data_graph', 'model_type' ],
    linkModelType )
  self.linkParameters( 'output_transformation',
    [ 'output_graph', 'model_type' ], linkOutputTrans )
  self.linkParameters( 'output_t1_to_global_transformation',
    [ 'output_graph', 'model_type' ], linkOutputT1Trans )
  self.setOptional( 'output_transformation' )
  self.setOptional( 'initial_transformation' )
  self.setOptional( 'output_t1_to_global_transformation' )
  self.model_type = 'Global registration'

def execution( self, context ):
  tmpfile = context.temporary( 'Text file' )
  # find script filename (since it is not in the PATH)
  progname = os.path.join( os.path.dirname( os.path.dirname( \
    registration.__file__ ) ), 'scripts', 'sigraph', 'sulci_registration',
    'independent_tag_with_registration.py' )
  cmd = [ sys.executable, progname, '-i', self.data_graph, '-o',
    self.output_graph, '-t', self.labels_translation_map, '-d', self.model,
    '-c', self.posterior_probabilities, '-l', tmpfile,
    '-p', self.labels_priors, '--mode', 'global' ]
  if self.model_type == 'Talairach':
    cmd += [ '--maxiter', 0 ]
  else:
    if self.output_transformation is not None \
      and self.model_type == 'Global registration':
      cmd += [ '--motion', self.output_transformation ]
  if self.initial_transformation is not None:
    cmd += [ '--input-motion', self.initial_transformation,
      '--no-talairach' ]
  # now run it
  context.system( *cmd )
  trManager = registration.getTransformationManager()
  if self.output_transformation and self.model_type == 'Global registration':
    ref = trManager.createNewReferentialFor( self.output_graph,
      name='Global registred SPAM' )
    if self.output_t1_to_global_transformation is not None:
      if self.initial_transformation is not None:
        context.system( 'AimsComposeTransformation', '-i',
          self.initial_transformation, '-j', self.output_transformation, '-o',
          self.output_t1_to_global_transformation )
      else:
        tmp = context.temporary( 'Transformation Matrix' )
        context.system( 'AimsGraphExtractTransformation',
          '-i', self.data_graph, '-o', tmp )
        context.system( 'AimsComposeTransformation', '-i',
          self.output_transformation, '-j', tmp, '-o',
          self.output_t1_to_global_transformation )
      trManager.setNewTransformationInfo(
        self.output_t1_to_global_transformation,
        source_referential = self.output_graph,
        destination_referential \
          = registration.globallyRegistredSPAMReferentialId )
    # set back standard subject ref to output_graph, until we find a better
    # solution to handle refs/transfo ambiguities
    # however the new ref / trans have been created ans can be used if needed.
    trManager.copyReferential( self.data_graph, self.output_graph )
  else:
    trManager.copyReferential( self.data_graph, self.output_graph )

