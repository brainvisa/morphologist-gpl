.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.SplitBrain.SplitBrain
=========================================


.. _morphologist.capsul.SplitBrain.SplitBrain:

SplitBrain
----------

.. currentmodule:: morphologist.capsul.SplitBrain




.. note::

    * Type 'SplitBrain.help()' for a full description of this process parameters.
    * Type '<SplitBrain>.get_input_spec()' for a full description of this process input trait types.
    * Type '<SplitBrain>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+---------------------------------------------------------------------+
| | **use_template**: a boolean (['Bool'] - mandatory)                |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **bary_factor**: a legal value (['Enum'] - mandatory)             |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **initial_erosion**: a float (['Float'] - mandatory)              |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **white_ridges**: a file name (['File'] - mandatory)              |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **cc_min_size**: an integer (['Int'] - mandatory)                 |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **variant**: a legal value (['Enum'] - mandatory)                 |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **commissure_coordinates**: a file name (['File'] - mandatory)    |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **split_template**: a file name (['File'] - mandatory)            |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **fix_random_seed**: a boolean (['Bool'] - mandatory)             |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **use_ridges**: a boolean (['Bool'] - mandatory)                  |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **t1mri_nobias**: a file name (['File'] - mandatory)              |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **brain_mask**: a file name (['File'] - mandatory)                |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **histo_analysis**: a file name (['File'] - mandatory)            |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **mode**: a legal value (['Enum'] - mandatory)                    |
| |     No description.                                               |
+---------------------------------------------------------------------+

Outputs
~~~~~~~

+-----------------------------------+
| | **split_brain**: a file name    |
| |     No description.             |
+-----------------------------------+
