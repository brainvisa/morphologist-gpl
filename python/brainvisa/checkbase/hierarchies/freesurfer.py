# -*- coding: utf-8 -*-
import os
from brainvisa.checkbase.hierarchies import *
from brainvisa.checkbase.hierarchies.checkbase import Checkbase

patterns = { }
keyitems = []

class FreeSurferCheckbase(Checkbase):
    def __init__(self, directory):
        from brainvisa.checkbase.hierarchies import freesurfer as free
        self.patterns = free.patterns
        self.keyitems = free.keyitems
        Checkbase.__init__(self, directory)

    def get_subjects(self, save = True):
        subjects = [each for each in os.listdir(self.directory) \
              if os.path.isdir(os.path.join(self.directory, each))]
        if save: self.subjects = subjects
        return subjects

    def check_database_for_existing_files(self):
        return ({}, {})

    def perform_checks(self):
        pass
        #self.get_multiple_subjects()
