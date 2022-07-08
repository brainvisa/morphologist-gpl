
from brainvisa.data.ontology.base import *
from brainvisa import registration

#------------------------------------------------------------------------------
# New referentials and transformations organization
#------------------------------------------------------------------------------

registration_content = lambda: (
    '*', SetType('Referential'),
    '*', SetType('Transformation matrix'),
)


mesh_content = lambda: (
    "<subject>_brain", SetType('Brain Mesh'), SetWeakAttr('side', 'both'),
    "<subject>_Lhemi", SetType('Left Hemisphere Mesh'),
    SetWeakAttr('side', 'left', 'averaged', 'No', 'inflated', 'No',
                'vertex_corr', 'No'), SetPriorityOffset(+1),
    "<subject>_Rhemi", SetType('Right Hemisphere Mesh'),
    SetWeakAttr('side', 'right', 'averaged', 'No', 'inflated', 'No',
                'vertex_corr', 'No'), SetPriorityOffset(+1),
    "<subject>_Lwhite", SetType('Left Hemisphere White Mesh'),
    SetWeakAttr('side', 'left', 'averaged', 'No', 'inflated', 'No',
                'vertex_corr', 'No'), SetPriorityOffset(+1),
    "<subject>_Rwhite", SetType('Right Hemisphere White Mesh'),
    SetWeakAttr('side', 'right', 'averaged', 'No', 'inflated', 'No',
                'vertex_corr', 'No'), SetPriorityOffset(+1),
    "<subject>_Lwhite_inflated", SetType('Inflated Hemisphere White Mesh'),
    SetWeakAttr('side', 'left', 'averaged', 'No', 'inflated', 'Yes',
                'vertex_corr', 'No'),
    "<subject>_Rwhite_inflated", SetType('Inflated Hemisphere White Mesh'),
    SetWeakAttr('side', 'right', 'averaged', 'No', 'inflated', 'Yes',
                'vertex_corr', 'No'),
    "<subject>_Lwhite_fine", SetType('Left Fine Hemisphere White Mesh'),
    SetWeakAttr('side', 'left', 'averaged', 'No', 'inflated', 'No',
                'vertex_corr', 'No'),
    "<subject>_Rwhite_fine", SetType('Right Fine Hemisphere White Mesh'),
    SetWeakAttr('side', 'right', 'averaged', 'No', 'inflated', 'No',
                'vertex_corr', 'No'),
    "<subject>_head", SetType('Head Mesh'), SetWeakAttr('side', 'both'),
    "<subject>_Lhemi_hull", SetType('Hemisphere Hull Mesh'),
    SetWeakAttr('side', 'left', 'averaged', 'No', 'inflated', 'No',
                'vertex_corr', 'No'),
    "<subject>_Rhemi_hull", SetType('Hemisphere Hull Mesh'),
    SetWeakAttr('side', 'right', 'averaged', 'No', 'inflated', 'No',
                'vertex_corr', 'No'),
    "<subject>_Bhemi_hull", SetType('Hemisphere Hull Mesh'),
    SetWeakAttr('side', 'both', 'averaged', 'No', 'inflated', 'No',
                'vertex_corr', 'No'),
    "<subject>_brain_hull", SetType('Brain Hull Mesh'),
    SetWeakAttr('side', 'both', 'averaged', 'No', 'inflated', 'No',
                'vertex_corr', 'No'),
    "<subject>_Lmedian", SetType('Median Mesh'),
    SetWeakAttr('side', 'left', 'averaged', 'No', 'inflated', 'No',
                'vertex_corr', 'No'),
    "<subject>_Rmedian", SetType('Median Mesh'),
    SetWeakAttr('side', 'right', 'averaged', 'No', 'inflated', 'No',
                'vertex_corr', 'No'),
    "cortex_<subject>_mni", SetType('MNI Cortex Mesh'), SetWeakAttr(
        'side', 'both'),  # utilise en lecture seulement
    "*", SetType('Mesh'),
)


