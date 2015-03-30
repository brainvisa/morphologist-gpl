.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.spam_recognitionglobal.spam_recognitionglobal
=================================================================


.. _morphologist.capsul.spam_recognitionglobal.spam_recognitionglobal:

spam_recognitionglobal
----------------------

.. currentmodule:: morphologist.capsul.spam_recognitionglobal




.. note::

    * Type 'spam_recognitionglobal.help()' for a full description of this process parameters.
    * Type '<spam_recognitionglobal>.get_input_spec()' for a full description of this process input trait types.
    * Type '<spam_recognitionglobal>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+---------------------------------------------------------------------+
| | **model_type**: a legal value (['Enum'] - mandatory)              |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **labels_translation_map**: a file name (['File'] - mandatory)    |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **model**: a file name (['File'] - mandatory)                     |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **labels_priors**: a file name (['File'] - mandatory)             |
| |     No description.                                               |
+---------------------------------------------------------------------+
| | **data_graph**: a file name (['File'] - mandatory)                |
| |     No description.                                               |
+---------------------------------------------------------------------+

[Optional]

+--------------------------------------------------------------------+
| | **initial_transformation**: a file name (['File'] - optional)    |
| |     No description.                                              |
+--------------------------------------------------------------------+

Outputs
~~~~~~~

+----------------------------------------------------------+
| | **output_transformation**: a file name                 |
| |     No description.                                    |
+----------------------------------------------------------+
| | **posterior_probabilities**: a file name               |
| |     No description.                                    |
+----------------------------------------------------------+
| | **output_t1_to_global_transformation**: a file name    |
| |     No description.                                    |
+----------------------------------------------------------+
| | **output_graph**: a file name                          |
| |     No description.                                    |
+----------------------------------------------------------+
