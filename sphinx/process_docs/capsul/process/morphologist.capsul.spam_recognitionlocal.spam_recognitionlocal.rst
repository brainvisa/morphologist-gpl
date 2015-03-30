.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.spam_recognitionlocal.spam_recognitionlocal
===============================================================


.. _morphologist.capsul.spam_recognitionlocal.spam_recognitionlocal:

spam_recognitionlocal
---------------------

.. currentmodule:: morphologist.capsul.spam_recognitionlocal




.. note::

    * Type 'spam_recognitionlocal.help()' for a full description of this process parameters.
    * Type '<spam_recognitionlocal>.get_input_spec()' for a full description of this process input trait types.
    * Type '<spam_recognitionlocal>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+---------------------------------------------------------------------+
| | **labels_translation_map**: a file name (['File'] - mandatory)    |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **translation_priors**: a file name (['File'] - mandatory)        |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **local_referentials**: a file name (['File'] - mandatory)        |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **labels_priors**: a file name (['File'] - mandatory)             |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **angle_priors**: a file name (['File'] - mandatory)              |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **data_graph**: a file name (['File'] - mandatory)                |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **model**: a file name (['File'] - mandatory)                     |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **direction_priors**: a file name (['File'] - mandatory)          |
| |     No description.                                               |
+---------------------------------------------------------------------+

[Optional]

+--------------------------------------------------------------------+
| | **initial_transformation**: a file name (['File'] - optional)    |
| |     No description.                                              |
+--------------------------------------------------------------------+
| | **global_transformation**: a file name (['File'] - optional)     |
| |     No description.                                              |
+--------------------------------------------------------------------+

Outputs
~~~~~~~

+---------------------------------------------------------+
| | **output_local_transformations**: a directory name    |
| |     No description.                                   |
+---------------------------------------------------------+
| | **posterior_probabilities**: a file name              |
| |     No description.                                   |
+---------------------------------------------------------+
| | **output_graph**: a file name                         |
| |     No description.                                   |
+---------------------------------------------------------+
