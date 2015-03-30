.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.T1BiasCorrection.T1BiasCorrection
=====================================================


.. _morphologist.capsul.T1BiasCorrection.T1BiasCorrection:

T1BiasCorrection
----------------

.. currentmodule:: morphologist.capsul.T1BiasCorrection




.. note::

    * Type 'T1BiasCorrection.help()' for a full description of this process parameters.
    * Type '<T1BiasCorrection>.get_input_spec()' for a full description of this process input trait types.
    * Type '<T1BiasCorrection>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+--------------------------------------------------------------------+
| | **wridges_weight**: a float (['Float'] - mandatory)              |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **field_rigidity**: a float (['Float'] - mandatory)              |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **ngrid**: an integer (['Int'] - mandatory)                      |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **t1mri**: a file name (['File'] - mandatory)                    |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **write_meancurvature**: a legal value (['Enum'] - mandatory)    |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **variance_fraction**: an integer (['Int'] - mandatory)          |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **write_wridges**: a legal value (['Enum'] - mandatory)          |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **sampling**: a float (['Float'] - mandatory)                    |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **edge_mask**: a legal value (['Enum'] - mandatory)              |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **fix_random_seed**: a boolean (['Bool'] - mandatory)            |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **mode**: a legal value (['Enum'] - mandatory)                   |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **write_hfiltered**: a legal value (['Enum'] - mandatory)        |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **write_variance**: a legal value (['Enum'] - mandatory)         |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **zdir_multiply_regul**: a float (['Float'] - mandatory)         |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **delete_last_n_slices**: a string (['Str'] - mandatory)         |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **write_edges**: a legal value (['Enum'] - mandatory)            |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **write_field**: a legal value (['Enum'] - mandatory)            |
| |     No description.                                              |
+--------------------------------------------------------------------+

[Optional]

+--------------------------------------------------------------------+
| | **commissure_coordinates**: a file name (['File'] - optional)    |
| |     No description.                                              |
+--------------------------------------------------------------------+

Outputs
~~~~~~~

+-------------------------------------+
| | **white_ridges**: a file name     |
| |     No description.               |
+-------------------------------------+
| | **hfiltered**: a file name        |
| |     No description.               |
+-------------------------------------+
| | **field**: a file name            |
| |     No description.               |
+-------------------------------------+
| | **edges**: a file name            |
| |     No description.               |
+-------------------------------------+
| | **t1mri_nobias**: a file name     |
| |     No description.               |
+-------------------------------------+
| | **meancurvature**: a file name    |
| |     No description.               |
+-------------------------------------+
| | **variance**: a file name         |
| |     No description.               |
+-------------------------------------+
