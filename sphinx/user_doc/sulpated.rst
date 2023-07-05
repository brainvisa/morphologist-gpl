========
SulPatEd
========

Sulcal Patterns Editor: edit patterns labels for a brainvisa database.

Sulpated, is a graphical interface to manually label sulci and sulcal patterns.

It is originally a "small tool program" and its setup is not completely automatic. This means there is a config file to write.


Summary
=======

* reads a BV sulci database with labeled sulci
* writes pattern information in another output database
* handles locking ands conflicts between several users working on the same data, backups are saved

The program is run using the follwing base command, with additional options (see later):

.. code-block:: bash

    python3 -m morphologist.sulpated

A config file is expected in the output database directory, this file should be named ``patterns_def.json``. See the `Write a config file`_ section for details.

If the config file contains the sulci and input database locations, then the sulci and input databases commandline parameters (``-s``/``-i`` options) are not needed.
If the config file contains the region information, then the region commandline parameter (``-r``) is not needed.
An input database query filter is applied to select data we are working on (for instance select a sulci recognition session). This query may be either passed on the commandline (``-f`` option), or given in the config file.

Files, conflicts and backup files:
----------------------------------

Output pattern files are written in the output directory.

Output sulci graphs are written in the "sulci" database. If an earlier save of the same data is present, il will be overwritten. Use the "input" database (``-i``) to avoid this.

When a conflict is detected: ie another user has saved a file after we have read and modified it, then the new file will be saved at a different place in order to avoid overwriting and losing the other user modifications. The backup location is always in the output database, and suffixed with ``.backup.<user>``, ``<user>`` being the user login.

There is currently no tool to display diffs and resolve conflicts: the user has to do it by his own. Normally it should not happen often.


Before starting
===============

Create an output patterns data directory
----------------------------------------

This is the directory where pattern information, and possible backups will be saved in.


Setup Brainvisa databases
-------------------------

* Read/write database (needed): a BV database has to be defined and enabled in Brainvisa in order to read and write sulcal graphs in. It is the "sulci" database. It may be located inside the output patterns data directory.

* Optionnally, an additional read-only database can be defined and enabled in BrainVisa. It is the "input" database. It will be used to read input sulci graphs from. Nothing will be written into it, everything will be written in the "sulci" database.


Write a config file
-------------------

``patterns_def.json`` is a JSON format file. It should contain, at least, the patterns definition, plus optionally input database information.

Config file contents:

* ``patterns_definition``: a dict of regions with patterns inside
  Patterns are a dict of pattern names with associated items, for now just a color
  ex::

      "patterns_definition":
      {
          "orbito_frontal": {
              "P1": {"color": [1, 0, 0]},
              "P2": {"color": [1, 1, 0]},
              "P3": {"color": [0, 0, 1]}
          }
      }

* ``database_definition``: optional dict which may contain:

  * ``database_filter``: optional dict with brainvisa filter values, ex::

      "database_filter":
      {
          "sulci_recognition_session": "default_session",
          "graph_vsersion": "3.1"
      }

  * ``output_database_filter``: optional dict with brainvisa filter values, like for database_filter, but applies to output sulci graphs, in addition to database_filter (and higher priority). Having an output filter allows to write output data with different attributes, like ``sulci_recognition_session`` or ``graph_version`` for instance.
  * ``region``: optional string, specifies the working region name. ex::

      "region": "orbito_frontal"

  * ``sulci_database``: optional string, specifies the location of the sulci database (read/write to allow saving modified labeled sulci graphs)
  * ``input_database``: optional string, specifies the location of an additional input, read-only, sulci database. Sulci will be read from here only if they are not found in the sulci_database, and all will be written in the sulci_database.
  * ``force_sulci_locks_state``: optional boolean, specifies if locks should be assumed to a given value instead of all read from disk::

      "force_sulci_locks_state": true

    for large databases, reading the locks simply takes too long, and we need to use this option. Forcing the value to ``true`` is riskier, but anyway locks will be really checked before saving any data.


The GUI
=======

Then run the following command from a terminal inside the BrainVisa container

.. code-block:: bash

    python3 -m morphologist.sulpated -o /path/to/data

The ``-o`` option is not needed if it is started from the output patterns directory.


Example of full config file
===========================

::

    {
        "database_definition":
        {
            "database_filter":
            {
                "sulci_recognition_session": "session1",
                "graph_version": "3.3"
            },
            "output_database_filter":
            {
                "graph_version": "3.3",
                "sulci_recognition_session": "base2023"
            },
            "region": "SR",
            "ro_database": "/home/dr144257/data/archi-sulci",
            "sulci_database": "/home/dr144257/data/archi-sulci-sulpat/archi-sulci-2023"
        },
        "patterns_definition":
        {
            "SR": {
                "FCM.ant.bout": {
                    "color": [0, 0, 1]
                },
                "SR_inf": {
                    "color": [1, 0, 0]
                },
                "SR_sup": {
                    "color": [1, 1, 0]
                },
                "IntraCing": {
                    "color": [1, 0.5, 0.5]
                }
            }
        }
    }

