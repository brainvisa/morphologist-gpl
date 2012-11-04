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

name = 'Morphologist 2012, parallel version'
userLevel = 0

# sulci recognition methodes identifiers
ann_model = 'Abstract Neural Network (ANN)'
ann_model_2001 = 'ANN, older 2000-2001 labels'
spam_model_tal = 'Statistical Parametric Anatomy Map (SPAM), in Talairach space'
spam_model_global = 'SPAM, global registration'
spam_model_local = 'SPAM, global+local registration'
spam_model_markov = 'SPAM, global registration + Markovian'


# signature
signature = Signature(
  'mri', ReadDiskItem( "Raw T1 MRI", 'Aims readable volume formats' ),
  'mri_corrected', WriteDiskItem( "T1 MRI Bias Corrected",
      'Aims writable volume formats' ),
  'perform_normalization', Boolean(),
  'Normalised',Choice('No','MNI from SPM','MNI from Mritotal',
      'Marseille from SPM'),
  'Anterior_Commissure', Point3D(),
  'Posterior_Commissure', Point3D(),
  'Interhemispheric_Point', Point3D(),
  'Left_Hemisphere_Point', Point3D(),
  'sulci_graphs_version', Choice( '3.1', '3.0' ),
  'perform_sulci_recognition', Boolean(),
  'sulci_recognition_method', Choice( ann_model, ann_model_2001,
    spam_model_tal, spam_model_global, spam_model_local, spam_model_markov ),
)


class changeTalairach:
  def __init__( self, proc ):
    self.proc = weakref.proxy( proc )
  def __call__( self, node ):
    if node.isSelected():
      self.proc.executionNode().Par.Seg.TalairachTransformation.setSelected(
        True )
      self.proc.perform_normalization = False
    else:
      self.proc.executionNode().Par.Seg.TalairachTransformation.setSelected(
        False )
      self.proc.perform_normalization = True

class linkCheckModels:
  spamModelsChecked = False

  def __init__( self, proc ):
    self.proc = weakref.proxy( proc )

  def __call__( self, node ):
    eNode = self.proc.executionNode().Par.Seg.Hemispheres
    if eNode.LeftHemisphere.SulciRecognition.isSelected() \
      == eNode.RightHemisphere.SulciRecognition.isSelected():
      self.proc.perform_sulci_recognition \
        = eNode.LeftHemisphere.SulciRecognition.isSelected()
    if not linkCheckModels.spamModelsChecked:
      if eNode.LeftHemisphere.SulciRecognition.isSelected() \
        or eNode.RightHemisphere.SulciRecognition.isSelected():
        proc = getProcessInstance( 'check_spam_models' )
        linkCheckModels.spamModelsChecked = True
        if proc:
          defaultContext().runProcess( proc )


# unselects thickness processing if graphs are not built or are graphs 3.0
class selectThickness( object ):
  def __init__( self, proc, side ):
    self.proc = weakref.proxy( proc )
    self.side = side
  def __call__( self, node ):
    node = self.proc.executionNode().Par.Seg.Hemispheres
    if self.side == 'Left':
      h = node.LeftHemisphere
    else:
      h = node.RightHemisphere
    graph = h.Meshes.Graph
    if graph.isSelected() and graph.CorticalFoldsGraph_3_1.isSelected():
      h.GraphThickness.setSelected( True )
    else:
      h.GraphThickness.setSelected( False )


class changeSkullStrippedNoprmalization:
  def __init__( self, proc ):
    self.proc = weakref.proxy( proc )
  def __call__( self, node ):
    eNode = self.proc.executionNode()
    if node.isSelected():
      eNode.Par.Seg.TalairachTransformation.setSelected( False )
    else:
      if eNode.PrepareSubject.StandardACPC.isSelected():
        self.proc.executionNode().Par.Seg.TalairachTransformation.setSelected(
          True )


