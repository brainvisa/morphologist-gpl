# -*- coding: utf-8 -*-
import os
from general import *
from brainvisa.checkbase import *
from brainvisa.checkbase.hierarchies.checkbase import Checkbase

patterns = { 'raw': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P=subject).%s'%image_extensions),
                 'acpc': os.path.join('(?P<database>[\w -/]+)' ,'(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P=subject).APC'),
                 'nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'nobias_(?P=subject).%s'%image_extensions),
                 'greywhite': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', '(?P<side>[LR]?)grey_white_(?P=subject).%s'%image_extensions),
                 'brainmask': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'brain_(?P=subject).%s'%image_extensions),
                 'split': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'voronoi_(?P=subject).%s'%image_extensions),
                 'whitemeshes': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[LR]?)white.%s'%mesh_extensions),
                 'hemimeshes': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[LR]?)hemi.%s'%mesh_extensions),
                 'sulci': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'folds', '(?P<graph_version>[\d.]+)', '(?P<side>[LR]?)(?P=subject).arg'),
                 'spm_nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'nobias_(?P=subject).%s'%image_extensions),
                 'spm_greymap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_grey_probamap.%s'%image_extensions),
                 'spm_whitemap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_white_probamap.%s'%image_extensions)}

keyitems = ['raw', 'acpc', 'nobias', 'greywhite', 'brainmask', 'split', 'whitemeshes', 'hemimeshes', 'sulci', 'spm_greymap', 'spm_whitemap']

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
        centres = self.get_centres(save = False)
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
       from brainvisa.checkbase.hierarchies import morphologist as morpho
       if not keyitems: keyitems = morpho.keyitems
       morphologist_attributes = {'subject': subject, 'group': '*', 'database': self.directory, 'modality': '*',
                   'acquisition': '*', 'analysis':'*', 'side':'*', 'graph_version':'*', 'whasa_analysis':'*'}
       if attributes is None: attributes = morphologist_attributes
       from glob import glob
       items = {}
       for each in keyitems:
           items[each] = glob(processregexp(morpho.patterns[each], attributes))
           if len(items[each]) == 0:
               items.pop(each)
       return items

    def get_subject_missingfiles(self, subject):
        items = self.get_subject_hierarchy_files(subject)
        missing = []
        for key, value in items.items():
            if len(value) == 0:
                missing.append(key)
        return missing

    def check_database_for_missing_files(self, save = True):
        all_subjects = self.get_flat_subjects()
        incompletesubjects = {}
        for subject in all_subjects:
            missing = self.get_subject_missingfiles(subject)
            if len(missing) > 0:
                incompletesubjects[subject] = missing
        if save: self.incompletesubjects = incompletesubjects
        return incompletesubjects

    def check_database_for_existing_files(self, save = True):
       from brainvisa.checkbase.hierarchies import morphologist as morpho
       all_subjects = self.get_flat_subjects()
       all_subjects_files = {}
       not_recognized = {}
       for subject in all_subjects:
         try:
             subject_files = get_subject_files(self.directory, subject)
         except Exception:
             not_recognized.setdefault(subject, []).append('subject id exists multiple times')
             subject_files = []
         for each in subject_files:
            m = parsefilepath(each, morpho.patterns) #snapshots_patterns)
            if m:
              datatype, attributes = m
              all_subjects_files.setdefault(subject, {})
              all_subjects_files[subject][datatype] = attributes
            else:
              not_recognized.setdefault(subject, []).append(each)
       if save: self.existingfiles = (all_subjects_files, not_recognized)
       return all_subjects_files, not_recognized

    #def check_database_for_complete_subjects(self):


