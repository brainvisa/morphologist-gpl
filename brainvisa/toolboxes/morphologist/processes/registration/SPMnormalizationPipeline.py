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
import shfjGlobals
import registration
import types
import sys

name = 'SPM Normalization Pipeline'
userLevel=1

def validation():
  try:
    from soma import aims
  except:
    raise ValidationError( 'aims module not here' )
  configuration = Application().configuration
  if( ( not configuration.SPM.spm8_standalone_command \
      or not (configuration.SPM.spm8_standalone_mcr_path or (sys.platform == "win32")) ) ) \
    and not distutils.spawn.find_executable( \
      configuration.matlab.executable ):
    raise ValidationError( 'SPM or matlab is not found' )
  # the previous test seems not to be good enough...
  try:
    di = ReadDiskItem( 'anatomical Template', ['NIFTI-1 image', 'gz compressed NIFTI-1 image', 'MINC image'] )
  except ValueError:
    raise ValidationError( 'fMRI toolbox not present' )

signature = Signature(
  't1mri', ReadDiskItem( 'Raw T1 MRI', ['NIFTI-1 image', 'gz compressed NIFTI-1 image', 'SPM image'] ),
  'transformation',
    WriteDiskItem( 'Transform Raw T1 MRI to Talairach-MNI template-SPM',
      'Transformation matrix' ),
  'spm_transformation', WriteDiskItem("SPM2 normalization matrix", 'Matlab file'),
  'normalized_t1mri', WriteDiskItem("Raw T1 MRI", ['NIFTI-1 image', 'SPM image' ], 
                                    {"normalization" : "SPM"}),
  'template', ReadDiskItem( 'anatomical Template',
    ['NIFTI-1 image', 'gz compressed NIFTI-1 image', 'MINC image'] ),
  #'set_transformation_in_source_volume', Boolean(),
  'allow_flip_initial_MRI', Boolean(),
  'allow_retry_initialization', Boolean(),
  'reoriented_t1mri', WriteDiskItem("Raw T1 MRI",
                                    'aims writable volume formats'),
)


class changeAllowFlip:
  def __init__( self, proc ):
    self.proc = weakref.proxy( proc )
  def __call__( self, node ):
    #eNode = self.proc.executionNode()
    if node.isSelected():
      if not self.proc.allow_flip_initial_MRI:
        self.proc.allow_flip_initial_MRI = True
        #eNode.removeLink('transformation',
                         #'ConvertSPMnormalizationToAIMS.write')
        #eNode.removeLink('ConvertSPMnormalizationToAIMS.write',
                         #'transformation')
        #eNode.addDoubleLink('transformation',
                            #'ReorientAnatomy.output_transformation')
        #eNode.addDoubleLink('reoriented_t1mri',
                            #'ReorientAnatomy.output_t1mri')
        #self.proc.transformation = eNode.ReorientAnatomy.output_transformation
    else:
      if self.proc.allow_flip_initial_MRI:
        self.proc.allow_flip_initial_MRI = False
        #eNode.removeLink('transformation',
                         #'ReorientAnatomy.output_transformation')
        #eNode.removeLink('ReorientAnatomy.output_transformation',
                         #'transformation')
        #eNode.addDoubleLink('transformation',
                            #'ConvertSPMnormalizationToAIMS.write')
        #eNode.removeLink('reoriented_t1mri',
                         #'ReorientAnatomy.output_t1mri')
        #eNode.removeLink('ReorientAnatomy.output_t1mri',
                         #'reoriented_t1mri')
        #self.proc.transformation = eNode.ConvertSPMnormalizationToAIMS.write

def allowFlip( self, *args, **kwargs ):
  eNode = self.executionNode()
  s = eNode.ReorientAnatomy.isSelected()
  if s != self.allow_flip_initial_MRI:
    eNode.ReorientAnatomy.setSelected( self.allow_flip_initial_MRI )