segmentation_content = lambda: (
    "brain_<subject>", SetType('T1 Brain Mask'), SetWeakAttr('side', 'both'),
    "skull_stripped_<subject>", SetType('Raw T1 MRI Brain Masked'), SetWeakAttr('side', 'both', 'skull_stripped', 'yes'),
    "Rgrey_white_<subject>", SetType(
        'Right Grey White Mask'), SetWeakAttr('side', 'right'),
    "Lgrey_white_<subject>", SetType(
        'Left Grey White Mask'), SetWeakAttr('side', 'left'),
    "cortex_<subject>", SetType(
        'Both CSF+GREY Mask'), SetWeakAttr('side', 'both'),
    "Lcortex_<subject>", SetType(
        'Left CSF+GREY Mask'), SetWeakAttr('side', 'left'),
    "Rcortex_<subject>", SetType(
        'Right CSF+GREY Mask'), SetWeakAttr('side', 'right'),
    "csf_<subject>", SetType('Both CSF Mask'), SetWeakAttr('side', 'both'),
    "Lcsf_<subject>", SetType('Left CSF Mask'), SetWeakAttr('side', 'left'),
    "Rcsf_<subject>", SetType('Right CSF Mask'), SetWeakAttr('side', 'right'),
    "Lskeleton_<subject>", SetType(
        'Left Cortex Skeleton'), SetWeakAttr('side', 'left'),
    "Rskeleton_<subject>", SetType(
        'Right Cortex Skeleton'), SetWeakAttr('side', 'right'),
    "Lroots_<subject>", SetType(
        'Left Cortex Catchment Bassins'), SetWeakAttr('side', 'left'),
    "Rroots_<subject>", SetType(
        'Right Cortex Catchment Bassins'), SetWeakAttr('side', 'right'),
    "voronoi_<subject>", SetType(
        'Split Brain Mask'), SetWeakAttr('side', 'both'),
    "head_<subject>", SetType('Head Mask'),
    "<subject>_Lwhite_curv", SetType(
        'White Curvature Texture'), SetWeakAttr('side', 'left'),
    "<subject>_Rwhite_curv", SetType(
        'White Curvature Texture'), SetWeakAttr('side', 'right'),
    "<subject>_Lwhite_depth", SetType(
        'White Depth Texture'), SetWeakAttr('side', 'left'),
    "<subject>_Rwhite_depth", SetType(
        'White Depth Texture'), SetWeakAttr('side', 'right'),
    "<subject>_Lgyri_resampled", SetType(
        'Resampled Hemisphere Gyri Texture'), SetWeakAttr('side', 'left'),
    "<subject>_Rgyri_resampled", SetType(
        'Resampled Hemisphere Gyri Texture'), SetWeakAttr('side', 'right'),
    "<subject>_Bgyri_resampled", SetType(
        'Resampled Hemisphere Gyri Texture'), SetWeakAttr('side', 'both'),
    "Lgw_interface_<subject>", SetType(
        'Grey White Mid-Interface Volume'), SetWeakAttr('side', 'left'),
    "Rgw_interface_<subject>", SetType(
        'Grey White Mid-Interface Volume'), SetWeakAttr('side', 'right'),
    "lesiondistance_<subject>", SetType('Lesion distance map'),
    "corpus_callosum_mask", SetType('Corpus Callosum mask'),
    "ventricles_<subject>", SetType('Ventricles Mask'),
    "brain_volumes_<subject>", SetType('Brain volumetry measurements'),

    'mesh', SetContent(*mesh_content()),

)

