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

name = 'T1 Pipeline 2007'
userLevel = 0

signature = Signature(
  'mri', ReadDiskItem( "Raw T1 MRI", shfjGlobals.vipVolumeFormats ),
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
    self.proc = proc
  def __call__( self, node ):
    if node.isSelected():
      self.proc.executionNode().TalairachTransformation.setSelected( True )
      self.proc.perform_normalization = False
    else:
      self.proc.executionNode().TalairachTransformation.setSelected( False )
      self.proc.perform_normalization = True


def initialization( self ):
  def changeNormalize( self, proc ):
    eNode = self.executionNode()
    if len( list( eNode.PrepareSubject.executionNode().children() ) ) > 1:
      s = eNode.PrepareSubject.StandardACPC.isSelected()
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
                  ProcessExecutionNode( 'acpcOrNormalization', optional = 1 ) )


  eNode.addChild( 'BiasCorrection',
                  ProcessExecutionNode( 'T1BiasCorrectionGeneral',
                                        optional = 1 ) )

  eNode.addChild( 'HistoAnalysis',
                   ProcessExecutionNode( 'HistoAnalysisGeneral',
                                         optional = 1 ) )

  eNode.addChild( 'BrainSegmentation',
                   ProcessExecutionNode( 'BrainSegmentationGeneral',
                                         optional = 1 ) )

  eNode.addChild( 'SplitBrain',
                   ProcessExecutionNode( 'SplitBrainGeneral', optional = 1 ) )

  eNode.addChild( 'TalairachTransformation',
                   ProcessExecutionNode( 'TalairachTransformation',
                                         optional = 1 ) )

  eNode.addChild( 'GreyWhiteInterface',
                   ProcessExecutionNode( 'GreyWhiteInterfaceGeneral',
                                         optional = 1 ) )

  eNode.addChild( 'HemispheresMesh',
                  ProcessExecutionNode( 'AnaGetOpenedHemiSurface',
                                        optional = 1 ) )

  eNode.addChild( 'HeadMesh', ProcessExecutionNode( 'headMesh',
                                                    optional = 1 ) )

  eNode.addChild( 'CorticalFoldsGraph',
                  ProcessExecutionNode( 'CorticalFoldsGraphGeneral',
                                        optional = 1 ) )


  reco = getProcess( 'recognitionGeneral' )
  if reco:
    # these recognition processes are part of the sulci toolbox and are
    # not necessarily present.
    eNode2 = ProcessExecutionNode( 'recognitionGeneral', optional = 1 )
    eNode3 = ProcessExecutionNode( 'recognitionGeneral', optional = 1 )
    eNode1 = ParallelExecutionNode( 'SulciRecognition', optional = 1, selected=0  )
    eNode1.addChild( 'LeftSulciRecognition', eNode2 )
    eNode1.addChild( 'RightSulciRecognition', eNode3 )
    eNode.addChild( 'SulciRecognition', eNode1 )

  # links

  eNode.addLink( 'PrepareSubject.T1mri', 'mri' )
  eNode.addLink( 'mri', 'PrepareSubject.T1mri' )

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



  #eNode.BiasCorrection.removeLink( 'mri_corrected', 'mri' )
  eNode.addLink( 'BiasCorrection.mri', 'mri' )
  eNode.addLink( 'mri', 'BiasCorrection.mri' )
  eNode.addLink( 'BiasCorrection.mri_corrected', 'mri_corrected' )
  eNode.addLink( 'mri_corrected', 'BiasCorrection.mri_corrected' )


  eNode.HistoAnalysis.removeLink( 'hfiltered', 'mri_corrected' )
  eNode.HistoAnalysis.removeLink( 'white_ridges', 'mri_corrected' )

  eNode.addLink( 'HistoAnalysis.mri_corrected',
                 'BiasCorrection.mri_corrected' )
  eNode.addLink( 'BiasCorrection.mri_corrected',
                 'HistoAnalysis.mri_corrected' )

  eNode.addLink( 'HistoAnalysis.hfiltered', 'BiasCorrection.hfiltered' )
  eNode.addLink( 'HistoAnalysis.white_ridges', 'BiasCorrection.white_ridges' )


  eNode.BrainSegmentation.removeLink( 'histo_analysis', 'mri_corrected' )
  eNode.BrainSegmentation.removeLink( 'Commissure_coordinates',
                                      'mri_corrected' )
  eNode.BrainSegmentation.removeLink( 'white_ridges', 'mri_corrected' )

  eNode.addLink( 'BrainSegmentation.mri_corrected',
                 'BiasCorrection.mri_corrected' )
  eNode.addLink( 'BiasCorrection.mri_corrected',
                 'BrainSegmentation.mri_corrected' )

  eNode.addLink( 'BrainSegmentation.histo_analysis',
                 'HistoAnalysis.histo_analysis' )
  eNode.addLink( 'HistoAnalysis.histo_analysis',
                 'BrainSegmentation.histo_analysis' )

  eNode.addLink( 'BrainSegmentation.Commissure_coordinates',
                 'PrepareSubject.Commissure_coordinates' )
  eNode.addLink( 'PrepareSubject.Commissure_coordinates',
                 'BrainSegmentation.Commissure_coordinates' )

  eNode.addLink( 'BrainSegmentation.white_ridges',
                 'BiasCorrection.white_ridges' )
  eNode.addLink( 'BiasCorrection.white_ridges',
                 'BrainSegmentation.white_ridges' )


  eNode.SplitBrain.removeLink( 'histo_analysis', 'mri_corrected' )
  eNode.SplitBrain.removeLink( 'brain_mask', 'histo_analysis' )
  eNode.SplitBrain.removeLink( 'commissure_coordinates', 'mri_corrected' )
  eNode.SplitBrain.removeLink( 'white_ridges', 'mri_corrected' )

  eNode.addLink( 'SplitBrain.mri_corrected',
                 'BiasCorrection.mri_corrected' )
  eNode.addLink( 'BiasCorrection.mri_corrected',
                 'SplitBrain.mri_corrected' )

  eNode.addLink( 'SplitBrain.histo_analysis',
                 'HistoAnalysis.histo_analysis' )
  eNode.addLink( 'HistoAnalysis.histo_analysis',
                 'SplitBrain.histo_analysis' )

  eNode.addLink( 'SplitBrain.brain_mask',
                 'BrainSegmentation.brain_mask' )
  eNode.addLink( 'BrainSegmentation.brain_mask',
                 'SplitBrain.brain_mask' )

  eNode.addLink( 'SplitBrain.commissure_coordinates',
                 'PrepareSubject.Commissure_coordinates' )
  eNode.addLink( 'PrepareSubject.Commissure_coordinates',
                 'SplitBrain.commissure_coordinates' )