# process initialization code
def initialization( self ):
  def changeNormalize( self, proc ):
    eNode = self.executionNode()
    if len( list( eNode.PrepareSubject.executionNode().children() ) ) > 1:
      if hasattr( eNode.PrepareSubject, 'StandardACPC' ):
        s = eNode.PrepareSubject.StandardACPC.isSelected()
      else:
        s = False
      if s == self.perform_normalization:
        y = list(eNode.PrepareSubject.executionNode().children())
        y[0].setSelected( not self.perform_normalization )
        y[1].setSelected( self.perform_normalization )
        ul = self.userLevel
        if s:
          ul = 3
        # the following userlevel stuff doesn't work
        self.signature[ 'Normalised' ].userLevel = ul
        self.signature[ 'Anterior_Commissure' ].userLevel = ul
        self.signature[ 'Posterior_Commissure' ].userLevel = ul
        self.signature[ 'Interhemispheric_Point' ].userLevel = ul
        self.signature[ 'Left_Hemisphere_Point' ].userLevel = ul
        # enabling this produces widgets deletion problems
        #self.changeSignature( self.signature )
    return self.Normalised

  def linkSide( p ):
    '''Translates between older processes using "Left", "Right" and newer ones
    using "left", "right"'''
    if p is not None and p == p.lower():
      return p[0].upper() + p[1:]
    else:
      return p.lower()

  def setGraphVersion( ver, names, parameterized ):
    '''Select appropriate sub-processes for a given graph version chosen from
    the main pipeline option'''
    eNode = parameterized[0].executionNode().Par.Seg.Hemispheres
    if ver == '3.1':
      eNode.LeftHemisphere.Meshes.Graph.CorticalFoldsGraph_3_1.setSelected( True )
      eNode.RightHemisphere.Meshes.Graph.CorticalFoldsGraph_3_1.setSelected( True )
    else:
      eNode.LeftHemisphere.Meshes.Graph.CorticalFoldsGraph_3_0.setSelected( True )
      eNode.RightHemisphere.Meshes.Graph.CorticalFoldsGraph_3_0.setSelected( True )

  def enableRecognition( enabled, names, parameterized ):
    '''Select appropriate sub-processes when recognition is switched from
    the main pipeline option'''
    eNode = parameterized[0].executionNode().Par.Seg.Hemispheres
    eNode.LeftHemisphere.SulciRecognition.setSelected( enabled )
    eNode.RightHemisphere.SulciRecognition.setSelected( enabled )

  def setRecognitionMethod( meth, names, parameterized ):
    '''Select appropriate sub-processes and parameters when recognition method
    is chosen from the main pipeline option'''
    eNode = parameterized[0].executionNode().Par.Seg.Hemispheres
    if meth == ann_model:
      eNode.LeftHemisphere.SulciRecognition.recognition2000.setSelected( True )
      eNode.RightHemisphere.SulciRecognition.recognition2000.setSelected( True )
      eNode.LeftHemisphere.SulciRecognition.recognition2000.model_hint = 0
      eNode.RightHemisphere.SulciRecognition.recognition2000.model_hint = 0
    elif meth == ann_model_2001:
      eNode.LeftHemisphere.SulciRecognition.recognition2000.setSelected( True )
      eNode.RightHemisphere.SulciRecognition.recognition2000.setSelected( True )
      eNode.LeftHemisphere.SulciRecognition.recognition2000.model_hint = 1
      eNode.RightHemisphere.SulciRecognition.recognition2000.model_hint = 1
    elif meth == spam_model_tal:
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.setSelected( True )
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.setSelected( True )
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.global_recognition.setSelected( True )
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.global_recognition.setSelected( True )
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.local_or_markovian.setSelected( False )
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.local_or_markovian.setSelected( False )
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.global_recognition.model_type = 'Talairach'
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.global_recognition.model_type = 'Talairach'
    elif meth == spam_model_global:
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.setSelected( True )
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.setSelected( True )
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.global_recognition.setSelected( True )
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.global_recognition.setSelected( True )
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.local_or_markovian.setSelected( False )
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.local_or_markovian.setSelected( False )
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.global_recognition.model_type = 'Global registration'
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.global_recognition.model_type = 'Global registration'
    elif meth == spam_model_local:
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.setSelected( True )
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.setSelected( True )
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.global_recognition.setSelected( True )
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.global_recognition.setSelected( True )
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.local_or_markovian.setSelected( True )
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.local_or_markovian.setSelected( True )
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.local_or_markovian.local_recognition.setSelected( True )
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.local_or_markovian.local_recognition.setSelected( True )
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.global_recognition.model_type = 'Global registration'
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.global_recognition.model_type = 'Global registration'
    elif meth == spam_model_markov:
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.setSelected( True )
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.setSelected( True )
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.global_recognition.setSelected( True )
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.global_recognition.setSelected( True )
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.local_or_markovian.setSelected( True )
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.local_or_markovian.setSelected( True )
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.local_or_markovian.markovian_recognition.setSelected( True )
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.local_or_markovian.markovian_recognition.setSelected( True )
      eNode.LeftHemisphere.SulciRecognition.SPAM_recognition09.global_recognition.model_type = 'Global registration'
      eNode.RightHemisphere.SulciRecognition.SPAM_recognition09.global_recognition.model_type = 'Global registration'

  # real initialization code: build the pipeline structure
  eNode = SerialExecutionNode( self.name, parameterized=self )

  eNode.addChild( 'PrepareSubject',
                  ProcessExecutionNode( 'acpcOrNormalization', optional = 1 ) )
  eNode.addChild( 'BiasCorrection',
                  ProcessExecutionNode( 'T1BiasCorrection',
                                        optional = 1 ) )
  eNode.addChild( 'HistoAnalysis',
                   ProcessExecutionNode( 'NobiasHistoAnalysis',
                                         optional = 1 ) )
  eNode.addChild( 'BrainSegmentation',
                   ProcessExecutionNode( 'BrainSegmentation',
                                         optional = 1 ) )
  paraNode = ParallelExecutionNode( 'Parallel Node', optional=True,
    expandedInGui=True )
  eNode.addChild( 'Par', paraNode )

  segNode = SerialExecutionNode( 'Segmentation', optional=True,
    expandedInGui=True )

  segNode.addChild( 'SplitBrain',
                    ProcessExecutionNode( 'SplitBrain', optional = 1 ) )
  segNode.addChild( 'TalairachTransformation',
                   ProcessExecutionNode( 'TalairachTransformation',
                                         optional = 1 ) )

  hemiProc = ParallelExecutionNode( 'Hemispheres processing', optional=True,
      expandedInGui=True )
  leftNode = SerialExecutionNode( 'Left hemisphere', optional=True,
      expandedInGui=True )
  rightNode = SerialExecutionNode( 'Right hemisphere', optional=True,
      expandedInGui=True )
  leftNode.addChild( 'GreyWhiteClassification',
                   ProcessExecutionNode( 'GreyWhiteClassificationHemi',
                                         optional = 1 ) )
  leftNode.GreyWhiteClassification.side = 'left'
  leftNode.GreyWhiteClassification.signature[ 'side' ].userLevel = 3
  rightNode.addChild( 'GreyWhiteClassification',
                   ProcessExecutionNode( 'GreyWhiteClassificationHemi',
                                         optional = 1 ) )
  rightNode.GreyWhiteClassification.side = 'right'
  rightNode.GreyWhiteClassification.signature[ 'side' ].userLevel = 3
  leftNode.addChild( 'GreyWhiteTopology',
                   ProcessExecutionNode( 'GreyWhiteTopology',
                                         optional = 1 ) )
  rightNode.addChild( 'GreyWhiteTopology',
                   ProcessExecutionNode( 'GreyWhiteTopology',
                                         optional = 1 ) )

  leftMeshes = ParallelExecutionNode( 'Left meshes and graph', optional=True,
    expandedInGui=True )
  rightMeshes = ParallelExecutionNode( 'Right meshes ans graph', optional=True,
    expandedInGui=True )
  leftMeshes.addChild( 'GreyWhiteMesh',
                   ProcessExecutionNode( 'GreyWhiteMesh',
                                         optional = 1 ) )
  rightMeshes.addChild( 'GreyWhiteMesh',
                   ProcessExecutionNode( 'GreyWhiteMesh',
                                         optional = 1 ) )
  leftMeshes.addChild( 'PialMesh',
                   ProcessExecutionNode( 'hemispheremesh',
                                         optional = 1 ) )
  rightMeshes.addChild( 'PialMesh',
                   ProcessExecutionNode( 'hemispheremesh',
                                         optional = 1 ) )
  leftMeshes.addChild( 'Graph',
                   ProcessExecutionNode( 'CorticalFoldsGraphHemi',
                                         optional = 1 ) )
  rightMeshes.addChild( 'Graph',
                   ProcessExecutionNode( 'CorticalFoldsGraphHemi',
                                         optional = 1 ) )
  rightMeshes.Graph.side = 'Right'

  leftNode.addChild( 'Meshes', leftMeshes )
  rightNode.addChild( 'Meshes', rightMeshes )
  hemiProc.addChild( 'LeftHemisphere', leftNode )
  hemiProc.addChild( 'RightHemisphere', rightNode )
  segNode.addChild( 'Hemispheres', hemiProc )

  paraNode.addChild( 'HeadMesh', ProcessExecutionNode( 'headMesh',
                                                    optional = 1 ) )

  hasNorm = False
  try:
    p = getProcessInstance( 'normalization_skullstripped' )
    if p:
      p.validationDelayed()
      hasNorm = True
  except:
    pass
  if hasNorm:
    ssnNode = SerialExecutionNode( 'Re-normalization, skull-stripped',
      optional=True, selected=False )
    paraNode.addChild( 'SStrippedRenorm', ssnNode )
    ssnNode.addChild( 'Renorm',
      ProcessExecutionNode( 'normalization_skullstripped', optional=True ) )
    ssnNode.addChild( 'TalFromN',
      ProcessExecutionNode( 'TalairachTransformationFromNormalization' ) )

  paraNode.addChild( 'Seg', segNode )

  # links

  eNode.addDoubleLink( 'PrepareSubject.T1mri', 'mri' )

  if hasattr( eNode.PrepareSubject, 'StandardACPC' ):
    eNode.addDoubleLink( 'PrepareSubject.StandardACPC.Normalised',
      'Normalised' )
    eNode.addDoubleLink( 'PrepareSubject.StandardACPC.Anterior_Commissure',
      'Anterior_Commissure' )
    eNode.addDoubleLink( 'PrepareSubject.StandardACPC.Posterior_Commissure',
      'Posterior_Commissure' )
    eNode.addDoubleLink( 'PrepareSubject.StandardACPC.Interhemispheric_Point',
      'Interhemispheric_Point' )
    eNode.addDoubleLink( 'PrepareSubject.StandardACPC.Left_Hemisphere_Point',
      'Left_Hemisphere_Point' )
  self.setOptional( 'Normalised' )
  self.setOptional( 'Anterior_Commissure' )
  self.setOptional( 'Posterior_Commissure' )
  self.setOptional( 'Interhemispheric_Point' )
  self.setOptional( 'Left_Hemisphere_Point' )

  self.signature[ 'Anterior_Commissure' ].add3DLink( self, 'mri' )
  self.signature[ 'Posterior_Commissure' ].add3DLink( self, 'mri' )
  self.signature[ 'Interhemispheric_Point' ].add3DLink( self, 'mri' )
  self.signature[ 'Left_Hemisphere_Point' ].add3DLink( self, 'mri' )


  #eNode.BiasCorrection.removeLink( 'mri_corrected', 'mri' )
  eNode.addDoubleLink( 'BiasCorrection.mri', 'mri' )
  eNode.addDoubleLink( 'BiasCorrection.mri_corrected', 'mri_corrected' )

  eNode.HistoAnalysis.removeLink( 'hfiltered', 'mri_corrected' )
  eNode.HistoAnalysis.removeLink( 'white_ridges', 'mri_corrected' )

  eNode.addDoubleLink( 'HistoAnalysis.mri_corrected',
                       'BiasCorrection.mri_corrected' )
  eNode.addDoubleLink( 'HistoAnalysis.hfiltered', 'BiasCorrection.hfiltered' )
  eNode.addDoubleLink( 'HistoAnalysis.white_ridges',
                       'BiasCorrection.white_ridges' )

  eNode.BrainSegmentation.removeLink( 'histo_analysis', 'mri_corrected' )
  eNode.BrainSegmentation.removeLink( 'commissure_coordinates',
                                      'mri_corrected' )
  eNode.BrainSegmentation.removeLink( 'white_ridges', 'mri_corrected' )

  eNode.addDoubleLink( 'BrainSegmentation.mri_corrected',
                       'BiasCorrection.mri_corrected' )

  eNode.addDoubleLink( 'BrainSegmentation.histo_analysis',
                       'HistoAnalysis.histo_analysis' )

  eNode.addDoubleLink( 'BrainSegmentation.commissure_coordinates',
                       'PrepareSubject.commissure_coordinates' )

  eNode.addDoubleLink( 'BrainSegmentation.white_ridges',
                       'BiasCorrection.white_ridges' )

  eNode.BrainSegmentation.removeLink( 'variance', 'mri_corrected' )
  eNode.BrainSegmentation.removeLink( 'edges', 'mri_corrected' )

  eNode.addDoubleLink( 'BrainSegmentation.variance',
                       'BiasCorrection.variance' )
  eNode.addDoubleLink( 'BrainSegmentation.edges',
                       'BiasCorrection.edges' )

  segNode.SplitBrain.removeLink( 'histo_analysis', 'mri_corrected' )
  segNode.SplitBrain.removeLink( 'brain_mask', 'mri_corrected' )
  segNode.SplitBrain.removeLink( 'commissure_coordinates', 'mri_corrected' )
  segNode.SplitBrain.removeLink( 'white_ridges', 'mri_corrected' )

  eNode.addDoubleLink( 'Par.Seg.SplitBrain.mri_corrected',
                       'BiasCorrection.mri_corrected' )
  eNode.addDoubleLink( 'Par.Seg.SplitBrain.histo_analysis',
                       'HistoAnalysis.histo_analysis' )
  eNode.addDoubleLink( 'Par.Seg.SplitBrain.brain_mask',
                       'BrainSegmentation.brain_mask' )
  eNode.addDoubleLink( 'Par.Seg.SplitBrain.commissure_coordinates',
                       'PrepareSubject.commissure_coordinates' )
  eNode.addDoubleLink( 'Par.Seg.SplitBrain.white_ridges',
                       'BiasCorrection.white_ridges' )

  segNode.TalairachTransformation.removeLink( 'commissure_coordinates',
                                              'split_mask' )

  segNode.addDoubleLink( 'TalairachTransformation.split_mask',
                         'SplitBrain.split_mask' )
  eNode.addDoubleLink( \
    'Par.Seg.TalairachTransformation.commissure_coordinates',
    'PrepareSubject.commissure_coordinates' )

  paraNode.HeadMesh.removeLink( 'histo_analysis', 'mri_corrected' )

  eNode.addDoubleLink( 'Par.HeadMesh.mri_corrected',
      'BiasCorrection.mri_corrected' )
  eNode.addDoubleLink( 'Par.HeadMesh.histo_analysis',
      'HistoAnalysis.histo_analysis' )

  # skull-stripped normalization
  if hasNorm:
    ssnNode.Renorm.removeLink( 'brain_mask', 't1mri' )

    eNode.addDoubleLink( 'mri', 'Par.SStrippedRenorm.Renorm.t1mri' )
    eNode.addDoubleLink( 'BrainSegmentation.brain_mask',
        'Par.SStrippedRenorm.Renorm.brain_mask' )

    ssnNode.TalFromN.removeLink( 'Talairach_transform',
      'normalization_transformation' )
    ssnNode.TalFromN.removeLink( 'commissure_coordinates',
      'Talairach_transform' )
    ssnNode.TalFromN.removeLink( 't1mri', 'commissure_coordinates' )

    ssnNode.addDoubleLink( 'TalFromN.t1mri', 'Renorm.t1mri' )
    ssnNode.addDoubleLink( 'TalFromN.normalization_transformation',
      'Renorm.transformation' )
    paraNode.addDoubleLink( \
      'SStrippedRenorm.TalFromN.Talairach_transform',
      'Seg.TalairachTransformation.Talairach_transform' )
    eNode.addDoubleLink( \
      'Par.SStrippedRenorm.TalFromN.commissure_coordinates',
      'PrepareSubject.commissure_coordinates' )

  reco = getProcess('recognitionGeneral')

  # in each hemisphere
  for hemiNode, hemiP, side in \
    ( ( leftNode, 'Par.Seg.Hemispheres.LeftHemisphere', 'Left' ),
      ( rightNode, 'Par.Seg.Hemispheres.RightHemisphere', 'Right' ) ):

    classifNode = hemiNode.GreyWhiteClassification
    classifNode.removeLink( 'histo_analysis', 'mri_corrected' )
    classifNode.removeLink( 'split_mask', 'mri_corrected' )
    classifNode.removeLink( 'edges', 'mri_corrected' )
    classifNode.removeLink( 'commissure_coordinates', 'mri_corrected' )

    classifP = hemiP + '.GreyWhiteClassification'
    eNode.addDoubleLink( \
      classifP + '.mri_corrected', 'BiasCorrection.mri_corrected' )
    eNode.addDoubleLink( \
      classifP + '.histo_analysis', 'HistoAnalysis.histo_analysis' )
    eNode.addDoubleLink( classifP + '.split_mask',
      'Par.Seg.SplitBrain.split_mask' )
    eNode.addDoubleLink( classifP + '.edges', 'BiasCorrection.edges' )
    eNode.addDoubleLink( classifP + '.commissure_coordinates',
      'PrepareSubject.commissure_coordinates' )

    gwtNode = hemiNode.GreyWhiteTopology
    gwtNode.removeLink( 'histo_analysis', 'mri_corrected' )
    gwtNode.removeLink( 'mri_corrected', 'grey_white' )

    eNode.addDoubleLink( \
      hemiP + '.GreyWhiteTopology.mri_corrected',
      'BiasCorrection.mri_corrected' )
    eNode.addDoubleLink( \
      hemiP + '.GreyWhiteTopology.histo_analysis',
      'HistoAnalysis.histo_analysis' )
    eNode.addDoubleLink( \
      hemiP + '.GreyWhiteTopology.grey_white',
      hemiP + '.GreyWhiteClassification.grey_white' )

    eNode.addDoubleLink( \
      hemiP + '.Meshes.GreyWhiteMesh.hemi_cortex',
      hemiP + '.GreyWhiteTopology.hemi_cortex' )

    meshes = hemiNode.Meshes
    meshes.PialMesh.removeLink( 'split_mask', 'mri_corrected' )
    meshes.PialMesh.removeLink( 'mri_corrected', 'hemi_cortex' )

    meshP = hemiP + '.Meshes'
    eNode.addDoubleLink( \
      meshP + '.PialMesh.mri_corrected', 'BiasCorrection.mri_corrected' )
    eNode.addDoubleLink( \
      meshP + '.PialMesh.split_mask', 'Par.Seg.SplitBrain.split_mask' )
    eNode.addDoubleLink( \
      meshP + '.PialMesh.hemi_cortex',
      hemiP + '.GreyWhiteTopology.hemi_cortex' )

    # graphs

    # 3.1
    graph = meshes.Graph
    graph.removeLink( 'split_mask', 'mri_corrected' )
    graph.removeLink( 'commissure_coordinates', 'mri_corrected' )
    graph.removeLink( 'Talairach_transform', 'split_mask' )
    graph.CorticalFoldsGraph_3_1.removeLink( 'hemi_cortex', 'split_mask' )
    graph.CorticalFoldsGraph_3_1.removeLink( 'hemi_cortex', 'side' )
    graph.CorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.clearLinksTo( \
      'GW_interface')
    graph.CorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.clearLinksTo( \
      'white_mesh')
    graph.CorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.clearLinksTo( \
      'hemi_mesh')

    eNode.addDoubleLink( \
      meshP + '.Graph.mri_corrected', 'BiasCorrection.mri_corrected' )
    eNode.addDoubleLink(
      meshP + '.Graph.split_mask', 'Par.Seg.SplitBrain.split_mask' )
    eNode.addDoubleLink( \
      meshP + '.Graph.commissure_coordinates',
      'PrepareSubject.commissure_coordinates' )
    eNode.addDoubleLink( \
      meshP + '.Graph.Talairach_transform',
      'Par.Seg.TalairachTransformation.Talairach_transform' )

    hemiNode.addDoubleLink( \
      'Meshes.Graph.side', 'GreyWhiteClassification.side', linkSide )
    hemiNode.addDoubleLink( \
      'Meshes.Graph.CorticalFoldsGraph_3_1.hemi_cortex',
      'GreyWhiteTopology.hemi_cortex' )
    hemiNode.addDoubleLink( \
      'Meshes.Graph.CorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.' \
      'GW_interface',
      'GreyWhiteClassification.grey_white' )
    hemiNode.Meshes.addDoubleLink( \
      'Graph.CorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.white_mesh',
      'GreyWhiteMesh.white_mesh' )
    hemiNode.Meshes.addDoubleLink( \
      'Graph.CorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.hemi_mesh',
      'PialMesh.hemi_mesh' )

    # 3.0
    graph.CorticalFoldsGraph_3_0.removeLink( 'hemi_cortex', 'split_mask' )
    graph.CorticalFoldsGraph_3_0.removeLink( 'hemi_cortex', 'side' )

    hemiNode.addDoubleLink( \
      'Meshes.Graph.CorticalFoldsGraph_3_0.hemi_cortex',
      'GreyWhiteTopology.hemi_cortex' )

    # change thickness process location in three because of its dependencies
    grthick = graph.CorticalFoldsGraph_3_1.CorticalFoldsGraphThickness
    graph.CorticalFoldsGraph_3_1._process.executionNode().removeChild( \
      'CorticalFoldsGraphThickness' )
    hemiNode.addChild( 'GraphThickness', grthick )

    # disable thickness if graph 3.1 is unselected
    graph._selectionChange.add( selectThickness( self, side ) )
    graph.CorticalFoldsGraph_3_1._selectionChange.add( \
      selectThickness( self, side ) )

    graph.addExecutionDependencies( ssnNode )

    # sulci recognition
    if reco:
      hemiNode.addChild( 'SulciRecognition',
        ProcessExecutionNode( 'recognitionGeneral', optional=1, selected=0 ) )

      hemiNode.addDoubleLink( \
        'SulciRecognition.data_graph', 'Meshes.Graph.graph' )

      hemiNode.SulciRecognition._selectionChange.add( linkCheckModels( self ) )


  # back to global pipeline

  self.perform_sulci_recognition = False
  self.sulci_recognition_method = spam_model_local

  eNode.addLink( None, 'sulci_graphs_version', setGraphVersion )
  if reco:
    eNode.addLink( None, 'perform_sulci_recognition', enableRecognition )
    eNode.addLink( None, 'sulci_recognition_method', setRecognitionMethod )
  else:
    self.signature[ 'perform_sulci_recognition' ].userLevel = 3
    self.signature[ 'sulci_recognition_method' ].userLevel = 3

  if len( list( eNode.PrepareSubject.executionNode().children() ) ) == 1:
    self.perform_normalization = False
    self.signature[ 'perform_normalization' ].userLevel = 3
  if not hasattr( eNode.PrepareSubject, 'StandardACPC' ) \
    or not eNode.PrepareSubject.StandardACPC.isSelected():
    segNode.TalairachTransformation.setSelected( False )
    self.perform_normalization = True
  else:
    self.perform_normalization = False
  x = changeTalairach( self )
  if hasattr( eNode.PrepareSubject, 'StandardACPC' ):
    eNode.PrepareSubject.StandardACPC._selectionChange.add( x )
  self.linkParameters( 'Normalised', 'perform_normalization', changeNormalize )

  x = changeSkullStrippedNoprmalization( self )
  paraNode.SStrippedRenorm._selectionChange.add( x )

  self.setExecutionNode( eNode )

  # just for now, still stick with AC/PC for test and compatibility
  self.perform_normalization = False
  changeNormalize( self, self )
