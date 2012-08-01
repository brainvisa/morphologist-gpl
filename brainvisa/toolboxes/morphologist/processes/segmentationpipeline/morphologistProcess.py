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
import shfjGlobals, registration


name = 'Simplified Morphologist'
userLevel = 2

signature = Signature(
    't1mri', ReadDiskItem( 'Raw T1 MRI',
        'Aims readable volume formats' ),
    #Commissure Coordinates
    'method_ACPC', Choice( "Manually", "SPM Normalization" ),
    'commissure_coordinates', WriteDiskItem( 'Commissure coordinates',
        'Commissure coordinates' ),
    'anterior_commissure', Point3D(),
    'posterior_commissure', Point3D(),
    'interhemispheric_point', Point3D(),
    'left_hemisphere_point', Point3D(),
        ##SPM Normalization
    'anatomical_template', ReadDiskItem( 'anatomical Template',
        ['NIFTI-1 image', 'MINC image', 'SPM image'] ),
    'job_file', WriteDiskItem( 'SPM2 parameters', 'Matlab file' ),
    'transformations_information', WriteDiskItem( 'SPM2 normalization matrix',
        'Matlab file' ),
    'normalized_t1mri', WriteDiskItem( 'Raw T1 MRI',
        [ 'NIFTI-1 image', 'SPM image' ], {"normalization":"SPM"} ),
    'talairach_MNI_transform', WriteDiskItem( 'Transform Raw T1 MRI to Talairach-MNI template-SPM',
        'Transformation matrix', ),
        ##Talairach Transformation
    'source_referential', ReadDiskItem( 'Referential of Raw T1 MRI', 'Referential' ),
    'normalized_referential', ReadDiskItem( 'Referential', 'Referential' ),
    'tal_to_normalized_transform', ListOf( ReadDiskItem( 'Transformation',
        'Transformation matrix' ) ),
    #Bias Correction
    't1mri_nobias', WriteDiskItem( 'T1 MRI Bias Corrected',
        'Aims writable volume formats' ),
    'hfiltered', WriteDiskItem( 'T1 MRI Filtered For Histo',
        'Aims writable volume formats' ),
    'white_ridges', WriteDiskItem( 'T1 MRI White Matter Ridges',
        'Aims writable volume formats', exactType=1 ),
    'variance', WriteDiskItem( 'T1 MRI Variance',
        'Aims writable volume formats' ),
    'edges', WriteDiskItem( 'T1 MRI Edges',
        'Aims writable volume formats' ),
    'field', WriteDiskItem( "T1 MRI Bias Field",
        'Aims writable volume formats' ),
    'meancurvature', WriteDiskItem( "T1 MRI Mean Curvature",
        'Aims writable volume formats' ),
    #Histogram Analysis
    'histo_analysis', WriteDiskItem( 'Histo Analysis',
        'Histo Analysis' ),
    #Brain Mask Segmentation
    'brain_mask', WriteDiskItem( 'T1 Brain Mask',
        'Aims writable volume formats' ),
    #Split Brain Mask
    'split_brain', WriteDiskItem( 'Split Brain Mask',
        'Aims writable volume formats' ),
    'split_template', ReadDiskItem( 'Hemispheres Template',
        'Aims readable volume formats' ),
    #Talairach Transformation
    'talairach_ACPC_transform', WriteDiskItem( 'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
        'Transformation matrix' ),
    #Grey/White Classification
        ##Left
    'left_grey_white', WriteDiskItem( 'Left Grey White Mask',
        'Aims writable volume formats' ),
        ##Right
    'right_grey_white', WriteDiskItem( 'Right Grey White Mask',
        'Aims writable volume formats' ),
    #Grey/White Surface
        ##Left
    'left_hemi_cortex', WriteDiskItem( 'Left CSF+GREY Mask',
        'Aims writable volume formats' ),
    'left_white_mesh', WriteDiskItem( 'Left Hemisphere White Mesh',
        'Aims mesh formats' ),
        ##Right
    'right_hemi_cortex', WriteDiskItem( 'Right CSF+GREY Mask',
        'Aims writable volume formats' ),
    'right_white_mesh', WriteDiskItem( 'Right Hemisphere White Mesh',
        'Aims mesh formats' ),
    #Spherical Hemispheres Surface
        ##Left
    'left_hemi_mesh', WriteDiskItem( 'Left Hemisphere Mesh',
        'Aims mesh formats' ),
        ##Right
    'right_hemi_mesh', WriteDiskItem( 'Right Hemisphere Mesh',
        'Aims mesh formats' ),
    #Cortical Folds Graph
        ##Left
    'left_graph', WriteDiskItem( 'Left Cortical folds graph',
        'Graph', requiredAttributes = {'labelled':'No', 'graph_version':'3.1'} ),
    'left_skeleton', WriteDiskItem( 'Left Cortex Skeleton',
        'Aims writable volume formats' ),
    'left_roots', WriteDiskItem( 'Left Cortex Catchment Bassins',
        'Aims writable volume formats' ),
    'left_sulci_voronoi', WriteDiskItem( 'Sulci Voronoi',
        'Aims writable volume formats', requiredAttributes = {'side':'left'} ),
    'left_middle_cortex', WriteDiskItem ( 'Grey White Mid-Interface Volume',
        'Aims writable volume formats', requiredAttributes = {'side':'left'} ),
        ##Right
    'right_graph', WriteDiskItem( 'Right Cortical folds graph',
        'Graph', requiredAttributes = {'labelled':'No', 'graph_version':'3.1'} ),
    'right_skeleton', WriteDiskItem( 'Right Cortex Skeleton',
        'Aims writable volume formats' ),
    'right_roots', WriteDiskItem( 'Right Cortex Catchment Bassins',
        'Aims writable volume formats' ),
    'right_sulci_voronoi', WriteDiskItem( 'Sulci Voronoi',
        'Aims writable volume formats', requiredAttributes = {'side':'right'} ),
    'right_middle_cortex', WriteDiskItem ( 'Grey White Mid-Interface Volume',
        'Aims writable volume formats', requiredAttributes = {'side':'right'} ),
    #Sulci Recognition
    'labels_translation_map', ReadDiskItem( 'Label Translation',
        [ 'Label Translation', 'DEF Label translation' ] ),
        ##Left
    'left_labelled_graph', WriteDiskItem( 'Labelled Cortical folds graph',
        'Graph and data', requiredAttributes = {'side':'left', 'labelled':'Yes', 'automatically_labelled':'Yes'} ),
    'left_posterior_probabilities', WriteDiskItem( 'Sulci Labels Segmentwise Posterior Probabilities',
        'CSV file', requiredAttributes = {'side':'left'} ),
    'left_labels_priors', ReadDiskItem( 'Sulci Labels Priors',
        'Text Data Table', requiredAttributes = {'side':'left'} ),
            ###Global
    'left_global_model', ReadDiskItem( 'Sulci Segments Model',
        'Text Data Table', requiredAttributes = {'side':'left'} ),
    'left_tal_to_global_transform', WriteDiskItem( 'Sulci Talairach to Global SPAM transformation',
        'Transformation matrix', requiredAttributes = {'side':'left'} ),
    'left_t1_to_global_transform', WriteDiskItem( 'Raw T1 to Global SPAM transformation',
        'Transformation matrix', requiredAttributes = {'side':'left'} ),
            ###Local
    'left_local_model', ReadDiskItem( 'Sulci Segments Model',
        'Text Data Table', requiredAttributes = {'side':'left'} ),
    'left_local_referentials', ReadDiskItem( 'Sulci Local referentials',
        'Text Data Table', requiredAttributes = {'side':'left'} ),
    'left_direction_priors', ReadDiskItem( 'Sulci Direction Transformation Priors',
        'Text Data Table', requiredAttributes = {'side':'left'} ),
    'left_angle_priors', ReadDiskItem( 'Sulci Angle Transformation Priors',
        'Text Data Table', requiredAttributes = {'side':'left'} ),
    'left_translation_priors', ReadDiskItem( 'Sulci Translation Transformation Priors',
        'Text Data Table', requiredAttributes = {'side':'left'} ),
    'left_global_to_local_transforms', WriteDiskItem( 'Sulci Local SPAM transformations Directory',
        'Directory', requiredAttributes = {'side':'left'} ),
        ##Right
    'right_labelled_graph', WriteDiskItem( 'Labelled Cortical folds graph',
        'Graph and data', requiredAttributes = {'side':'right', 'labelled':'Yes', 'automatically_labelled':'Yes'} ),
    'right_posterior_probabilities', WriteDiskItem( 'Sulci Labels Segmentwise Posterior Probabilities',
        'CSV file', requiredAttributes = {'side':'right'} ),
    'right_labels_priors', ReadDiskItem( 'Sulci Labels Priors',
        'Text Data Table', requiredAttributes = {'side':'right'} ),
            ###Global
    'right_global_model', ReadDiskItem( 'Sulci Segments Model',
        'Text Data Table', requiredAttributes = {'side':'right'} ),
    'right_tal_to_global_transform', WriteDiskItem( 'Sulci Talairach to Global SPAM transformation',
        'Transformation matrix', requiredAttributes = {'side':'right'} ),
    'right_t1_to_global_transform', WriteDiskItem( 'Raw T1 to Global SPAM transformation',
        'Transformation matrix', requiredAttributes = {'side':'right'} ),
            ###Local
    'right_local_model', ReadDiskItem( 'Sulci Segments Model',
        'Text Data Table', requiredAttributes = {'side':'right'} ),
    'right_local_referentials', ReadDiskItem( 'Sulci Local referentials',
        'Text Data Table', requiredAttributes = {'side':'right'} ),
    'right_direction_priors', ReadDiskItem( 'Sulci Direction Transformation Priors',
        'Text Data Table', requiredAttributes = {'side':'right'} ),
    'right_angle_priors', ReadDiskItem( 'Sulci Angle Transformation Priors',
        'Text Data Table', requiredAttributes = {'side':'right'} ),
    'right_translation_priors', ReadDiskItem( 'Sulci Translation Transformation Priors',
        'Text Data Table', requiredAttributes = {'side':'right'} ),
    'right_global_to_local_transforms', WriteDiskItem( 'Sulci Local SPAM transformations Directory',
        'Directory', requiredAttributes = {'side':'right'} ),
)


