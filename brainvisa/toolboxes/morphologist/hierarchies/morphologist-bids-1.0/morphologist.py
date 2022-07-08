
from brainvisa.morphologist.morpho_hierarchy import *


raw_t1 = (
    '<subject>', SetType('Raw T1 MRI'), SetPriorityOffset(+1),
    SetWeakAttr('normalized', 'no'),
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
                '{acquisition}', SetContent(*morpho_snapshots()),
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

        # The "registration" directory in each center contains
        # all the referentials and transformations for cross-subject
        # registration.
        'registration', SetType('Registration Directory'),
        SetContent(*registration_content()),

        'sub-{subject}', SetFileNameStrongAttribute('subject'),
        SetType('Subject'),
        SetDefaultAttributeValue('center', default_center),
        SetContent(
            'ses-{session}',
            SetContent(
                # The "registration" directory in each subject contains:
                #   - all the referentials related to this subjects
                #   - all the transformations that links two referetials
                #     from this directory or from the common referentials
                #     directory (in "shared" directory)
                'registration', SetType('Registration Directory'),
                SetContent(*registration_content()),

                'anat', SetContent(
                    't1mri', SetWeakAttr('modality', 't1mri'),
                    SetContent(
                        '{acquisition}', SetType('Acquisition'),
                        SetDefaultAttributeValue('acquisition',
                                                 default_acquisition),
                        SetNonMandatoryKeyAttribute('acquisition'),
                        DeclareAttributes('time_point', 'time_duration',
                                          'rescan', 'acquisition_date'),
                        SetContent(*raw_t1, *t1mri_acq_content()),
                    ),
                ),
            ),
        ),
    ),
)


# labeled graphs

insert(
    'sub-{subject}/ses-{session}/anat/t1mri/{acquisition}/{analysis}/folds/{graph_version}',
    '{sulci_recognition_session}_auto',
    SetDefaultAttributeValue('sulci_recognition_session', default_session),
    SetWeakAttr(
        'labelled', 'Yes', 'manually_labelled', 'No',
        'automatically_labelled', 'Yes', 'best', 'No'),
    SetContent(*auto_labeled_sulci_content()),

    '{sulci_recognition_session}_manual', SetDefaultAttributeValue('sulci_recognition_session', default_session), SetWeakAttr(
        'labelled', 'Yes', 'manually_labelled', 'Yes',
        'automatically_labelled', 'No', 'best', 'No'),
    SetContent(*manual_labeled_sulci_content()),

    '{sulci_recognition_session}_best', SetDefaultAttributeValue('sulci_recognition_session', default_session), SetWeakAttr(
        'labelled', 'Yes', 'manually_labelled', 'No',
        'automatically_labelled', 'Yes', 'best', 'Yes'), SetPriorityOffset(-1),
    SetContent(*best_labeled_sulci_content()),

)

