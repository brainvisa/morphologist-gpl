.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.SPMnormalizationPipeline.SPMnormalizationPipeline
=====================================================================


.. _morphologist.capsul.SPMnormalizationPipeline.SPMnormalizationPipeline:

SPMnormalizationPipeline
------------------------

.. currentmodule:: morphologist.capsul.SPMnormalizationPipeline




.. note::

    * Type 'SPMnormalizationPipeline.help()' for a full description of this process parameters.
    * Type '<SPMnormalizationPipeline>.get_input_spec()' for a full description of this process input trait types.
    * Type '<SPMnormalizationPipeline>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+----------------------------------------------------------------------------+
| | **t1mri**: a file name (['File'] - mandatory)                            |
| |     No description.                                                      |
+----------------------------------------------------------------------------+
| | **allow_retry_initialization**: a boolean (['Bool'] - mandatory)         |
| |     No description.                                                      |
+----------------------------------------------------------------------------+
| | **nodes_activation**: a Controller or None (['Instance'] - mandatory)    |
| |     No description.                                                      |
+----------------------------------------------------------------------------+
| | **allow_flip_initial_MRI**: a boolean (['Bool'] - mandatory)             |
| |     No description.                                                      |
+----------------------------------------------------------------------------+

[Optional]

+---------------------------------------------------------------------------------+
| | **NormalizeSPM_init_translation_origin**: a legal value (['Enum'] -           |
| |     optional)                                                                 |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **ReorientAnatomy_commissures_coordinates**: a file name (['File'] -          |
| |     optional)                                                                 |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeSPM_nbiteration**: an integer (['Int'] - optional)                 |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeSPM_cutoff_option**: an integer (['Int'] - optional)               |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **NormalizeSPM_voxel_size**: a legal value (['Enum'] - optional)              |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **template**: a file name (['File'] - optional)                               |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **ConvertSPMnormalizationToAIMS_normalized_volume**: a file name (['File']    |
| |     - optional)                                                               |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **ConvertSPMnormalizationToAIMS_removeSource**: a boolean (['Bool'] -         |
| |     optional)                                                                 |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **ConvertSPMnormalizationToAIMS_target**: a legal value (['Enum'] -           |
| |     optional)                                                                 |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+

Outputs
~~~~~~~

+----------------------------------------------------+
| | **ReorientAnatomy_output_t1mri**: a file name    |
| |     No description.                              |
+----------------------------------------------------+
| | **NormalizeSPM_job_file**: a file name           |
| |     No description.                              |
+----------------------------------------------------+
| | **spm_transformation**: a file name              |
| |     No description.                              |
+----------------------------------------------------+
| | **transformation**: a file name                  |
| |     No description.                              |
+----------------------------------------------------+
| | **normalized_t1mri**: a file name                |
| |     No description.                              |
+----------------------------------------------------+