t1mri_acq_content = lambda: (
    # t1mri before processing in acquisition level
    #"<subject>", SetType( 'Raw T1 MRI' ), SetPriorityOffset( +1 ), SetWeakAttr( 'normalized', 'no' ),
    "<subject>", SetType('Commissure coordinates'),
    "normalized_{normalization}_<subject>", SetType(
        'Raw T1 MRI'), SetWeakAttr('normalized', 'yes'),
    "<subject>_sn", SetType('SPM2 normalization matrix'),
    "<subject>_job_anat_normalization", SetType('SPM2 parameters'),
    "<subject>_fsl", SetType('FSL Transformation'),
    # lesion mask
    "lesion_<subject>", SetType(
        'Lesion Mask'), SetPriorityOffset(+1), SetWeakAttr('normalized', 'no'),
    "lesion_normalized_{normalization}_<subject>", SetType(
        'Lesion Mask'), SetWeakAttr('normalized', 'yes'),

    # "r<subject>", SetType( 'Registered Raw T1 MRI with fMRI' ), SetWeakAttr( 'fMRI_register', 'Yes' ),
    # "wr<subject>", SetType( 'Registered Raw T1 MRI with fMRI' ), SetWeakAttr( 'fMRI_register', 'Yes' ),
    'registration', SetType('Registration Directory'),
    SetContent(
        'RawT1-<subject>_<acquisition>_TO_unknown_atlas_WITH_bal',
        SetType("baladin Transformation"),
        'RawT1-<subject>_<acquisition>', SetType('Referential of Raw T1 MRI'),
        'RawT1-<subject>_<acquisition>_TO_Talairach-ACPC', SetType(
            'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist'),
        'RawT1-<subject>_<acquisition>_TO_Talairach-MNI', SetType(
            'Transform Raw T1 MRI to Talairach-MNI template-SPM'),

        'RawT1-<subject>_<acquisition>_TO_Scanner_Based', SetType(
            'Transformation to Scanner Based Referential'),
        'RawT1-<subject>_<acquisition>_Scanner_Based', SetType('Scanner Based Referential'), SetWeakAttr(
            'destination_referential', str(registration.talairachMNIReferentialId)),
    ),

    "{analysis}", SetType('T1 MRI Analysis Directory'),
    SetDefaultAttributeValue('analysis', default_analysis),
    SetNonMandatoryKeyAttribute('analysis'),
    SetContent(  # processing results in analysis
        "nobias_<subject>", SetType('T1 MRI Bias Corrected'),
        "biasfield_<subject>", SetType('T1 MRI Bias Field'),
        "whiteridge_<subject>", SetType('T1 MRI White Matter Ridges'),
        "variance_<subject>", SetType('T1 MRI Variance'),
        "edges_<subject>", SetType('T1 MRI Edges'),
        "mean_curvature_<subject>", SetType('T1 MRI Mean Curvature'),
        "hfiltered_<subject>", SetType('T1 MRI Filtered For Histo'),
        "nobias_<subject>", SetType('Histogram'),
        "nobias_<subject>", SetType('Histo Analysis'),

        'segmentation', SetContent(*segmentation_content()),

        'folds', SetContent(  # sulci, gyri
            "{graph_version}",
            SetDefaultAttributeValue('graph_version', default_graph_version),
            SetContent(
                "L<subject>", SetType('Cortical folds graph'), SetWeakAttr('side', 'left', 'labelled', 'No'),
                "R<subject>", SetType('Cortical folds graph'), SetWeakAttr('side', 'right', 'labelled', 'No'),
                "Lsulcivoronoi_<subject>", SetType(
                    'Sulci Voronoi'), SetWeakAttr('side', 'left'),
                "Rsulcivoronoi_<subject>", SetType(
                    'Sulci Voronoi'), SetWeakAttr('side', 'right'),
                "Lsulci_mask_<subject>", SetType(
                    'Left Sulci Mask'), SetWeakAttr('side', 'left'),
                "Rsulci_mask_<subject>", SetType(
                    'Right Sulci Mask'), SetWeakAttr('side', 'right')
            )
        ),  # folds

        'nuclei', SetContent(  # SetWeakAttr( 'category', 'nuclei' ), #SetWeakAttr( 'category', 'deepnuclei' ),
            # ces types ne sont utilises dans aucun process
            #  '<subject>_deep_nuclei_mask', SetType( 'Deep Nuclei Mask' ),
            #  '<subject>_deep_nuclei_graph', SetType( 'Deep Nuclei Graph' ),
            # type Nucleus graph utilie par un process AnatomistShowNucleusGraph (viewer), entree, pas de writer
            "<subject>_deep_nuclei", SetType(
                'Deep Nuclei Graph'), SetWeakAttr('graph_type', 'NucleusArg')
            #"<subject>-nucleus",SetType( 'Nucleus graph' ),SetWeakAttr( 'graph_type', 'NucleusArg') # -> Deep Nuclei Graph
        ),  # nuclei

        'ROI', SetContent(),

    ),  # analysis
)  # t1mri


#==================================================================================================================================
# SNAPSHOTS
#==================================================================================================================================

# snapshots snapbase morphologist
snap_pialmesh_content = lambda: (
    "snapshot_left_pialmesh_{subject}_<acquisition>", SetType(
        'Snapshot Pial Mesh'), SetWeakAttr('side', 'left', 'processing', 'morphologist'),
    "snapshot_right_pialmesh_{subject}_<acquisition>", SetType(
        'Snapshot Pial Mesh'), SetWeakAttr('side', 'right', 'processing', 'morphologist'),
)
snap_sulci_content = lambda: (
    "snapshot_left_sulci_{subject}_<acquisition>", SetType(
        'Snapshot Sulci'), SetWeakAttr('side', 'left', 'processing', 'morphologist'),
    "snapshot_right_sulci_{subject}_<acquisition>", SetType(
        'Snapshot Sulci'), SetWeakAttr('side', 'right', 'processing', 'morphologist'),
)
snap_whitemesh_content = lambda: (
    "snapshot_left_whitemesh_{subject}_<acquisition>", SetType(
        'Snapshot White Mesh'), SetWeakAttr('side', 'left', 'processing', 'morphologist'),
    "snapshot_right_whitemesh_{subject}_<acquisition>", SetType(
        'Snapshot White Mesh'), SetWeakAttr('side', 'right', 'processing', 'morphologist'),
)