class APCReader:
  def __init__( self, key ):
    self._key = key

  def __call__( self, values, process ):
    acp = None
    if values.commissure_coordinates is not None:
      acp = values.commissure_coordinates
    result = None
    key_mm = self._key + 'mm'
    if acp is not None and acp.isReadable():
      f = open( acp.fullPath() )
      for l in f.readlines():
        l = l.split( ':', 1 )
        if len(l) == 2 and l[0] == key_mm:
          return [ float(i) for i in l[1].split() ]
        if len(l) == 2 and l[0] == self._key and values.t1mri is not None:
          vs = values.t1mri.get( 'voxel_size' )
          if vs:
            pos = l[1].split()
            if len( pos ) == 3:
              result = [ float(i) * j for i,j in zip( pos, vs ) ]
    return result


def initialization( self ):
    
    #Commissure Coordinates
    self.method_ACPC = "Manually"
    self.linkParameters( 'commissure_coordinates', 't1mri' )
    
    self.setOptional( 'anterior_commissure' )
    self.setOptional( 'posterior_commissure' )
    self.setOptional( 'interhemispheric_point' )
    self.setOptional( 'left_hemisphere_point' )
    
    self.signature[ 'anterior_commissure' ].add3DLink( self, 't1mri' )
    self.signature[ 'posterior_commissure' ].add3DLink( self, 't1mri' )
    self.signature[ 'interhemispheric_point' ].add3DLink( self, 't1mri' )
    self.signature[ 'left_hemisphere_point' ].add3DLink( self, 't1mri' )
    
    self.linkParameters( 'anterior_commissure',
        'commissure_coordinates', APCReader( 'AC' ) )
    self.linkParameters( 'posterior_commissure',
        'commissure_coordinates', APCReader( 'PC' ) )
    self.linkParameters( 'interhemispheric_point',
        'commissure_coordinates', APCReader( 'IH' ) )
    
        ##SPM Normalization
    def linkNormRef( proc, param ):
        trManager = registration.getTransformationManager()
        if proc.talairach_MNI_transform:
            s = proc.talairach_MNI_transform.get( 'destination_referential', None )
            if s:
                return trManager.referential( s )
        return trManager.referential( registration.talairachMNIReferentialId )
    def linkACPC_to_norm( proc, param ):
        trManager = registration.getTransformationManager()
        if proc.normalized_referential:
            _mniToACPCpaths = trManager.findPaths( registration.talairachACPCReferentialId,
                self.normalized_referential.uuid() )
            for x in _mniToACPCpaths:
                return x
            else:
                return []
    self.anatomical_template = self.signature[ 'anatomical_template' ].findValue(
        { 'databasename' : 'spm', 'skull_stripped' : 'no' } )
    self.linkParameters( 'job_file', 't1mri' )
    self.linkParameters( 'transformations_information', 't1mri' )
    self.linkParameters( 'normalized_t1mri', 't1mri' )
    self.linkParameters( 'talairach_MNI_transform', 'transformations_information' )
    
    self.linkParameters( 'source_referential', 't1mri' )
    self.linkParameters( 'normalized_referential',
        'talairach_MNI_transform', linkNormRef )
    self.linkParameters( 'tal_to_normalized_transform',
        'normalized_referential', linkACPC_to_norm )
    
    self.setOptional( 'anatomical_template' )
    self.setOptional( 'job_file' )
    
    self.signature[ 'anatomical_template' ].userLevel = 100
    self.signature[ 'job_file' ].userLevel = 100
    self.signature[ 'transformations_information' ].userLevel = 100
    self.signature[ 'normalized_t1mri' ].userLevel = 100
    self.signature[ 'talairach_MNI_transform' ].userLevel = 100
    self.signature[ 'source_referential' ].userLevel = 100
    self.signature[ 'normalized_referential' ].userLevel = 100
    self.signature[ 'tal_to_normalized_transform' ].userLevel = 100
    
    #Bias Correction
    self.linkParameters( 't1mri_nobias', 't1mri' )
    self.linkParameters( 'hfiltered', 't1mri' )
    self.linkParameters( 'white_ridges', 't1mri' )
    self.linkParameters( 'variance', 't1mri' )
    self.linkParameters( 'edges', 't1mri' )
    self.linkParameters( 'field', 't1mri' )
    self.linkParameters( 'meancurvature', 't1mri' )
    
    self.signature[ 'hfiltered' ].userLevel = 100
    self.signature[ 'white_ridges' ].userLevel = 100
    self.signature[ 'variance' ].userLevel = 100
    self.signature[ 'edges' ].userLevel = 100
    self.signature[ 'field' ].userLevel = 100
    self.signature[ 'meancurvature' ].userLevel = 100
    
    #Histogram Analysis
    self.linkParameters( 'histo_analysis', 't1mri_nobias' )
    
    #Brain Mask Segmentation
    self.linkParameters( 'brain_mask', 't1mri_nobias' )
    
    #Split Brain Mask
    self.linkParameters( 'split_brain', 'brain_mask' )
    self.split_template = self.signature[ 'split_template' ].findValue( {} )
    
    self.signature[ 'split_template' ].userLevel = 100
    
    #Talairach Transformation
    self.linkParameters( 'talairach_ACPC_transform', 't1mri' )
    
    self.signature[ 'talairach_ACPC_transform' ].userLevel = 100
    
    #Grey/White Classification
        ##Left
    self.linkParameters( 'left_grey_white', 'split_brain' )
        ##Right
    self.linkParameters( 'right_grey_white', 'split_brain' )
    
    #Grey/White Surface
        ##Left
    self.linkParameters( 'left_hemi_cortex', 't1mri_nobias' )
    self.linkParameters( 'left_white_mesh', 't1mri_nobias' )
    
    self.signature[ 'left_hemi_cortex' ].userLevel = 100
        ##Right
    self.linkParameters( 'right_hemi_cortex', 't1mri_nobias' )
    self.linkParameters( 'right_white_mesh', 't1mri_nobias' )
    
    self.signature[ 'right_hemi_cortex' ].userLevel = 100
    
    #Spherical Hemispheres Surface
        ##Left
    self.linkParameters( 'left_hemi_mesh', 'left_hemi_cortex' )
        ##Right
    self.linkParameters( 'right_hemi_mesh', 'right_hemi_cortex' )
    
    #Cortical Folds Graph
        ##Left
    self.linkParameters( 'left_graph', 't1mri_nobias' )
    self.linkParameters( 'left_skeleton', 't1mri_nobias' )
    self.linkParameters( 'left_roots', 't1mri_nobias' )
    self.linkParameters( 'left_sulci_voronoi', 't1mri_nobias' )
    self.linkParameters( 'left_middle_cortex', 't1mri_nobias' )
    
    self.signature[ 'left_skeleton' ].userLevel = 100
    self.signature[ 'left_roots' ].userLevel = 100
    self.signature[ 'left_sulci_voronoi' ].userLevel = 100
    self.signature[ 'left_middle_cortex' ].userLevel = 100
        ##Right
    self.linkParameters( 'right_graph', 't1mri_nobias' )
    self.linkParameters( 'right_skeleton', 't1mri_nobias' )
    self.linkParameters( 'right_roots', 't1mri_nobias' )
    self.linkParameters( 'right_sulci_voronoi', 't1mri_nobias' )
    self.linkParameters( 'right_middle_cortex', 't1mri_nobias' )
    
    self.signature[ 'right_skeleton' ].userLevel = 100
    self.signature[ 'right_roots' ].userLevel = 100
    self.signature[ 'right_sulci_voronoi' ].userLevel = 100
    self.signature[ 'right_middle_cortex' ].userLevel = 100
    
    #Sulci Recognition
    self.labels_translation_map = self.signature[ 'labels_translation_map' ].findValue(
        { 'filename_variable' : 'sulci_model_2008' } )
    self.signature[ 'labels_translation_map' ].userLevel = 100
        ##Left
    self.linkParameters( 'left_labelled_graph', 'left_graph' )
    self.linkParameters( 'left_posterior_probabilities', 'left_graph' )
    self.linkParameters( 'left_labels_priors', 'left_graph' )
    
    self.signature[ 'left_posterior_probabilities' ].userLevel = 100
    self.signature[ 'left_labels_priors' ].userLevel = 100
            ###Global
    self.left_global_model = self.signature[ 'left_global_model' ].findValue(
        { 'sulci_segments_model_type':'global_registered_spam' } )
    self.linkParameters( 'left_tal_to_global_transform', 'left_graph' )
    self.linkParameters( 'left_t1_to_global_transform', 'left_graph' )
    
    self.signature[ 'left_global_model' ].userLevel = 100
    self.signature[ 'left_tal_to_global_transform' ].userLevel = 100
    self.signature[ 'left_t1_to_global_transform' ].userLevel = 100
            ###Local
    self.left_local_model = self.signature[ 'left_local_model' ].findValue(
        { 'sulci_segments_model_type':'locally_from_global_registred_spam' } )
    self.linkParameters( 'left_local_referentials', 'left_graph' )
    self.linkParameters( 'left_direction_priors', 'left_graph' )
    self.linkParameters( 'left_angle_priors', 'left_graph' )
    self.linkParameters( 'left_translation_priors', 'left_graph' )
    self.linkParameters( 'left_global_to_local_transforms', 'left_graph' )
    
    self.signature[ 'left_local_model' ].userLevel = 100
    self.signature[ 'left_local_referentials' ].userLevel = 100
    self.signature[ 'left_direction_priors' ].userLevel = 100
    self.signature[ 'left_angle_priors' ].userLevel = 100
    self.signature[ 'left_translation_priors' ].userLevel = 100
    self.signature[ 'left_global_to_local_transforms' ].userLevel = 100
        ##Right
    self.linkParameters( 'right_labelled_graph', 'right_graph' )
    self.linkParameters( 'right_posterior_probabilities', 'right_graph' )
    self.linkParameters( 'right_labels_priors', 'right_graph' )
    
    self.signature[ 'right_posterior_probabilities' ].userLevel = 100
    self.signature[ 'right_labels_priors' ].userLevel = 100
            ###Global
    self.right_global_model = self.signature[ 'right_global_model' ].findValue(
        { 'sulci_segments_model_type':'global_registered_spam' } )
    self.linkParameters( 'right_tal_to_global_transform', 'right_graph' )
    self.linkParameters( 'right_t1_to_global_transform', 'right_graph' )
    
    self.signature[ 'right_global_model' ].userLevel = 100
    self.signature[ 'right_tal_to_global_transform' ].userLevel = 100
    self.signature[ 'right_t1_to_global_transform' ].userLevel = 100
            ###Local
    self.right_local_model = self.signature[ 'right_local_model' ].findValue(
        { 'sulci_segments_model_type':'locally_from_global_registred_spam' } )
    self.linkParameters( 'right_local_referentials', 'right_graph' )
    self.linkParameters( 'right_direction_priors', 'right_graph' )
    self.linkParameters( 'right_angle_priors', 'right_graph' )
    self.linkParameters( 'right_translation_priors', 'right_graph' )
    self.linkParameters( 'right_global_to_local_transforms', 'right_graph' )
    
    self.signature[ 'right_local_model' ].userLevel = 100
    self.signature[ 'right_local_referentials' ].userLevel = 100
    self.signature[ 'right_direction_priors' ].userLevel = 100
    self.signature[ 'right_angle_priors' ].userLevel = 100
    self.signature[ 'right_translation_priors' ].userLevel = 100
    self.signature[ 'right_global_to_local_transforms' ].userLevel = 100


