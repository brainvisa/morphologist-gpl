.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.axon.brainsegmentation.BrainSegmentation
============================================================


.. _morphologist.capsul.axon.brainsegmentation.BrainSegmentation:

BrainSegmentation
-----------------

.. currentmodule:: morphologist.capsul.axon.brainsegmentation




.. note::

    * Type 'BrainSegmentation.help()' for a full description of this process parameters.
    * Type '<BrainSegmentation>.get_input_spec()' for a full description of this process input trait types.
    * Type '<BrainSegmentation>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+-------------------------------------------------------------+
| | **layer**: a legal value (['Enum'] - mandatory)           |
| |     No description.                                       |
+-------------------------------------------------------------+
| | **visu**: a legal value (['Enum'] - mandatory)            |
| |     No description.                                       |
+-------------------------------------------------------------+
| | **variant**: a legal value (['Enum'] - mandatory)         |
| |     No description.                                       |
+-------------------------------------------------------------+
| | **first_slice**: an integer (['Int'] - mandatory)         |
| |     No description.                                       |
+-------------------------------------------------------------+
| | **edges**: a file name (['File'] - mandatory)             |
| |     No description.                                       |
+-------------------------------------------------------------+
| | **fix_random_seed**: a boolean (['Bool'] - mandatory)     |
| |     No description.                                       |
+-------------------------------------------------------------+
| | **t1mri_nobias**: a file name (['File'] - mandatory)      |
| |     No description.                                       |
+-------------------------------------------------------------+
| | **last_slice**: an integer (['Int'] - mandatory)          |
| |     No description.                                       |
+-------------------------------------------------------------+
| | **variance**: a file name (['File'] - mandatory)          |
| |     No description.                                       |
+-------------------------------------------------------------+
| | **erosion_size**: a float (['Float'] - mandatory)         |
| |     No description.                                       |
+-------------------------------------------------------------+
| | **histo_analysis**: a file name (['File'] - mandatory)    |
| |     No description.                                       |
+-------------------------------------------------------------+

[Optional]

+--------------------------------------------------------------------+
| | **white_ridges**: a file name (['File'] - optional)              |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **commissure_coordinates**: a file name (['File'] - optional)    |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **lesion_mask**: a file name (['File'] - optional)               |
| |     No description.                                              |
+--------------------------------------------------------------------+

Outputs
~~~~~~~

+----------------------------------+
| | **brain_mask**: a file name    |
| |     No description.            |
+----------------------------------+