morpho_snapshots = lambda: (
    'greywhite',
    SetContent(
        "snapshot_greywhite_{subject}_<acquisition>",
        SetType('Snapshot Grey White'),
        SetWeakAttr('processing', 'morphologist')
    ),

    'splitbrain',
    SetContent(
        "snapshot_splitbrain_{subject}_<acquisition>",
        SetType('Snapshot Split Brain'),
        SetWeakAttr('processing', 'morphologist')
    ),

    'meshcut',
    SetContent(
        "snapshot_meshcut_{subject}_<acquisition>", SetType('Snapshot Meshcut'),
        SetWeakAttr('processing', 'morphologist')
    ),

    'brainmask',
    SetContent(
        "snapshot_brainmask_{subject}_<acquisition>",
        SetType('Snapshot Brain Mask'),
        SetWeakAttr('processing', 'morphologist')
    ),

    'raw',
    SetContent(
        "snapshot_raw_{subject}_<acquisition>", SetType('Snapshot Raw T1'),
        SetWeakAttr('processing', 'morphologist')
    ),

    'tablet',
    SetContent(
        "snapshot_tablet_{subject}_<acquisition>",
        SetType('Snapshot Tablet Raw T1'),
        SetWeakAttr('processing', 'morphologist')
    ),

    'pialmesh', SetContent(*snap_pialmesh_content()),
    'sulci', SetContent(*snap_sulci_content()),
    'whitemesh', SetContent(*snap_whitemesh_content()),

    # snapbase qc morphologist
    'greywhite',
    SetContent(
        "qc_greywhite", SetType('Snapshots Grey White Quality Scores'),
        SetWeakAttr('processing', 'morphologist')
    ),
    'splitbrain',
    SetContent(
        "qc_splitbrain", SetType('Snapshots Split Brain Quality Scores'),
        SetWeakAttr('processing', 'morphologist')
    ),
    'meshcut',
    SetContent(
        "qc_meshcut", SetType('Snapshots Meshcut Quality Scores'),
        SetWeakAttr('processing', 'morphologist')
    ),
    'pialmesh',
    SetContent(
        "qc_pialmesh", SetType('Snapshots Pial Mesh Quality Scores'),
        SetWeakAttr('processing', 'morphologist')
    ),
    'sulci',
    SetContent(
        "qc_sulci", SetType('Snapshots Sulci Quality Scores'),
      SetWeakAttr('processing', 'morphologist')
    ),
    'whitemesh',
    SetContent(
        "qc_whitemesh", SetType('Snapshots White Mesh Quality Scores'),
        SetWeakAttr('processing', 'morphologist')
    ),

    'whiteMatter',
    SetContent(
        "snapshot_<processing>_white_{subject}_<acquisition>",
        SetType('Snapshot Probability Map'),
        SetWeakAttr('tissue_class', 'white')
    ),
    'greyMatter',
    SetContent(
        "snapshot_<processing>_grey_{subject}_<acquisition>",
        SetType('Snapshot Probability Map'),
        SetWeakAttr('tissue_class', 'grey')
    ),
    'csf',
    SetContent(
        "snapshot_<processing>_csf_{subject}_<acquisition>",
        SetType('Snapshot Probability Map'),
        SetWeakAttr('tissue_class', 'csf')
    ),
)


#==================================================================================================================================
# TABLES
#==================================================================================================================================

tables_content = lambda: (
    "sulcalopenings_morphologist",
    SetType('Sulcal Openings Table'),
    SetWeakAttr('processing', 'morphologist'),
    "tissues_volumes_morphologist",
    SetType('Global Volumetry Table'),
    SetWeakAttr('processing', 'morphologist'),
    "history_sulcalopenings_morphologist",
    SetType('History Sulcal Openings Table'),
    SetWeakAttr('processing', 'morphologist'),
    "history_tissues_volumes_morphologist",
    SetType('History Global Volumetry Table'),
    SetWeakAttr('processing', 'morphologist'),
    "tissues_volumes_{processing}",
    SetType('Global Volumetry Table'),
    "history_tissues_volumes_{processing}",
    SetType('History Global Volumetry Table'),
    "snapshots_features_morphologist",
    SetType('Snapshots Features Table'),
    SetWeakAttr('processing', 'morphologist'),
    "snapshots_features_{processing}",
    SetType('Snapshots Features Table'),
)