def execution( self, context ):
    
    #Commissure Coordinates
    context.write( "Computing AC/PC Coordinates..." )
    if self.method_ACPC == "Manually":
        context.runProcess("preparesubject",
                            T1mri=self.t1mri,
                            commissure_coordinates=self.commissure_coordinates,
                            Anterior_Commissure=self.anterior_commissure,
                            Posterior_Commissure=self.posterior_commissure,
                            Interhemispheric_Point=self.interhemispheric_point,
                            Left_Hemisphere_Point=self.left_hemisphere_point,
                            older_MNI_normalization="")
    
    if self.method_ACPC == "SPM Normalization":
        context.runProcess("Normalization_SPM_reinit",
                            anatomy_data=self.t1mri,
                            anatomical_template=self.anatomical_template,
                            job_file=self.job_file,
                            transformations_informations=self.transformations_information,
                            normalized_anatomy_data=self.normalized_t1mri)
        context.runProcess("SPMsn3dToAims",
                            read=self.transformations_information,
                            write=self.talairach_MNI_transform,
                            source_volume=self.t1mri,
                            normalized_volume="")
        context.runProcess("TalairachTransformationFromNormalization",
                            normalization_transformation=self.talairach_MNI_transform,
                            Talairach_transform=self.talairach_ACPC_transform,
                            commissure_coordinates=self.commissure_coordinates,
                            t1mri=self.t1mri,
                            source_referential=self.source_referential,
                            normalized_referential=self.normalized_referential,
                            transform_chain_ACPC_to_Normalized=self.tal_to_normalized_transform)
    
    #Bias Correction
    context.write( "Computing T1 Bias Correction..." )
    context.runProcess("T1BiasCorrection",
                        mri=self.t1mri,
                        mri_corrected=self.t1mri_nobias,
                        field=self.field,
                        hfiltered=self.hfiltered,
                        white_ridges=self.white_ridges,
                        meancurvature=self.meancurvature,
                        variance=self.variance,
                        edges=self.edges,
                        commissure_coordinates=self.commissure_coordinates)
    
    #Histogram Analysis
    context.write( "Computing Histogram Analysis..." )
    context.runProcess("NobiasHistoAnalysis",
                        mri_corrected=self.t1mri_nobias,
                        histo_analysis=self.histo_analysis,
                        hfiltered=self.hfiltered,
                        white_ridges=self.white_ridges)
    
    #Brain Mask Segmentation
    context.write( "Computing Brain Segmentation..." )
    context.runProcess("BrainSegmentation",
                        mri_corrected=self.t1mri_nobias,
                        brain_mask=self.brain_mask,
                        white_ridges=self.white_ridges,
                        commissure_coordinates=self.commissure_coordinates,
                        variance=self.variance,
                        edges=self.edges,
                        histo_analysis=self.histo_analysis,
                        lesion_mask="")
    #Split Brain Mask
    context.write( "Computing Split Brain..." )
    context.runProcess("SplitBrain",
                        mri_corrected=self.t1mri_nobias,
                        split_mask=self.split_brain,
                        white_ridges=self.white_ridges,
                        histo_analysis=self.histo_analysis,
                        brain_mask=self.brain_mask,
                        split_template=self.split_template,
                        commissure_coordinates=self.commissure_coordinates)
    
    #Talairach Transformation
    if self.method_ACPC == "Manually":
        context.write( "Computing Talairach Transformation..." )
        context.runProcess("TalairachTransformation",
                            split_mask=self.split_brain,
                            commissure_coordinates=self.commissure_coordinates,
                            Talairach_transform=self.talairach_ACPC_transform)
    
    #Grey/White Classification
    context.write( "Computing Grey/White Classification..." )
    context.runProcess("GreyWhiteClassification",
                        mri_corrected=self.t1mri_nobias,
                        histo_analysis=self.histo_analysis,
                        split_mask=self.split_brain,
                        edges=self.edges,
                        commissure_coordinates=self.commissure_coordinates,
                        left_grey_white=self.left_grey_white,
                        right_grey_white=self.right_grey_white)
    
    #Grey/White Surface
    context.write( "Computing Grey/White Surface..." )
    context.runProcess("GreyWhiteSurface",
                        mri_corrected=self.t1mri_nobias,
                        histo_analysis=self.histo_analysis,
                        left_grey_white=self.left_grey_white,
                        right_grey_white=self.right_grey_white,
                        left_hemi_cortex=self.left_hemi_cortex,
                        right_hemi_cortex=self.right_hemi_cortex,
                        left_white_mesh=self.left_white_mesh,
                        right_white_mesh=self.right_white_mesh)
    
    #Spherical Hemispheres Surface
    context.write( "Computing Hemispheres Surface..." )
    context.runProcess("GetSphericalHemiSurface",
                        mri_corrected=self.t1mri_nobias,
                        split_mask=self.split_brain,
                        left_hemi_cortex=self.left_hemi_cortex,
                        right_hemi_cortex=self.right_hemi_cortex,
                        left_hemi_mesh=self.left_hemi_mesh,
                        right_hemi_mesh=self.right_hemi_mesh)
    
    #Cortical Folds Graph
    context.write( "Computing Cortical Folds Graph..." )
    ###Left
    context.runProcess("graphstructure_3_1",
                        mri_corrected=self.t1mri_nobias,
                        split_mask=self.split_brain,
                        hemi_cortex=self.left_hemi_cortex,
                        skeleton=self.left_skeleton,
                        roots=self.left_roots,
                        graph=self.left_graph,
                        commissure_coordinates=self.commissure_coordinates,
                        Talairach_transform=self.talairach_ACPC_transform)
    context.runProcess("sulcivoronoi",
                        graph=self.left_graph,
                        hemi_cortex=self.left_hemi_cortex,
                        sulci_voronoi=self.left_sulci_voronoi)
    context.runProcess("CorticalFoldsGraphThickness",
                        graph=self.left_graph,
                        hemi_cortex=self.left_hemi_cortex,
                        GW_interface=self.left_grey_white,
                        white_mesh=self.left_white_mesh,
                        hemi_mesh=self.left_hemi_mesh,
                        output_graph=self.left_graph,
                        output_mid_interface=self.left_middle_cortex,
                        sulci_voronoi=self.left_sulci_voronoi)
    ###Right
    context.runProcess("graphstructure_3_1",
                        mri_corrected=self.t1mri_nobias,
                        split_mask=self.split_brain,
                        hemi_cortex=self.right_hemi_cortex,
                        skeleton=self.right_skeleton,
                        roots=self.right_roots,
                        graph=self.right_graph,
                        commissure_coordinates=self.commissure_coordinates,
                        Talairach_transform=self.talairach_ACPC_transform)
    context.runProcess("sulcivoronoi",
                        graph=self.right_graph,
                        hemi_cortex=self.right_hemi_cortex,
                        sulci_voronoi=self.right_sulci_voronoi)
    context.runProcess("CorticalFoldsGraphThickness",
                        graph=self.right_graph,
                        hemi_cortex=self.right_hemi_cortex,
                        GW_interface=self.right_grey_white,
                        white_mesh=self.right_white_mesh,
                        hemi_mesh=self.right_hemi_mesh,
                        output_graph=self.right_graph,
                        output_mid_interface=self.right_middle_cortex,
                        sulci_voronoi=self.right_sulci_voronoi)
    
    #Sulci Recognition
    context.write( "Computing Sulci Recognition..." )
        ##Left
            ###Global
    context.runProcess("spam_recognitionglobal",
                        data_graph=self.left_graph,
                        output_graph=self.left_labelled_graph,
                        model=self.left_global_model,
                        posterior_probabilities=self.left_posterior_probabilities,
                        labels_translation_map=self.labels_translation_map,
                        labels_priors=self.left_labels_priors,
                        output_transformation=self.left_tal_to_global_transform,
                        initial_transformation="",
                        output_t1_to_global_transformation=self.left_t1_to_global_transform)
            ###Local
    context.runProcess("spam_recognitionlocal",
                        data_graph=self.left_graph,
                        output_graph=self.left_labelled_graph,
                        model=self.left_local_model,
                        posterior_probabilities=self.left_posterior_probabilities,
                        labels_translation_map=self.labels_translation_map,
                        labels_priors=self.left_labels_priors,
                        local_referentials=self.left_local_referentials,
                        direction_priors=self.left_direction_priors,
                        angle_priors=self.left_angle_priors,
                        translation_priors=self.left_translation_priors,
                        output_local_transformations=self.left_global_to_local_transforms,
                        initial_transformation="",
                        global_transformation=self.left_tal_to_global_transform)
    
        ##Right
            ###Global
    context.runProcess("spam_recognitionglobal",
                        data_graph=self.right_graph,
                        output_graph=self.right_labelled_graph,
                        model=self.right_global_model,
                        posterior_probabilities=self.right_posterior_probabilities,
                        labels_translation_map=self.labels_translation_map,
                        labels_priors=self.right_labels_priors,
                        output_transformation=self.right_tal_to_global_transform,
                        initial_transformation="",
                        output_t1_to_global_transformation=self.right_t1_to_global_transform)
            ###Local
    context.runProcess("spam_recognitionlocal",
                        data_graph=self.right_graph,
                        output_graph=self.right_labelled_graph,
                        model=self.right_local_model,
                        posterior_probabilities=self.right_posterior_probabilities,
                        labels_translation_map=self.labels_translation_map,
                        labels_priors=self.right_labels_priors,
                        local_referentials=self.right_local_referentials,
                        direction_priors=self.right_direction_priors,
                        angle_priors=self.right_angle_priors,
                        translation_priors=self.right_translation_priors,
                        output_local_transformations=self.right_global_to_local_transforms,
                        initial_transformation="",
                        global_transformation=self.right_tal_to_global_transform)
    
    
    
    
