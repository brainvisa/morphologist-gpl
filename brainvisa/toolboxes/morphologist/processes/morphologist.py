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

name = 'Morphologist 2015'
userLevel = 0

signature = Signature(
    't1mri', ReadDiskItem( 'Raw T1 MRI',
        'Aims readable volume formats' ),
    'perform_normalization', Boolean(),
    'anterior_commissure', Point3D(),
    'posterior_commissure', Point3D(),
    'interhemispheric_point', Point3D(),
    'left_hemisphere_point', Point3D(),
    't1mri_nobias', WriteDiskItem( 'T1 MRI Bias Corrected',
        'Aims writable volume formats' ),
    'histo_analysis', WriteDiskItem( 'Histo Analysis', 'Histo Analysis' ),
    'split_brain', WriteDiskItem( 'Split Brain Mask',
        'Aims writable volume formats' ),
    'left_graph', WriteDiskItem( 'Left Cortical Folds Graph',
        'Graph', requiredAttributes = {'labelled':'No', 'side':'left'} ),
    'right_graph', WriteDiskItem( 'Right Cortical Folds Graph',
        'Graph', requiredAttributes = {'labelled':'No', 'side':'right'} ),
    'perform_sulci_recognition', Boolean(),
    'left_labelled_graph', WriteDiskItem( 'Labelled Cortical Folds Graph',
        'Graph', requiredAttributes = {'labelled':'Yes', 'side':'left'} ),
    'right_labelled_graph', WriteDiskItem( 'Labelled Cortical Folds Graph',
        'Graph', requiredAttributes = {'labelled':'Yes', 'side':'right'} ),
)


class changeTalairach:
    def __init__( self, proc ):
        self.proc = weakref.proxy( proc )
    def __call__( self, node ):
        if node.isSelected():
            self.proc.executionNode().TalairachTransformation.setSelected( True )
            self.proc.executionNode().Renorm.setSelected(False)
            self.proc.perform_normalization = False
        else:
            self.proc.executionNode().TalairachTransformation.setSelected( False )
            self.proc.executionNode().Renorm.setSelected(True)
            self.proc.perform_normalization = True

class linkCheckModels:
    spamModelsChecked = False

    def __init__( self, proc ):
        self.proc = weakref.proxy( proc )

    def __call__( self, node ):
        eNode = self.proc.executionNode().HemispheresProcessing
        if eNode.LeftHemisphere.SulciRecognition.isSelected() == eNode.RightHemisphere.SulciRecognition.isSelected():
            self.proc.perform_sulci_recognition = eNode.LeftHemisphere.SulciRecognition.isSelected()
        if not linkCheckModels.spamModelsChecked:
            if eNode.LeftHemisphere.SulciRecognition.isSelected() \
                or eNode.RightHemisphere.SulciRecognition.isSelected():
                proc = getProcessInstance( 'check_spam_models' )
                linkCheckModels.spamModelsChecked = True
                if proc:
                    defaultContext().runProcess( proc )


