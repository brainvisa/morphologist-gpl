# -*- coding: utf-8 -*-
import os
from brainvisa.checkbase.hierarchies import *
from brainvisa.checkbase.hierarchies.checkbase import Checkbase

patterns = {'sulci' : os.path.join('(?P<database>[\w -/]+)', 'snapshots_sulci_(?P<side>[LR]?)_(?P<mode>\w+)_(?P<group>\w+)_(?P<subject>\w{12})_(?P<acquisition>[\w -/]+).png') ,
            'spm8white' : os.path.join('(?P<database>[\w -/]+)', 'snapshots_spm_white_None_(?P<subject>\d{7}_\w{4})_(?P<acquisition>[\w -/]+).png') ,
            'spm8csf' : os.path.join('(?P<database>[\w -/]+)', 'snapshots_spm_CSF_None_(?P<subject>\w+)_(?P<acquisition>[\w -/]+).png') ,
            'spm8grey' : os.path.join('(?P<database>[\w -/]+)', 'snapshots_spm_grey_None_(?P<subject>\w+)_(?P<acquisition>[\w -/]+).png') ,




      }
keyitems = ['sulci', 'spm8white', 'spm8csf', 'spm8grey']

class SnapshotsCheckbase(Checkbase):
    def __init__(self, directory):
        from brainvisa.checkbase.hierarchies import snapshots as snap
        self.patterns = snap.patterns
        self.keyitems = snap.keyitems
        Checkbase.__init__(self, directory)

    def check_database_for_existing_files(self, patterns = None, save = True):
       from brainvisa.checkbase.hierarchies import snapshots as snap
       if not patterns: patterns = snap.patterns
       from brainvisa.checkbase.hierarchies import parsefilepath
       not_recognized = []
       all_subjects_files = {}
       from glob import glob
       import os
       files = []
       for root, dirs, f in os.walk(self.directory):
          files.extend(f)

       for each in files:
            each = os.path.join(self.directory, each)
            m = parsefilepath(each, snap.patterns)
            print m
            if m:
              datatype, attributes = m
              subject = attributes['subject']
              all_subjects_files.setdefault(subject, {})
              if all_subjects_files[subject].has_key(datatype):
                 if isinstance(all_subjects_files[subject][datatype], list):
                    all_subjects_files[subject][datatype].append(attributes)
                 elif isinstance(all_subjects_files[subject][datatype], dict):
                    items = []
                    items.extend([all_subjects_files[subject][datatype], attributes])
                    all_subjects_files[subject][datatype] = items
              else:
                 all_subjects_files[subject][datatype] = attributes
            else:
              not_recognized.append(each)
       if save: self.existingfiles = (all_subjects_files, not_recognized)
       return all_subjects_files, not_recognized

    def perform_checks(self):
        self.check_database_for_existing_files()

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
