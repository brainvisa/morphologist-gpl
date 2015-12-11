.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.axon.reorientanatomy.ReorientAnatomy
========================================================


.. _morphologist.capsul.axon.reorientanatomy.ReorientAnatomy:

ReorientAnatomy
---------------

.. currentmodule:: morphologist.capsul.axon.reorientanatomy




.. note::

    * Type 'ReorientAnatomy.help()' for a full description of this process parameters.
    * Type '<ReorientAnatomy>.get_input_spec()' for a full description of this process input trait types.
    * Type '<ReorientAnatomy>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+-------------------------------------------------------------------+
| | **t1mri**: a file name (['File'] - mandatory)                   |
| |     No description.                                             |
+-------------------------------------------------------------------+
| | **transformation**: a file name (['File'] - mandatory)          |
| |     No description.                                             |
+-------------------------------------------------------------------+
| | **allow_flip_initial_MRI**: a boolean (['Bool'] - mandatory)    |
| |     No description.                                             |
+-------------------------------------------------------------------+

[Optional]

+---------------------------------------------------------------------+
| | **commissures_coordinates**: a file name (['File'] - optional)    |
| |     No description.                                               |
+---------------------------------------------------------------------+

Outputs
~~~~~~~

+------------------------------------------------------+
| | **output_transformation**: a file name             |
| |     No description.                                |
+------------------------------------------------------+
| | **output_commissures_coordinates**: a file name    |
| |     No description.                                |
+------------------------------------------------------+
| | **output_t1mri**: a file name                      |
| |     No description.                                |
+------------------------------------------------------+
