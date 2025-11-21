
from brainvisa.morphologist.morpho_hierarchy import *
from brainvisa import registration


default_session = '0'
default_bids = 'run-0'
default_center = 'subjects'
default_analysis = '0'
default_sulci = '0'
default_sulci_version = '3.1'

sub = 'sub-<subject>_ses-<session>_<bids>'

raw_t1 = (
    'sub-<subject>_ses-<session>_<bids>_desc-conform_T1w', SetType('Raw T1 MRI'), SetPriorityOffset(+1),
    SetWeakAttr('normalized', 'no'),
)


def mesh_content():
    content = (
        f"{sub}_brain", SetType('Brain Mesh'), SetWeakAttr('side', 'both'),
        f"{sub}_hemi-L_pial.surf", SetType('Left Hemisphere Mesh'),
        SetWeakAttr('side', 'left', 'averaged', 'No', 'inflated', 'No',
                    'vertex_corr', 'No'), SetPriorityOffset(+1),
        f"{sub}_hemi-R_pial.surf", SetType('Right Hemisphere Mesh'),
        SetWeakAttr('side', 'right', 'averaged', 'No', 'inflated', 'No',
                    'vertex_corr', 'No'), SetPriorityOffset(+1),
        f"{sub}_hemi-L_white.surf", SetType('Left Hemisphere White Mesh'),
        SetWeakAttr('side', 'left', 'averaged', 'No', 'inflated', 'No',
                    'vertex_corr', 'No'), SetPriorityOffset(+1),
        f"{sub}_hemi-R_white.surf", SetType('Right Hemisphere White Mesh'),
        SetWeakAttr('side', 'right', 'averaged', 'No', 'inflated', 'No',
                    'vertex_corr', 'No'), SetPriorityOffset(+1),
        f"{sub}_hemi-L_white_inflated.surf", SetType('Inflated Hemisphere White Mesh'),
        SetWeakAttr('side', 'left', 'averaged', 'No', 'inflated', 'Yes',
                    'vertex_corr', 'No'),
        f"{sub}_hemi-R_white_inflated.surf", SetType('Inflated Hemisphere White Mesh'),
        SetWeakAttr('side', 'right', 'averaged', 'No', 'inflated', 'Yes',
                    'vertex_corr', 'No'),
        f"{sub}_hemi-L_white_fine.surf", SetType('Left Fine Hemisphere White Mesh'),
        SetWeakAttr('side', 'left', 'averaged', 'No', 'inflated', 'No',
                    'vertex_corr', 'No'),
        f"{sub}_hemi-R_white_fine.surf", SetType('Right Fine Hemisphere White Mesh'),
        SetWeakAttr('side', 'right', 'averaged', 'No', 'inflated', 'No',
                    'vertex_corr', 'No'),
        f"{sub}_head.surf", SetType('Head Mesh'), SetWeakAttr('side', 'both'),
        f"{sub}_hemi-L_pial_hull.surf", SetType('Hemisphere Hull Mesh'),
        SetWeakAttr('side', 'left', 'averaged', 'No', 'inflated', 'No',
                    'vertex_corr', 'No'),
        f"{sub}_hemi-R_pial_hull.surf", SetType('Hemisphere Hull Mesh'),
        SetWeakAttr('side', 'right', 'averaged', 'No', 'inflated', 'No',
                    'vertex_corr', 'No'),
        f"{sub}_pial_hull.surf", SetType('Hemisphere Hull Mesh'),
        SetWeakAttr('side', 'both', 'averaged', 'No', 'inflated', 'No',
                    'vertex_corr', 'No'),
        f"{sub}_brain_hull.surf", SetType('Brain Hull Mesh'),
        SetWeakAttr('side', 'both', 'averaged', 'No', 'inflated', 'No',
                    'vertex_corr', 'No'),
        f"{sub}_hemi-L_median.surf", SetType('Median Mesh'),
        SetWeakAttr('side', 'left', 'averaged', 'No', 'inflated', 'No',
                    'vertex_corr', 'No'),
        f"{sub}_hemi-R_median.surf", SetType('Median Mesh'),
        SetWeakAttr('side', 'right', 'averaged', 'No', 'inflated', 'No',
                    'vertex_corr', 'No'),
        f"{sub}_cortex_mni.surf", SetType('MNI Cortex Mesh'), SetWeakAttr(
            'side', 'both'),  # utilise en lecture seulement
        "*", SetType('Mesh'),
    )

    return content


