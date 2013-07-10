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
      'aseg_stats' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'stats', 'aseg.stats$'),
      'left_aparc_stats' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'stats', '(?P<side>[l]?)h.aparc.stats$'),
      'right_aparc_stats' : os.path.join('(?P<database>[\w -/]+)', '(?P<subject>\w+)', 'stats', '(?P<side>[r]?)h.aparc.stats$'),
      }

keyitems = ['nu','wmparc','left_aparc_stats','right_aparc_stats']

freesurfer_surface_regions = ['bankssts',
 'caudalanteriorcingulate',
 'caudalmiddlefrontal',
 'cuneus',
 'entorhinal',
 'fusiform',
 'inferiorparietal',
 'inferiortemporal',
 'isthmuscingulate',
 'lateraloccipital',
 'lateralorbitofrontal',
 'lingual',
 'medialorbitofrontal',
 'middletemporal',
 'parahippocampal',
 'paracentral',
 'parsopercularis',
 'parsorbitalis',
 'parstriangularis',
 'pericalcarine',
 'postcentral',
 'posteriorcingulate',
 'precentral',
 'precuneus',
 'rostralanteriorcingulate',
 'rostralmiddlefrontal',
 'superiorfrontal',
 'superiorparietal',
 'superiortemporal',
 'supramarginal',
 'frontalpole',
 'temporalpole',
 'transversetemporal',
 'insula']

freesurfer_atlas_regions = ['BrainSegVol', 'BrainSegVolNotVent', 'TotalGrayVol', 'eTIV', 'lhCortexVol', 'rhCortexVol', 'lhCorticalWhiteMatterVol', 'rhCorticalWhiteMatterVol', 'CorticalWhiteMatterVol',
         'SubCortGrayVol', 'CortexVol', 'SupraTentorialVol', 'SupraTentorialVolNotVent', 'SurfaceHoles']
freesurfer_atlas_regions2 = ['Left-Hippocampus', 'Left-Amygdala', 'Right-Hippocampus', 'Right-Amygdala']

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
        self.check_database_for_existing_files()
        #self.get_multiple_subjects()

    def compute_volumes(self, fastmode = True):
        if not hasattr(self, 'subjects'): self.get_subjects()
        if not hasattr(self, 'existingfiles'):
            if fastmode:
               files = self.get_files_of_type('aseg_stats')
            else:
               self.check_database_for_existing_files()
               files = self.existingfiles[0]
        import string
        self.volumes = {}
        for subject in files.keys():
           key = 'aseg_stats'
           if files[subject].has_key(key):
              path = getfilepath(key, files[subject][key], patterns=self.patterns)
              test = open(path, 'r').readlines()
              res = [string.split(each.rstrip('\n'), ', ') for each in test]
              measures = {}
              for region in freesurfer_atlas_regions:
                  m = [each for each in res if region in each]
                  if len(m) > 0:
                     v = float(m[0][m[0].index(region) + 2])
                     measures[region] = v

              res = [string.split(each.rstrip('\n')) for each in test]
              for region in freesurfer_atlas_regions2:
                  m = [each for each in res if region in each]
                  if len(m) > 0: measures[region] = float(m[0][m[0].index(region) - 1])


              self.volumes.setdefault(subject, {})
              self.volumes[subject] = measures


    def compute_thicknesses(self, fastmode = True):
        if not hasattr(self, 'subjects'): self.get_subjects()
        if not hasattr(self, 'existingfiles'):
            if fastmode:
               print 'get_files_of_type'
               files = self.get_files_of_type(['left_aparc_stats', 'right_aparc_stats'])
            else:
               self.check_database_for_existing_files()
               files = self.existingfiles[0]
        import string
        self.thicknesses = {}
        for subject in files.keys():
           for key in ['left_aparc_stats', 'right_aparc_stats']:
              if files[subject].has_key(key):
                 path = getfilepath(key, files[subject][key], patterns=self.patterns)
                 test = open(path, 'r').readlines()
                 res = [string.split(each.rstrip('\n')) for each in test]
                 measures = {}
                 for region in freesurfer_surface_regions:
                     m = [each for each in res if each[0] == region]
                     if len(m) > 0: measures[region] = m[0]

                 self.thicknesses.setdefault(subject, {})
                 self.thicknesses[subject][key] = measures

                 res = [string.split(each.rstrip('\n'), ', ') for each in test]
                 avg = [each for each in res if 'MeanThickness' in each][0]
                 avg_thick = float(avg[avg.index('MeanThickness') + 2])
                 self.thicknesses[subject][key]['average'] = avg_thick

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