def initialization( self ):
    def changeNormalize( enabled, names, parameterized ):
        eNode = parameterized[0].executionNode()
        if len( list( eNode.PrepareSubject.executionNode().children() ) ) > 1:
            if hasattr( eNode.PrepareSubject, 'StandardACPC' ):
                s = eNode.PrepareSubject.StandardACPC.isSelected()
            else:
                s = False
            if s == parameterized[0].perform_normalization:
                y = list(eNode.PrepareSubject.executionNode().children())
                y[0].setSelected( not self.perform_normalization )
                y[1].setSelected( self.perform_normalization )
                eNode.Renorm.setSelected( self.perform_normalization )

    def enableRecognition( enabled, names, parameterized ):
        '''Select appropriate sub-processes when recognition is switched from
        the main pipeline option'''
        eNode = parameterized[0].executionNode().HemispheresProcessing
        eNode.LeftHemisphere.SulciRecognition.setSelected( enabled )
        eNode.RightHemisphere.SulciRecognition.setSelected( enabled )

    # Architecture of the Pipeline
    eNode = SerialExecutionNode( self.name, parameterized=self )

    eNode.addChild( 'PrepareSubject',
                    ProcessExecutionNode( 'acpcOrNormalization',
                                          optional = 1,
                                          altname = _t_('Image orientation handling') ) )
    eNode.addChild( 'BiasCorrection',
                    ProcessExecutionNode( 'T1BiasCorrection',
                                          optional = 1 ) )
    eNode.addChild( 'HistoAnalysis',
                    ProcessExecutionNode( 'NobiasHistoAnalysis',
                                          optional = 1 ) )
    eNode.addChild( 'BrainSegmentation',
                    ProcessExecutionNode( 'BrainSegmentation',
                                          optional = 1 ) )

        ## Re-Normalization
    hasNorm = False
    try :
        p = getProcessInstance( 'normalization_skullstripped' )
        if p:
            p.validationDelayed()
            hasNorm = True
            print hasNorm
    except:
        pass
    if hasNorm:
        eNode.addChild( 'Renorm',
                        ProcessExecutionNode( p, optional = 1 ) )

    eNode.addChild( 'SplitBrain',
                    ProcessExecutionNode( 'SplitBrain',
                                          optional = 1 ) )
    eNode.addChild( 'TalairachTransformation',
                    ProcessExecutionNode( 'TalairachTransformation',
                                          optional = 1 ) )
    eNode.addChild( 'HeadMesh',
                    ProcessExecutionNode( 'headMesh',
                                          optional = 1 ) )

    hemiProc = ParallelExecutionNode( 'Hemispheres Processing',
                                      optional = True,
                                      expandedInGui = True )

    eNode.addChild( 'HemispheresProcessing', hemiProc )

    leftNode = SerialExecutionNode( 'Left hemisphere',
                                    optional = True,
                                    expandedInGui = True )
    rightNode = SerialExecutionNode( 'Right hemisphere',
                                     optional = True,
                                     expandedInGui = True )

    hemiProc.addChild( 'LeftHemisphere', leftNode )
    hemiProc.addChild( 'RightHemisphere', rightNode )

    leftNode.addChild( 'GreyWhiteClassification',
                       ProcessExecutionNode( 'GreyWhiteClassificationHemi',
                                             optional = 1,
                                             altname = _t_('Grey White Classification') ) )
    leftNode.GreyWhiteClassification.side = 'left'
    leftNode.GreyWhiteClassification.signature[ 'side' ].userLevel = 3
    rightNode.addChild( 'GreyWhiteClassification',
                        ProcessExecutionNode( 'GreyWhiteClassificationHemi',
                                              optional = 1,
                                              altname = _t_('Grey White Classification') ) )
    rightNode.GreyWhiteClassification.side = 'right'
    rightNode.GreyWhiteClassification.signature[ 'side' ].userLevel = 3
    leftNode.addChild( 'GreyWhiteTopology',
                       ProcessExecutionNode( 'GreyWhiteTopology',
                                             optional = 1,
                                             altname = _t_('Grey White Topology Correction') ) )
    rightNode.addChild( 'GreyWhiteTopology',
                        ProcessExecutionNode( 'GreyWhiteTopology',
                                              optional = 1,
                                              altname = _t_('Grey White Topology Correction') ) )
    leftNode.addChild( 'GreyWhiteMesh',
                       ProcessExecutionNode( 'GreyWhiteMesh',
                                             optional = 1,
                                             altname = _t_('Grey White Mesh') ) )
    rightNode.addChild( 'GreyWhiteMesh',
                        ProcessExecutionNode( 'GreyWhiteMesh',
                                              optional = 1,
                                              altname = _t_('Grey White Mesh') ) )
    leftNode.addChild( 'SulciSkeleton',
                       ProcessExecutionNode( 'sulciskeleton',
                                             optional = 1,
                                             altname = _t_('Sulci Skeleton and Roots') ) )
    rightNode.addChild( 'SulciSkeleton',
                        ProcessExecutionNode( 'sulciskeleton',
                                             optional = 1,
                                             altname = _t_('Sulci Skeleton and Roots') ) )
    leftNode.addChild( 'PialMesh',
                       ProcessExecutionNode( 'hemispheremesh',
                                             optional = 1,
                                             altname = _t_('Pial Mesh') ) )
    rightNode.addChild( 'PialMesh',
                        ProcessExecutionNode( 'hemispheremesh',
                                             optional = 1,
                                             altname = _t_('Pial Mesh') ) )
    leftNode.addChild( 'CorticalFoldsGraph',
                        ProcessExecutionNode( 'corticalfoldsgraph',
                                              optional = 1,
                                              altname = _t_('Cortical Folds Graph') ) )
    rightNode.addChild( 'CorticalFoldsGraph',
                        ProcessExecutionNode( 'corticalfoldsgraph',
                                              optional = 1,
                                              altname = _t_('Cortical Folds Graph') ) )

    reco = getProcess('recognitionGeneral')
    if reco:
        leftNode.addChild( 'SulciRecognition',
                        ProcessExecutionNode( 'recognitionGeneral',
                                              optional = 1, selected = 0 ) )
        rightNode.addChild( 'SulciRecognition',
                        ProcessExecutionNode( 'recognitionGeneral',
                                              optional = 1, selected = 0 ) )

    # Links
    ## Commissures Coordinates
    eNode.addDoubleLink( 'PrepareSubject.T1mri', 't1mri' )

    if hasattr( eNode.PrepareSubject, 'StandardACPC' ):
        eNode.addDoubleLink( 'PrepareSubject.StandardACPC.Anterior_Commissure',
                             'anterior_commissure' )
        eNode.addDoubleLink( 'PrepareSubject.StandardACPC.Posterior_Commissure',
                             'posterior_commissure' )
        eNode.addDoubleLink( 'PrepareSubject.StandardACPC.Interhemispheric_Point',
                             'interhemispheric_point' )
        eNode.addDoubleLink( 'PrepareSubject.StandardACPC.Left_Hemisphere_Point',
                             'left_hemisphere_point' )

    self.setOptional( 'anterior_commissure' )
    self.setOptional( 'posterior_commissure' )
    self.setOptional( 'interhemispheric_point' )
    self.setOptional( 'left_hemisphere_point' )

    self.signature[ 'anterior_commissure' ].add3DLink( self, 'mri' )
    self.signature[ 'posterior_commissure' ].add3DLink( self, 'mri' )
    self.signature[ 'interhemispheric_point' ].add3DLink( self, 'mri' )
    self.signature[ 'left_hemisphere_point' ].add3DLink( self, 'mri' )

    ## Bias Correction
    eNode.BiasCorrection.removeLink( 'commissure_coordinates', 't1mri' )
    eNode.addDoubleLink('BiasCorrection.t1mri',
                        'PrepareSubject.reoriented_t1mri')
    eNode.addDoubleLink( 'BiasCorrection.commissure_coordinates',
      'PrepareSubject.commissure_coordinates' )
    eNode.addDoubleLink( 'BiasCorrection.t1mri_nobias', 't1mri_nobias' )

    ## Histogram Analysis
    eNode.HistoAnalysis.removeLink( 'hfiltered', 't1mri_nobias' )
    eNode.HistoAnalysis.removeLink( 'white_ridges', 't1mri_nobias' )

    eNode.addDoubleLink( 'HistoAnalysis.t1mri_nobias',
                         'BiasCorrection.t1mri_nobias' )
    eNode.addLink( 'HistoAnalysis.hfiltered', 'BiasCorrection.hfiltered' )
    eNode.addLink( 'HistoAnalysis.white_ridges', 'BiasCorrection.white_ridges' )
    eNode.addDoubleLink( 'HistoAnalysis.histo_analysis', 'histo_analysis' )

    ## Brain Segmentation
    eNode.BrainSegmentation.removeLink( 'histo_analysis', 't1mri_nobias' )
    eNode.BrainSegmentation.removeLink( 'commissure_coordinates', 't1mri_nobias' )
    eNode.BrainSegmentation.removeLink( 'white_ridges', 't1mri_nobias' )
    eNode.BrainSegmentation.removeLink( 'variance', 't1mri_nobias' )
    eNode.BrainSegmentation.removeLink( 'edges', 't1mri_nobias' )

    eNode.addDoubleLink( 'BrainSegmentation.t1mri_nobias',
                         'BiasCorrection.t1mri_nobias' )
    eNode.addDoubleLink( 'BrainSegmentation.histo_analysis',
                         'HistoAnalysis.histo_analysis' )
    eNode.addDoubleLink( 'BrainSegmentation.commissure_coordinates',
                         'PrepareSubject.commissure_coordinates' )
    eNode.addDoubleLink( 'BrainSegmentation.white_ridges',
                         'BiasCorrection.white_ridges' )
    eNode.addDoubleLink( 'BrainSegmentation.variance',
                         'BiasCorrection.variance' )
    eNode.addDoubleLink( 'BrainSegmentation.edges',
                         'BiasCorrection.edges' )

    ## Re-Normalization
    if hasNorm:
        eNode.Renorm.removeLink( 'brain_mask', 't1mri' )
        eNode.Renorm.removeLink( 'transformation', 't1mri' )
        eNode.Renorm.removeLink( 'talairach_transformation', 't1mri' )
        eNode.Renorm.TalairachFromNormalization.removeLink(
            'commissure_coordinates', 'Talairach_transform')

        eNode.addDoubleLink( 'Renorm.t1mri', 't1mri' )
        eNode.addDoubleLink( 'Renorm.brain_mask',
                             'BrainSegmentation.brain_mask' )
        eNode.addDoubleLink('Renorm.transformation',
            'PrepareSubject.Normalization.Normalization.transformation')
        eNode.addDoubleLink('Renorm.talairach_transformation',
            'PrepareSubject.Normalization.TalairachFromNormalization.Talairach_transform')
        eNode.addDoubleLink(
            'Renorm.TalairachFromNormalization.commissure_coordinates',
            'PrepareSubject.commissure_coordinates')

    ## Split Brain
    eNode.SplitBrain.removeLink( 't1mri_nobias', 'brain_mask' )
    eNode.SplitBrain.removeLink( 'histo_analysis', 't1mri_nobias' )
    eNode.SplitBrain.removeLink( 'commissure_coordinates', 't1mri_nobias' )
    eNode.SplitBrain.removeLink( 'white_ridges', 't1mri_nobias' )

    eNode.addDoubleLink( 'SplitBrain.t1mri_nobias',
                         'BiasCorrection.t1mri_nobias' )
    eNode.addDoubleLink( 'SplitBrain.histo_analysis',
                         'HistoAnalysis.histo_analysis' )
    eNode.addDoubleLink( 'SplitBrain.brain_mask',
                         'BrainSegmentation.brain_mask' )
    eNode.addDoubleLink( 'SplitBrain.commissure_coordinates',
                         'PrepareSubject.commissure_coordinates' )
    eNode.addDoubleLink( 'SplitBrain.white_ridges',
                         'BiasCorrection.white_ridges' )
    eNode.addDoubleLink( 'SplitBrain.split_brain',
                         'split_brain' )

    ## Talairach Transformation
    eNode.TalairachTransformation.removeLink( 'commissure_coordinates', 'split_mask' )

    eNode.addDoubleLink( 'TalairachTransformation.split_mask',
                         'SplitBrain.split_brain' )
    eNode.addDoubleLink( 'TalairachTransformation.commissure_coordinates',
                         'PrepareSubject.commissure_coordinates' )

    ## Head Mesh
    eNode.HeadMesh.removeLink( 'histo_analysis', 't1mri_nobias' )

    eNode.addDoubleLink( 'HeadMesh.t1mri_nobias',
                         'BiasCorrection.t1mri_nobias' )
    eNode.addDoubleLink( 'HeadMesh.histo_analysis',
                         'HistoAnalysis.histo_analysis' )

    lhemi = 'HemispheresProcessing.LeftHemisphere'
    rhemi = 'HemispheresProcessing.RightHemisphere'

    ## Grey White Classification
    leftNode.GreyWhiteClassification.removeLink( 'histo_analysis', 't1mri_nobias' )
    leftNode.GreyWhiteClassification.removeLink( 'split_brain', 't1mri_nobias' )
    leftNode.GreyWhiteClassification.removeLink( 'edges', 't1mri_nobias' )
    leftNode.GreyWhiteClassification.removeLink( 'commissure_coordinates', 't1mri_nobias' )
    rightNode.GreyWhiteClassification.removeLink( 'histo_analysis', 't1mri_nobias' )
    rightNode.GreyWhiteClassification.removeLink( 'split_brain', 't1mri_nobias' )
    rightNode.GreyWhiteClassification.removeLink( 'edges', 't1mri_nobias' )
    rightNode.GreyWhiteClassification.removeLink( 'commissure_coordinates', 't1mri_nobias' )

    eNode.addDoubleLink( \
        lhemi + '.GreyWhiteClassification.t1mri_nobias',
        'BiasCorrection.t1mri_nobias' )
    eNode.addDoubleLink( \
        lhemi + '.GreyWhiteClassification.histo_analysis',
        'HistoAnalysis.histo_analysis' )
    eNode.addDoubleLink( \
        lhemi + '.GreyWhiteClassification.split_brain',
        'SplitBrain.split_brain' )
    eNode.addDoubleLink( \
        lhemi + '.GreyWhiteClassification.edges',
        'BiasCorrection.edges' )
    eNode.addDoubleLink( \
        lhemi + '.GreyWhiteClassification.commissure_coordinates',
        'PrepareSubject.commissure_coordinates' )
    eNode.addDoubleLink( \
        rhemi + '.GreyWhiteClassification.t1mri_nobias',
        'BiasCorrection.t1mri_nobias' )
    eNode.addDoubleLink( \
        rhemi + '.GreyWhiteClassification.histo_analysis',
        'HistoAnalysis.histo_analysis' )
    eNode.addDoubleLink( \
        rhemi + '.GreyWhiteClassification.split_brain',
        'SplitBrain.split_brain' )
    eNode.addDoubleLink( \
        rhemi + '.GreyWhiteClassification.edges',
        'BiasCorrection.edges' )
    eNode.addDoubleLink( \
        rhemi + '.GreyWhiteClassification.commissure_coordinates',
        'PrepareSubject.commissure_coordinates' )

    ## Grey White Topology
    leftNode.GreyWhiteTopology.removeLink( 't1mri_nobias', 'grey_white' )
    leftNode.GreyWhiteTopology.removeLink( 'histo_analysis', 't1mri_nobias' )
    rightNode.GreyWhiteTopology.removeLink( 't1mri_nobias', 'grey_white' )
    rightNode.GreyWhiteTopology.removeLink( 'histo_analysis', 't1mri_nobias' )

    eNode.addDoubleLink( \
        lhemi + '.GreyWhiteTopology.t1mri_nobias',
        'BiasCorrection.t1mri_nobias' )
    eNode.addDoubleLink( \
        lhemi + '.GreyWhiteTopology.histo_analysis',
        'HistoAnalysis.histo_analysis' )
    eNode.addDoubleLink( \
        lhemi + '.GreyWhiteTopology.grey_white',
        lhemi + '.GreyWhiteClassification.grey_white' )
    eNode.addDoubleLink( \
        rhemi + '.GreyWhiteTopology.t1mri_nobias',
        'BiasCorrection.t1mri_nobias' )
    eNode.addDoubleLink( \
        rhemi + '.GreyWhiteTopology.histo_analysis',
        'HistoAnalysis.histo_analysis' )
    eNode.addDoubleLink( \
        rhemi + '.GreyWhiteTopology.grey_white',
        rhemi + '.GreyWhiteClassification.grey_white' )

    ## Grey White Mesh
    eNode.addDoubleLink( \
        lhemi + '.GreyWhiteMesh.hemi_cortex',
        lhemi + '.GreyWhiteTopology.hemi_cortex' )
    eNode.addDoubleLink( \
        rhemi + '.GreyWhiteMesh.hemi_cortex',
        rhemi + '.GreyWhiteTopology.hemi_cortex' )

    ## Sulci Skeleton
    leftNode.SulciSkeleton.removeLink( 'grey_white', 'hemi_cortex' )
    leftNode.SulciSkeleton.removeLink( 't1mri_nobias', 'hemi_cortex' )
    rightNode.SulciSkeleton.removeLink( 'grey_white', 'hemi_cortex' )
    rightNode.SulciSkeleton.removeLink( 't1mri_nobias', 'hemi_cortex' )

    eNode.addDoubleLink( \
        lhemi + '.SulciSkeleton.hemi_cortex',
        lhemi + '.GreyWhiteTopology.hemi_cortex' )
    eNode.addDoubleLink( \
        lhemi + '.SulciSkeleton.grey_white',
        lhemi + '.GreyWhiteClassification.grey_white' )
    eNode.addDoubleLink( \
        lhemi + '.SulciSkeleton.t1mri_nobias',
        'BiasCorrection.t1mri_nobias' )
    eNode.addDoubleLink( \
        rhemi + '.SulciSkeleton.hemi_cortex',
        rhemi + '.GreyWhiteTopology.hemi_cortex' )
    eNode.addDoubleLink( \
        rhemi + '.SulciSkeleton.grey_white',
        rhemi + '.GreyWhiteClassification.grey_white' )
    eNode.addDoubleLink( \
        rhemi + '.SulciSkeleton.t1mri_nobias',
        'BiasCorrection.t1mri_nobias' )

    ## Pial Mesh
    leftNode.PialMesh.removeLink( 'grey_white', 'hemi_cortex' )
    leftNode.PialMesh.removeLink( 't1mri_nobias', 'hemi_cortex' )
    leftNode.PialMesh.removeLink( 'skeleton', 'hemi_cortex' )
    rightNode.PialMesh.removeLink( 'grey_white', 'hemi_cortex' )
    rightNode.PialMesh.removeLink( 't1mri_nobias', 'hemi_cortex' )
    rightNode.PialMesh.removeLink( 'skeleton', 'hemi_cortex' )

    eNode.addDoubleLink( \
        lhemi + '.PialMesh.hemi_cortex',
        lhemi + '.GreyWhiteTopology.hemi_cortex' )
    eNode.addDoubleLink( \
        lhemi + '.PialMesh.grey_white',
        lhemi + '.GreyWhiteClassification.grey_white' )
    eNode.addDoubleLink( \
        lhemi + '.PialMesh.t1mri_nobias',
        'BiasCorrection.t1mri_nobias' )
    eNode.addDoubleLink( \
        lhemi + '.PialMesh.skeleton',
        lhemi + '.SulciSkeleton.skeleton' )
    eNode.addDoubleLink( \
        rhemi + '.PialMesh.hemi_cortex',
        rhemi + '.GreyWhiteTopology.hemi_cortex' )
    eNode.addDoubleLink( \
        rhemi + '.PialMesh.grey_white',
        rhemi + '.GreyWhiteClassification.grey_white' )
    eNode.addDoubleLink( \
        rhemi + '.PialMesh.t1mri_nobias',
        'BiasCorrection.t1mri_nobias' )
    eNode.addDoubleLink( \
        rhemi + '.PialMesh.skeleton',
        rhemi + '.SulciSkeleton.skeleton' )

    ## Cortical Folds Graph
    leftNode.CorticalFoldsGraph.removeLink( 'roots', 'skeleton' )
    leftNode.CorticalFoldsGraph.removeLink( 'grey_white', 'skeleton' )
    leftNode.CorticalFoldsGraph.removeLink( 'hemi_cortex', 'grey_white' )
    leftNode.CorticalFoldsGraph.removeLink( 'split_brain', 'skeleton' )
    leftNode.CorticalFoldsGraph.removeLink( 'white_mesh', 'grey_white' )
    leftNode.CorticalFoldsGraph.removeLink( 'pial_mesh', 'white_mesh' )
    leftNode.CorticalFoldsGraph.removeLink( 'commissure_coordinates', 'grey_white' )
    leftNode.CorticalFoldsGraph.removeLink( 'talairach_transform', 'grey_white' )
    rightNode.CorticalFoldsGraph.removeLink( 'roots', 'skeleton' )
    rightNode.CorticalFoldsGraph.removeLink( 'grey_white', 'skeleton' )
    rightNode.CorticalFoldsGraph.removeLink( 'hemi_cortex', 'grey_white' )
    rightNode.CorticalFoldsGraph.removeLink( 'split_brain', 'skeleton' )
    rightNode.CorticalFoldsGraph.removeLink( 'white_mesh', 'grey_white' )
    rightNode.CorticalFoldsGraph.removeLink( 'pial_mesh', 'white_mesh' )
    rightNode.CorticalFoldsGraph.removeLink( 'commissure_coordinates', 'grey_white' )
    rightNode.CorticalFoldsGraph.removeLink( 'talairach_transform', 'grey_white' )

    eNode.addDoubleLink( \
        lhemi + '.CorticalFoldsGraph.skeleton',
        lhemi + '.SulciSkeleton.skeleton')
    eNode.addDoubleLink( \
        lhemi + '.CorticalFoldsGraph.roots',
        lhemi + '.SulciSkeleton.roots' )
    eNode.addDoubleLink( \
        lhemi + '.CorticalFoldsGraph.grey_white',
        lhemi + '.GreyWhiteClassification.grey_white')
    eNode.addDoubleLink( \
        lhemi + '.CorticalFoldsGraph.hemi_cortex',
        lhemi + '.GreyWhiteTopology.hemi_cortex' )
    eNode.addDoubleLink( 'split_brain',
        lhemi + '.CorticalFoldsGraph.split_brain' )
    eNode.addDoubleLink( \
        lhemi + '.CorticalFoldsGraph.white_mesh',
        lhemi + '.GreyWhiteMesh.white_mesh')
    eNode.addDoubleLink( \
        lhemi + '.CorticalFoldsGraph.pial_mesh',
        lhemi + '.PialMesh.pial_mesh' )
    eNode.addDoubleLink( \
        lhemi + '.CorticalFoldsGraph.commissure_coordinates',
        'PrepareSubject.commissure_coordinates' )
    eNode.addDoubleLink( \
        lhemi + '.CorticalFoldsGraph.talairach_transform',
        'TalairachTransformation.Talairach_transform' )
    eNode.addDoubleLink( \
        rhemi + '.CorticalFoldsGraph.skeleton',
        rhemi + '.SulciSkeleton.skeleton')
    eNode.addDoubleLink( \
        rhemi + '.CorticalFoldsGraph.roots',
        rhemi + '.SulciSkeleton.roots' )
    eNode.addDoubleLink( \
        rhemi + '.CorticalFoldsGraph.grey_white',
        rhemi + '.GreyWhiteClassification.grey_white')
    eNode.addDoubleLink( \
        rhemi + '.CorticalFoldsGraph.hemi_cortex',
        rhemi + '.GreyWhiteTopology.hemi_cortex' )
    eNode.addDoubleLink( 'split_brain',
        rhemi + '.CorticalFoldsGraph.split_brain' )
    eNode.addDoubleLink( \
        rhemi + '.CorticalFoldsGraph.white_mesh',
        rhemi + '.GreyWhiteMesh.white_mesh')
    eNode.addDoubleLink( \
        rhemi + '.CorticalFoldsGraph.pial_mesh',
        rhemi + '.PialMesh.pial_mesh' )
    eNode.addDoubleLink( \
        rhemi + '.CorticalFoldsGraph.commissure_coordinates',
        'PrepareSubject.commissure_coordinates' )
    eNode.addDoubleLink( \
        rhemi + '.CorticalFoldsGraph.talairach_transform',
        'TalairachTransformation.Talairach_transform' )

    eNode.addDoubleLink( \
        lhemi + '.CorticalFoldsGraph.graph_version',
        rhemi + '.CorticalFoldsGraph.graph_version' )
    eNode.addDoubleLink( lhemi + '.CorticalFoldsGraph.graph', 'left_graph' )
    eNode.addDoubleLink( rhemi + '.CorticalFoldsGraph.graph', 'right_graph' )

    ## Sulci Recognition
    if reco:
        leftNode.addDoubleLink( 'SulciRecognition.data_graph', 'CorticalFoldsGraph.graph' )
        rightNode.addDoubleLink( 'SulciRecognition.data_graph', 'CorticalFoldsGraph.graph' )
        eNode.addDoubleLink( lhemi + '.SulciRecognition.output_graph', 'left_labelled_graph' )
        eNode.addDoubleLink( rhemi + '.SulciRecognition.output_graph', 'right_labelled_graph' )

        leftNode.SulciRecognition._selectionChange.add( linkCheckModels( self ) )
        rightNode.SulciRecognition._selectionChange.add( linkCheckModels( self ) )

    self.perform_sulci_recognition = False
    self.setOptional( 'left_labelled_graph' )
    self.setOptional( 'right_labelled_graph' )

    if reco:
        eNode.addLink( None, 'perform_sulci_recognition', enableRecognition )
    else:
        self.signature[ 'perform_sulci_recognition' ].userLevel = 3
        self.signature[ 'left_labelled_graph' ].userLevel = 3
        self.signature[ 'right_labelled_graph' ].userLevel = 3

    if not hasattr( eNode.PrepareSubject, 'Normalization' ):
        self.perform_normalization = False
        self.signature[ 'perform_normalization' ].userLevel = 3
    else:
        print 'perform_normalization = True'
        self.perform_normalization = True

    x = changeTalairach( self )
    if hasattr( eNode.PrepareSubject, 'StandardACPC' ):
        eNode.PrepareSubject.StandardACPC._selectionChange.add( x )
    eNode.addLink( None, 'perform_normalization', changeNormalize )

    self.setExecutionNode( eNode )

    eNode.TalairachTransformation.setSelected( False )
