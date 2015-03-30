.. AUTO-GENERATED FILE -- DO NOT EDIT!

:orphan:

morphologist.capsul.preparesubject.preparesubject
=================================================


.. _morphologist.capsul.preparesubject.preparesubject:

preparesubject
--------------

.. currentmodule:: morphologist.capsul.preparesubject




.. note::

    * Type 'preparesubject.help()' for a full description of this process parameters.
    * Type '<preparesubject>.get_input_spec()' for a full description of this process input trait types.
    * Type '<preparesubject>.get_output_spec()' for a full description of this process output trait types.


Inputs
~~~~~~

[Mandatory]

+---------------------------------------------------------------------------+
| | **T1mri**: a file name (['File'] - mandatory)                           |
| |     No description.                                                     |
+---------------------------------------------------------------------------+
| | **Normalised**: a legal value (['Enum'] - mandatory)                    |
| |     No description.                                                     |
+---------------------------------------------------------------------------+
| | **remove_older_MNI_normalization**: a boolean (['Bool'] - mandatory)    |
| |     No description.                                                     |
+---------------------------------------------------------------------------+
| | **allow_flip_initial_MRI**: a boolean (['Bool'] - mandatory)            |
| |     No description.                                                     |
+---------------------------------------------------------------------------+

[Optional]

+----------------------------------------------------------------------------+
| | **Left_Hemisphere_Point**: a legal value (['List_Float'] - optional)     |
| |     No description.                                                      |
+----------------------------------------------------------------------------+
| | **Interhemispheric_Point**: a legal value (['List_Float'] - optional)    |
| |     No description.                                                      |
+----------------------------------------------------------------------------+
| | **older_MNI_normalization**: a file name (['File'] - optional)           |
| |     No description.                                                      |
+----------------------------------------------------------------------------+
| | **Posterior_Commissure**: a legal value (['List_Float'] - optional)      |
| |     No description.                                                      |
+----------------------------------------------------------------------------+
| | **Anterior_Commissure**: a legal value (['List_Float'] - optional)       |
| |     No description.                                                      |
+----------------------------------------------------------------------------+

Outputs
~~~~~~~

+----------------------------------------------+
| | **commissure_coordinates**: a file name    |
| |     No description.                        |
+----------------------------------------------+
