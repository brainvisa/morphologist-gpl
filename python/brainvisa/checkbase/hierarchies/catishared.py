# -*- coding: utf-8 -*-
import os
from brainvisa.checkbase.hierarchies import *
from brainvisa.checkbase.hierarchies.checkbase import Checkbase

patterns = { 't1natnii': os.path.join('(?P<database>[\w -/]+)', 'CONVERTED', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', '3DT1', '(?P=subject)_(?P=timepoint)_3DT1_(?P<sequence>S\d{3}).nii.gz$'),
             't1geonii': os.path.join('(?P<database>[\w -/]+)', 'CONVERTED', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', '3DT1', '(?P=subject)_(?P=timepoint)_3DT1_(?P<sequence>S\d{3})_(?P<correction>\w+).nii.gz$'),
             't1biasnii': os.path.join('(?P<database>[\w -/]+)', 'CONVERTED', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', '3DT1', '(?P=subject)_(?P=timepoint)_3DT1_(?P<sequence>S\d{3})_(?P<correction>\w+).nii.gz$'),
             't1biasgeonii': os.path.join('(?P<database>[\w -/]+)', 'CONVERTED', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', '3DT1', '(?P=subject)_(?P=timepoint)_3DT1_(?P<sequence>S\d{3})_(?P<correction>\w+).nii.gz$'),
             't1geo2dnii': os.path.join('(?P<database>[\w -/]+)', 'CONVERTED', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', '3DT1', '(?P=subject)_(?P=timepoint)_3DT1_(?P<sequence>S\d{3})_(?P<correction>\w+).nii.gz$'),
             't1geo3dnii': os.path.join('(?P<database>[\w -/]+)', 'CONVERTED', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', '3DT1', '(?P=subject)_(?P=timepoint)_3DT1_(?P<sequence>S\d{3})_(?P<correction>\w+).nii.gz$'),
             't1natdcm': os.path.join('(?P<database>[\w -/]+)', 'CONVERTED', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', '3DT1', '(?P=subject)_(?P=timepoint)_3DT1_(?P<sequence>S\d{3}).tar.gz$'),
             't1geodcm': os.path.join('(?P<database>[\w -/]+)', 'CONVERTED', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', '3DT1', '(?P=subject)_(?P=timepoint)_3DT1_(?P<sequence>S\d{3})_(?P<correction>\w+).tar.gz$'),
             'action_3dt1': os.path.join('(?P<database>[\w -/]+)', 'ACTIONS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'mri_3dt1_(?P<datetime>\d{8}_\d{6}).actions.json$'),
             'left_greywhite': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'left_greywhite_(?P=subject).nii.gz$'),
             'right_greywhite': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'right_greywhite_(?P=subject).nii.gz$'),
             'split_brain': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'split_(?P=subject).nii.gz$'),
             'split_md5': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'split_(?P=subject).nii.md5$'),
             'brain_mask': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'brain_(?P=subject).nii.gz$'),
             'snapshot_splitbrain': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'snapshot_splitbrain_(?P=subject).png$'),
             'spm8_nobias': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'spm8_nobias_(?P=subject).nii.gz$'),
             'spm8_grey': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'spm8_probamap_grey_(?P=subject).nii.gz$'),
             'spm8_white': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'spm8_probamap_white_(?P=subject).nii.gz$'),
             'spm8_csf': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'spm8_probamap_csf_(?P=subject).nii.gz$'),
             'snapshot_spm8_grey': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'snapshot_spm8_grey_(?P=subject).png$'),
             'snapshot_spm8_white': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'snapshot_spm8_white_(?P=subject).png$'),
             'snapshot_spm8_csf': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'snapshot_spm8_csf_(?P=subject).png$'),
             'snapshot_greywhite': os.path.join('(?P<database>[\w -/]+)', 'ANALYSIS', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<timepoint>\w+)', 'MRI', 'snapshot_greywhite_(?P=subject).png$'),

