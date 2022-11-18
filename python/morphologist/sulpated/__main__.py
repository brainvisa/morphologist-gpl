#!/usr/bin/env python

'''
SULPATED
========

SUlcal PAtterns EDitor

In order to work, a few things have to be prepared:

- create a directory for sulcal paterns data storage
- create a BrainVisa database compatible with Morphologist. It may be inside the above sulcal patterns directory.
- Activate and Update this (new) database, and the input (read-only) database, if any.
- create a patterns definition file in the toor of the sulcal patterns directory, ``patterns_def.json``

Only Sulpated should be used when working on a sulcal patterns edition session: its modification notification is based on the polling of a single file, and will not notice or take into account "external" modifications such as writing a sulcal graph from BrainVisa or directly using Anatomist (even if checks are made before writing a file to avoid overwriting data modifiied by someone else).

Otherwise Sulpated is supposed to handle multiuser sessions, and conflicts happening in this situation. When another user writes a file we are currently modifying, saving it will be done in a separate user backup.
'''

import argparse
from argparse import ArgumentParser
import sys
import os
import os.path as osp
import json

parser = ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
    description='Sulcal Patterns Editor: edit patterns labels for a brainvisa database.\n'
    '- reads a BV sulci database with labeled sulci\n'
    '- writes pattern information in another output database'
    '- handles locking ands conflicts between several users working on the '
    'same data, backups are saved\n\n'
    'A config file is expected in the output database directory, this file '
    'should be named "patterns_def.json". This JSON format file should '
    'contain, at least, the patterns definition, plus optionally input '
    'database information.\n\n'
    'If the config file contains the input database location, then the input '
    'database commandline parameter (-d) is not needed.\n'
    'If the config file contains the region information, then the region '
    'commandline parameter (-r) is not needed.\n'
    'An input database query filter is applied to select data we are working '
    'on (for instance select a sulci recognition session). This query may be '
    'either passed on the commandline (-f option), or given in the config '
    'file.\n\n'
    'Config file contents:\n\n'
    '- "patterns_definition": a dict of regions with patterns inside\n'
    '  Patterns are a dict of pattern names with associated items, for now '
    'just a color\n'
    '  ex:\n'
    '      "patterns_definition":\n'
    '      {\n'
    '          "orbito_frontal": {\n'
    '              "P1": {"color": [1, 0, 0]},\n'
    '              "P2": {"color": [1, 1, 0]},\n'
    '              "P3": {"color": [0, 0, 1]}\n'
    '          }\n'
    '      }\n'
    '- database_definition: optional dict which may contain:\n'
    '  - database_filter: optional dict with brainvisa filter values, ex:\n'
    '    "database_filter":\n'
    '    {\n'
    '        "sulci_recognition_session": "default_session",\n'
    '        "graph_version": "3.1"\n'
    '    }\n'
    '  - regon: optional string, specifies the working region name. ex:\n'
    '    "region": "orbito_frontal"\n'
    '  - sulci_database: optional string, specifies the location of the sulci database (read/write to allow saving modified labeled sulci graphs)\n'
    '  - input_database: optional string, specifies the location of an '
    'additional input, read-only, sulci database. Sulci will be read from '
    'here only if they are not found in the sulci_database, and all will be '
    'written in the sulci_database.\n'
    '  - force_sulci_locks_state: optional boolean, specifies if locks should '
    'be assumed to a given value instead of all read from disk:\n'
    '    "force_sulci_locks_state": true\n'
    '    for large databases, reading the locks simply takes too long, and we '
    'need to use this option. Forcing the value to "true" is safer, but '
    'anyway locks will be realy checked before saving any data.\n\n'
    'Files, conflicts and backup files:\n\n'
    'Output files are normally written in the output database directory. '
    '**But** for now, sulci files are written in the input database and '
    'overwrite existing ones. Thi behaviour may be changed in the future.\n'
    'When a conflict is detected: ie another user has saved a file after we '
    'have read and modified it, then the new file will be saved at a '
    'different place in order to avoid overwriting and losing the other user '
    'modifications. The backup location is always in the output database, and '
    'suffixed with ".backup.<user>", "<user>" being the user login.\n'
    'There is currently no tool to displaty diffs and resolve conflicts: the '
    'user has to do it by his own. Normally it should not happen often.'
)
parser.add_argument('-o', '--output',
                    help='output brainvisa database location [default: write '
                    'in the input one]')
parser.add_argument('-s', '--sulci_db',
                    help='input/output sulci brainvisa database location')
parser.add_argument('-i', '--input_db',
                    help='additional read-only brainvisa sulci database '
                    'location')
parser.add_argument('-r', '--region',
                    help='region to edit (ex: orbito_frontal)')
parser.add_argument('-f', '--filter',
                    help='database filter dict, ex: \'{"side": "left"}\'')

options = parser.parse_args()

mypath = osp.dirname(sys.argv[0])
sys.path.insert(0, mypath)

from . import sulpated_gui
from soma.qt_gui.qt_backend import Qt

run_loop = False
if Qt.QApplication.instance() is None:
    qapp = Qt.QApplication([sys.argv[0]])
    run_loop = True

db_filter = {}
if options.filter:
    db_filter = json.loads(options.filter)

spe = sulpated_gui.SulcalPatternsEditor(sulci_db=options.sulci_db,
                                        region=options.region,
                                        out_db=options.output,
                                        db_filter=db_filter,
                                        ro_db=options.input_db)
spe.show()

if run_loop:
    qapp.exec()