def segmentation_content():
    content = (
        f"{sub}_nobias", SetType('T1 MRI Bias Corrected'),
        f"{sub}_biasfield", SetType('T1 MRI Bias Field'),
        f"{sub}_whiteridge", SetType('T1 MRI White Matter Ridges'),
        f"{sub}_variance", SetType('T1 MRI Variance'),
        f"{sub}_edges", SetType('T1 MRI Edges'),
        f"{sub}_mean_curvature", SetType('T1 MRI Mean Curvature'),
        f"{sub}_hfiltered", SetType('T1 MRI Filtered For Histo'),
        f"{sub}_nobias", SetType('Histogram'),
        f"{sub}_nobias", SetType('Histo Analysis'),
        f"{sub}_brain", SetType('T1 Brain Mask'), SetWeakAttr('side', 'both'),
        f"{sub}_skull_stripped", SetType('Raw T1 MRI Brain Masked'),
        SetWeakAttr('side', 'both', 'skull_stripped', 'yes'),
        f"{sub}_hemi-L_grey_white",
        SetType('Left Grey White Mask'), SetWeakAttr('side', 'left'),
        f"{sub}_hemi-R_grey_white",
        SetType('Right Grey White Mask'), SetWeakAttr('side', 'right'),
        f"{sub}_cortex",
        SetType('Both CSF+GREY Mask'), SetWeakAttr('side', 'both'),
        f"{sub}_hemi-L_cortex",
        SetType('Left CSF+GREY Mask'), SetWeakAttr('side', 'left'),
        f"{sub}_hemi-R_cortex",
        SetType('Right CSF+GREY Mask'), SetWeakAttr('side', 'right'),
        f"{sub}_csf", SetType('Both CSF Mask'), SetWeakAttr('side', 'both'),
        f"{sub}_hemi-L_csf", SetType('Left CSF Mask'), SetWeakAttr('side', 'left'),
        f"{sub}_hemi-R_csf", SetType('Right CSF Mask'), SetWeakAttr('side', 'right'),
        f"{sub}_hemi-L_skeleton",
        SetType('Left Cortex Skeleton'), SetWeakAttr('side', 'left'),
        f"{sub}_hemi-R_skeleton",
        SetType('Right Cortex Skeleton'), SetWeakAttr('side', 'right'),
        f"{sub}_hemi-L_roots", SetType(
            'Left Cortex Catchment Bassins'), SetWeakAttr('side', 'left'),
        f"{sub}_hemi-R_roots", SetType(
            'Right Cortex Catchment Bassins'), SetWeakAttr('side', 'right'),
        f"{sub}_voronoi", SetType('Split Brain Mask'),
        f"{sub}_head", SetType('Head Mask'),
        f"{sub}_hemi-L_white_curv.shape", SetType(
            'White Curvature Texture'), SetWeakAttr('side', 'left'),
        f"{sub}_hemi-R_white_curv.shape", SetType(
            'White Curvature Texture'), SetWeakAttr('side', 'right'),
        f"{sub}_hemi-L_white_depth.shape", SetType(
            'White Depth Texture'), SetWeakAttr('side', 'left'),
        f"{sub}_hemi-R_white_depth.shape", SetType(
            'White Depth Texture'), SetWeakAttr('side', 'right'),
        f"{sub}_hemi-L_gyri_resampled.shape", SetType(
            'Resampled Hemisphere Gyri Texture'), SetWeakAttr('side', 'left'),
        f"{sub}_hemi-R_gyri_resampled.shape", SetType(
            'Resampled Hemisphere Gyri Texture'), SetWeakAttr('side', 'right'),
        f"{sub}_gyri_resampled.shape", SetType(
            'Resampled Hemisphere Gyri Texture'), SetWeakAttr('side', 'both'),
        f"{sub}_hemi-L_gw_interface", SetType(
            'Grey White Mid-Interface Volume'), SetWeakAttr('side', 'left'),
        f"{sub}_hemi-R_gw_interface", SetType(
            'Grey White Mid-Interface Volume'), SetWeakAttr('side', 'right'),
        f"{sub}_lesiondistance", SetType('Lesion distance map'),
        f"{sub}_corpus_callosum_mask", SetType('Corpus Callosum mask'),
        f"{sub}_ventricles", SetType('Ventricles Mask'),
        f"{sub}_sul-{{sulci_recognition_session}}_brain_volumes",
        SetType('Brain volumetry measurements'),
        f"{sub}_brain_volumes", SetType('Brain volumetry measurements'),
    )

    return content


