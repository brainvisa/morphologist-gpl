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

include('base')

#local helper
templ_model1 = ('*', SetType('Template model'),
                '*', SetType('Template model domain'))
templ_model2 = SetContent(
    'model', SetContent(*(
        templ_model1 + ('{model_element_type}', SetContent(*templ_model1)))),
    'hull_junction', SetType('Template model'),
    SetWeakAttr('model_element_type', 'hull_junction'),
    'fakerel', SetType('Template model'),
    SetWeakAttr('model_element_type', 'fake_relation'),
    '*', SetType('Sigraph Learner'),
)

descriptive_models = (
    'labels_priors',
    SetContent(
        '*_priors_{side}',
        SetContent(
            '*_priors', SetType('Sulci Labels Priors'),
        ),
    ),
    'segments',
    SetContent(
        # side is not defined as {side} because of ambiguities in the pattern
        # '{sulci_segments_model_type}_{side}'
        '{sulci_segments_model_type}_left', SetWeakAttr( 'side', 'left' ),
            SetContent(
            '*_distribs', SetType( 'Sulci Segments Model' ),
            '*_direction_trm_priors', SetType( 'Sulci Direction Transformation Priors' ),
            '*_angle_trm_priors', SetType( 'Sulci Angle Transformation Priors' ),
            '*_translation_trm_priors', SetType( 'Sulci Translation Transformation Priors' ),
            'local_referentials', SetType( 'Sulci Local referentials' ),
            'meshes', SetContent(
              'Lwhite_spam', SetType( 'White SPAM mesh' ),
              'global_SPAM', SetType( 'Referential' ),
              'white_SPAM', SetType( 'Referential' ),
              'Lwhite_TO_global_spam', SetType( 'Transformation' ),
            ),
          ),
        '{sulci_segments_model_type}_right', SetWeakAttr( 'side', 'right' ),
            SetContent(
            '*_distribs', SetType( 'Sulci Segments Model' ),
            '*_direction_trm_priors', SetType( 'Sulci Direction Transformation Priors' ),
            '*_angle_trm_priors', SetType( 'Sulci Angle Transformation Priors' ),
            '*_translation_trm_priors', SetType( 'Sulci Translation Transformation Priors' ),
            'local_referentials', SetType( 'Sulci Local referentials' ),
            'meshes', SetContent(
              'Rwhite_spam', SetType( 'White SPAM mesh' ),
            ),
          ),
    ),
    'segments_relations', SetContent(
        '*_relations_{side}', SetContent(
          '*_distribs', SetType( 'Sulci Segments Relations Model' ),
        )
    )
)

insertFirst( 'nomenclature/hierarchy',
  'sulcal_root_colors', SetPriorityOffset( +10 ), SetType( 'Nomenclature' ),
)

insertLast('nomenclature/translation',
    'sulci_default_list', SetType( 'Sulci groups list' ), SetWeakAttr( 'version', 'default' ),
)

insertLast('nomenclature/translation',
  '*', SetType( "Label Translation" ),
)

insert( '',
  'models', SetContent(
    'models_{sulci_database}', SetContent(
      'discriminative_models', SetContent(
        "model_templates", templ_model2,
        '{graph_version}', SetWeakAttr( 'trained', 'No', 'talairach', 'Yes' ),
        SetContent(
          # remove these specific model entries when issue #1247 is fixed
          "Lfolds_noroots",
            SetWeakAttr( 'side', 'left', 'model', 'folds_noroots' ),
            SetContent(
              "L*", SetType( 'Model graph' ), SetWeakAttr( 'trained', 'Yes' ),
              "L*", SetType( 'Data description' ),
          ),
          "Rfolds_noroots",
            SetWeakAttr( 'side', 'right', 'model', 'folds_noroots' ),
            SetContent(
              "R*", SetType( 'Model graph' ), SetWeakAttr( 'trained', 'Yes' ),
              "R*", SetType( 'Data description' ),
          ),
          "Lfolds_noroots_fd4_native_2010", SetPriorityOffset( -1 ),
            SetWeakAttr( 'side', 'left', 'talairach', 'No',
              'model', 'folds_noroots_fd4_native_2010' ),
            SetContent(
              "*", SetType( 'Model graph' ),
              "*", SetType( 'Data description' ),
          ),
          "Rfolds_noroots_fd4_native_2010", SetPriorityOffset( -1 ),
            SetWeakAttr( 'side', 'right', 'talairach', 'No',
              'model', 'folds_noroots_fd4_native_2010' ),
            SetContent(
              "*", SetType( 'Model graph' ),
              "*", SetType( 'Data description' ),
          ),
          "L{model}", SetWeakAttr( 'side', 'left' ), SetContent(
            "*", SetType( 'Model graph' ),
            "*", SetType( 'Data description' ),
          ),
          "R{model}", SetWeakAttr( 'side', 'right' ), SetContent(
            "*", SetType( 'Model graph' ),
            "*", SetType( 'Data description' ),
          ),
          "{model}", SetContent(
          # the _none_ trick just avoids to have an empty filename_variable
          # which makes links fail. If you find a better way...
            "<model>", SetWeakAttr( 'filename_variable', '_none_'),
              SetType( 'Model graph' ),
            "<model>", SetWeakAttr( 'filename_variable', '_none'),
              SetType( 'Data description' ),
            "R*", SetWeakAttr( 'side', 'right' ), SetType( 'Model graph' ),
            "R*", SetWeakAttr( 'side', 'right' ), SetType( 'Data description' ),
            "L*", SetWeakAttr( 'side', 'left' ), SetType( 'Model graph' ),
            "L*", SetWeakAttr( 'side', 'left' ), SetType( 'Data description' ),
            "*", SetType( 'Model graph' ),
            "*", SetType( 'Data description' ),
          ),
        ),
      ),
      'descriptive_models', SetContent( *descriptive_models ),
    ),
  ),
)
