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

include('base')
include('anatomy')

templ_sulci1 = (
    "L<subject>Auto_<sulci_recognition_session>", SetType(
        'Labelled Cortical folds graph'),
    SetWeakAttr('side', 'left', 'labelled', 'Yes', 'manually_labelled',
                'No', 'automatically_labelled', 'Yes', 'parallel_recognition', 'No'),
    "L<subject>Auto_<sulci_recognition_session>", SetType(
        'Left siRelax Fold Energy'),
    SetWeakAttr('side', 'left', 'labelled', 'Yes',
                'manually_labelled', 'No', 'automatically_labelled', 'Yes'),
    "R<subject>Auto_<sulci_recognition_session>", SetType(
        'Labelled Cortical folds graph'),
    SetWeakAttr('side', 'right', 'labelled', 'Yes', 'manually_labelled',
                'No', 'automatically_labelled', 'Yes', 'parallel_recognition', 'No'),
    "R<subject>Auto_<sulci_recognition_session>", SetType(
        'Right siRelax Fold Energy'),
    SetWeakAttr('side', 'right', 'labelled', 'Yes',
                'manually_labelled', 'No', 'automatically_labelled', 'Yes'),
)


templ_sulci2 = (
    "L<subject>", SetType('Cortical folds graph'), SetWeakAttr(
        'side', 'left', 'labelled', 'No'),
    "L<subject>Base", SetType('Labelled Cortical folds graph'), SetWeakAttr(
        'side', 'left', 'labelled', 'Yes', 'manually_labelled', 'Yes', 'automatically_labelled', 'No'),
    "R<subject>", SetType('Cortical folds graph'), SetWeakAttr(
        'side', 'right',  'labelled', 'No'),
    "R<subject>Base", SetType('Labelled Cortical folds graph'), SetWeakAttr(
        'side', 'right', 'labelled', 'Yes', 'manually_labelled', 'Yes', 'automatically_labelled', 'No'),
    '*.data',

    'default', SetWeakAttr('sulci_recognition_session', 'default'),
    SetPriorityOffset(+1),
    apply(SetContent, templ_sulci1),
    '{sulci_recognition_session}',
    apply(SetContent, templ_sulci1),
)

sulci_content = (
    "default", SetWeakAttr('sulciGraph', 'default'), SetWeakAttr(
        'graph_version', '3.1'), SetPriorityOffset(+1),
    apply(SetContent, templ_sulci2),
    '{sulciGraph}', SetWeakAttr('graph_version', '3.1'),
    apply(SetContent, templ_sulci2),
)


insert('{protocol}/{subject}',

       "sulci", SetWeakAttr('acquisition', ''),
       apply(SetContent, sulci_content +
             ('{acquisition}', apply(SetContent, sulci_content), )),
       )

insert('{protocol}/{subject}/graphe/{sulci_recognition_session}',
       "L<subject>Auto_<sulci_recognition_session>", SetType('Left siRelax Fold Energy'), SetPriorityOffset(
           +1), SetWeakAttr('side', 'left', 'labelled', 'Yes', 'manually_labelled', 'No', 'automatically_labelled', 'Yes'),
       "R<subject>Auto_<sulci_recognition_session>", SetType('Right siRelax Fold Energy'), SetPriorityOffset(
           +1), SetWeakAttr('side', 'right', 'labelled', 'Yes', 'manually_labelled', 'No', 'automatically_labelled', 'Yes'),
       )

insert('{protocol}/{subject}/sulci/{sulci_recognition_session}',
       "L<subject>Auto_<sulci_recognition_session>", SetType(
           'Left siRelax Fold Energy'),
       SetWeakAttr('side', 'left', 'labelled', 'Yes',
                   'manually_labelled', 'No', 'automatically_labelled', 'Yes'),
       "R<subject>Auto_<sulci_recognition_session>", SetType(
           'Right siRelax Fold Energy'),
       SetWeakAttr('side', 'right', 'labelled', 'Yes',
                   'manually_labelled', 'No', 'automatically_labelled', 'Yes'),
       )
