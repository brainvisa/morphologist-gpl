# -*- coding: utf-8 -*-
# Copyright CEA and IFR 49 (2000-2005)
#
#  This software and supporting documentation were developed by
#      CEA/DSV/SHFJ and IFR 49
#      4 place du General Leclerc
#      91401 Orsay cedex
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
import registration
include( 'registration' )
include( '3DT1_spm' )

snap_pialmesh_content = (
    "snapshot_left_pialmesh_{subject}_{acquisition}", SetType( 'Left Snapshot Pial Mesh'), SetWeakAttr( 'side', 'left' ),
    "snapshot_right_pialmesh_{subject}_{acquisition}", SetType( 'Right Snapshot Pial Mesh'), SetWeakAttr( 'side', 'right' ),
)
snap_sulci_content = (
    "snapshot_left_sulci_{subject}_{acquisition}", SetType( 'Left Snapshot Sulci'), SetWeakAttr( 'side', 'left' ),
    "snapshot_right_sulci_{subject}_{acquisition}", SetType( 'Right Snapshot Sulci'), SetWeakAttr( 'side', 'right' ),
)
snap_whitemesh_content = (
    "snapshot_left_whitemesh_{subject}_{acquisition}", SetType( 'Left Snapshot White Mesh'), SetWeakAttr( 'side', 'left' ),
    "snapshot_right_whitemesh_{subject}_{acquisition}", SetType( 'Right Snapshot White Mesh'), SetWeakAttr( 'side', 'right' ),
)