# ========
# SULCI
# ========

auto_labeled_sulci_content = lambda: (
    # SULCI - labelled graphs, siRelax folds energy, segmentation
    'L<subject>_<sulci_recognition_session>_auto', SetType(
        'Labelled Cortical folds graph'), SetWeakAttr('side', 'left', 'parallel_recognition', 'No'),
    'R<subject>_<sulci_recognition_session>_auto', SetType(
        'Labelled Cortical folds graph'), SetWeakAttr('side', 'right', 'parallel_recognition', 'No'),

    'L<subject>_<sulci_recognition_session>_auto', SetType(
        'siRelax Fold Energy'), SetWeakAttr('side', 'left'),
    'R<subject>_<sulci_recognition_session>_auto', SetType(
        'siRelax Fold Energy'), SetWeakAttr('side', 'right'),
    'L<subject>_<sulci_recognition_session>_auto_proba',
    SetType('Sulci Labels Segmentwise Posterior Probabilities'),
    SetWeakAttr('side', 'left'),
    'R<subject>_<sulci_recognition_session>_auto_proba',
    SetType('Sulci Labels Segmentwise Posterior Probabilities'),
    SetWeakAttr('side', 'right'),
    'L<subject>_<sulci_recognition_session>_auto_Tal_TO_SPAM',
    SetType('Sulci Talairach to Global SPAM transformation'),
    SetWeakAttr('side', 'left'),
    'R<subject>_<sulci_recognition_session>_auto_Tal_TO_SPAM',
    SetType('Sulci Talairach to Global SPAM transformation'),
    SetWeakAttr('side', 'right'),
    'L<subject>_<sulci_recognition_session>_auto_T1_TO_SPAM',
    SetType('Raw T1 to Global SPAM transformation'),
    SetWeakAttr('side', 'left'),
    'R<subject>_<sulci_recognition_session>_auto_T1_TO_SPAM',
    SetType('Raw T1 to Global SPAM transformation'),
    SetWeakAttr('side', 'right'),
    'L<subject>_<sulci_recognition_session>_auto', SetType(
        'Referential of Labelled Cortical folds graph'), SetWeakAttr('side', 'left', 'parallel_recognition', 'No'),
    'R<subject>_<sulci_recognition_session>_auto', SetType(
        'Referential of Labelled Cortical folds graph'), SetWeakAttr('side', 'right', 'parallel_recognition', 'No'),

    'L<subject>_<sulci_recognition_session>_auto_global_TO_local',
    SetType('Sulci Local SPAM transformations Directory'),
    SetWeakAttr('side', 'left'), SetContent(
        '*_{sulcus}', SetType('Sulci Global to Local SPAM transformation'),
    ),
    'R<subject>_<sulci_recognition_session>_auto_global_TO_local',
    SetType('Sulci Local SPAM transformations Directory'),
    SetWeakAttr('side', 'right'), SetContent(
        '*_{sulcus}', SetType('Sulci Global to Local SPAM transformation'),
    ),
    '<subject>_<sulci_recognition_session>_auto_sulcal_morphometry', SetType(
        'Sulcal morphometry measurements'), SetWeakAttr('side', 'both'),

    'segmentation', SetContent(
        "LSulci_<subject>_<sulci_recognition_session>_auto", SetType(
            'Sulci Volume'), SetWeakAttr('side', 'left'),
        "RSulci_<subject>_<sulci_recognition_session>_auto", SetType(
            'Sulci Volume'), SetWeakAttr('side', 'right'),
        "LBottom_<subject>_<sulci_recognition_session>_auto", SetType(
            'Bottom Volume'), SetWeakAttr('side', 'left'),
        "RBottom_<subject>_<sulci_recognition_session>_auto", SetType(
            'Bottom Volume'), SetWeakAttr('side', 'right'),
        "LHullJunction_<subject>_<sulci_recognition_session>_auto", SetType(
            'Hull Junction Volume'), SetWeakAttr('side', 'left'),
        "RHullJunction_<subject>_<sulci_recognition_session>_auto", SetType(
            'Hull Junction Volume'), SetWeakAttr('side', 'right'),
        "LSimpleSurface_<subject>_<sulci_recognition_session>_auto", SetType(
            'Simple Surface Volume'), SetWeakAttr('side', 'left'),
        "RSimpleSurface_<subject>_<sulci_recognition_session>_auto", SetType(
            'Simple Surface Volume'), SetWeakAttr('side', 'right'),
    ),

    "*.data",
)


