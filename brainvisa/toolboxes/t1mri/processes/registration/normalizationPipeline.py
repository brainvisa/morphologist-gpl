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

from neuroProcesses import *
import shfjGlobals, math
import registration
from brainvisa import anatomist
from brainvisa import quaternion

name = 'Normalization pipeline'
userLevel = 0

def validationDelayed():
  '''validation cannot be done at startup since some sub-processes may not be
loaded yet. But this validationDelayed method can be used later.
  '''
  try:
    fsl = getProcess( 'FSLnormalizationPipeline' )
  except:
    fsl = None
  try:
    spm = getProcess( 'SPMnormalizationPipeline' )
  except:
    spm = None
  if not fsl and not spm:
    raise ValidationError( 'No normalization process could be found working' )

signature = Signature(
  't1mri', ReadDiskItem( "Raw T1 MRI", shfjGlobals.aimsVolumeFormats ),
  'transformation',
    WriteDiskItem( 'Transform Raw T1 MRI to Talairach-MNI template-SPM',
      'Transformation matrix' ),
  )

def initialization( self ):
  try:
    fsl = getProcess( 'FSLnormalizationPipeline' )
  except:
    fsl = None
  try:
    spm = getProcess( 'SPMnormalizationPipeline' )
  except:
    spm = None

  eNode = SelectionExecutionNode( self.name, parameterized=self )

  if fsl:
    eNode.addChild( 'NormalizeFSL',
      ProcessExecutionNode( 'FSLnormalizationPipeline',
        selected=(spm is None) ) )

    eNode.addLink( 'NormalizeFSL.t1mri', 't1mri' )
    eNode.addLink( 't1mri', 'NormalizeFSL.t1mri' )
    eNode.addLink( 'NormalizeFSL.transformation', 'transformation' )
    eNode.addLink( 'transformation', 'NormalizeFSL.transformation' )

  if spm:
    eNode.addChild( 'NormalizeSPM',
      ProcessExecutionNode( 'SPMnormalizationPipeline', selected=1 ) )

    eNode.addLink( 'NormalizeSPM.t1mri', 't1mri' )
    eNode.addLink( 't1mri', 'NormalizeSPM.t1mri' )
    if not fsl: # TODO: fix links in sub-processes
      eNode.addLink( 'NormalizeSPM.transformation', 'transformation' )
      eNode.addLink( 'transformation', 'NormalizeSPM.transformation' )

  self.setExecutionNode( eNode )