##  eNode.addLink( 'SplitBrain.use_ridges',
##                 'BiasCorrection.write_wridges' )
##  eNode.addLink( 'BiasCorrection.write_wridges',
##                 'SplitBrain.use_ridges' )

  eNode.addLink( 'SplitBrain.white_ridges',
                 'BiasCorrection.white_ridges' )
  eNode.addLink( 'BiasCorrection.white_ridges',
                 'SplitBrain.white_ridges' )


  eNode.TalairachTransformation.removeLink( 'Commissure_coordinates',
                                            'split_mask' )

  eNode.addLink( 'TalairachTransformation.split_mask',
                 'SplitBrain.split_mask' )
  eNode.addLink( 'SplitBrain.split_mask',
                 'TalairachTransformation.split_mask' )

  eNode.addLink( 'TalairachTransformation.Commissure_coordinates',
                 'PrepareSubject.Commissure_coordinates' )
  eNode.addLink( 'PrepareSubject.Commissure_coordinates',
                 'TalairachTransformation.Commissure_coordinates' )


  eNode.GreyWhiteInterface.removeLink( 'histo_analysis', 'mri_corrected' )
  eNode.GreyWhiteInterface.removeLink( 'split_mask', 'histo_analysis' )
  eNode.GreyWhiteInterface.removeLink( 'white_ridges', 'mri_corrected' )

  eNode.addLink( 'GreyWhiteInterface.mri_corrected',
                 'BiasCorrection.mri_corrected' )
  eNode.addLink( 'BiasCorrection.mri_corrected',
                 'GreyWhiteInterface.mri_corrected' )

  eNode.addLink( 'GreyWhiteInterface.histo_analysis',
                 'HistoAnalysis.histo_analysis' )
  eNode.addLink( 'HistoAnalysis.histo_analysis',
                 'GreyWhiteInterface.histo_analysis' )

  eNode.addLink( 'GreyWhiteInterface.split_mask',
                 'SplitBrain.split_mask' )
  eNode.addLink( 'SplitBrain.split_mask',
                 'GreyWhiteInterface.split_mask' )

