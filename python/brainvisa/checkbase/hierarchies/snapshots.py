# -*- coding: utf-8 -*-
import os
from brainvisa.checkbase.hierarchies import *
from brainvisa.checkbase.hierarchies.checkbase import Checkbase

patterns = {'sulci' : os.path.join('(?P<database>[\w -/]+)', 'snapshots_sulci_(?P<side>[LR]?)_(?P<mode>\w+)_(?P<group>\w+)_(?P<subject>\w+)_(?P<acquisition>[\w -/]+).png') }
keyitems = []

class SnapshotsCheckbase(Checkbase):
    def __init__(self, directory):
        from brainvisa.checkbase.hierarchies import snapshots as snap
        self.patterns = snap.patterns
        self.keyitems = snap.keyitems
        Checkbase.__init__(self, directory)

    def check_database_for_existing_files(self):
        return ({}, {})

    def get_subject_files(self, subject):
        ''' Returns a list of files whose path match a specific subject.
        For hierarchies like the one used by SnapBase, only files with name matching the
        subject's one are returned. '''

        from glob import glob
        import re, os
        subject_files = []
        files = get_files(self.directory)
        for f in files:
          m = re.match('[\w -/]*%s\w*'%subject, f)
          if m:
            subject_files.append(f)
        return subject_files
