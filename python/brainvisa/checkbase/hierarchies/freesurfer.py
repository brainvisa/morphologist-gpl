# -*- coding: utf-8 -*-
import os
from brainvisa.checkbase.hierarchies import *
from brainvisa.checkbase.hierarchies.checkbase import Checkbase

longitudinal_patterns = { 'nu' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)_acquis_', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P=subject).(?P<extension>%s)'%image_extensions),
}
patterns = { #mri
      'nu' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', 'mri', 'nu\.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'nu_noneck' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', 'mri', 'nu_noneck\.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'norm' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', 'mri', 'norm\.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'brain' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', 'mri', 'brain\.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'brainmask' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', 'mri', 'brainmask\.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'aseg' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', 'mri', 'aseg\.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'orig' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', 'mri', 'orig\.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'filled' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', 'mri', 'filled\.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'wm' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', 'mri', 'wm\.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'ribbon' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', 'mri', 'ribbon\.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'T1' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', 'mri', 'T1\.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'wm.seg' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', 'mri', 'wm.seg\.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'wmparc' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', 'mri', 'wmparc\.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'left_ribbon' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', 'mri', '(?P<side>[l]?)h\.ribbon\.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      'right_ribbon' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', 'mri', '(?P<side>[r]?)h\.ribbon\.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      #mri/orig

      'orig001' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', 'mri', 'orig', '001\.(?P<extension>%s)'%'[\w.]+$'), #image_extensions),
      }

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

    def check_database_for_existing_files(self, patterns = None, save = True):
       from brainvisa.checkbase.hierarchies import freesurfer as free
       if not patterns: patterns = free.patterns
       return self._check_database_for_existing_files(patterns, save)


    def perform_checks(self):
        pass
        #self.get_multiple_subjects()

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
