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

name = 'Morphologist 2012'
userLevel = 0

signature = Signature(
  'mri', ReadDiskItem( "Raw T1 MRI", 'aims readable Volume Formats' ),
  'mri_corrected', WriteDiskItem( "T1 MRI Bias Corrected",
      'Aims writable volume formats' ),
  'perform_normalization', Boolean(),
  'Normalised',Choice('No','MNI from SPM','MNI from Mritotal',
      'Marseille from SPM'),
  'Anterior_Commissure', Point3D(),
  'Posterior_Commissure', Point3D(),
  'Interhemispheric_Point', Point3D(),
  'Left_Hemisphere_Point', Point3D(),
  )


class changeTalairach:
  def __init__( self, proc ):
    self.proc = weakref.proxy( proc )
  def __call__( self, node ):
    if node.isSelected():
      self.proc.executionNode().TalairachTransformation.setSelected( True )
      self.proc.perform_normalization = False
    else:
      self.proc.executionNode().TalairachTransformation.setSelected( False )
      self.proc.perform_normalization = True

class linkCheckModels:
  spamModelsChecked = False

  def __init__( self, proc ):
    self.proc = weakref.proxy( proc )

  def __call__( self, node ):
    if not linkCheckModels.spamModelsChecked:
      eNode = self.proc.executionNode()
      if eNode.SulciRecognition.isSelected():
        proc = getProcessInstance( 'check_spam_models' )
        linkCheckModels.spamModelsChecked = True
        if proc:
          defaultContext().runProcess( proc )


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


  eNode = SerialExecutionNode( self.name, parameterized=self )

  eNode.addChild( 'PrepareSubject',
                  ProcessExecutionNode( 'acpcOrNormalization', optional = 1,
                  altname=_t_('Image orientation handling') ) )


  eNode.addChild( 'BiasCorrection',
                  ProcessExecutionNode( 'T1BiasCorrection',
                                        optional = 1 ) )

  eNode.addChild( 'HistoAnalysis',
                   ProcessExecutionNode( 'NobiasHistoAnalysis',
                                         optional = 1 ) )

  eNode.addChild( 'BrainSegmentation',
                   ProcessExecutionNode( 'BrainSegmentation',
                                         optional = 1 ) )

  eNode.addChild( 'SplitBrain',
                   ProcessExecutionNode( 'SplitBrain', optional = 1 ) )

  eNode.addChild( 'TalairachTransformation',
                   ProcessExecutionNode( 'TalairachTransformation',
                                         optional = 1 ) )

  eNode.addChild( 'GreyWhiteClassification',
                   ProcessExecutionNode( 'GreyWhiteClassification',
                                         optional = 1 ) )
  eNode.addChild( 'GreyWhiteSurface',
                   ProcessExecutionNode( 'GreyWhiteSurface',
                                         optional = 1 ) )

  eNode.addChild( 'HemispheresMesh',
                  ProcessExecutionNode( 'GetSphericalHemiSurface',
                                        optional = 1 ) )

  eNode.addChild( 'HeadMesh', ProcessExecutionNode( 'headMesh',
                                                    optional = 1 ) )

  eNode.addChild( 'CorticalFoldsGraph',
                  ProcessExecutionNode( 'CorticalFoldsGraphGeneral',
                                        optional = 1 ) )

  reco = getProcess('recognitionGeneral')
  if reco:
    eNode.addChild( 'SulciRecognition',
      ProcessExecutionNode( 'Sulci Recognition (both hemispheres)',
        optional=1, selected=0 ) )

  # links

  eNode.addLink( 'PrepareSubject.T1mri', 'mri' )
  eNode.addLink( 'mri', 'PrepareSubject.T1mri' )

  if hasattr( eNode.PrepareSubject, 'StandardACPC' ):
    eNode.addLink( 'PrepareSubject.StandardACPC.Normalised', 'Normalised' )
    eNode.addLink( 'Normalised', 'PrepareSubject.StandardACPC.Normalised' )
    eNode.addLink( 'PrepareSubject.StandardACPC.Anterior_Commissure',
      'Anterior_Commissure' )
    eNode.addLink( 'Anterior_Commissure',
      'PrepareSubject.StandardACPC.Anterior_Commissure' )
    eNode.addLink( 'PrepareSubject.StandardACPC.Posterior_Commissure',
      'Posterior_Commissure' )
    eNode.addLink( 'Posterior_Commissure',
      'PrepareSubject.StandardACPC.Posterior_Commissure' )
    eNode.addLink( 'PrepareSubject.StandardACPC.Interhemispheric_Point',
      'Interhemispheric_Point' )
    eNode.addLink( 'Interhemispheric_Point',
      'PrepareSubject.StandardACPC.Interhemispheric_Point' )
    eNode.addLink( 'PrepareSubject.StandardACPC.Left_Hemisphere_Point',
      'Left_Hemisphere_Point' )
    eNode.addLink( 'Left_Hemisphere_Point',
      'PrepareSubject.StandardACPC.Left_Hemisphere_Point' )
  self.setOptional( 'Normalised' )
  self.setOptional( 'Anterior_Commissure' )
  self.setOptional( 'Posterior_Commissure' )
  self.setOptional( 'Interhemispheric_Point' )
  self.setOptional( 'Left_Hemisphere_Point' )

  self.signature[ 'Anterior_Commissure' ].add3DLink( self, 'mri' )
  self.signature[ 'Posterior_Commissure' ].add3DLink( self, 'mri' )
  self.signature[ 'Interhemispheric_Point' ].add3DLink( self, 'mri' )
  self.signature[ 'Left_Hemisphere_Point' ].add3DLink( self, 'mri' )



  #eNode.BiasCorrection.removeLink( 't1mri_nobias', 't1mri' )
  eNode.BiasCorrection.removeLink( 'commissure_coordinates', 't1mri' )
  eNode.addDoubleLink( 'BiasCorrection.commissure_coordinates',
      'PrepareSubject.commissure_coordinates' )
  eNode.addLink( 'BiasCorrection.t1mri', 'mri' )
  eNode.addLink( 'mri', 'BiasCorrection.t1mri' )
  eNode.addLink( 'BiasCorrection.t1mri_nobias', 'mri_corrected' )
  eNode.addLink( 'mri_corrected', 'BiasCorrection.t1mri_nobias' )


  eNode.HistoAnalysis.removeLink( 'hfiltered', 't1mri_nobias' )
  eNode.HistoAnalysis.removeLink( 'white_ridges', 't1mri_nobias' )

  eNode.addLink( 'HistoAnalysis.t1mri_nobias',
                 'BiasCorrection.t1mri_nobias' )
  eNode.addLink( 'BiasCorrection.t1mri_nobias',
                 'HistoAnalysis.t1mri_nobias' )

  eNode.addLink( 'HistoAnalysis.hfiltered', 'BiasCorrection.hfiltered' )
  eNode.addLink( 'HistoAnalysis.white_ridges', 'BiasCorrection.white_ridges' )


  eNode.BrainSegmentation.removeLink( 'histo_analysis', 't1mri_nobias' )
  eNode.BrainSegmentation.removeLink( 'commissure_coordinates',
                                      't1mri_nobias' )
  eNode.BrainSegmentation.removeLink( 'white_ridges', 't1mri_nobias' )

  eNode.addLink( 'BrainSegmentation.t1mri_nobias',
                 'BiasCorrection.t1mri_nobias' )
  eNode.addLink( 'BiasCorrection.t1mri_nobias',
                 'BrainSegmentation.t1mri_nobias' )

  eNode.addLink( 'BrainSegmentation.histo_analysis',
                 'HistoAnalysis.histo_analysis' )
  eNode.addLink( 'HistoAnalysis.histo_analysis',
                 'BrainSegmentation.histo_analysis' )

  eNode.addLink( 'BrainSegmentation.commissure_coordinates',
                 'PrepareSubject.commissure_coordinates' )
  eNode.addLink( 'PrepareSubject.commissure_coordinates',
                 'BrainSegmentation.commissure_coordinates' )

  eNode.addLink( 'BrainSegmentation.white_ridges',
                 'BiasCorrection.white_ridges' )
  eNode.addLink( 'BiasCorrection.white_ridges',
                 'BrainSegmentation.white_ridges' )

  eNode.BrainSegmentation.removeLink( 'variance', 't1mri_nobias' )
  eNode.BrainSegmentation.removeLink( 'edges', 't1mri_nobias' )
  eNode.addDoubleLink( 'BrainSegmentation.variance',
                       'BiasCorrection.variance' )
  eNode.addDoubleLink( 'BrainSegmentation.edges',
                       'BiasCorrection.edges' )


  eNode.SplitBrain.removeLink( 'histo_analysis', 't1mri_nobias' )
  eNode.SplitBrain.removeLink( 't1mri_nobias', 'brain_mask' )
  eNode.SplitBrain.removeLink( 'commissure_coordinates', 't1mri_nobias' )
  eNode.SplitBrain.removeLink( 'white_ridges', 't1mri_nobias' )

  eNode.addLink( 'SplitBrain.t1mri_nobias',
                 'BiasCorrection.t1mri_nobias' )
  eNode.addLink( 'BiasCorrection.t1mri_nobias',
                 'SplitBrain.t1mri_nobias' )

  eNode.addLink( 'SplitBrain.histo_analysis',
                 'HistoAnalysis.histo_analysis' )
  eNode.addLink( 'HistoAnalysis.histo_analysis',
                 'SplitBrain.histo_analysis' )

  eNode.addLink( 'SplitBrain.brain_mask',
                 'BrainSegmentation.brain_mask' )
  eNode.addLink( 'BrainSegmentation.brain_mask',
                 'SplitBrain.brain_mask' )

  eNode.addLink( 'SplitBrain.commissure_coordinates',
                 'PrepareSubject.commissure_coordinates' )
  eNode.addLink( 'PrepareSubject.commissure_coordinates',
                 'SplitBrain.commissure_coordinates' )

  eNode.addLink( 'SplitBrain.white_ridges',
                 'BiasCorrection.white_ridges' )
  eNode.addLink( 'BiasCorrection.white_ridges',
                 'SplitBrain.white_ridges' )


  eNode.TalairachTransformation.removeLink( 'commissure_coordinates',
                                            'split_mask' )

  eNode.addLink( 'TalairachTransformation.split_mask',
                 'SplitBrain.split_brain' )
  eNode.addLink( 'SplitBrain.split_brain',
                 'TalairachTransformation.split_mask' )

  eNode.addLink( 'TalairachTransformation.commissure_coordinates',
                 'PrepareSubject.commissure_coordinates' )
  eNode.addLink( 'PrepareSubject.commissure_coordinates',
                 'TalairachTransformation.commissure_coordinates' )


  eNode.GreyWhiteClassification.removeLink( 'histo_analysis', 'mri_corrected' )
  eNode.GreyWhiteClassification.removeLink( 'split_mask', 'mri_corrected' )
  eNode.GreyWhiteClassification.removeLink( 'edges', 'mri_corrected' )
  eNode.GreyWhiteClassification.removeLink( 'commissure_coordinates', 'mri_corrected' )

  eNode.addDoubleLink( 'GreyWhiteClassification.mri_corrected',
                       'BiasCorrection.t1mri_nobias' )
  eNode.addDoubleLink( 'GreyWhiteClassification.histo_analysis',
                       'HistoAnalysis.histo_analysis' )
  eNode.addDoubleLink( 'GreyWhiteClassification.split_mask',
                       'SplitBrain.split_brain' )
  eNode.addDoubleLink( 'GreyWhiteClassification.edges',
                       'BiasCorrection.edges' )
  eNode.addDoubleLink( 'GreyWhiteClassification.commissure_coordinates',
                       'PrepareSubject.commissure_coordinates' )


  eNode.GreyWhiteSurface.removeLink( 'histo_analysis', 'mri_corrected' )
  eNode.GreyWhiteSurface.removeLink( 'left_grey_white', 'mri_corrected' )
  eNode.GreyWhiteSurface.removeLink( 'right_grey_white', 'mri_corrected' )

  eNode.addDoubleLink( 'GreyWhiteSurface.mri_corrected',
                       'BiasCorrection.t1mri_nobias' )
  eNode.addDoubleLink( 'GreyWhiteSurface.histo_analysis',
                       'HistoAnalysis.histo_analysis' )
  eNode.addDoubleLink( 'GreyWhiteSurface.left_grey_white',
                       'GreyWhiteClassification.left_grey_white' )
  eNode.addDoubleLink( 'GreyWhiteSurface.right_grey_white',
                       'GreyWhiteClassification.right_grey_white' )

  eNode.HemispheresMesh.removeLink( 'split_mask', 'mri_corrected' )
  eNode.HemispheresMesh.removeLink( 'left_hemi_cortex', 'split_mask' )
  eNode.HemispheresMesh.removeLink( 'right_hemi_cortex', 'left_hemi_cortex' )

  eNode.addLink( 'HemispheresMesh.mri_corrected',
                 'BiasCorrection.t1mri_nobias' )
  eNode.addLink( 'BiasCorrection.t1mri_nobias',
                 'HemispheresMesh.mri_corrected' )

  eNode.addLink( 'HemispheresMesh.split_mask',
                 'SplitBrain.split_brain' )
  eNode.addLink( 'SplitBrain.split_brain',
                 'HemispheresMesh.split_mask' )

  eNode.addDoubleLink( 'HemispheresMesh.left_hemi_cortex',
                       'GreyWhiteSurface.left_hemi_cortex' )

  eNode.addDoubleLink( 'HemispheresMesh.right_hemi_cortex',
                       'GreyWhiteSurface.right_hemi_cortex' )


  eNode.HeadMesh.removeLink( 'histo_analysis', 't1mri_nobias' )

  eNode.addLink( 'HeadMesh.t1mri_nobias',
                 'BiasCorrection.t1mri_nobias' )
  eNode.addLink( 'BiasCorrection.t1mri_nobias',
                 'HeadMesh.t1mri_nobias' )

  eNode.addLink( 'HeadMesh.histo_analysis',
                 'HistoAnalysis.histo_analysis' )
  eNode.addLink( 'HistoAnalysis.histo_analysis',
                 'HeadMesh.histo_analysis' )


  eNode.CorticalFoldsGraph.removeLink( 'split_mask', 'mri_corrected' )
  eNode.CorticalFoldsGraph.removeLink( 'commissure_coordinates',
                                       'mri_corrected' )
  eNode.CorticalFoldsGraph.removeLink( 'Talairach_transform', 'split_mask' )
  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.\
    removeLink( 'hemi_cortex', 'split_mask' )
  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.\
    removeLink( 'hemi_cortex', 'side' )
  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.\
    removeLink('hemi_cortex', 'split_mask' )
  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.\
    removeLink( 'hemi_cortex', 'side' )
  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.clearLinksTo('GW_interface')
  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.clearLinksTo('white_mesh')
  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.clearLinksTo('hemi_mesh')
  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.clearLinksTo('GW_interface')
  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.clearLinksTo('white_mesh')
  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.clearLinksTo('hemi_mesh')
  
  eNode.addLink( 'CorticalFoldsGraph.mri_corrected',
                 'BiasCorrection.t1mri_nobias' )
  eNode.addLink( 'BiasCorrection.t1mri_nobias',
                 'CorticalFoldsGraph.mri_corrected' )

  eNode.addLink( 'CorticalFoldsGraph.split_mask',
                 'SplitBrain.split_brain' )
  eNode.addLink( 'SplitBrain.split_brain',
                 'CorticalFoldsGraph.split_mask' )

  eNode.addLink( 'CorticalFoldsGraph.commissure_coordinates',
                 'PrepareSubject.commissure_coordinates' )
  eNode.addLink( 'PrepareSubject.commissure_coordinates',
                 'CorticalFoldsGraph.commissure_coordinates' )

  eNode.addLink( 'CorticalFoldsGraph.Talairach_transform',
                 'TalairachTransformation.Talairach_transform' )
  eNode.addLink( 'TalairachTransformation.Talairach_transform',
                 'CorticalFoldsGraph.Talairach_transform' )

  eNode.addLink( 'CorticalFoldsGraph.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.hemi_cortex',
                 'HemispheresMesh.left_hemi_cortex' )
  eNode.addLink( 'HemispheresMesh.left_hemi_cortex',
                 'CorticalFoldsGraph.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.hemi_cortex' )

  eNode.addLink( 'CorticalFoldsGraph.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.hemi_cortex',
                 'HemispheresMesh.right_hemi_cortex' )
  eNode.addLink( 'HemispheresMesh.right_hemi_cortex',
                 'CorticalFoldsGraph.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.hemi_cortex' )
  
  eNode.addLink( 'CorticalFoldsGraph.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.GW_interface', 'GreyWhiteClassification.left_grey_white' )
  eNode.addLink( 'CorticalFoldsGraph.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.white_mesh', 'GreyWhiteSurface.left_white_mesh' )
  eNode.addLink( 'CorticalFoldsGraph.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.hemi_mesh', 'HemispheresMesh.left_hemi_mesh' )
  eNode.addLink( 'CorticalFoldsGraph.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.GW_interface', 'GreyWhiteClassification.right_grey_white')
  eNode.addLink( 'CorticalFoldsGraph.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.white_mesh', 'GreyWhiteSurface.right_white_mesh' )
  eNode.addLink( 'CorticalFoldsGraph.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.hemi_mesh', 'HemispheresMesh.right_hemi_mesh' )


  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_0.LeftCorticalFoldsGraph_3_0.\
    removeLink( 'hemi_cortex', 'split_mask' )
  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_0.LeftCorticalFoldsGraph_3_0.\
    removeLink( 'hemi_cortex', 'side' )
  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_0.RightCorticalFoldsGraph_3_0.\
    removeLink('hemi_cortex', 'split_mask' )
  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_0.RightCorticalFoldsGraph_3_0.\
    removeLink( 'hemi_cortex', 'side' )
  
  eNode.addLink( \
    'CorticalFoldsGraph.CorticalFoldsGraph_3_0.LeftCorticalFoldsGraph_3_0.hemi_cortex',
    'HemispheresMesh.left_hemi_cortex' )
  eNode.addLink( \
    'HemispheresMesh.left_hemi_cortex',
    'CorticalFoldsGraph.CorticalFoldsGraph_3_0.LeftCorticalFoldsGraph_3_0.hemi_cortex' )

  eNode.addLink( \
    'CorticalFoldsGraph.CorticalFoldsGraph_3_0.RightCorticalFoldsGraph_3_0.hemi_cortex',
    'HemispheresMesh.right_hemi_cortex' )
  eNode.addLink( \
    'HemispheresMesh.right_hemi_cortex',
    'CorticalFoldsGraph.CorticalFoldsGraph_3_0.RightCorticalFoldsGraph_3_0.hemi_cortex' )

  if reco:
    eNode.removeLink( 'SulciRecognition.right_data_graph',
        'SulciRecognition.left_data_graph' )
    eNode.addLink( 'SulciRecognition.left_data_graph',
        'CorticalFoldsGraph.left_graph' )
    eNode.addLink( 'CorticalFoldsGraph.left_graph',
        'SulciRecognition.left_data_graph' )
    eNode.addLink( 'SulciRecognition.right_data_graph',
        'CorticalFoldsGraph.right_graph' )
    eNode.addLink( 'CorticalFoldsGraph.right_graph',
        'SulciRecognition.right_data_graph' )

    eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.side = 'Left'
    eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.side = 'Right'
    eNode.SulciRecognition._selectionChange.add( linkCheckModels( self ) )

  if len( list( eNode.PrepareSubject.executionNode().children() ) ) == 1:
    self.perform_normalization = False
    self.signature[ 'perform_normalization' ].userLevel = 3
  if not hasattr( eNode.PrepareSubject, 'StandardACPC' ) \
    or not eNode.PrepareSubject.StandardACPC.isSelected():
    eNode.TalairachTransformation.setSelected( False )
    self.perform_normalization = True
  else:
    self.perform_normalization = False
  x = changeTalairach( self )
  if hasattr( eNode.PrepareSubject, 'StandardACPC' ):
    eNode.PrepareSubject.StandardACPC._selectionChange.add( x )
  self.linkParameters( 'Normalised', 'perform_normalization', changeNormalize )

  self.setExecutionNode( eNode )

  # just for now, still stick with AC/PC for test and compatibility
  self.perform_normalization = False
  changeNormalize( self, self )
