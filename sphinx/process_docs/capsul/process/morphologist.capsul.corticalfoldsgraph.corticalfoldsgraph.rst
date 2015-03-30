.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.corticalfoldsgraph.corticalfoldsgraph
=========================================================


.. _morphologist.capsul.corticalfoldsgraph.corticalfoldsgraph:

corticalfoldsgraph
------------------

.. currentmodule:: morphologist.capsul.corticalfoldsgraph




.. note::

    * Type 'corticalfoldsgraph.help()' for a full description of this process parameters.
    * Type '<corticalfoldsgraph>.get_input_spec()' for a full description of this process input trait types.
    * Type '<corticalfoldsgraph>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+-----------------------------------------------------------------------+
| | **compute_fold_meshes**: a boolean (['Bool'] - mandatory)           |
| |     No description.                                                 |
+-----------------------------------------------------------------------+
| | **graph_version**: a legal value (['Enum'] - mandatory)             |
| |     No description.                                                 |
+-----------------------------------------------------------------------+
| | **skeleton**: a file name (['File'] - mandatory)                    |
| |     No description.                                                 |
+-----------------------------------------------------------------------+
| | **write_cortex_mid_interface**: a boolean (['Bool'] - mandatory)    |
| |     No description.                                                 |
+-----------------------------------------------------------------------+
| | **allow_multithreading**: a boolean (['Bool'] - mandatory)          |
| |     No description.                                                 |
+-----------------------------------------------------------------------+
| | **hemi_cortex**: a file name (['File'] - mandatory)                 |
| |     No description.                                                 |
+-----------------------------------------------------------------------+
| | **pial_mesh**: a file name (['File'] - mandatory)                   |
| |     No description.                                                 |
+-----------------------------------------------------------------------+
| | **talairach_transform**: a file name (['File'] - mandatory)         |
| |     No description.                                                 |
+-----------------------------------------------------------------------+
| | **grey_white**: a file name (['File'] - mandatory)                  |
| |     No description.                                                 |
+-----------------------------------------------------------------------+
| | **roots**: a file name (['File'] - mandatory)                       |
| |     No description.                                                 |
+-----------------------------------------------------------------------+
| | **white_mesh**: a file name (['File'] - mandatory)                  |
| |     No description.                                                 |
+-----------------------------------------------------------------------+

[Optional]

+--------------------------------------------------------------------+
| | **split_brain**: a file name (['File'] - optional)               |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **commissure_coordinates**: a file name (['File'] - optional)    |
| |     No description.                                              |
+--------------------------------------------------------------------+

Outputs
~~~~~~~

+--------------------------------------------+
| | **graph**: a file name                   |
| |     No description.                      |
+--------------------------------------------+
| | **cortex_mid_interface**: a file name    |
| |     No description.                      |
+--------------------------------------------+
| | **sulci_voronoi**: a file name           |
| |     No description.                      |
+--------------------------------------------+