manual_labeled_sulci_content = lambda: (
    # SULCI - labelled graphs, segmentation
    'L<subject>_<sulci_recognition_session>_manual', SetType(
        'Labelled Cortical folds graph'), SetWeakAttr('side', 'left', 'parallel_recognition', 'No'),
    'R<subject>_<sulci_recognition_session>_manual', SetType(
        'Labelled Cortical folds graph'), SetWeakAttr('side', 'right', 'parallel_recognition', 'No'),

    '<subject>_<sulci_recognition_session>_manual_sulcal_morphometry', SetType(
        'Sulcal morphometry measurements'), SetWeakAttr('side', 'both'),

    'segmentation', SetContent(
        "LSulci_<subject>_<sulci_recognition_session>_manual", SetType(
            'Sulci Volume'), SetWeakAttr('side', 'left'),
        "RSulci_<subject>_<sulci_recognition_session>_manual", SetType(
            'Sulci Volume'), SetWeakAttr('side', 'right'),
        "LBottom_<subject>_<sulci_recognition_session>_manual", SetType(
            'Bottom Volume'), SetWeakAttr('side', 'left'),
        "RBottom_<subject>_<sulci_recognition_session>_manual", SetType(
            'Bottom Volume'), SetWeakAttr('side', 'right'),
        "LHullJunction_<subject>_<sulci_recognition_session>_manual", SetType(
            'Hull Junction Volume'), SetWeakAttr('side', 'left'),
        "RHullJunction_<subject>_<sulci_recognition_session>_manual", SetType(
            'Hull Junction Volume'), SetWeakAttr('side', 'right'),
        "LSimpleSurface_<subject>_<sulci_recognition_session>_manual", SetType(
            'Simple Surface Volume'), SetWeakAttr('side', 'left'),
        "RSimpleSurface_<subject>_<sulci_recognition_session>_manual", SetType(
            'Simple Surface Volume'), SetWeakAttr('side', 'right'),
    ),

    "*.data"
)


best_labeled_sulci_content = lambda: (
    # SULCI - labelled graphs, siRelax folds energy, segmentation
    'L<subject>_<sulci_recognition_session>_best', SetType(
        'Labelled Cortical folds graph'), SetWeakAttr('side', 'left', 'parallel_recognition', 'No'),
    'R<subject>_<sulci_recognition_session>_best', SetType(
        'Labelled Cortical folds graph'), SetWeakAttr('side', 'right', 'parallel_recognition', 'No'),

    'L<subject>_<sulci_recognition_session>_best', SetType(
        'siRelax Fold Energy'), SetWeakAttr('side', 'left'),
    'R<subject>_<sulci_recognition_session>_best', SetType(
        'siRelax Fold Energy'), SetWeakAttr('side', 'right'),

    'segmentation', SetContent(
        "LSulci_<subject>_<sulci_recognition_session>_best", SetType(
            'Sulci Volume'), SetWeakAttr('side', 'left'),
        "RSulci_<subject>_<sulci_recognition_session>_best", SetType(
            'Sulci Volume'), SetWeakAttr('side', 'right'),
        "LBottom_<subject>_<sulci_recognition_session>_best", SetType(
            'Bottom Volume'), SetWeakAttr('side', 'left'),
        "RBottom_<subject>_<sulci_recognition_session>_best", SetType(
            'Bottom Volume'), SetWeakAttr('side', 'right'),
        "LHullJunction_<subject>_<sulci_recognition_session>_best", SetType(
            'Hull Junction Volume'), SetWeakAttr('side', 'left'),
        "RHullJunction_<subject>_<sulci_recognition_session>_best", SetType(
            'Hull Junction Volume'), SetWeakAttr('side', 'right'),
        "LSimpleSurface_<subject>_<sulci_recognition_session>_best", SetType(
            'Simple Surface Volume'), SetWeakAttr('side', 'left'),
        "RSimpleSurface_<subject>_<sulci_recognition_session>_best", SetType(
            'Simple Surface Volume'), SetWeakAttr('side', 'right'),
    ),

    "*.data"
)

