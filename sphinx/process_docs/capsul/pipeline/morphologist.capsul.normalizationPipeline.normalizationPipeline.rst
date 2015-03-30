.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.normalizationPipeline.normalizationPipeline
===============================================================


.. _morphologist.capsul.normalizationPipeline.normalizationPipeline:

normalizationPipeline
---------------------

.. currentmodule:: morphologist.capsul.normalizationPipeline




.. note::

    * Type 'normalizationPipeline.help()' for a full description of this process parameters.
    * Type '<normalizationPipeline>.get_input_spec()' for a full description of this process input trait types.
    * Type '<normalizationPipeline>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+------------------------------------------------------------------------------+
| | **t1mri**: a file name (['File'] - mandatory)                              |
| |     No description.                                                        |
+------------------------------------------------------------------------------+
| | **nodes_activation**: a Controller or None (['Instance'] - mandatory)      |
| |     No description.                                                        |
+------------------------------------------------------------------------------+
| | **select_Normalization_pipeline**: a legal value (['Enum'] - mandatory)    |
| |     No description.                                                        |
+------------------------------------------------------------------------------+
| | **allow_flip_initial_MRI**: a boolean (['Bool'] - mandatory)               |
| |     No description.                                                        |
+------------------------------------------------------------------------------+

[Optional]

+---------------------------------------------------------------------------------+
| | **NormalizeFSL_template**: a file name (['File'] - optional)                  |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeSPM_NormalizeSPM_cutoff_option**: an integer (['Int'] -            |
| |     optional)                                                                 |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **Normalization_AimsMIRegister_mni_to_acpc**: a file name (['File'] -         |
| |     optional)                                                                 |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeFSL_NormalizeFSL_search_cost_function**: a legal value             |
| |     (['Enum'] - optional)                                                     |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeSPM_ConvertSPMnormalizationToAIMS_target**: a legal value          |
| |     (['Enum'] - optional)                                                     |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeSPM_template**: a file name (['File'] - optional)                  |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeSPM_allow_retry_initialization**: a boolean (['Bool'] -            |
| |     optional)                                                                 |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **Normalization_AimsMIRegister_smoothing**: a float (['Float'] - optional)    |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeFSL_allow_retry_initialization**: a boolean (['Bool'] -            |
| |     optional)                                                                 |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeFSL_set_transformation_in_source_volume**: a boolean (['Bool']     |
| |     - optional)                                                               |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeSPM_NormalizeSPM_nbiteration**: an integer (['Int'] - optional)    |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeFSL_alignment**: a legal value (['Enum'] - optional)               |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeBaladin_set_transformation_in_source_volume**: a boolean           |
| |     (['Bool'] - optional)                                                     |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeSPM_NormalizeSPM_voxel_size**: a legal value (['Enum'] -           |
| |     optional)                                                                 |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeSPM_ConvertSPMnormalizationToAIMS_removeSource**: a boolean        |
| |     (['Bool'] - optional)                                                     |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeFSL_NormalizeFSL_init_translation_origin**: a legal value          |
| |     (['Enum'] - optional)                                                     |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeSPM_NormalizeSPM_init_translation_origin**: a legal value          |
| |     (['Enum'] - optional)                                                     |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeFSL_ConvertFSLnormalizationToAIMS_standard_template**: a legal     |
| |     value (['Enum'] - optional)                                               |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeFSL_NormalizeFSL_cost_function**: a legal value (['Enum'] -        |
| |     optional)                                                                 |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **commissures_coordinates**: a file name (['File'] - optional)                |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **Normalization_AimsMIRegister_anatomical_template**: a file name             |
| |     (['File'] - optional)                                                     |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeBaladin_template**: a file name (['File'] - optional)              |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeSPM_ConvertSPMnormalizationToAIMS_normalized_volume**: a file      |
| |     name (['File'] - optional)                                                |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+

Outputs
~~~~~~~

+-------------------------------------------------------------------------------+
| | **Normalization_AimsMIRegister_transformation_to_ACPC**: a file name        |
| |     No description.                                                         |
+-------------------------------------------------------------------------------+
| | **NormalizeSPM_NormalizeSPM_job_file**: a file name                         |
| |     No description.                                                         |
+-------------------------------------------------------------------------------+
| | **NormalizeSPM_spm_transformation**: a file name                            |
| |     No description.                                                         |
+-------------------------------------------------------------------------------+
| | **NormalizeBaladin_NormalizeBaladin_transformation_matrix**: a file name    |
| |     No description.                                                         |
+-------------------------------------------------------------------------------+
| | **reoriented_t1mri**: any value                                             |
| |     No description.                                                         |
+-------------------------------------------------------------------------------+
| | **normalized**: any value                                                   |
| |     No description.                                                         |
+-------------------------------------------------------------------------------+
| | **Normalization_AimsMIRegister_transformation_to_template**: a file name    |
| |     No description.                                                         |
+-------------------------------------------------------------------------------+
| | **NormalizeFSL_NormalizeFSL_transformation_matrix**: a file name            |
| |     No description.                                                         |
+-------------------------------------------------------------------------------+
| | **transformation**: any value                                               |
| |     No description.                                                         |
+-------------------------------------------------------------------------------+
