.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.axon.sulcilabelling.SulciLabelling
======================================================


.. _morphologist.capsul.axon.sulcilabelling.SulciLabelling:

SulciLabelling
--------------

.. currentmodule:: morphologist.capsul.axon.sulcilabelling




.. note::

    * Type 'SulciLabelling.help()' for a full description of this process parameters.
    * Type '<SulciLabelling>.get_input_spec()' for a full description of this process input trait types.
    * Type '<SulciLabelling>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+----------------------------------------------------------------------------+
| | **select_Sulci_Recognition**: a legal value (['Enum'] - mandatory)       |
| |     No description.                                                      |
+----------------------------------------------------------------------------+
| | **nodes_activation**: a legal value (['ControllerTrait'] - mandatory)    |
| |     No description.                                                      |
+----------------------------------------------------------------------------+
| | **data_graph**: a file name (['File'] - mandatory)                       |
| |     No description.                                                      |
+----------------------------------------------------------------------------+

[Optional]

+---------------------------------------------------------------------------------+
| | **SPAM_recognition09_local_recognition_translation_priors**: a file name      |
| |     (['File'] - optional)                                                     |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **SPAM_recognition09_local_recognition_local_referentials**: a file name      |
| |     (['File'] - optional)                                                     |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **SPAM_recognition09_global_recognition_initial_transformation**: a file      |
| |     name (['File'] - optional)                                                |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **recognition2000_model**: a file name (['File'] - optional)                  |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **SPAM_recognition09_global_recognition_model**: a file name (['File'] -      |
| |     optional)                                                                 |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **SPAM_recognition09_global_recognition_labels_priors**: a file name          |
| |     (['File'] - optional)                                                     |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **recognition2000_rate**: a float (['Float'] - optional)                      |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **SPAM_recognition09_local_recognition_direction_priors**: a file name        |
| |     (['File'] - optional)                                                     |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **SPAM_recognition09_local_recognition_angle_priors**: a file name            |
| |     (['File'] - optional)                                                     |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **SPAM_recognition09_markovian_recognition_model**: a file name (['File']     |
| |     - optional)                                                               |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **recognition2000_stopRate**: a float (['Float'] - optional)                  |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **SPAM_recognition09_local_or_markovian**: a legal value (['Enum'] -          |
| |     optional)                                                                 |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **recognition2000_forbid_unknown_label**: a boolean (['Bool'] - optional)     |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **recognition2000_model_hint**: a legal value (['Enum'] - optional)           |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **SPAM_recognition09_global_recognition_labels_translation_map**: a file      |
| |     name (['File'] - optional)                                                |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **SPAM_recognition09_local_recognition_model**: a file name (['File'] -       |
| |     optional)                                                                 |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **recognition2000_niterBelowStopProp**: an integer (['Int'] - optional)       |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **SPAM_recognition09_global_recognition_model_type**: a legal value           |
| |     (['Enum'] - optional)                                                     |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+
| | **SPAM_recognition09_markovian_recognition_segments_relations_model**: a f    |
| |     ile name (['File'] - optional)                                            |
| |     No description.                                                           |
+---------------------------------------------------------------------------------+

Outputs
~~~~~~~

+--------------------------------------------------------------------------------------+
| | **SPAM_recognition09_global_recognition_posterior_probabilities**: a file          |
| |     name                                                                           |
| |     No description.                                                                |
+--------------------------------------------------------------------------------------+
| | **SPAM_recognition09_global_recognition_output_t1_to_global_transformation**: a    |
| |      file name                                                                     |
| |     No description.                                                                |
+--------------------------------------------------------------------------------------+
| | **SPAM_recognition09_local_recognition_output_local_transformations**: a d         |
| |     irectory name                                                                  |
| |     No description.                                                                |
+--------------------------------------------------------------------------------------+
| | **SPAM_recognition09_global_recognition_output_transformation**: a file            |
| |     name                                                                           |
| |     No description.                                                                |
+--------------------------------------------------------------------------------------+
| | **SPAM_recognition09_local_recognition_posterior_probabilities**: a file           |
| |     name                                                                           |
| |     No description.                                                                |
+--------------------------------------------------------------------------------------+
| | **recognition2000_energy_plot_file**: a file name                                  |
| |     No description.                                                                |
+--------------------------------------------------------------------------------------+
| | **output_graph**: any value                                                        |
| |     No description.                                                                |
+--------------------------------------------------------------------------------------+
| | **SPAM_recognition09_markovian_recognition_posterior_probabilities**: a            |
| |     file name                                                                      |
| |     No description.                                                                |
+--------------------------------------------------------------------------------------+

Pipeline schema
~~~~~~~~~~~~~~~

.. image:: ../schema/morphologist.capsul.axon.sulcilabelling.SulciLabelling.png
    :height: 400px
    :align: center

