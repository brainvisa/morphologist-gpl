.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.axon.biascorrection.BiasCorrection
======================================================


.. _morphologist.capsul.axon.biascorrection.BiasCorrection:

BiasCorrection
--------------

.. currentmodule:: morphologist.capsul.axon.biascorrection




.. note::

    * Type 'BiasCorrection.help()' for a full description of this process parameters.
    * Type '<BiasCorrection>.get_input_spec()' for a full description of this process input trait types.
    * Type '<BiasCorrection>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+--------------------------------------------------------------+
| | **use_hfiltered**: a boolean (['Bool'] - mandatory)        |
| |     No description.                                        |
+--------------------------------------------------------------+
| | **undersampling**: a legal value (['Enum'] - mandatory)    |
| |     No description.                                        |
+--------------------------------------------------------------+
| | **fix_random_seed**: a boolean (['Bool'] - mandatory)      |
| |     No description.                                        |
+--------------------------------------------------------------+
| | **use_wridges**: a boolean (['Bool'] - mandatory)          |
| |     No description.                                        |
+--------------------------------------------------------------+
| | **t1mri_nobias**: a file name (['File'] - mandatory)       |
| |     No description.                                        |
+--------------------------------------------------------------+

[Optional]

+----------------------------------------------------------+
| | **hfiltered**: a file name (['File'] - optional)       |
| |     No description.                                    |
+----------------------------------------------------------+
| | **white_ridges**: a file name (['File'] - optional)    |
| |     No description.                                    |
+----------------------------------------------------------+

Outputs
~~~~~~~

+--------------------------------------+
| | **histo_analysis**: a file name    |
| |     No description.                |
+--------------------------------------+
| | **histo**: a file name             |
| |     No description.                |
+--------------------------------------+