def labeled_sulci_content(auto):
    sulc = f'{sub}_sul-<sulci_recognition_session>'
    content = [
        # SULCI - labelled graphs, siRelax folds energy, segmentation
        f'{sulc}_hemi-L_{auto}', SetType(
            'Labelled Cortical folds graph'), SetWeakAttr('side', 'left', 'parallel_recognition', 'No'),
        f'{sulc}_hemi-R_{auto}', SetType(
            'Labelled Cortical folds graph'), SetWeakAttr('side', 'right', 'parallel_recognition', 'No'),
    ]

    if auto == 'auto':
        content += [
            f'{sulc}_hemi-L_auto', SetType(
                'siRelax Fold Energy'), SetWeakAttr('side', 'left'),
            f'{sulc}_hemi-R_auto', SetType(
                'siRelax Fold Energy'), SetWeakAttr('side', 'right'),
            f'{sulc}_hemi-L_auto_proba',
            SetType('Sulci Labels Segmentwise Posterior Probabilities'),
            SetWeakAttr('side', 'left'),
            f'{sulc}_hemi-R_auto_proba',
            SetType('Sulci Labels Segmentwise Posterior Probabilities'),
            SetWeakAttr('side', 'right'),
            f'{sulc}_hemi-L_auto_Tal_TO_SPAM',
            SetType('Sulci Talairach to Global SPAM transformation'),
            SetWeakAttr('side', 'left'),
            f'{sulc}_hemi-R_auto_Tal_TO_SPAM',
            SetType('Sulci Talairach to Global SPAM transformation'),
            SetWeakAttr('side', 'right'),
            f'{sulc}_hemi-L_auto_T1_TO_SPAM',
            SetType('Raw T1 to Global SPAM transformation'),
            SetWeakAttr('side', 'left'),
            f'{sulc}_hemi-R_auto_T1_TO_SPAM',
            SetType('Raw T1 to Global SPAM transformation'),
            SetWeakAttr('side', 'right'),
            f'{sulc}_hemi-L_auto', SetType(
                'Referential of Labelled Cortical folds graph'), SetWeakAttr('side', 'left', 'parallel_recognition', 'No'),
            f'{sulc}_hemi-R_auto', SetType(
                'Referential of Labelled Cortical folds graph'), SetWeakAttr('side', 'right', 'parallel_recognition', 'No'),

            f'{sulc}_hemi-L_auto_global_TO_local',
            SetType('Sulci Local SPAM transformations Directory'),
            SetWeakAttr('side', 'left'), SetContent(
                '*_{sulcus}', SetType('Sulci Global to Local SPAM transformation'),
            ),
            f'{sulc}_hemi-R_auto_global_TO_local',
            SetType('Sulci Local SPAM transformations Directory'),
            SetWeakAttr('side', 'right'), SetContent(
                '*_{sulcus}', SetType('Sulci Global to Local SPAM transformation'),
            ),
        ]

    content += [
        f'{sulc}_{auto}_sulcal_morphometry',
        SetType('Sulcal morphometry measurements'),
        SetWeakAttr('side', 'both'),

        'segmentation', SetContent(
            f'{sulc}_hemi-L_sulci_{auto}',
            SetType('Sulci Volume'), SetWeakAttr('side', 'left'),
            f'{sulc}_hemi-R_sulci_{auto}',
            SetType('Sulci Volume'), SetWeakAttr('side', 'right'),
            f'{sulc}_hemi-L_bottom_{auto}',
            SetType('Bottom Volume'), SetWeakAttr('side', 'left'),
            f'{sulc}_hemi-R_bottom_{auto}',
            SetType('Bottom Volume'), SetWeakAttr('side', 'right'),
            f'{sulc}_hemi-L_hull_junction_{auto}',
            SetType('Hull Junction Volume'), SetWeakAttr('side', 'left'),
            f'{sulc}_hemi-R_hull_junction_{auto}',
            SetType('Hull Junction Volume'), SetWeakAttr('side', 'right'),
            f'{sulc}_hemi-L_simple_surface_{auto}',
            SetType('Simple Surface Volume'), SetWeakAttr('side', 'left'),
            f'{sulc}_hemi-R_simple_surface_{auto}',
            SetType('Simple Surface Volume'), SetWeakAttr('side', 'right'),
        ),

        "*.data",
    ]

    return content


