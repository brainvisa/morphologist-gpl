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
        from brainvisa.checkbase.hierarchies import morphologist as morpho
        self.patterns = morpho.patterns
        self.keyitems = morpho.keyitems
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


    def get_subject_hierarchy_files(self, subject, patterns = None, attributes = None):
       from brainvisa.checkbase.hierarchies import morphologist as morpho
       if not patterns: patterns = morpho.patterns
       return self._get_subject_hierarchy_files(subject, patterns, attributes)


    def get_subject_missing_files(self, subject, keyitems = None):
        from brainvisa.checkbase.hierarchies import morphologist as morpho
        if not keyitems: keyitems = morpho.keyitems
        return self._get_subject_missing_files(subject, keyitems)


    def check_database_for_existing_files(self, patterns = None, save = True):
       from brainvisa.checkbase.hierarchies import morphologist as morpho
       if not patterns: patterns = morpho.patterns
       return self._check_database_for_existing_files(patterns, save)


    def get_complete_subjects(self, keyitems = None, save = True):
       from brainvisa.checkbase.hierarchies import morphologist as morpho
       if not keyitems: keyitems = morpho.keyitems
       return self._get_complete_subjects(keyitems, save)

    def perform_checks(self):
        self.check_database_for_existing_files()
        self.get_multiple_subjects()
        self.get_complete_subjects()
        self.get_empty_subjects()
