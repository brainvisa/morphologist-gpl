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

include( 'base' )
include( 'registration' )


anatomy_content = (
#    "<subject>_TO_talairach", SetType( 'Transformation matrix' ),# SetWeakAttr( 'from', '%<subject>', 'to', 'Talairach' ),
#    'talairach_TO_<subject>', SetType( 'Transformation matrix' ),# SetWeakAttr( 'from', 'Talairach', 'to', '%<subject>' ),
#    '<subject>_TO_spm_template', SetType( 'Transformation matrix' ),# SetWeakAttr( 'from', '%<subject>', 'to', 'spm_template' ),
#    "spm_template_TO_<subject>", SetType( 'Transformation matrix' ),# SetWeakAttr( 'from', 'spm_template', 'to', '%<subject>' ),
    "<subject>", SetType( 'Raw T1 MRI' ), SetWeakAttr( 'spm_normalized', 'no' ), SetWeakAttr( 'fMRI_register', 'No' ), SetPriorityOffset( +1 ),
    "r<subject>", SetType( 'Registered Raw T1 MRI with fMRI' ), SetWeakAttr( 'fMRI_register', 'Yes' ),
    "<subject>_t2", SetType( 'T2 MRI' ),
    "nobias_<subject>", SetType( 'T1 MRI Bias Corrected' ),
    "biasfield_<subject>", SetType( 'T1 MRI Bias Field' ),
    "whiteridge_<subject>", SetType( 'T1 MRI White Matter Ridges' ),
    "variance_<subject>", SetType( 'T1 MRI Variance' ),
    "edges_<subject>", SetType( 'T1 MRI Edges' ),
    "mean_curvature_<subject>", SetType( 'T1 MRI Mean Curvature' ),
    "hfiltered_<subject>", SetType( 'T1 MRI Filtered For Histo' ),
    "w<subject>", SetType( 'Raw T1 MRI' ), SetWeakAttr( 'spm_normalized', 'yes' ),
    "mri_ext_<subject>", SetType( 'MRI Ext Edge Image' ),
    "nobias_<subject>", SetType( 'Histo Analysis' ),
    "<subject>", SetType('Commissure coordinates'),
    "<subject>_*", SetType( 'Raw T1 MRI' ),
    "<subject>_t2_*", SetType( 'T2 MRI' ),
    "n<subject>_*", SetType( 'Raw T1 MRI' ), SetWeakAttr( 'fMRI_register', 'No' ),
    "wr<subject>", SetType( 'Registered Raw T1 MRI with fMRI' ), SetWeakAttr( 'fMRI_register', 'Yes' ),
    "nobias_<subject>_*", SetType( 'T1 MRI Bias Corrected' ),
    "nnobias_<subject>_*", SetType( 'T1 MRI Bias Corrected' ),
    "nobias_<subject>_*", SetType( 'Histo Analysis' ),
    "<subject>_sn", SetType("SPM2 normalization matrix"),
#    "*", SetType('Subject General Info'),
#    "subject_info_<subject>*", SetType('Subject General Info'),
)