#                 'nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'nobias_(?P=subject).(?P<extension>%s)'%image_extensions),
#                 'left_greywhite': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', '(?P<side>[L]?)grey_white_(?P=subject).(?P<extension>%s)'%image_extensions),
#                 'right_greywhite': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', '(?P<side>[R]?)grey_white_(?P=subject).(?P<extension>%s)'%image_extensions),
#                 'brainmask': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'brain_(?P=subject).(?P<extension>%s)'%image_extensions),
#                 'left_white': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[L]?)white.(?P<extension>%s)'%mesh_extensions),
#                 'right_white': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[R]?)white.(?P<extension>%s)'%mesh_extensions),
#                 'left_hemi': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[L]?)hemi.(?P<extension>%s)'%mesh_extensions),
#                 'right_hemi': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[R]?)hemi.(?P<extension>%s)'%mesh_extensions),
#                 'left_sulci': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'folds', '(?P<graph_version>[\d.]+)', '(?P<side>[L]?)(?P=subject).arg'),
#                 'right_sulci': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'folds', '(?P<graph_version>[\d.]+)', '(?P<side>[R]?)(?P=subject).arg'),
#                 'spm_nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'nobias_(?P=subject).(?P<extension>%s)'%image_extensions),
#                 'spm_greymap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_grey_probamap.(?P<extension>%s)'%image_extensions),
#                 'spm_whitemap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_white_probamap.(?P<extension>%s)'%image_extensions),
#                 'spm_csfmap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_csf_probamap.(?P<extension>%s)'%image_extensions),
#                 'spm_greymap_warped': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_grey_probamap_warped.(?P<extension>%s)'%image_extensions),
#                 'spm_whitemap_warped': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_white_probamap_warped.(?P<extension>%s)'%image_extensions),
#                 'spm_csfmap_warped': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_csf_probamap_warped.(?P<extension>%s)'%image_extensions),
#                 'spm_greymap_modulated': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_grey_probamap_modulated.(?P<extension>%s)'%image_extensions),
#                 'spm_whitemap_modulated': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_white_probamap_modulated.(?P<extension>%s)'%image_extensions),
#                 'spm_csfmap_modulated': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_csf_probamap_modulated.(?P<extension>%s)'%image_extensions),
#                 'spm_tiv_logfile' : os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_TIV_log_file.txt$'),

}

#import re
#for k, v in patterns.items():
#   patterns[k] = re.sub(r':?\\+', '\', r'%s'%v)

keyitems = ['t1natnii', 't1geonii', 't1natdcm', 't1geodcm', 'split_brain', 'brain_mask', 'snapshot_split', 'action_3dt1', 'spm8_nobias', 'spm8_grey', 'spm8_white', 'spm8_csf']


class CATISharedCheckbase(Checkbase):
    def __init__(self, directory):
        from brainvisa.checkbase.hierarchies import catishared as cs
        self.patterns = cs.patterns
        self.keyitems = cs.keyitems
        Checkbase.__init__(self, directory)

    def get_centres(self, subdir = 'CONVERTED', save = True):
        centres = []
        subdirs = ['CONVERTED', 'ACTIONS', 'ANALYSIS', 'RAWDATA']
        for centre in os.listdir(os.path.join(self.directory, subdir)):
            path = os.path.join(self.directory, subdir, centre)
            if os.path.isdir(path):
               centres.append(centre)
        return centres

    def get_subjects(self, subdir = 'CONVERTED', save = True):
        centres = self.get_centres(subdir)
        centres_dic = {}
        for centre in centres:
            centres_dic[centre] = []
            subjects = os.listdir(os.path.join(self.directory, subdir, centre))
            for subject in subjects:
               if os.path.isdir(os.path.join(self.directory, subdir, centre, subject)):
                    centres_dic[centre].append(subject)
        return centres_dic

    def get_flat_subjects(self, subdir = 'CONVERTED'):
        all_subjects = []
        subjects = self.get_subjects(subdir)
        if hasattr(subjects, 'values'):
         for each in subjects.values():
            all_subjects.extend(each)
        else:
           all_subjects.extend(subjects)
        return all_subjects

    def get_subject_missing_files(self, subject, keyitems = None):
        from brainvisa.checkbase.hierarchies import catishared as cati
        if not keyitems: keyitems = cati.keyitems
        return self._get_subject_missing_files(subject, keyitems)

    def check_database_for_existing_files(self, patterns = None, save = True):
       from brainvisa.checkbase.hierarchies import catishared as cati
       if not patterns: patterns = cati.patterns
       return self._check_database_for_existing_files(patterns, save)


    def get_subject_files(self, subject, subdir = '*'):
        ''' Returns a list of files whose path match a specific subject.
        If the database directory matches a 'BrainVisa'-like structure with dedicated levels
        for groups and subjects, then the whole collection of files under that subject
        level is returned.'''

        from glob import glob
        import re, os
        subject_dirs = []
        subdirs = [e for e in glob(os.path.join(self.directory, subdir)) if os.path.isdir(e)]
        for s in subdirs:
           subject_dir = glob(os.path.join(self.directory, s, '*', subject))
           if len(subject_dir) == 1:
              subject_dirs.append(subject_dir[0])
        subject_files = []

        for subject_dir in subject_dirs:
           for root, dirs, files in os.walk(subject_dir):
             for f in files:
                subject_files.append(os.path.join(root,f))
        return subject_files

    def match_catishared_vs_cubicweb():
        import catidb
        db = catidb.CatiDB('user', 'Passe, le mot.')

        subjects = self.get_flat_subjects()
        cubic_subjects = db.subjects('MEMENTO')