mesh_content = (
    "<subject>_brain", SetType( 'Brain Mesh' ), SetWeakAttr( 'side', 'both' ),
    "<subject>_Lhemi", SetType( 'Left Hemisphere Mesh' ), SetWeakAttr( 'side', 'left' ), SetPriorityOffset( +1 ),
    "<subject>_Rhemi", SetType( 'Right Hemisphere Mesh' ), SetWeakAttr( 'side', 'right' ), SetPriorityOffset( +1 ),
    "<subject>_Lwhite", SetType( 'Left Hemisphere White Mesh' ), SetWeakAttr( 'side', 'left' ), SetPriorityOffset( +1 ),
    "<subject>_Rwhite", SetType( 'Right Hemisphere White Mesh' ), SetWeakAttr( 'side', 'right' ), SetPriorityOffset( +1 ),
    "<subject>_Lwhite_inflated", SetType( 'Inflated Hemisphere White Mesh' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rwhite_inflated", SetType( 'Inflated Hemisphere White Mesh' ), SetWeakAttr( 'side', 'right' ),
    "<subject>_Lwhite_fine", SetType( 'Left Fine Hemisphere White Mesh' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rwhite_fine", SetType( 'Right Fine Hemisphere White Mesh' ), SetWeakAttr( 'side', 'right' ),
    "<subject>_head", SetType( 'Head Mesh' ), SetWeakAttr( 'side', 'both' ),
    "<subject>_Lhemi_hull", SetType( 'Hemisphere Hull Mesh' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rhemi_hull", SetType( 'Hemisphere Hull Mesh' ), SetWeakAttr( 'side', 'right' ),
    "<subject>_Bhemi_hull", SetType( 'Hemisphere Hull Mesh' ), SetWeakAttr( 'side', 'both' ),
    "<subject>_brain_hull", SetType( 'Brain Hull Mesh' ), SetWeakAttr( 'side', 'both' ), 
    "<subject>_Lmedian", SetType( 'Median Mesh' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rmedian", SetType( 'Median Mesh' ), SetWeakAttr( 'side', 'right' ), 
    "<subject>_Lconformal", SetType( 'Conformal White Mesh' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rconformal", SetType( 'Conformal White Mesh' ), SetWeakAttr( 'side', 'right' ),
    "cortex_<subject>_mni", SetType( 'MNI Cortex Mesh' ), SetWeakAttr( 'side', 'both' ), ## utilise en lecture seulement
    "<subject>_Lwhite_resampled", SetType("Resampled Hemisphere White Mesh"), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rwhite_resampled", SetType("Resampled Hemisphere White Mesh"), SetWeakAttr( 'side', 'right' ),
    "<subject>_Bwhite_resampled", SetType("Resampled Hemisphere White Mesh"), SetWeakAttr( 'side', 'both' ),

    "<subject>_Lwhite_sphere", SetType("Spherical Mesh"), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rwhite_sphere", SetType("Spherical Mesh"), SetWeakAttr( 'side', 'right' ),

#    "template_spherical_Lwhite", SetType("Template Hemisphere Spherical Mesh"), SetWeakAttr( 'side', 'left' ),
#    "template_spherical_Rwhite", SetType("Template Hemisphere Spherical Mesh"), SetWeakAttr( 'side', 'right' ),
    "*", SetType( 'Mesh'),
)

segmentation_content = (
    "brain_<subject>", SetType( 'T1 Brain Mask' ), SetWeakAttr( 'side', 'both' ),
    "Rgrey_white_<subject>", SetType( 'Right Grey White Mask' ), SetWeakAttr( 'side', 'right' ),
    "Lgrey_white_<subject>", SetType( 'Left Grey White Mask' ), SetWeakAttr( 'side', 'left' ),
    "cortex_<subject>", SetType( 'Both CSF+GREY Mask' ), SetWeakAttr( 'side', 'both' ),
    "Lcortex_<subject>", SetType( 'Left CSF+GREY Mask' ), SetWeakAttr( 'side', 'left' ),
    "Rcortex_<subject>", SetType( 'Right CSF+GREY Mask' ), SetWeakAttr( 'side', 'right' ),
    "csf_<subject>", SetType( 'Both CSF Mask' ), SetWeakAttr( 'side', 'both' ),
    "Lcsf_<subject>", SetType( 'Left CSF Mask' ), SetWeakAttr( 'side', 'left' ),
    "Rcsf_<subject>", SetType( 'Right CSF Mask' ), SetWeakAttr( 'side', 'right' ),
    "Lskeleton_<subject>", SetType( 'Left Cortex Skeleton' ), SetWeakAttr( 'side', 'left' ),
    "Rskeleton_<subject>", SetType( 'Right Cortex Skeleton' ), SetWeakAttr( 'side', 'right' ),
    "Lroots_<subject>", SetType( 'Left Cortex Catchment Bassins' ), SetWeakAttr( 'side', 'left' ),
    "Rroots_<subject>", SetType( 'Right Cortex Catchment Bassins' ), SetWeakAttr( 'side', 'right' ),
    "voronoi_<subject>", SetType( 'Split Brain Mask' ), SetWeakAttr( 'side', 'both' ),
    "head_<subject>", SetType( "Head Mask" ),
    "<subject>_Lwhite_curv", SetType( 'White Curvature Texture' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rwhite_curv", SetType( 'White Curvature Texture' ), SetWeakAttr( 'side', 'right' ),
    "<subject>_Lwhite_depth", SetType( 'White Depth Texture' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rwhite_depth", SetType( 'White Depth Texture' ), SetWeakAttr( 'side', 'right' ),
    "<subject>_Lgyri_resampled", SetType("Resampled Hemisphere Gyri Texture"), SetWeakAttr("side", "left"),
    "<subject>_Rgyri_resampled", SetType("Resampled Hemisphere Gyri Texture"), SetWeakAttr("side", "right"),
    "<subject>_Bgyri_resampled", SetType("Resampled Hemisphere Gyri Texture"), SetWeakAttr("side", "both"),
    "Lgw_interface_<subject>", SetType( 'Grey White Mid-Interface Volume' ),
    SetWeakAttr( 'side', 'left' ),
    "Rgw_interface_<subject>", SetType( 'Grey White Mid-Interface Volume' ),
    SetWeakAttr( 'side', 'right' ),
    "lesiondistance_<subject>", SetType( 'Lesion distance map' ),
    'corpus_callosum_mask', SetType( 'Corpus Callosum mask' ),

    'mesh',
    apply( SetContent, mesh_content),
)

t1mri_acq_content = (
    # t1mri before processing in acquisition level
    #"<subject>", SetType( 'Raw T1 MRI' ), SetPriorityOffset( +1 ), SetWeakAttr( 'normalized', 'no' ),
    "<subject>", SetType( 'Commissure coordinates' ),
    "normalized_{normalization}_<subject>", SetType( 'Raw T1 MRI' ), SetWeakAttr( 'normalized', 'yes' ),
    "<subject>_sn", SetType( 'SPM2 normalization matrix' ),
    "<subject>_job_anat_normalization", SetType( 'SPM2 parameters' ),
    "<subject>_fsl", SetType( 'FSL Transformation' ),
    # lesion mask
    "lesion_<subject>", SetType( 'Lesion Mask' ), SetPriorityOffset( +1 ), SetWeakAttr( 'normalized', 'no' ),
    "lesion_normalized_{normalization}_<subject>", SetType( 'Lesion Mask' ), SetWeakAttr( 'normalized', 'yes' ),

    #      "r<subject>", SetType( 'Registered Raw T1 MRI with fMRI' ), SetWeakAttr( 'fMRI_register', 'Yes' ),
    #    "wr<subject>", SetType( 'Registered Raw T1 MRI with fMRI' ), SetWeakAttr( 'fMRI_register', 'Yes' ),
    'registration', SetContent(
      'RawT1-<subject>_<acquisition>_TO_unknown_atlas_WITH_bal', SetType("baladin Transformation"),
      'RawT1-<subject>_<acquisition>', SetType( 'Referential of Raw T1 MRI' ),
      'RawT1-<subject>_<acquisition>_TO_Talairach-ACPC', SetType( 'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist' ),
      'RawT1-<subject>_<acquisition>_TO_Talairach-MNI', SetType( 'Transform Raw T1 MRI to Talairach-MNI template-SPM'),

      'RawT1-<subject>_<acquisition>_TO_Scanner_Based', SetType( 'Transformation to Scanner Based Referential' ),
      'RawT1-<subject>_<acquisition>_Scanner_Based', SetType( 'Scanner Based Referential' ),

      SetWeakAttr('destination_referential', str(registration.talairachMNIReferentialId)),
    ),
    "{analysis}",
      SetContent( # processing results in analysis
        #"nobias_<subject>", SetType( 'T1 MRI Bias Corrected' ),
        "biasfield_<subject>", SetType( 'T1 MRI Bias Field' ),
        "whiteridge_<subject>", SetType( 'T1 MRI White Matter Ridges' ),
        "variance_<subject>", SetType( 'T1 MRI Variance' ),
        "edges_<subject>", SetType( 'T1 MRI Edges' ),
        "mean_curvature_<subject>", SetType( 'T1 MRI Mean Curvature' ),
        "hfiltered_<subject>", SetType( 'T1 MRI Filtered For Histo' ),
        "nobias_<subject>", SetType( 'Histogram' ),
        "nobias_<subject>", SetType( 'Histo Analysis' ),

        'segmentation',
        apply( SetContent, segmentation_content),

        'folds', SetContent( # sulci, gyri
          "{graph_version}", SetDefaultAttributeValue( 'graph_version', default_graph_version ), SetContent(
          "L<subject>", SetType( 'Left Cortical folds graph' ), SetWeakAttr( 'side', 'left', 'labelled', 'No', 'manually_labelled', 'No', 'automatically_labelled', 'No',  ),
          "R<subject>", SetType( 'Right Cortical folds graph' ), SetWeakAttr( 'side', 'right',  'labelled', 'No' ),
          "Lsulcivoronoi_<subject>", SetType( 'Sulci Voronoi' ),
            SetWeakAttr( 'side', 'left' ),
          "Rsulcivoronoi_<subject>", SetType( 'Sulci Voronoi' ),
            SetWeakAttr( 'side', 'right' ),
          )
        ),

        ## existe-t-il un rapport avec nuclear imaging? nuclei doit il etre dans t1mri ? :
        'nuclei', #SetWeakAttr( 'category', 'nuclei' ), #SetWeakAttr( 'category', 'deepnuclei' ),
        SetContent(
          ## ces types ne sont utilises dans aucun process
          #  '<subject>_deep_nuclei_mask', SetType( 'Deep Nuclei Mask' ),
          #  '<subject>_deep_nuclei_graph', SetType( 'Deep Nuclei Graph' ),
          ## type Nucleus graph utilie par un process AnatomistShowNucleusGraph (viewer), entree, pas de writer
          "<subject>_deep_nuclei",SetType( 'Deep Nuclei Graph' ),SetWeakAttr( 'graph_type', 'NucleusArg')
          #"<subject>-nucleus",SetType( 'Nucleus graph' ),SetWeakAttr( 'graph_type', 'NucleusArg') # -> Deep Nuclei Graph
        ),

      'ROI', SetContent(),
    ), # analysis
)#t1mri

apply( insert, ( '{center}/{subject}/t1mri/{acquisition}', ) + \
  t1mri_acq_content,
)

# snapshots snapbase

insert('snapshots/morphologist/greywhite',
  "snapshot_greywhite_{subject}_{acquisition}", SetType( 'Snapshot Grey White')
)

insert('snapshots/morphologist/splitbrain',
  "snapshot_splitbrain_{subject}_{acquisition}", SetType( 'Snapshot Split Brain')
)

insert('snapshots/morphologist/meshcut',
    "snapshot_meshcut_{subject}_{acquisition}", SetType( 'Snapshot Meshcut')
)

insert('snapshots/morphologist/brainmask',
    "snapshot_brainmask_{subject}_{acquisition}", SetType( 'Snapshot Brain Mask')
)

insert('snapshots/morphologist/raw',
    "snapshot_raw_{subject}_{acquisition}", SetType( 'Snapshot Raw T1')
)

insert('snapshots/morphologist/tablet',
    "snapshot_tablet_{subject}_{acquisition}", SetType( 'Snapshot Tablet Raw T1')
)

apply( insert, ('snapshots/morphologist/pialmesh', ) + \
  snap_pialmesh_content,
)

apply( insert, ('snapshots/morphologist/sulci', ) + \
  snap_sulci_content,
)

apply( insert, ('snapshots/morphologist/whitemesh', ) + \
  snap_whitemesh_content,
)


#----------------- Registration -------------------------

#insertFirst( '{center}/{subject}/registration',
  #'RawT1-<subject>-{acquisition}', SetType( 'Referential of Raw T1 MRI' ),
  #'RawT1-<subject>_{acquisition}_TO_Talairach-ACPC', SetType( 'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist' ),
#)

#insertFirst( '{center}/registration',
  ### idem que pour subject/registration
  #'RawT1-{source.subject}-{source.acquisition}_TO_RawT1-{dest.subject}-{dest.acquisition}', SetType( 'Transform Raw T1 MRI to Raw T1 MRI' ),
#)
