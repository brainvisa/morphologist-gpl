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
import types

name = 'SPM Normalization Pipeline'
userLevel=0

def validation():
  if not distutils.spawn.find_executable( 'matlab' ):
    raise ValidationError( 'matlab is not found' )
  try:
    from soma import aims
  except:
    raise ValidationError( 'aims module not here' )
  p = getProcess( 'Normalization' )
  if not p:
    raise ValidationError( 'SPM Normalization process is not available - either the fMRI toolbox is not installed, or Matlab / SPM is not installed and in the PATH' )
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
  'template', ReadDiskItem( 'anatomical Template',
    ['NIFTI-1 image', 'gz compressed NIFTI-1 image', 'MINC image'] ),
  #'set_transformation_in_source_volume', Boolean(),
  'allow_flip_initial_MRI', Boolean(), 
)


class changeAllowFlip:
  def __init__( self, proc ):
    self.proc = proc
  def __call__( self, node ):
    if node.isSelected():
      if not self.proc.allow_flip_initial_MRI:
        self.proc.allow_flip_initial_MRI = True
    else:
      if self.proc.allow_flip_initial_MRI:
        self.proc.allow_flip_initial_MRI = False

def allowFlip( self, allow ):
  eNode = self.executionNode()
  s = eNode.ReorientAnatomy.isSelected()
  if s != self.allow_flip_initial_MRI:
    eNode.ReorientAnatomy.setSelected( self.allow_flip_initial_MRI )

def initialization( self ):
  def linkToAnat( t1mri ):
    if t1mri is None:
      return None
    return [ t1mri ]
  def linkToT1( anat ):
    if not anat:
      return None
    return anat[0]
  def linkToTrans( read ):
    if read is None:
      return None
    return [ read ]
  def linkToRead( trans ):
    if not trans:
      return None
    return trans[0]
  eNode = SerialExecutionNode( self.name, parameterized=self )

  eNode.addChild( 'NormlalizeSPM',
                  ProcessExecutionNode( 'Normalization' ) )
  eNode.addChild( 'ConvertSPMnormalizationToAIMS',
                  ProcessExecutionNode( 'SPMsn3dToAims' ) )
  eNode.addChild( 'ReorientAnatomy',
                  ProcessExecutionNode( 'reorientAnatomy', optional=True,
                  selected=False ) )

  # fix transformation_matrix type
  eNode.ConvertSPMnormalizationToAIMS.signature[ 'write' ] = \
    WriteDiskItem( 'Transform Raw T1 MRI to Talairach-MNI template-SPM',
      'Transformation matrix' )
  eNode.addLink( 'NormlalizeSPM.anatomy_data', 't1mri', linkToAnat )
  eNode.addLink( 't1mri', 'NormlalizeSPM.anatomy_data', linkToT1 )
  eNode.addLink( 'NormlalizeSPM.anatomical_template', 'template' )
  eNode.addLink( 'template', 'NormlalizeSPM.anatomical_template' )

  eNode.addLink( 'ConvertSPMnormalizationToAIMS.source_volume', 't1mri' )
  eNode.addLink( 't1mri', 'ConvertSPMnormalizationToAIMS.source_volume' )

  eNode.ConvertSPMnormalizationToAIMS.removeLink( 'normalized_volume',
    'read' )
  eNode.ConvertSPMnormalizationToAIMS.removeLink( 'source_volume', 'read' )

  eNode.addLink( 'transformation', 'ConvertSPMnormalizationToAIMS.write' )
  eNode.addLink( 'ConvertSPMnormalizationToAIMS.write', 'transformation' )

  eNode.addLink( 'NormlalizeSPM.transformations_informations',
    'ConvertSPMnormalizationToAIMS.read', linkToTrans )
  eNode.addLink( 'ConvertSPMnormalizationToAIMS.read',
    'NormlalizeSPM.transformations_informations', linkToRead )

  # force conversion to take exactly the same formats as the normalization
  # as input, because it uses the storage_to_memory matrix, which is
  # format-dependent
  eNode.ConvertSPMnormalizationToAIMS.signature[ 'source_volume' ].formats \
    = eNode.NormlalizeSPM.signature[ 'anatomy_data' ].contentType.formats
  # this seems not to work automatically
  self.template = self.signature[ 'template' ].findValue( \
    { 'databasename' : 'spm', 'skull_stripped' : 'no' } )

  eNode.ReorientAnatomy.removeLink( 'transformation', 't1mri' )
  eNode.addLink( 't1mri', 'ReorientAnatomy.t1mri' )
  eNode.addLink( 'ReorientAnatomy.t1mri', 't1mri' )
  eNode.addLink( 'transformation', 'ReorientAnatomy.transformation' )
  eNode.addLink( 'ReorientAnatomy.transformation', 'transformation' )
  eNode.addLink( 'allow_flip_initial_MRI',
    'ReorientAnatomy.allow_flip_initial_MRI' )
  eNode.addLink( 'ReorientAnatomy.allow_flip_initial_MRI',
    'allow_flip_initial_MRI' )

  self.setExecutionNode( eNode )

  self.allow_flip_initial_MRI = False
  self.addLink( None, 'allow_flip_initial_MRI',
    self.allowFlip )
  x = changeAllowFlip( self )
  eNode.ReorientAnatomy._selectionChange.add( x )

