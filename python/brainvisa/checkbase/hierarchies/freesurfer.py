# -*- coding: utf-8 -*-
import os
from brainvisa.checkbase.hierarchies import *
from brainvisa.checkbase.hierarchies.checkbase import Checkbase

longitudinal_patterns = { 'nu' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)_acquis_', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P=subject).(?P<extension>%s)'%image_extensions),
}
patterns = { #mri
      'nu' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'mri', 'nu.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'nu_noneck' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'mri', 'nu_noneck.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'norm' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'mri', 'norm.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'brain' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'mri', 'brain.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'brainmask' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'mri', 'brainmask.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'aseg' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'mri', 'aseg.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'orig' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'mri', 'orig.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'filled' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'mri', 'filled.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'wm' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'mri', 'wm.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'ribbon' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'mri', 'ribbon.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'T1' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'mri', 'T1.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'wm.seg' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'mri', 'wm.seg.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'wmparc' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'mri', 'wmparc.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'left_ribbon' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'mri', '(?P<side>[l]?)h.ribbon.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'right_ribbon' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'mri', '(?P<side>[r]?)h.ribbon.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),

      #mri/orig
      'orig001' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'mri', 'orig', '001.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),

      #stats
      'left_aparc_stats' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'stats', '(?P<side>[l]?)h.aparc.stats$'),
      'right_aparc_stats' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'stats', '(?P<side>[r]?)h.aparc.stats$'),
      }

keyitems = ['nu','wmparc','left_aparc_stats','right_aparc_stats']

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


    def get_subject_files(self, subject):
        ''' Returns a list of files whose path match a specific subject.
        If the database directory matches a 'FreeSurfer'-like structure with dedicated levels
        for subjects, then the whole collection of files under that subject
        level is returned.'''

        from glob import glob
        import re, os
        subject_dir = glob(os.path.join(self.directory, subject))
        subject_files = []
        assert(len(subject_dir) == 1)

        subject_dir = subject_dir[0]
        for root, dirs, files in os.walk(subject_dir):
          for f in files:
            subject_files.append(os.path.join(root,f))
        return subject_files

    def get_subject_hierarchy_files(self, subject, patterns = None, attributes = None):
       from brainvisa.checkbase.hierarchies import freesurfer as free
       if not patterns: patterns = free.patterns
       return self._get_subject_hierarchy_files(subject, patterns, attributes)


    def get_subject_missing_files(self, subject, keyitems = None):
        from brainvisa.checkbase.hierarchies import freesurfer as free
        if not keyitems: keyitems = free.keyitems
        return self._get_subject_missing_files(subject, keyitems)

    def check_database_for_existing_files(self, patterns = None, save = True):
       from brainvisa.checkbase.hierarchies import freesurfer as free
       if not patterns: patterns = free.patterns
       return self._check_database_for_existing_files(patterns, save)


    def perform_checks(self):
        pass
        #self.get_multiple_subjects()

    def get_thickness(self):
        if not hasattr(self, 'subjects'): self.get_subjects()
        if not hasattr(self, 'existingfiles'): self.check_database_for_existing_files()
        import string
        self.thicknesses = {}
        for subject in self.get_flat_subjects():
           for key in ['left_aparc_stats', 'right_aparc_stats']:
              test = open(self.existingfiles[0][subject][key]
              res = [string.splitfields(each.rstrip('\n')) for each in test]
              measures = [each for each in res if each[0] == 'entorhinal'][0]
              self.thicknesses[subject][key] = measures





class FreeSurferLongitudinalCheckbase(Checkbase):
    def __init__(self, directory):
        from brainvisa.checkbase.hierarchies import freesurfer as free
        self.patterns = free.longitudinal_patterns
        self.keyitems = free.keyitems
        Checkbase.__init__(self, directory)

    def get_subjects(self, save = True):
        subjects = [each for each in os.listdir(self.directory) \
              if os.path.isdir(os.path.join(self.directory, each))]
        if save: self.subjects = subjects
        return subjects

    def check_database_for_existing_files(self, patterns = None, save = True):
       from brainvisa.checkbase.hierarchies import freesurfer as free
       if not patterns: patterns = free.patterns
       return self._check_database_for_existing_files(patterns, save)


    def perform_checks(self):
        pass
        #self.get_multiple_subjects()
