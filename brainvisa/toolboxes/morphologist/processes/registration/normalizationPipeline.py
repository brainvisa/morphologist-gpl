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
import math
from brainvisa import registration
from brainvisa import anatomist
from brainvisa import quaternion
from brainvisa.configuration.neuroConfig import findInPath

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
  try:
    bal = getProcess( 'BaladinNormalizationPipeline' )
  except:
    bal = None
  mireg = findInPath('AimsMIRegister')
  if not fsl and not spm and not bal and not mireg:
    raise ValidationError( 'No normalization process could be found working' )
  return fsl, spm, bal

signature = Signature(
  't1mri', ReadDiskItem( "Raw T1 MRI", 'aims readable Volume Formats' ),
  'transformation',
    WriteDiskItem( 'Transform Raw T1 MRI to Talairach-MNI template-SPM',
      'Transformation matrix' ),
  'allow_flip_initial_MRI', Boolean(),
  'commissures_coordinates', ReadDiskItem( 'Commissure Coordinates', 
      'Commissure Coordinates' ),
  'reoriented_t1mri', WriteDiskItem("Raw T1 MRI",
                                    'aims writable volume formats'),
  'output_commissures_coordinates', WriteDiskItem('Commissure Coordinates',
      'Commissure Coordinates'),
  'init_translation_origin', Choice(('Center of the image', 0 ),
                                    ('Gravity center', 1)),
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
  try:
    bal = getProcess( 'BaladinNormalizationPipeline' )
  except:
    bal = None

  self.linkParameters( 'transformation', 't1mri' )
  self.allow_flip_initial_MRI = True
  self.setOptional('commissures_coordinates', 'output_commissures_coordinates')
  #self.linkParameters('commissures_coordinates', 't1mri')
  self.linkParameters('reoriented_t1mri', 't1mri')

  eNode = SelectionExecutionNode( self.name, parameterized=self )
  # for "future" pipeline switch
  eNode.selection_outputs = []

  if fsl:
    eNode.addChild( 'NormalizeFSL',
      ProcessExecutionNode( fsl,
        selected=(spm is None) ) )

    eNode.NormalizeFSL.removeLink( 'transformation', 't1mri' )
    eNode.NormalizeFSL.removeLink( 'reoriented_t1mri', 't1mri' )
    eNode.addDoubleLink( 'NormalizeFSL.t1mri', 't1mri' )
    eNode.addDoubleLink( 'NormalizeFSL.transformation', 'transformation' )
    eNode.addDoubleLink( 'NormalizeFSL.allow_flip_initial_MRI',
      'allow_flip_initial_MRI' )
    eNode.NormalizeFSL.ReorientAnatomy.removeLink( 'commissures_coordinates', 
      't1mri' )
    eNode.addDoubleLink( 
      'NormalizeFSL.ReorientAnatomy.commissures_coordinates', 
      'commissures_coordinates' )
    eNode.addDoubleLink(
      'NormalizeFSL.ReorientAnatomy.output_commissures_coordinates',
      'output_commissures_coordinates' )
    eNode.addDoubleLink('reoriented_t1mri', 'NormalizeFSL.reoriented_t1mri')
    eNode.addDoubleLink('init_translation_origin',
                        'NormalizeFSL.NormalizeFSL.init_translation_origin')

    eNode.selection_outputs.append(
      ['transformation', 'NormalizeFSL.normalized_anatomy_data',
       'reoriented_t1mri'] )

  if spm:
    eNode.addChild( 'NormalizeSPM',
      ProcessExecutionNode( spm, selected=1 ) )

    eNode.NormalizeSPM.removeLink( 'transformation', 't1mri' )
    eNode.NormalizeSPM.removeLink( 'reoriented_t1mri', 't1mri' )
    eNode.addDoubleLink( 'NormalizeSPM.t1mri', 't1mri' )
    eNode.addDoubleLink( 'NormalizeSPM.transformation', 'transformation' )
    eNode.addDoubleLink( 'NormalizeSPM.allow_flip_initial_MRI',
      'allow_flip_initial_MRI' )
    eNode.NormalizeSPM.ReorientAnatomy.removeLink( 'commissures_coordinates', 
      't1mri' )
    eNode.addDoubleLink( 
      'NormalizeSPM.ReorientAnatomy.commissures_coordinates', 
      'commissures_coordinates' )
    eNode.addDoubleLink(
      'NormalizeSPM.ReorientAnatomy.output_commissures_coordinates',
      'output_commissures_coordinates' )
    eNode.addDoubleLink('reoriented_t1mri', 'NormalizeSPM.reoriented_t1mri')
    eNode.addDoubleLink('init_translation_origin',
                        'NormalizeSPM.init_translation_origin')

    eNode.selection_outputs.append(
      ['transformation',
       'normalized_t1mri',
       'reoriented_t1mri'])

  if bal:
    eNode.addChild( 'NormalizeBaladin',
      ProcessExecutionNode( bal,
        selected=(bal is None) ) )

    eNode.NormalizeBaladin.removeLink( 'transformation', 't1mri' )
    eNode.NormalizeBaladin.removeLink( 'reoriented_t1mri', 't1mri' )
    eNode.addDoubleLink( 'NormalizeBaladin.t1mri', 't1mri' )
    eNode.addDoubleLink( 'NormalizeBaladin.transformation', 'transformation' )
    eNode.addDoubleLink( 'NormalizeBaladin.allow_flip_initial_MRI',
      'allow_flip_initial_MRI' )
    eNode.NormalizeBaladin.ReorientAnatomy.removeLink( 
      'commissures_coordinates', 't1mri' )
    eNode.addDoubleLink(
      'NormalizeBaladin.ReorientAnatomy.commissures_coordinates', 
      'commissures_coordinates' )
    eNode.addDoubleLink(
      'NormalizeBaladin.ReorientAnatomy.output_commissures_coordinates',
      'output_commissures_coordinates' )
    eNode.addDoubleLink('reoriented_t1mri',
                        'NormalizeBaladin.reoriented_t1mri')

    eNode.selection_outputs.append(
      ['transformation', 'NormalizeBaladin.normalized_anatomy_data',
       'reoriented_t1mri'])

  eNode.addChild( 'Normalization_AimsMIRegister',
    ProcessExecutionNode( 'normalization_aimsmiregister',
      selected=(fsl is None and spm is None and bal is None) ) )
  eNode.Normalization_AimsMIRegister.removeLink( 'transformation_to_MNI', 'anatomy_data' )
  eNode.addDoubleLink( 'Normalization_AimsMIRegister.anatomy_data', 't1mri' )
  eNode.addDoubleLink( 'Normalization_AimsMIRegister.transformation_to_MNI', 'transformation' )

  eNode.selection_outputs.append(
    ['transformation_to_MNI', 'normalized_anatomy_data', '/t1mri'])
  eNode.switch_output = ['transformation', 'normalized', 'reoriented_t1mri']

  self.setExecutionNode( eNode )

  self.capsul_do_not_export = [
    ('NormalizeFSL', 'ConvertFSLnormalizationToAIMS_write'),
    ('NormalizeBaladin', 'ConvertBaladinNormalizationToAIMS_write'),]


