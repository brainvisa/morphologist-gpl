.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.Normalization_FSL_reinit.Normalization_FSL_reinit
=====================================================================


.. _morphologist.capsul.Normalization_FSL_reinit.Normalization_FSL_reinit:

Normalization_FSL_reinit
------------------------

.. currentmodule:: morphologist.capsul.Normalization_FSL_reinit




.. note::

    * Type 'Normalization_FSL_reinit.help()' for a full description of this process parameters.
    * Type '<Normalization_FSL_reinit>.get_input_spec()' for a full description of this process input trait types.
    * Type '<Normalization_FSL_reinit>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+------------------------------------------------------------------------+
| | **init_translation_origin**: a legal value (['Enum'] - mandatory)    |
| |     No description.                                                  |
+------------------------------------------------------------------------+
| | **cost_function**: a legal value (['Enum'] - mandatory)              |
| |     No description.                                                  |
+------------------------------------------------------------------------+
| | **allow_retry_initialization**: a boolean (['Bool'] - mandatory)     |
| |     No description.                                                  |
+------------------------------------------------------------------------+
| | **anatomy_data**: a file name (['File'] - mandatory)                 |
| |     No description.                                                  |
+------------------------------------------------------------------------+
| | **search_cost_function**: a legal value (['Enum'] - mandatory)       |
| |     No description.                                                  |
+------------------------------------------------------------------------+
| | **anatomical_template**: a file name (['File'] - mandatory)          |
| |     No description.                                                  |
+------------------------------------------------------------------------+
| | **Alignment**: a legal value (['Enum'] - mandatory)                  |
| |     No description.                                                  |
+------------------------------------------------------------------------+

Outputs
~~~~~~~

+-----------------------------------------------+
| | **transformation_matrix**: a file name      |
| |     No description.                         |
+-----------------------------------------------+
| | **normalized_anatomy_data**: a file name    |
| |     No description.                         |
+-----------------------------------------------+
