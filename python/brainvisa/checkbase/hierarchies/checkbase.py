# -*- coding: utf-8 -*-

class Checkbase():
    def __init__(self, directory):
        import os
        assert (os.path.isdir(directory))
        self.directory = directory

    def get_centres(self, save = True):
        import morphologist as morpho
        m = morpho.MorphologistCheckbase(self.directory)
        if save: self.centres = m.get_centres()
        return m.centres

    def get_subjects(self, mode = 2, save = True):
        ''' mode : 1 - directory/subject
                   2 - directory/center/subject '''
        if mode == 2:
           import morphologist as morpho
           m = morpho.MorphologistCheckbase(self.directory)
           if save: self.subjects = m.get_subjects()
           return m.subjects
        elif mode == 1:
           f = free.FreeSurferCheckbase(self.directory)
           if save: self.subjects = f.get_subjects()
           return f.subjects

    def get_flat_subjects(self):
        all_subjects = []
        if not hasattr(self, 'subjects'): subjects = self.get_subjects()
        else: subjects = self.subjects
        if hasattr(subjects, 'values'):
         for each in subjects.values():
            all_subjects.extend(each)
        else:
           all_subjects.extend(subjects)
        return all_subjects

    def check_empty_directories(self):
        import os
        liste = []
        for root, dirs, files in os.walk(self.directory):
            for name in dirs:
                fname = os.path.join(root,name)
                if not os.listdir(fname): #to check wither the dir is empty
                    liste.append(fname)
        return liste

    def get_subject_files(self, subject):
        ''' Returns a list of files whose path match a specific subject.
        If the database directory matches a 'BrainVisa'-like structure with dedicated levels
        for groups and subjects, then the whole collection of files under that subject
        level is returned.
        For hierarchies like the one used by SnapBase, only files with name matching the
        subject's one are returned. '''

        raise NotImplementedError

    def get_files_of_type(self, itemtype):
         ''' Returns a dictionary with, for each subject found, a subdictionary describing files
         responding to the type(s) passed in itemtype as a string or a list'''
         if isinstance(itemtype, str): itemtype = [itemtype]
         from brainvisa.checkbase.hierarchies import getfilepath, parsefilepath

         files = {}
         from glob import glob
         import os
         for key in itemtype:
            globres = glob(getfilepath(key, {'database' : self.directory}, patterns = self.patterns))
            for each in globres:
               t, att = parsefilepath(each, patterns = self.patterns)
               files[att['subject']] = {key : att}

         return files


    def get_T1_images_sizes(self):
        def verif_ext_file(path_file):
            import os
            prefix, ext = os.path.splitext(path_file)
            if ext == ".gz":
                pref, exte = os.path.splitext(prefix)
                if exte == ".nii":
                   return True
            return False

        import os
        dic_image_T1 = {}
        for root, dirs, files in os.walk(self.directory):
            for fic in files:
                if verif_ext_file(fic):
                    dic_image_T1[os.path.join(root,fic)] = os.path.getsize(os.path.join(root,fic))
        return dic_image_T1

    def check_T1_images_sizes(self, min_size = 9, max_size = 18):
        liste = []
        nii = self.get_T1_images_sizes()
        for im in nii:
            if not (nii[im] < (max_size*1000000) and nii[im] > (min_size*1000000)):
                liste.append(im)
        return liste

    def get_multiple_subjects(self):
        ''' return a list of subjects whose ID is found multiple times in a database directory '''
        subjects = self.get_flat_subjects()
        multiple_subjects = []
        if len(set(subjects)) == len(subjects): return []

        for subject in set(subjects):
           if subjects.count(subject) != 1:
               multiple_subjects.append(subject)
        return multiple_subjects

    def is_subject_unique(self, subject):
        ''' return True if subject is unique '''
        subjects = self.get_flat_subjects()
        return subjects.count(subject) == 1


    def _get_subject_hierarchy_files(self, subject, patterns = None, attributes = None):
       ''' Returns a dictionary with all the items matching a dictionary of attributes
       ex : m.get_subject_hierarchy_files('toto')
            {'acpc': [{'acquisition': 'M000',
               'database': '/neurospin/cati/totodatabase',
               'group': 'group_toto',
               'modality': 't1mri',
               'subject': 'toto'}],
            'brainmask': [{'acquisition': 'M000',
                'analysis': 'default_analysis',
                'database': '/neurospin/cati/totodatabaze',
                'extension': 'nii.gz',
                'group': 'group_toto',
                'modality': 't1mri',
                'subject': 'toto'}],
             'greywhite': [{'acquisition': 'M000', ...}, ...], ...}'''
       if not attributes:
          attributes = {'subject' : subject}

       assert(attributes.has_key('subject'))
       attributes.setdefault('database', self.directory)

       from glob import glob
       from brainvisa.checkbase.hierarchies import getfilepath, parsefilepath
       items = {}
       globitems = []
       print patterns
       for each in patterns.keys():
           globitems = glob(getfilepath(each, attributes, patterns))
           print globitems
           for item in globitems:
              res = parsefilepath(item, patterns)
              if not res is None and res[0] == each:
                 items.setdefault(each, []).append(res[1])
       return items


    def _get_subject_missing_files(self, subject, keyitems = None):
        ''' Returns a list of missing items, regarding a set of items considered
        as important for a specific pipeline (morpho.keyitems) '''
        items = {}
        if not hasattr(self, 'existingfiles'):
           items = self.get_subject_hierarchy_files(subject)
        else:
           if self.existingfiles[0].has_key(subject):
              items = self.existingfiles[0][subject]

        missing = []
        for key in keyitems:
           if not items.has_key(key):
                missing.append(key)
        return missing


    def check_database_for_missing_files(self, save = True):
        ''' Returns a dictionary containing all the missing files of a hierarchy, indexed by
        subjects, regarding a set of key items specific to each pipeline. '''
        if not hasattr(self, 'get_subject_missing_files'): raise NotImplementedError
        if not hasattr(self, 'subjects'): self.get_subjects(save = True)
        if not hasattr(self, 'existingfiles'): self.check_database_for_existing_files(save = True)
        all_subjects = self.get_flat_subjects()
        incompletesubjects = {}
        for subject in all_subjects:
            missing = self.get_subject_missing_files(subject)
            if len(missing) > 0:
                incompletesubjects[subject] = missing
        if save: self.incompletesubjects = incompletesubjects
        return incompletesubjects


    def _check_database_for_existing_files(self, patterns = None, save = True):
       ''' This function browses a whole directory, subject after subject,
       in search for files matching software-specific patterns. All unidentified
       files is returned in a second list.'''
       from brainvisa.checkbase.hierarchies import parsefilepath
       all_subjects = self.get_flat_subjects()
       all_subjects_files = {}
       not_recognized = {}
       unique_subjects = set(all_subjects).difference(set(self.get_multiple_subjects()))
       for subject in unique_subjects:
         subject_files = self.get_subject_files(subject)
         for each in subject_files:
            m = parsefilepath(each, patterns)
            if m:
              datatype, attributes = m
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
              not_recognized.setdefault(subject, []).append(each)
       if save: self.existingfiles = (all_subjects_files, not_recognized)
       return all_subjects_files, not_recognized


    def _get_complete_subjects(self, keyitems = None, save = True):
       ''' Returns a list of subjects for which all key items have been found existing in
       the hierarchy (e.g. morpho.keyitems)'''
       if not hasattr(self, 'subjects'): self.get_subjects(save = True)
       if not hasattr(self, 'existingfiles'): self.check_database_for_existing_files(save = True)
       complete_subjects = []
       incomplete_subjects = []
       for subject in self.get_flat_subjects():
          if self.existingfiles[0].has_key(subject):
             c = len(set(self.existingfiles[0][subject].keys()).intersection(set(keyitems)))
             if c == len(keyitems):
                complete_subjects.append(subject)
             else:
                incomplete_subjects.append(subject)
       if save: self.complete_subjects = complete_subjects
       return self.complete_subjects


    def get_empty_subjects(self, save = True):
       ''' Returns a list of subjects for which no key items have been found existing in
       the hierarchy (e.g. morpho.keyitems). This helps filtering out directories mistaken for
       subjects.'''
       if not hasattr(self, 'subjects'): self.get_subjects(save = True)
       if not hasattr(self, 'existingfiles'): self.check_database_for_existing_files(save = True)
       empty_subjects = []
       for subject in set(self.get_flat_subjects()).difference(set(self.get_multiple_subjects())):
          if not self.existingfiles[0].has_key(subject):
              empty_subjects.append(subject)
       if save: self.empty_subjects = empty_subjects
       return self.empty_subjects


    def perform_checks(self):
        self.check_database_for_existing_files()
        self.get_multiple_subjects()
        self.get_complete_subjects()
        self.get_empty_subjects()


    def find_centre(self, subject):
      centres = self.get_centres()
      for c in centres:
         #if subject in self.get_subjects()[c]:
         for each in self.get_subjects()[c]:
            if each[-11:] == subject:
                return c