def initialization( self ):
  # TODO:
  #     - link NormalizeSPM.normalized_anatomy_data to
  #       ConvertSPMnormalizationToAIMS.normalized_volume
  #     - set an output to ReorientAnatomy, which is by default the same as
  #       the t1mri input (at least if allow_flip_initial_MRI is set)

  self.linkParameters('transformation', 't1mri')
  self.linkParameters('reoriented_t1mri', 't1mri')

  eNode = SerialExecutionNode( self.name, parameterized=self )

  eNode.addChild( 'NormalizeSPM',
                  ProcessExecutionNode( 'Normalization_SPM_reinit' ) )
  eNode.addChild( 'ConvertSPMnormalizationToAIMS',
                  ProcessExecutionNode( 'SPMsn3dToAims' ) )
  eNode.addChild( 'ReorientAnatomy',
                  ProcessExecutionNode( 'reorientAnatomy', optional=True,
                  selected=False ) )

  eNode.ConvertSPMnormalizationToAIMS.removeLink( 'normalized_volume',
    'read' )
  eNode.ConvertSPMnormalizationToAIMS.removeLink( 'source_volume', 'read' )
  #eNode.ConvertSPMnormalizationToAIMS.removeLink( 'write', 'source_volume' )
  eNode.ReorientAnatomy.removeLink( 'transformation', 't1mri' )
  eNode.ReorientAnatomy.removeLink( 'output_t1mri', 't1mri' )
  eNode.ReorientAnatomy.removeLink( 'output_transformation', 'output_t1mri' )

  eNode.addDoubleLink( 'NormalizeSPM.anatomy_data', 't1mri' )
  eNode.addDoubleLink( 'NormalizeSPM.allow_retry_initialization',
    'allow_retry_initialization' )
  eNode.addDoubleLink('NormalizeSPM.transformations_informations', 
                      'spm_transformation')
  eNode.addDoubleLink('NormalizeSPM.normalized_anatomy_data', 'normalized_t1mri')
  eNode.addDoubleLink( 'NormalizeSPM.anatomical_template', 'template' )

  # fix transformation_matrix type
  transinf = eNode.NormalizeSPM.signature[ 'transformations_informations' ]
  eNode.ConvertSPMnormalizationToAIMS.signature[ 'read' ] = \
    ReadDiskItem( transinf.type.name, transinf.formats )
  eNode.ConvertSPMnormalizationToAIMS.signature[ 'write' ] = \
    WriteDiskItem( 'Transform Raw T1 MRI to Talairach-MNI template-SPM',
      'Transformation matrix' )
  # force conversion to take exactly the same formats as the normalization
  # as input, because it uses the storage_to_memory matrix, which is
  # format-dependent
  eNode.ConvertSPMnormalizationToAIMS.signature[ 'source_volume' ].formats \
    = eNode.NormalizeSPM.signature[ 'anatomy_data' ].formats


  eNode.addDoubleLink( 'NormalizeSPM.transformations_informations',
    'ConvertSPMnormalizationToAIMS.read' )
  eNode.addDoubleLink('ConvertSPMnormalizationToAIMS.source_volume', 't1mri')
  eNode.addDoubleLink('ConvertSPMnormalizationToAIMS.write',
                      'ReorientAnatomy.transformation')

  # this seems not to work automatically
  self.template = self.signature[ 'template' ].findValue( \
    { 'databasename' : 'spm', 'skull_stripped' : 'no' } )

  eNode.addDoubleLink( 't1mri', 'ReorientAnatomy.t1mri' )
  #eNode.addDoubleLink('transformation', 'ConvertSPMnormalizationToAIMS.write')
  eNode.addDoubleLink('transformation',
                      'ReorientAnatomy.output_transformation')
  eNode.addDoubleLink( 'allow_flip_initial_MRI',
    'ReorientAnatomy.allow_flip_initial_MRI' )
  eNode.addDoubleLink( 'reoriented_t1mri', 'ReorientAnatomy.output_t1mri' )

  self.setExecutionNode( eNode )

  self.allow_flip_initial_MRI = True
  self.addLink( None, 'allow_flip_initial_MRI',
    ExecutionNode.MethodCallbackProxy( self.allowFlip ) )
  x = changeAllowFlip( self )
  eNode.ReorientAnatomy._selectionChange.add( x )
  self.allow_retry_initialization = True