##  eNode.addLink( 'SplitBrain.use_ridges',
##                 'BiasCorrection.write_wridges' )
##  eNode.addLink( 'BiasCorrection.write_wridges',
##                 'SplitBrain.use_ridges' )

  eNode.addLink( 'GreyWhiteInterface.white_ridges',
                 'BiasCorrection.white_ridges' )
  eNode.addLink( 'BiasCorrection.white_ridges',
                 'GreyWhiteInterface.white_ridges' )


  eNode.HemispheresMesh.removeLink( 'histo_analysis', 'mri_corrected' )
  eNode.HemispheresMesh.removeLink( 'brain_voronoi', 'histo_analysis' )

  eNode.addLink( 'HemispheresMesh.mri_corrected',
                 'BiasCorrection.mri_corrected' )
  eNode.addLink( 'BiasCorrection.mri_corrected',
                 'HemispheresMesh.mri_corrected' )

  eNode.addLink( 'HemispheresMesh.histo_analysis',
                 'HistoAnalysis.histo_analysis' )
  eNode.addLink( 'HistoAnalysis.histo_analysis',
                 'HemispheresMesh.histo_analysis' )

  eNode.addLink( 'HemispheresMesh.brain_voronoi',
                 'SplitBrain.split_mask' )
  eNode.addLink( 'SplitBrain.split_mask',
                 'HemispheresMesh.brain_voronoi' )


  eNode.HeadMesh.removeLink( 'histo_analysis', 'mri_corrected' )

  eNode.addLink( 'HeadMesh.mri_corrected',
                 'BiasCorrection.mri_corrected' )
  eNode.addLink( 'BiasCorrection.mri_corrected',
                 'HeadMesh.mri_corrected' )

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
                 'BiasCorrection.mri_corrected' )
  eNode.addLink( 'BiasCorrection.mri_corrected',
                 'CorticalFoldsGraph.mri_corrected' )

  eNode.addLink( 'CorticalFoldsGraph.split_mask',
                 'SplitBrain.split_mask' )
  eNode.addLink( 'SplitBrain.split_mask',
                 'CorticalFoldsGraph.split_mask' )

  eNode.addLink( 'CorticalFoldsGraph.commissure_coordinates',
                 'PrepareSubject.Commissure_coordinates' )
  eNode.addLink( 'PrepareSubject.Commissure_coordinates',
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
  
  eNode.addLink( 'CorticalFoldsGraph.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.GW_interface', 'GreyWhiteInterface.LGW_interface' )
  eNode.addLink( 'CorticalFoldsGraph.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.white_mesh', 'GreyWhiteInterface.left_white_mesh' )
  eNode.addLink( 'CorticalFoldsGraph.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.hemi_mesh', 'HemispheresMesh.left_hemi_mesh' )
  eNode.addLink( 'CorticalFoldsGraph.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.GW_interface', 'GreyWhiteInterface.RGW_interface')
  eNode.addLink( 'CorticalFoldsGraph.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.white_mesh', 'GreyWhiteInterface.right_white_mesh' )
  eNode.addLink( 'CorticalFoldsGraph.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.CorticalFoldsGraphThickness.hemi_mesh', 'HemispheresMesh.right_hemi_mesh' )


  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_0.clearLinksTo( \
    'histo_analysis' )
  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_0.clearLinksTo( \
    'left_hemi_cortex' )
  eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_0.clearLinksTo( \
    'right_hemi_cortex' )

  eNode.addLink( 'CorticalFoldsGraph.CorticalFoldsGraph_3_0.histo_analysis', 'HistoAnalysis.histo_analysis' )
  eNode.addLink( 'HistoAnalysis.histo_analysis', 'CorticalFoldsGraph.CorticalFoldsGraph_3_0.histo_analysis' )
  
  eNode.addLink( \
    'CorticalFoldsGraph.CorticalFoldsGraph_3_0.left_hemi_cortex',
    'HemispheresMesh.left_hemi_cortex' )
  eNode.addLink( \
    'HemispheresMesh.left_hemi_cortex',
    'CorticalFoldsGraph.CorticalFoldsGraph_3_0.left_hemi_cortex' )

  eNode.addLink( \
    'CorticalFoldsGraph.CorticalFoldsGraph_3_0.right_hemi_cortex',
    'HemispheresMesh.right_hemi_cortex' )
  eNode.addLink( \
    'HemispheresMesh.right_hemi_cortex',
    'CorticalFoldsGraph.CorticalFoldsGraph_3_0.right_hemi_cortex' )


  if reco:
    eNode.addLink( 'SulciRecognition.LeftSulciRecognition.data_graph',
                  'CorticalFoldsGraph.left_graph' )
    eNode.addLink( 'CorticalFoldsGraph.left_graph',
                  'SulciRecognition.LeftSulciRecognition.data_graph' )
  
    eNode.addLink( 'SulciRecognition.RightSulciRecognition.data_graph',
                  'CorticalFoldsGraph.right_graph' )
    eNode.addLink( 'CorticalFoldsGraph.right_graph',
                  'SulciRecognition.RightSulciRecognition.data_graph' )


    eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.side = 'Left'
    eNode.CorticalFoldsGraph.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.side = 'Right'

  if len( list( eNode.PrepareSubject.executionNode().children() ) ) == 1:
    self.perform_normalization = False
    self.signature[ 'perform_normalization' ].userLevel = 3
  if not eNode.PrepareSubject.StandardACPC.isSelected():
    eNode.TalairachTransformation.setSelected( False )
    self.perform_normalization = True
  else:
    self.perform_normalization = False
  x = changeTalairach( self )
  eNode.PrepareSubject.StandardACPC._selectionChange.add( x )
  self.linkParameters( 'Normalised', 'perform_normalization', changeNormalize )

  self.setExecutionNode( eNode )

  # just for now, still stick with AC/PC for test and compatibility
  self.perform_normalization = False
  changeNormalize( self, self )