segment_content = (
    "LSulci_<subject>", SetType( 'Left Sulci Volume' ), SetWeakAttr( 'side', 'left'),
    "RSulci_<subject>", SetType( 'Right Sulci Volume' ), SetWeakAttr( 'side', 'right'),
    "LBottom_<subject>", SetType( 'Left Bottom Volume' ), SetWeakAttr( 'side', 'left'),
    "RBottom_<subject>", SetType( 'Right Bottom Volume' ), SetWeakAttr( 'side', 'right'),
    "LHullJunction_<subject>", SetType( 'Left Hull Junction Volume' ), SetWeakAttr( 'side', 'left'),
    "LSimpleSurface_<subject>", SetType( 'Right Simple Surface Volume' ), SetWeakAttr( 'side', 'left'),
    "RHullJunction_<subject>", SetType( 'Left Hull Junction Volume' ), SetWeakAttr( 'side', 'right'),
    "RSimpleSurface_<subject>", SetType( 'Right Simple Surface Volume' ), SetWeakAttr( 'side', 'right'),
    "Lmoment_<subject>", SetType( 'Moment Vector' ), SetWeakAttr( 'side', 'left'),
    "Rmoment_<subject>", SetType( 'Moment Vector' ), SetWeakAttr( 'side', 'right'),
    "unflip_<subject>",SetType( 'Display BIC drawing' ), SetWeakAttr( 'side', 'both' ),
    "FCMunflip_<subject>",SetType( 'Anatomist BIC drawing' ), SetWeakAttr( 'side', 'both' ),
    "brain_<subject>", SetType( 'T1 Brain Mask' ), SetWeakAttr( 'side', 'both' ),
    "brain_<subject>_*", SetType( 'T1 Brain Mask' ),SetWeakAttr( 'side', 'both' ),
    "Rgrey_white_<subject>", SetType( 'Right Grey White Mask' ), SetWeakAttr( 'side', 'right' ),
    "Rgrey_white_<subject>_*", SetType( 'Right Grey White Mask' ), SetWeakAttr( 'side', 'right' ),
    "Lgrey_white_<subject>", SetType( 'Left Grey White Mask' ), SetWeakAttr( 'side', 'left' ),
    "Lgrey_white_<subject>_*", SetType( 'Left Grey White Mask' ), SetWeakAttr( 'side', 'left' ),
    "cortex_<subject>", SetType( 'Both CSF+GREY Mask' ), SetWeakAttr( 'side', 'both' ),
    "cortex_<subject>_*", SetType( 'Both CSF+GREY Mask' ), SetWeakAttr( 'side', 'both' ),
    "Lcortex_<subject>", SetType( 'Left CSF+GREY Mask' ), SetWeakAttr( 'side', 'left' ),
    "Lcortex_<subject>_*", SetType( 'Left CSF+GREY Mask' ), SetWeakAttr( 'side', 'left' ),
    "Rcortex_<subject>", SetType( 'Right CSF+GREY Mask' ), SetWeakAttr( 'side', 'right' ),
    "Rcortex_<subject>_*", SetType( 'Right CSF+GREY Mask' ), SetWeakAttr( 'side', 'right' ),
    "csf_<subject>", SetType( 'Both CSF Mask' ), SetWeakAttr( 'side', 'both' ),
    "csf_<subject>_*", SetType( 'Both CSF Mask' ), SetWeakAttr( 'side', 'both' ),
    "Lcsf_<subject>", SetType( 'Left CSF Mask' ), SetWeakAttr( 'side', 'left' ),
    "Lcsf_<subject>_*", SetType( 'Left CSF Mask' ), SetWeakAttr( 'side', 'left' ),
    "Rcsf_<subject>", SetType( 'Right CSF Mask' ), SetWeakAttr( 'side', 'right' ),
    "Rcsf_<subject>_*", SetType( 'Right CSF Mask' ), SetWeakAttr( 'side', 'right' ),
    "Lskeleton_<subject>", SetType( 'Left Cortex Skeleton' ), SetWeakAttr( 'side', 'left' ),
    "Lskeleton_<subject>_*", SetType( 'Left Cortex Skeleton' ), SetWeakAttr( 'side', 'left' ),
    "Rskeleton_<subject>", SetType( 'Right Cortex Skeleton' ), SetWeakAttr( 'side', 'right' ),
    "Rskeleton_<subject>_*", SetType( 'Right Cortex Skeleton' ), SetWeakAttr( 'side', 'right' ),
    "Lroots_<subject>", SetType( 'Left Cortex Catchment Bassins' ), SetWeakAttr( 'side', 'left' ),
    "Lroots_<subject>_*", SetType( 'Left Cortex Catchment Bassins' ), SetWeakAttr( 'side', 'left' ),
    "Rroots_<subject>", SetType( 'Right Cortex Catchment Bassins' ), SetWeakAttr( 'side', 'right' ),
    "Rroots_<subject>_*", SetType( 'Right Cortex Catchment Bassins' ), SetWeakAttr( 'side', 'right' ),
    "voronoi_<subject>", SetType( 'Split Brain Mask' ), SetWeakAttr( 'side', 'both' ),
    "voronoi_<subject>_*", SetType( 'Split Brain Mask' ), SetWeakAttr( 'side', 'both' ),
    "<subject>_Lwhite_curv", SetType( 'White Curvature Texture' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rwhite_curv", SetType( 'White Curvature Texture' ), SetWeakAttr( 'side', 'right' ),
    "<subject>_Lwhite_sulci", SetType( 'Sulci White Texture' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rwhite_sulci", SetType( 'Sulci White Texture' ), SetWeakAttr( 'side', 'right' ),
    "<subject>_Lsulci_patch", SetType( 'Sulci White Texture Patch' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rsulci_patch", SetType( 'Sulci White Texture Patch' ), SetWeakAttr( 'side', 'right' ),
    "<subject>_Lwhite_gyri", SetType( 'Gyri White Texture' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rwhite_gyri", SetType( 'Gyri White Texture' ), SetWeakAttr( 'side', 'right' ),
    "<subject>_Lwhite_gyri", SetType( 'Gyri White Volume' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rwhite_gyri", SetType( 'Gyri White Volume' ), SetWeakAttr( 'side', 'right' ),
    "<subject>_Lsulci_patch", SetType( 'Sulci White Volume Patch' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rsulci_patch", SetType( 'Sulci White Volume Patch' ), SetWeakAttr( 'side', 'right' ),
    "head_<subject>", SetType( "Head Mask" ),
)


mesh_content = (
    "<subject>_brain", SetType( 'Brain Mesh' ), SetWeakAttr( 'side', 'both' ),
    "<subject>_Lhemi", SetType( 'Left Hemisphere Mesh' ), SetWeakAttr( 'side', 'left' ), SetPriorityOffset( +1 ),
    "<subject>_Rhemi", SetType( 'Right Hemisphere Mesh' ), SetWeakAttr( 'side', 'right' ), SetPriorityOffset( +1 ),
    "<subject>_Lwhite", SetType( 'Left Hemisphere White Mesh' ), SetWeakAttr( 'side', 'left' ), SetPriorityOffset( +1 ),
    "<subject>_Rwhite", SetType( 'Right Hemisphere White Mesh' ), SetWeakAttr( 'side', 'right' ), SetPriorityOffset( +1 ),
    "<subject>_Lwhite_S", SetType( 'Left Hemisphere White Spherical Mesh' ), SetWeakAttr( 'side', 'left' ), SetPriorityOffset( +1 ),
    "<subject>_Rwhite_S", SetType( 'Right Hemisphere White Spherical Mesh' ), SetWeakAttr( 'side', 'right' ), SetPriorityOffset( +1 ),
    "<subject>_Lwhite_inflated", SetType( 'Inflated Hemisphere White Mesh' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rwhite_inflated", SetType( 'Inflated Hemisphere White Mesh' ), SetWeakAttr( 'side', 'right' ),
    "<subject>_Lwhite_fine", SetType( 'Left Fine Hemisphere White Mesh' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rwhite_fine", SetType( 'Right Fine Hemisphere White Mesh' ), SetWeakAttr( 'side', 'right' ),
    "<subject>_Lmedian", SetType( 'Median Mesh' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rmedian", SetType( 'Median Mesh' ), SetWeakAttr( 'side', 'right' ),
    "<subject>_head", SetType( 'Head Mesh' ), SetWeakAttr( 'side', 'both' ),
    "<subject>_skull", SetType( 'Skull Mesh' ), SetWeakAttr( 'side', 'both' ),
    "cortex_<subject>_mni", SetType( 'MNI Cortex Mesh' ), SetWeakAttr( 'side', 'both' ),
    "*", SetType( 'Mesh'),
)


graph_content = (
    "FCMunflip_<subject>",SetType( 'Roi Graph' ), SetWeakAttr( 'side', 'both' ),
    "Pons_<subject>",SetType( 'Roi Graph' ),SetWeakAttr( 'side', 'both' ),
    "<subject>-nucleus",SetType( 'Nucleus graph' ),SetWeakAttr( 'graph_type', 'NucleusArg'),
    "L<subject>", SetType( 'Cortical folds graph' ), SetWeakAttr( 'side', 'left', 'labelled', 'No', 'warped_to_vishnu', 'No' ),
    "L<subject>Base", SetType( 'Base Cortical folds graph' ), SetWeakAttr( 'side', 'left', 'labelled', 'Yes', 'manually_labelled', 'Yes', 'automatically_labelled', 'No', 'warped_to_vishnu', 'No' ),
    "L<subject>_TO_vishnu_Base", SetType( 'Base Cortical folds graph' ), SetWeakAttr( 'side', 'left', 'labelled', 'Yes', 'manually_labelled', 'Yes', 'automatically_labelled', 'No', 'warped_to_vishnu', 'Yes' ),
    "L<subject>Auto", SetType( 'Labelled Cortical folds graph' ), SetPriorityOffset( +1 ), SetWeakAttr( 'side', 'left', 'labelled', 'Yes', 'manually_labelled', 'No', 'automatically_labelled', 'Yes', 'warped_to_vishnu', 'No', 'parallel_recognition', 'No' ),
    "L<subject>AutoBest", SetType( 'Parallel Labelled Cortical folds graph' ), SetWeakAttr( 'side', 'left', 'labelled', 'Yes', 'manually_labelled', 'No', 'automatically_labelled', 'Yes', 'warped_to_vishnu', 'No', 'parallel_recognition', 'Best'),
    "L<subject>AutoWorst", SetType( 'Parallel Labelled Cortical folds graph' ), SetWeakAttr( 'side', 'left', 'labelled', 'Yes', 'manually_labelled', 'No', 'automatically_labelled', 'Yes', 'warped_to_vishnu', 'No', 'parallel_recognition', 'Worst'),
    "R<subject>", SetType( 'Cortical folds graph' ), SetWeakAttr( 'side', 'right',  'labelled', 'No', 'warped_to_vishnu', 'No'),
    "R<subject>Base", SetType( 'Base Cortical folds graph' ), SetWeakAttr( 'side', 'right', 'labelled', 'Yes', 'manually_labelled', 'Yes', 'automatically_labelled', 'No', 'warped_to_vishnu', 'No' ),
    "R<subject>_TO_vishnu_Base", SetType( 'Base Cortical folds graph' ), SetWeakAttr( 'side', 'right', 'labelled', 'Yes', 'manually_labelled', 'Yes', 'automatically_labelled', 'No', 'warped_to_vishnu', 'Yes' ),
    "R<subject>Auto", SetType( 'Labelled Cortical folds graph' ), SetPriorityOffset( +1 ), SetWeakAttr( 'side', 'right', 'labelled', 'Yes', 'manually_labelled', 'No', 'automatically_labelled', 'Yes', 'warped_to_vishnu', 'No', 'parallel_recognition', 'No' ),
    "R<subject>AutoBest", SetType( 'Parallel Labelled Cortical folds graph' ), SetWeakAttr( 'side', 'right', 'labelled', 'Yes', 'manually_labelled', 'No', 'automatically_labelled', 'Yes', 'warped_to_vishnu', 'No', 'parallel_recognition', 'Best'),
    "R<subject>AutoWorst", SetType( 'Parallel Labelled Cortical folds graph' ), SetWeakAttr( 'side', 'right', 'labelled', 'Yes', 'manually_labelled', 'No', 'automatically_labelled', 'Yes', 'warped_to_vishnu', 'No', 'parallel_recognition', 'Worst'),
    "<subject>_Rwhite_primal",SetType( 'Primal Sketch' ),SetWeakAttr( 'side', 'right' ),
    "<subject>_Lwhite_primal",SetType( 'Primal Sketch' ),SetWeakAttr( 'side', 'left' ),

    "<subject>_Rwhite_GLB",SetType( 'Grey Level Blob Graph' ),SetWeakAttr( 'side', 'right' ),
    "<subject>_Lwhite_GLB",SetType( 'Grey Level Blob Graph' ),SetWeakAttr( 'side', 'left' ),
    "<subject>_Rgyri",SetType( 'Gyri Graph' ),SetWeakAttr( 'side', 'right' ),
    "<subject>_Lgyri",SetType( 'Gyri Graph' ),SetWeakAttr( 'side', 'left' ),
    "<subject>_Rsulci_patch",SetType( 'Sulcal Patch Graph' ),SetWeakAttr( 'side', 'right' ),
    "<subject>_Lsulci_patch",SetType( 'Sulcal Patch Graph' ),SetWeakAttr( 'side', 'left' ),
    "<subject>_left_gyri_to_texture",SetType( 'Gyri To White Texture Translation' ),SetWeakAttr( 'side', 'left' ),
    "<subject>_right_gyri_to_texture",SetType( 'Gyri To White Texture Translation' ),SetWeakAttr( 'side', 'right' ),
    "<subject>_left_sulci_to_texture",SetType( 'Sulci To White Texture Translation' ),SetWeakAttr( 'side', 'left' ),
    "<subject>_right_sulci_to_texture",SetType( 'Sulci To White Texture Translation' ),SetWeakAttr( 'side', 'right' ),
    "<subject>_boundingbox_points",SetType('Bounding Box Points'),
    "Lsulcivoronoi_<subject>", SetType( 'Sulci Voronoi' ),
      SetWeakAttr( 'side', 'left' ),
    "Rsulcivoronoi_<subject>", SetType( 'Sulci Voronoi' ),
      SetWeakAttr( 'side', 'right' ),
    '{sulci_recognition_session}', SetContent(
      "L<subject>Auto_<sulci_recognition_session>", SetType( 'Labelled Cortical folds graph' ),
        SetWeakAttr( 'side', 'left', 'labelled', 'Yes', 'manually_labelled', 'No', 'automatically_labelled', 'Yes', 'warped_to_vishnu', 'No',
                     'parallel_recognition', 'No' ),
      "R<subject>Auto_<sulci_recognition_session>", SetType( 'Labelled Cortical folds graph' ),
        SetWeakAttr( 'side', 'right', 'labelled', 'Yes', 'manually_labelled', 'No', 'automatically_labelled', 'Yes', 'warped_to_vishnu', 'No',
                     'parallel_recognition', 'No' ),
    )
)


deepnuclei_content = (
    '<subject>_deep_nuclei_mask', SetType( 'Deep Nuclei Mask' ),
    '<subject>_deep_nuclei_graph', SetType( 'Deep Nuclei Graph' ),
)



insert( '{protocol}/{subject}',
  'anatomy', SetWeakAttr( 'acquisition', '' ),
    SetContent(*(anatomy_content
                 + ('{acquisition}', SetContent(*anatomy_content),))),
  'segment', SetWeakAttr( 'acquisition', '' ),
    SetContent(*(segment_content
                 + ('{acquisition}', SetContent(*segment_content),))),
  'tri', SetWeakAttr( 'acquisition', '' ), SetPriorityOffset( -10 ),
      SetContent(*mesh_content),
  'mesh', SetWeakAttr( 'acquisition', '' ),
    SetContent(*(mesh_content
                 + ('{acquisition}', SetContent(*mesh_content),))),
  'graphe', SetWeakAttr( 'acquisition', '' ), SetWeakAttr( 'sulci_recognition_session', 'default' ), SetWeakAttr( 'graph_version', '3.0' ), SetPriorityOffset( +2 ),
    SetContent(*(graph_content
                 + ('{acquisition}', SetContent(*graph_content),))),
  'deepnuclei', SetWeakAttr( 'acquisition', '' ),
    SetContent(*(deepnuclei_content
                 + ('{acquisition}', SetContent(*deepnuclei_content),))),
)

#----------------- Registration -------------------------

insertFirst( '{protocol}/{subject}/registration',
  'RawT1-<subject>', SetType( 'Referential of Raw T1 MRI' ),
  'RawT1-<subject>-{acquisition}', SetType( 'Referential of Raw T1 MRI' ),
  'RawT1-<subject>_TO_Talairach-ACPC', SetType( 'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist' ),
  'RawT1-<subject>_{acquisition}_TO_Talairach-ACPC', SetType( 'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist' ),
)

insertFirst( '{protocol}/registration',
  'RawT1-{source.subject}-{source.acquisition}_TO_RawT1-{dest.subject}-{dest.acquisition}', SetType( 'Transform Raw T1 MRI to Raw T1 MRI' ),
  'RawT1-{source.subject}_TO_RawT1-{dest.subject}-{dest.acquisition}', SetType( 'Transform Raw T1 MRI to Raw T1 MRI' ), SetPriorityOffset( -1 ),
  'RawT1-{source.subject}-{source.acquisition}_TO_RawT1-{dest.subject}', SetType( 'Transform Raw T1 MRI to Raw T1 MRI' ), SetPriorityOffset( -1 ),
  'RawT1-{source.subject}_TO_RawT1-{dest.subject}', SetType( 'Transform Raw T1 MRI to Raw T1 MRI' ), SetPriorityOffset( -2 ),
)
