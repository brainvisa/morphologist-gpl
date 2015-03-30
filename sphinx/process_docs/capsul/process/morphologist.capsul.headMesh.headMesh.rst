.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.headMesh.headMesh
=====================================


.. _morphologist.capsul.headMesh.headMesh:

headMesh
--------

.. currentmodule:: morphologist.capsul.headMesh




.. note::

    * Type 'headMesh.help()' for a full description of this process parameters.
    * Type '<headMesh>.get_input_spec()' for a full description of this process input trait types.
    * Type '<headMesh>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+-----------------------------------------------------------+
| | **keep_head_mask**: a boolean (['Bool'] - mandatory)    |
| |     No description.                                     |
+-----------------------------------------------------------+
| | **t1mri_nobias**: a file name (['File'] - mandatory)    |
| |     No description.                                     |
+-----------------------------------------------------------+

[Optional]

+------------------------------------------------------------+
| | **remove_mask**: a file name (['File'] - optional)       |
| |     No description.                                      |
+------------------------------------------------------------+
| | **threshold**: an integer (['Int'] - optional)           |
| |     No description.                                      |
+------------------------------------------------------------+
| | **first_slice**: an integer (['Int'] - optional)         |
| |     No description.                                      |
+------------------------------------------------------------+
| | **closing**: a float (['Float'] - optional)              |
| |     No description.                                      |
+------------------------------------------------------------+
| | **histo_analysis**: a file name (['File'] - optional)    |
| |     No description.                                      |
+------------------------------------------------------------+

Outputs
~~~~~~~

+---------------------------------+
| | **head_mask**: a file name    |
| |     No description.           |
+---------------------------------+
| | **head_mesh**: a file name    |
| |     No description.           |
+---------------------------------+
