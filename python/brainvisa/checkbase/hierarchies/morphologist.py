# -*- coding: utf-8 -*-
import os
from general import *
from brainvisa.checkbase import *
from brainvisa.checkbase.hierarchies.checkbase import Checkbase

patterns = { 'raw': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P=subject).(?P<extension>%s)'%image_extensions),
                 'acpc': os.path.join('(?P<database>[\w -/]+)' ,'(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P=subject).APC'),
                 'nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'nobias_(?P=subject).(?P<extension>%s)'%image_extensions),
                 'greywhite': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', '(?P<side>[LR]?)grey_white_(?P=subject).(?P<extension>%s)'%image_extensions),
                 'brainmask': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'brain_(?P=subject).(?P<extension>%s)'%image_extensions),
                 'split': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'voronoi_(?P=subject).(?P<extension>%s)'%image_extensions),
                 'whitemeshes': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[LR]?)white.%s'%mesh_extensions),
                 'hemimeshes': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[LR]?)hemi.%s'%mesh_extensions),
                 'sulci': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'folds', '(?P<graph_version>[\d.]+)', '(?P<side>[LR]?)(?P=subject).arg'),
                 'spm_nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'nobias_(?P=subject).(?P<extension>%s)'%image_extensions),
                 'spm_greymap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_grey_probamap.(?P<extension>%s)'%image_extensions),
                 'spm_whitemap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_white_probamap.(?P<extension>%s)'%image_extensions)}

keyitems = ['raw', 'acpc', 'nobias', 'greywhite', 'brainmask', 'split', 'whitemeshes', 'hemimeshes', 'sulci'] #, 'spm_greymap', 'spm_whitemap']

class MorphologistCheckbase(Checkbase):
    def __init__(self, directory):
        Checkbase.__init__(self, directory)

    def get_centres(self, excludelist = ['history_book'], save = True):
        centres = []
        for centre in os.listdir(self.directory):
            path = os.path.join(self.directory, centre)
            if os.path.isdir(path) and centre not in excludelist:
               centres.append(centre)
        if save: self.centres = centres
        return centres
        if save: self.centres = centres
        return centres

    def get_subjects(self, excludelist = ['sacha_log_files', 'whasa_log_files'], save = True):
        centres = self.get_centres()
        centres_dic = {}
        for centre in centres:
            centres_dic[centre] = []
            subjects = os.listdir(os.path.join(self.directory, centre))
            for subject in subjects:
                if os.path.isdir(os.path.join(self.directory, centre, subject)) and \
                        subject not in excludelist:
                    centres_dic[centre].append(subject)
        if save: self.subjects = centres_dic
        return centres_dic

    def get_subject_hierarchy_files(self, subject, keyitems = None, attributes = None):
       ''' Returns a dictionary with all the keyitems matching a dictionary of attributes
       ex : '''
       from brainvisa.checkbase.hierarchies import morphologist as morpho
       if not keyitems: keyitems = morpho.keyitems
       if not attributes:
          attributes = {'subject' : subject}

       assert(attributes.has_key('subject'))
       attributes.setdefault('database', self.directory)

       from glob import glob
       items = {}
       globitems = []
       for each in keyitems:
           #items[each] = glob(processregexp(morpho.patterns[each], attributes))
           globitems = glob(getfilepath(each, attributes))
           for item in globitems:
              res = parsefilepath(item)
              if not res is None and res[0] == each:
                 items.setdefault(each, []).append(res[1])
       return items

    def get_subject_missingfiles(self, subject):
        from brainvisa.checkbase.hierarchies import morphologist as morpho
        items = {}
        if not hasattr(self, 'existingfiles'):
           items = self.get_subject_hierarchy_files(subject)
        else:
           if self.existingfiles[0].has_key(subject):
              items = self.existingfiles[0][subject]

        missing = []
        for key in morpho.keyitems:
           if not items.has_key(key):
                missing.append(key)
        return missing

    def check_database_for_missing_files(self, save = True):
        from brainvisa.checkbase.hierarchies import morphologist as morpho
        if not hasattr(self, 'subjects'): self.get_subjects(save = True)
        if not hasattr(self, 'existingfiles'): self.check_database_for_existing_files(save = True)
        all_subjects = self.get_flat_subjects()
        incompletesubjects = {}
        for subject in all_subjects:
            missing = self.get_subject_missingfiles(subject)
            if len(missing) > 0:
                incompletesubjects[subject] = missing
        if save: self.incompletesubjects = incompletesubjects
        return incompletesubjects

    def check_database_for_existing_files(self, save = True):
       ''' This function browses a whole directory, subject after subject,
       in search for files matching software-specific patterns. All unidentified
       files is retsecond list.'''
       from brainvisa.checkbase.hierarchies import morphologist as morpho
       all_subjects = self.get_flat_subjects()
       all_subjects_files = {}
       not_recognized = {}
       unique_subjects = set(all_subjects).difference(set(self.get_multiple_subjects()))
       for subject in unique_subjects:
         subject_files = get_subject_files(self.directory, subject)
         for each in subject_files:
            m = parsefilepath(each, patterns = morpho.patterns) #snapshots_patterns)
            if m:
              datatype, attributes = m
              all_subjects_files.setdefault(subject, {})
              all_subjects_files[subject][datatype] = attributes
            else:
              not_recognized.setdefault(subject, []).append(each)
       if save: self.existingfiles = (all_subjects_files, not_recognized)
       return all_subjects_files, not_recognized

    def get_complete_subjects(self, save = True):
       from brainvisa.checkbase.hierarchies import morphologist as morpho
       if not hasattr(self, 'subjects'): self.get_subjects(save = True)
       if not hasattr(self, 'existingfiles'): self.check_database_for_existing_files(save = True)
       complete_subjects = []
       incomplete_subjects = []
       for subject in self.get_flat_subjects():
          if self.existingfiles[0].has_key(subject):
             c = len(set(self.existingfiles[0][subject].keys()).intersection(set(morpho.keyitems)))
             if c == len(morpho.keyitems):
                complete_subjects.append(subject)
             else:
                incomplete_subjects.append(subject)
       if save: self.complete_subjects = complete_subjects
       return self.complete_subjects

    def get_empty_subjects(self, save = True):
       from brainvisa.checkbase.hierarchies import morphologist as morpho
       if not hasattr(self, 'subjects'): self.get_subjects(save = True)
       if not hasattr(self, 'existingfiles'): self.check_database_for_existing_files(save = True)
       empty_subjects = []
       for subject in self.get_flat_subjects():
          if not self.existingfiles[0].has_key(subject):
             #c = len(set(self.existingfiles[0][subject].keys()).intersection(set(morpho.keyitems)))
             #if c == 0:
                empty_subjects.append(subject)
       if save: self.empty_subjects = empty_subjects
       return self.empty_subjects


