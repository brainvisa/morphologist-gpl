.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.axon.normalization_spm_reinit.Normalization_SPM_reinit
==========================================================================


.. _morphologist.capsul.axon.normalization_spm_reinit.Normalization_SPM_reinit:

Normalization_SPM_reinit
------------------------

.. currentmodule:: morphologist.capsul.axon.normalization_spm_reinit




.. note::

    * Type 'Normalization_SPM_reinit.help()' for a full description of this process parameters.
    * Type '<Normalization_SPM_reinit>.get_input_spec()' for a full description of this process input trait types.
    * Type '<Normalization_SPM_reinit>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+------------------------------------------------------------------------+
| | **anatomy_data**: a file name (['File'] - mandatory)                 |
| |     No description.                                                  |
+------------------------------------------------------------------------+
| | **init_translation_origin**: a legal value (['Enum'] - mandatory)    |
| |     No description.                                                  |
+------------------------------------------------------------------------+
| | **allow_retry_initialization**: a boolean (['Bool'] - mandatory)     |
| |     No description.                                                  |
+------------------------------------------------------------------------+
| | **voxel_size**: a legal value (['Enum'] - mandatory)                 |
| |     No description.                                                  |
+------------------------------------------------------------------------+
| | **nbiteration**: an integer (['Int'] - mandatory)                    |
| |     No description.                                                  |
+------------------------------------------------------------------------+
| | **cutoff_option**: an integer (['Int'] - mandatory)                  |
| |     No description.                                                  |
+------------------------------------------------------------------------+

[Optional]

+-----------------------------------------------------------------+
| | **anatomical_template**: a file name (['File'] - optional)    |
| |     No description.                                           |
+-----------------------------------------------------------------+

Outputs
~~~~~~~

+----------------------------------------------------+
| | **transformations_informations**: a file name    |
| |     No description.                              |
+----------------------------------------------------+
| | **job_file**: a file name                        |
| |     No description.                              |
+----------------------------------------------------+
| | **normalized_anatomy_data**: a file name         |
| |     No description.                              |
+----------------------------------------------------+
