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

name = 'Baladin Normalization Pipeline'
userLevel=1

def validation():
	import distutils.spawn
	try:
		from soma import aims
	except:
		raise ValidationError( 'aims module not here' )
	if not distutils.spawn.find_executable('baladin'):
		raise ValidationError(_t_("'baladin' commandline " + \
					"could not be found in PATH"))
signature = Signature(
  't1mri', ReadDiskItem( 'Raw T1 MRI',
    ['NIFTI-1 image', 'gz compressed NIFTI-1 image'] ),
  'transformation',
    WriteDiskItem( 'Transform Raw T1 MRI to Talairach-MNI template-SPM',
      'Transformation matrix', requiredAttributes=
	{'destination_referential' : str(registration.talairachMNIReferentialId)} ),
  'template', ReadDiskItem( "anatomical Template",
    ['NIFTI-1 image', 'gz compressed NIFTI-1 image'] ),
  'set_transformation_in_source_volume', Boolean(),
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
  self.linkParameters( 'transformation', 't1mri' )

  eNode = SerialExecutionNode( self.name, parameterized=self )

  eNode.addChild( 'NormalizeBaladin',
                  ProcessExecutionNode( 'Normalization_Baladin' ) )
  eNode.addChild( 'ConvertBaladinNormalizationToAIMS',
                  ProcessExecutionNode( 'BaladinNormalizationToAims' ) )
  eNode.addChild( 'ReorientAnatomy',
                  ProcessExecutionNode( 'reorientAnatomy', optional=True,
                  selected=False ) )

  eNode.addLink( 'NormalizeBaladin.anatomy_data', 't1mri' )
  eNode.addLink( 't1mri', 'NormalizeBaladin.anatomy_data' )
  eNode.addLink( 'NormalizeBaladin.anatomical_template', 'template' )
  eNode.addLink( 'template', 'NormalizeBaladin.anatomical_template' )

  eNode.addLink( 'ConvertBaladinNormalizationToAIMS.source_volume', 't1mri' )
  eNode.addLink( 't1mri', 'ConvertBaladinNormalizationToAIMS.source_volume' )

  eNode.ConvertBaladinNormalizationToAIMS.removeLink( 'registered_volume',
    'read' )
  eNode.ConvertBaladinNormalizationToAIMS.removeLink( 'source_volume', 'read' )

  eNode.addLink( \
    'ConvertBaladinNormalizationToAIMS.set_transformation_in_source_volume',
    'set_transformation_in_source_volume' )
  eNode.addLink( 'set_transformation_in_source_volume',
    'ConvertBaladinNormalizationToAIMS.set_transformation_in_source_volume' )
  eNode.addLink( 'transformation', 'ConvertBaladinNormalizationToAIMS.write' )
  eNode.addLink( 'ConvertBaladinNormalizationToAIMS.write', 'transformation' )

  eNode.addLink( 'template',
    'ConvertBaladinNormalizationToAIMS.registered_volume' )
  eNode.addLink( 'ConvertBaladinNormalizationToAIMS.registered_volume',
    'template' )
  eNode.addLink( 'NormalizeBaladin.transformation_matrix',
    'ConvertBaladinNormalizationToAIMS.read' )
  eNode.addLink( 'ConvertBaladinNormalizationToAIMS.read',
    'NormalizeBaladin.transformation_matrix' )

  eNode.ReorientAnatomy.removeLink( 'transformation', 't1mri' )
  eNode.addLink( 't1mri', 'ReorientAnatomy.t1mri' )
  eNode.addLink( 'ReorientAnatomy.t1mri', 't1mri' )
  eNode.addLink( 'transformation', 'ReorientAnatomy.transformation' )
  eNode.addLink( 'ReorientAnatomy.transformation', 'transformation' )
  eNode.addLink( 'allow_flip_initial_MRI',
    'ReorientAnatomy.allow_flip_initial_MRI' )
  eNode.addLink( 'ReorientAnatomy.allow_flip_initial_MRI',
    'allow_flip_initial_MRI' )

  # this seems not to work automatically
  self.template = eNode.child('NormalizeBaladin').anatomical_template
  self.setExecutionNode( eNode )

  self.allow_flip_initial_MRI = False
  self.addLink( None, 'allow_flip_initial_MRI', self.allowFlip )
  x = changeAllowFlip( self )
  eNode.ReorientAnatomy._selectionChange.add( x )