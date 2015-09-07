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
include( 'anatomy' )


insert( '{center}/{subject}/t1mri/{acquisition}/{analysis}/folds/{graph_version}',
  '{sulci_recognition_session}_auto', SetDefaultAttributeValue( 'sulci_recognition_session', default_session ), SetWeakAttr('labelled', 'Yes', 'manually_labelled', 'No', 'automatically_labelled', 'Yes', 'best', 'No'),
    SetContent(
    # SULCI - labelled graphs, siRelax folds energy, segmentation
    'L<subject>_<sulci_recognition_session>_auto', SetType( 'Labelled Cortical folds graph' ), SetWeakAttr( 'side', 'left', 'parallel_recognition', 'No' ),
    'R<subject>_<sulci_recognition_session>_auto', SetType( 'Labelled Cortical folds graph' ), SetWeakAttr( 'side', 'right', 'parallel_recognition', 'No' ),
    
    'L<subject>_<sulci_recognition_session>_auto', SetType( 'siRelax Fold Energy' ), SetWeakAttr('side', 'left'),
    'R<subject>_<sulci_recognition_session>_auto', SetType( 'siRelax Fold Energy' ), SetWeakAttr('side', 'right'),
    'L<subject>_<sulci_recognition_session>_auto_proba',
        SetType( 'Sulci Labels Segmentwise Posterior Probabilities' ),
        SetWeakAttr( 'side', 'left' ),
    'R<subject>_<sulci_recognition_session>_auto_proba',
        SetType( 'Sulci Labels Segmentwise Posterior Probabilities' ),
        SetWeakAttr( 'side', 'right' ),
    'L<subject>_<sulci_recognition_session>_auto_Tal_TO_SPAM',
        SetType( 'Sulci Talairach to Global SPAM transformation' ),
        SetWeakAttr( 'side', 'left' ),
    'R<subject>_<sulci_recognition_session>_auto_Tal_TO_SPAM',
        SetType( 'Sulci Talairach to Global SPAM transformation' ),
        SetWeakAttr( 'side', 'right' ),
    'L<subject>_<sulci_recognition_session>_auto_T1_TO_SPAM',
        SetType( 'Raw T1 to Global SPAM transformation' ),
        SetWeakAttr( 'side', 'left' ),
    'R<subject>_<sulci_recognition_session>_auto_T1_TO_SPAM',
        SetType( 'Raw T1 to Global SPAM transformation' ),
        SetWeakAttr( 'side', 'right' ),
    'L<subject>_<sulci_recognition_session>_auto', SetType( 'Referential of Labelled Cortical folds graph' ), SetWeakAttr( 'side', 'left', 'parallel_recognition', 'No' ),
    'R<subject>_<sulci_recognition_session>_auto', SetType( 'Referential of Labelled Cortical folds graph' ), SetWeakAttr( 'side', 'right', 'parallel_recognition', 'No' ),

    'L<subject>_<sulci_recognition_session>_auto_global_TO_local',
        SetType( 'Sulci Local SPAM transformations Directory' ),
        SetWeakAttr( 'side', 'left' ), SetContent(
            '*_{sulcus}', SetType( 'Sulci Global to Local SPAM transformation' ),
          ),
    'R<subject>_<sulci_recognition_session>_auto_global_TO_local',
        SetType( 'Sulci Local SPAM transformations Directory' ),
        SetWeakAttr( 'side', 'right' ), SetContent(
            '*_{sulcus}', SetType( 'Sulci Global to Local SPAM transformation' ),
          ),
    '<subject>_<sulci_recognition_session>_auto_sulcal_morphometry', SetType('Sulcal morphometry measurements'), SetWeakAttr('side', 'both'),

    'segmentation', SetContent(
        "LSulci_<subject>_<sulci_recognition_session>_auto", SetType( 'Sulci Volume' ), SetWeakAttr('side', 'left'),
        "RSulci_<subject>_<sulci_recognition_session>_auto", SetType( 'Sulci Volume' ), SetWeakAttr('side', 'right'),
        "LBottom_<subject>_<sulci_recognition_session>_auto", SetType( 'Bottom Volume' ), SetWeakAttr('side', 'left'),
        "RBottom_<subject>_<sulci_recognition_session>_auto", SetType( 'Bottom Volume' ), SetWeakAttr('side', 'right'),
        "LHullJunction_<subject>_<sulci_recognition_session>_auto", SetType( 'Hull Junction Volume' ), SetWeakAttr('side', 'left'),
        "RHullJunction_<subject>_<sulci_recognition_session>_auto", SetType( 'Hull Junction Volume' ), SetWeakAttr('side', 'right'),
        "LSimpleSurface_<subject>_<sulci_recognition_session>_auto", SetType( 'Simple Surface Volume' ), SetWeakAttr('side', 'left'),
        "RSimpleSurface_<subject>_<sulci_recognition_session>_auto", SetType( 'Simple Surface Volume' ), SetWeakAttr('side', 'right'),
    ),
    
    "*.data"
        ),
  '{sulci_recognition_session}_manual', SetDefaultAttributeValue( 'sulci_recognition_session', default_session ), SetWeakAttr('labelled', 'Yes', 'manually_labelled', 'Yes', 'automatically_labelled', 'No', 'best', 'No' ),
    SetContent(
    # SULCI - labelled graphs, siRelax folds energy, segmentation
    'L<subject>_<sulci_recognition_session>_manual', SetType( 'Labelled Cortical folds graph' ), SetWeakAttr( 'side', 'left', 'parallel_recognition', 'No' ),
    'R<subject>_<sulci_recognition_session>_manual', SetType( 'Labelled Cortical folds graph' ), SetWeakAttr( 'side', 'right', 'parallel_recognition', 'No' ),
    
    'L<subject>_<sulci_recognition_session>_manual', SetType( 'siRelax Fold Energy' ), SetWeakAttr('side', 'left'),
    'R<subject>_<sulci_recognition_session>_manual', SetType( 'siRelax Fold Energy' ), SetWeakAttr('side', 'right'),

    '<subject>_<sulci_recognition_session>_manual_sulcal_morphometry', SetType('Sulcal morphometry measurements'), SetWeakAttr('side', 'both'),

    'segmentation', SetContent(
        "LSulci_<subject>_<sulci_recognition_session>_manual", SetType( 'Sulci Volume' ), SetWeakAttr('side', 'left'),
        "RSulci_<subject>_<sulci_recognition_session>_manual", SetType( 'Sulci Volume' ), SetWeakAttr('side', 'right'),
        "LBottom_<subject>_<sulci_recognition_session>_manual", SetType( 'Bottom Volume' ), SetWeakAttr('side', 'left'),
        "RBottom_<subject>_<sulci_recognition_session>_manual", SetType( 'Bottom Volume' ), SetWeakAttr('side', 'right'),
        "LHullJunction_<subject>_<sulci_recognition_session>_manual", SetType( 'Hull Junction Volume' ), SetWeakAttr('side', 'left'),
        "RHullJunction_<subject>_<sulci_recognition_session>_manual", SetType( 'Hull Junction Volume' ), SetWeakAttr('side', 'right'),
        "LSimpleSurface_<subject>_<sulci_recognition_session>_manual", SetType( 'Simple Surface Volume' ), SetWeakAttr('side', 'left'),
        "RSimpleSurface_<subject>_<sulci_recognition_session>_manual", SetType( 'Simple Surface Volume' ), SetWeakAttr('side', 'right'),
    ),
    
    "*.data"
        ), 
  '{sulci_recognition_session}_best', SetDefaultAttributeValue( 'sulci_recognition_session', default_session ), SetWeakAttr('labelled', 'Yes', 'manually_labelled', 'No', 'automatically_labelled', 'Yes', 'best', 'Yes'), SetPriorityOffset(-1),
    SetContent(
    # SULCI - labelled graphs, siRelax folds energy, segmentation
    'L<subject>_<sulci_recognition_session>_best', SetType( 'Labelled Cortical folds graph' ), SetWeakAttr( 'side', 'left', 'parallel_recognition', 'No' ),
    'R<subject>_<sulci_recognition_session>_best', SetType( 'Labelled Cortical folds graph' ), SetWeakAttr( 'side', 'right', 'parallel_recognition', 'No' ),
    
    'L<subject>_<sulci_recognition_session>_best', SetType( 'siRelax Fold Energy' ), SetWeakAttr('side', 'left'),
    'R<subject>_<sulci_recognition_session>_best', SetType( 'siRelax Fold Energy' ), SetWeakAttr('side', 'right'),

    'segmentation', SetContent(
        "LSulci_<subject>_<sulci_recognition_session>_best", SetType( 'Sulci Volume' ), SetWeakAttr('side', 'left'),
        "RSulci_<subject>_<sulci_recognition_session>_best", SetType( 'Sulci Volume' ), SetWeakAttr('side', 'right'),
        "LBottom_<subject>_<sulci_recognition_session>_best", SetType( 'Bottom Volume' ), SetWeakAttr('side', 'left'),
        "RBottom_<subject>_<sulci_recognition_session>_best", SetType( 'Bottom Volume' ), SetWeakAttr('side', 'right'),
        "LHullJunction_<subject>_<sulci_recognition_session>_best", SetType( 'Hull Junction Volume' ), SetWeakAttr('side', 'left'),
        "RHullJunction_<subject>_<sulci_recognition_session>_best", SetType( 'Hull Junction Volume' ), SetWeakAttr('side', 'right'),
        "LSimpleSurface_<subject>_<sulci_recognition_session>_best", SetType( 'Simple Surface Volume' ), SetWeakAttr('side', 'left'),
        "RSimpleSurface_<subject>_<sulci_recognition_session>_best", SetType( 'Simple Surface Volume' ), SetWeakAttr('side', 'right'),
    ),
    
    "*.data"
        )
  
)
