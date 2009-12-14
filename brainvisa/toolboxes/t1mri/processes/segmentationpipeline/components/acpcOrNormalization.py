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
import shfjGlobals, math
import registration
from brainvisa import anatomist
from brainvisa import quaternion

name = 'AC/PC Or Normalization'
userLevel = 0

signature = Signature(
  'T1mri', ReadDiskItem( "Raw T1 MRI", shfjGlobals.aimsVolumeFormats ),
  'Commissure_coordinates', WriteDiskItem( 'Commissure coordinates','Commissure coordinates'),
  )

def validation():
  ps = getProcess( 'preparesubject' )
  np = getProcess( 'FSLnormalizationPipeline' )
  if not ps and not np:
    raise ValidationError( 'Neither PrepareSubject nor FSLnormalizationPipeline processes are available' )

def initialization( self ):
  ps = getProcess( 'preparesubject' )
  np = getProcess( 'FSLnormalizationPipeline' )

  eNode = SelectionExecutionNode( self.name, parameterized=self )

  if ps:
    if np:
      sel = 0
    else:
      sel = 1
    eNode.addChild( 'StandardACPC',
      ProcessExecutionNode( 'preparesubject', selected=sel ) )

    eNode.addLink( 'StandardACPC.T1mri', 'T1mri' )
    eNode.addLink( 'T1mri', 'StandardACPC.T1mri' )
    eNode.addLink( 'StandardACPC.Commissure_coordinates',
      'Commissure_coordinates' )
    eNode.addLink( 'Commissure_coordinates',
      'StandardACPC.Commissure_coordinates' )

  if np:
    eNode1 = SerialExecutionNode( 'Normalization', selected=1 )
    eNode1.addChild( 'NormalizeFSL',
      ProcessExecutionNode( 'FSLnormalizationPipeline' ) )
    eNode1.addChild( 'TalairachFromNormalization',
      ProcessExecutionNode( 'TalairachTransformationFromNormalization' ) )
    eNode.addChild( 'Normalization', eNode1 )

    eNode.addLink( 'Normalization.NormalizeFSL.t1mri', 'T1mri' )
    eNode.addLink( 'T1mri', 'Normalization.NormalizeFSL.t1mri' )

    if ps:
      eNode1.TalairachFromNormalization.removeLink( 'Commissure_coordinates',
        'Talairach_transform' )

    eNode.addLink( 'Normalization.TalairachFromNormalization.t1mri', 'T1mri' )
    eNode.addLink( 'T1mri', 'Normalization.TalairachFromNormalization.t1mri' )
    eNode.addLink( \
      'Normalization.TalairachFromNormalization.normalization_transformation',
      'Normalization.NormalizeFSL.transformation' )
    eNode.addLink( 'Normalization.NormalizeFSL.transformation',
      'Normalization.TalairachFromNormalization.normalization_transformation' )
    eNode.addLink( \
      'Normalization.TalairachFromNormalization.Commissure_coordinates',
      'Commissure_coordinates' )
    eNode.addLink( 'Commissure_coordinates',
      'Normalization.TalairachFromNormalization.Commissure_coordinates' )

  self.setExecutionNode( eNode )