def sulci_content():
    return (
        'sul-{sulci_recognition_session}_auto',
        SetDefaultAttributeValue('sulci_recognition_session', default_sulci),
        SetWeakAttr(
            'labelled', 'Yes', 'manually_labelled', 'No',
            'automatically_labelled', 'Yes', 'best', 'No'),
        SetContent(*labeled_sulci_content('auto')),

        'sul-{sulci_recognition_session}_manual', SetDefaultAttributeValue('sulci_recognition_session', default_sulci), SetWeakAttr(
            'labelled', 'Yes', 'manually_labelled', 'Yes',
            'automatically_labelled', 'No', 'best', 'No'),
        SetContent(*labeled_sulci_content('manual')),

        'sul-{sulci_recognition_session}_best', SetDefaultAttributeValue('sulci_recognition_session', default_sulci), SetWeakAttr(
            'labelled', 'Yes', 'manually_labelled', 'No',
            'automatically_labelled', 'Yes', 'best', 'Yes'), SetPriorityOffset(-1),
        SetContent(*best_labeled_sulci_content()),

    )


def t1mri_acq_content():

    content = (
        f"{sub}", SetType('Commissure coordinates'),
        f'{sub}_normalized_{{normalization}}',
        SetType('Raw T1 MRI'), SetWeakAttr('normalized', 'yes'),
        f"{sub}_sn", SetType('SPM2 normalization matrix'),
        f"{sub}_job_anat_normalization", SetType('SPM2 parameters'),
        f"{sub}_fsl", SetType('FSL Transformation'),
        # lesion mask
        f"{sub}_lesion", SetType('Lesion Mask'), SetPriorityOffset(+1),
        SetWeakAttr('normalized', 'no'),
        f"{sub}_lesion_normalized_{{normalization}}",
        SetType('Lesion Mask'), SetWeakAttr('normalized', 'yes'),

        'registration', SetType('Registration Directory'),
        SetContent(
            f'{sub}_T1w_TO_unknown_atlas_WITH_bal',
            SetType("baladin Transformation"),
            f'{sub}_T1w', SetType('Referential of Raw T1 MRI'),
            f'{sub}_T1w_TO_Talairach-ACPC',
            SetType('Transform Raw T1 MRI to Talairach-AC/PC-Anatomist'),
            f'{sub}_T1w_TO_MNI152',
            SetType('Transform Raw T1 MRI to Talairach-MNI template-SPM'),

            f'{sub}_T1w_TO_scanner',
            SetType('Transformation to Scanner Based Referential'),
            f'{sub}_T1w_scanner', SetType('Scanner Based Referential'), SetWeakAttr(
                'destination_referential', str(registration.talairachMNIReferentialId)),
        ),  # registration

        "ana-{analysis}", SetType('T1 MRI Analysis Directory'),
        SetDefaultAttributeValue('analysis', default_analysis),
        SetNonMandatoryKeyAttribute('analysis'),
        SetContent(  # processing results in analysis
            f'{sub}_sul-{{sulci_recognition_session}}_morphologist_report',
            SetType('Morphologist report'),
            f'{sub}_morphologist_report', SetType('Morphologist report'),
            f'{sub}_sul-{{sulci_recognition_session}}_morphologist_report',
            SetType('Morphologist JSON report'),
            f'{sub}_morphologist_report', SetType('Morphologist JSON report'),

            'segmentation', SetContent(*segmentation_content()),
            'mesh', SetContent(*mesh_content()),

            'folds', SetContent(  # sulci, gyri
                "{graph_version}",
                SetDefaultAttributeValue('graph_version',
                                         default_graph_version),
                SetContent(
                    f"{sub}_hemi-L", SetType('Cortical folds graph'), SetWeakAttr('side', 'left', 'labelled', 'No'),
                    f"{sub}_hemi-R", SetType('Cortical folds graph'), SetWeakAttr('side', 'right', 'labelled', 'No'),
                    f"{sub}_hemi-L_sulcivoronoi", SetType(
                        'Sulci Voronoi'), SetWeakAttr('side', 'left'),
                    f"{sub}_hemi-R_sulcivoronoi", SetType(
                        'Sulci Voronoi'), SetWeakAttr('side', 'right'),
                    f"{sub}_hemi-L_sulci_mask", SetType(
                        'Left Sulci Mask'), SetWeakAttr('side', 'left'),
                    f"{sub}_hemi-R_sulci_mask", SetType(
                        'Right Sulci Mask'), SetWeakAttr('side', 'right'),

                    *sulci_content(),
                ),
            ),  # folds

        ),  # analysis
    )

    return content


