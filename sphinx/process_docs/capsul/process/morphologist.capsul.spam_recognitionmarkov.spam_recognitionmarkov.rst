.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.spam_recognitionmarkov.spam_recognitionmarkov
=================================================================


.. _morphologist.capsul.spam_recognitionmarkov.spam_recognitionmarkov:

spam_recognitionmarkov
----------------------

.. currentmodule:: morphologist.capsul.spam_recognitionmarkov




.. note::

    * Type 'spam_recognitionmarkov.help()' for a full description of this process parameters.
    * Type '<spam_recognitionmarkov>.get_input_spec()' for a full description of this process input trait types.
    * Type '<spam_recognitionmarkov>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+-----------------------------------------------------------------------+
| | **labels_translation_map**: a file name (['File'] - mandatory)      |
| |     No description.                                                 |
+-----------------------------------------------------------------------+
| | **model**: a file name (['File'] - mandatory)                       |
| |     No description.                                                 |
+-----------------------------------------------------------------------+
| | **labels_priors**: a file name (['File'] - mandatory)               |
| |     No description.                                                 |
+-----------------------------------------------------------------------+
| | **segments_relations_model**: a file name (['File'] - mandatory)    |
| |     No description.                                                 |
+-----------------------------------------------------------------------+
| | **data_graph**: a file name (['File'] - mandatory)                  |
| |     No description.                                                 |
+-----------------------------------------------------------------------+

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

+-----------------------------------------------+
| | **posterior_probabilities**: a file name    |
| |     No description.                         |
+-----------------------------------------------+
| | **output_graph**: a file name               |
| |     No description.                         |
+-----------------------------------------------+
