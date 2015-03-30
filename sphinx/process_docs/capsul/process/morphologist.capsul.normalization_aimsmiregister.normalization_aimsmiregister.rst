.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.normalization_aimsmiregister.normalization_aimsmiregister
=============================================================================


.. _morphologist.capsul.normalization_aimsmiregister.normalization_aimsmiregister:

normalization_aimsmiregister
----------------------------

.. currentmodule:: morphologist.capsul.normalization_aimsmiregister




.. note::

    * Type 'normalization_aimsmiregister.help()' for a full description of this process parameters.
    * Type '<normalization_aimsmiregister>.get_input_spec()' for a full description of this process input trait types.
    * Type '<normalization_aimsmiregister>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+------------------------------------------------------------------+
| | **anatomical_template**: a file name (['File'] - mandatory)    |
| |     No description.                                            |
+------------------------------------------------------------------+
| | **anatomy_data**: a file name (['File'] - mandatory)           |
| |     No description.                                            |
+------------------------------------------------------------------+
| | **smoothing**: a float (['Float'] - mandatory)                 |
| |     No description.                                            |
+------------------------------------------------------------------+

[Optional]

+---------------------------------------------------------+
| | **mni_to_acpc**: a file name (['File'] - optional)    |
| |     No description.                                   |
+---------------------------------------------------------+

Outputs
~~~~~~~

+--------------------------------------------------+
| | **transformation_to_MNI**: a file name         |
| |     No description.                            |
+--------------------------------------------------+
| | **transformation_to_template**: a file name    |
| |     No description.                            |
+--------------------------------------------------+
| | **transformation_to_ACPC**: a file name        |
| |     No description.                            |
+--------------------------------------------------+
| | **normalized_anatomy_data**: a file name       |
| |     No description.                            |
+--------------------------------------------------+