def snap_content(snap_type, di_type):
    content = (
        f"{sub}_snapshot_{snap_type}", SetType(
            di_type), SetWeakAttr('side', 'left', 'processing', 'morphologist'),
    )

    return content


def morpho_snapshots():
    content = (
        'greywhite',
        SetContent(
            *snap_content('greywhite', 'Snapshot Grey White'),
        ),

        'splitbrain',
        SetContent(
            *snap_content('splitbrain', 'Snapshot Split brain'),
        ),

        'meshcut',
        SetContent(
            *snap_content('meshcut', 'Snapshot MeshCut'),
        ),

        'brainmask',
        SetContent(
            *snap_content('brainmask', 'Snapshot Brain Mask'),
        ),

        'raw',
        SetContent(
            *snap_content('raw', 'Snapshot Raw T1'),
        ),

        'tablet',
        SetContent(
            *snap_content('tablet', 'Snapshot Tablet Raw T1'),
        ),

        'pialmesh', SetContent(
            *snap_content('left_pialmesh', 'Snapshot Pial Mesh'),
            SetWeakAttr('side', 'left'),
            *snap_content('right_pialmesh', 'Snapshot Pial Mesh'),
            SetWeakAttr('side', 'right'),
        ),
        'sulci', SetContent(
            *snap_content('left_sulci', 'Snapshot Sulci'),
            SetWeakAttr('side', 'left'),
            *snap_content('right_sulci', 'Snapshot Sulci'),
            SetWeakAttr('side', 'right'),
        ),
        'whitemesh', SetContent(
            *snap_content('left_whitemesh', 'Snapshot White Mesh'),
            SetWeakAttr('side', 'left'),
            *snap_content('right_whitemesh', 'Snapshot White Mesh'),
            SetWeakAttr('side', 'right'),
        ),

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

    return content


#==============================================================================
# TABLES
#==============================================================================

def tables_content():
    return (
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
        "morphologist_normative_brain_volumes_stats",
        SetType('Normative brain volumes stats'),
    )


hierarchy = (
    SetWeakAttr('database', '%f'),
    SetContent(
        *db_entries(),
        'analyzes',
        SetContent(
            # '{analysis}', SetType( 'Analysis Dir' ),#WARNING : all directory after analyzes was catch by it
            # SetContent(# Set Content must be present even if it is empty, otherwise it is impossible to insert something in subject directory
            #),
        ),
        'snapshots', SetType('Snapshots Dir'),
        SetContent(
            'morphologist', SetContent(
                'ana-{analysis}', SetContent(
                    *morpho_snapshots()
                ),
            ),
            # snapbase qc spm
            '{processing}', SetContent(
                'ana-{analysis}',
                SetContent(
                    "qc_<processing>",
                    SetType('Snapshots Probability Map Quality Scores'),
                ),
            ),
        ),
        'tables', SetType('Tables Directory'),
        SetContent(
            '{acquisition}',
            SetContent(*tables_content())
        ),
        "group_analysis",
        SetContent(
            '{group_of_subjects}',
            SetContent(
                '<group_of_subjects>_group', SetType('Group definition'),
            ),
        ),
        'qc',
        SetContent(
            'qc', SetType('QC table'),
        ),

        'sub-{subject}', SetFileNameStrongAttribute('subject'),
        SetType('Subject'),
        SetDefaultAttributeValue('center', default_center),
        SetContent(
            'ses-{session}',
            SetDefaultAttributeValue('session', default_session),
            SetContent(
                '{bids}',
                SetDefaultAttributeValue('bids', default_bids),
                DeclareAttributes('time_point', 'time_duration',
                                  'rescan', 'acquisition_date'),
                SetContent(
                    # The "registration" directory in each subject contains:
                    #   - all the referentials related to this subjects
                    #   - all the transformations that links two referetials
                    #     from this directory or from the common referentials
                    #     directory (in "shared" directory)
                    'registration', SetType('Registration Directory'),
                    SetContent(*registration_content()),
                    *raw_t1,
                    *t1mri_acq_content(),
                ),
            ),
        ),
    ),
)

