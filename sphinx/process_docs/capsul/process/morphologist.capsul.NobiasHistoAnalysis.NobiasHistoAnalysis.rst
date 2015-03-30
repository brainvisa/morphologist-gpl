.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.NobiasHistoAnalysis.NobiasHistoAnalysis
===========================================================


.. _morphologist.capsul.NobiasHistoAnalysis.NobiasHistoAnalysis:

NobiasHistoAnalysis
-------------------

.. currentmodule:: morphologist.capsul.NobiasHistoAnalysis




.. note::

    * Type 'NobiasHistoAnalysis.help()' for a full description of this process parameters.
    * Type '<NobiasHistoAnalysis>.get_input_spec()' for a full description of this process input trait types.
    * Type '<NobiasHistoAnalysis>.get_output_spec()' for a full description of this process output trait types.


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
