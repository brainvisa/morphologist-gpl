# -*- coding: utf-8 -*-
import os

class Checkbase():
    def __init__(self, directory):
        assert (os.path.isdir(directory))
        self.directory = directory

    def get_centres(self):
        from hierarchies import morphologist as morpho
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
        subjects = self.get_subjects()
        for each in subjects.values():
          all_subjects.extend(each)
        return all_subjects

    def check_empty_directories(self):
        liste = []
        for root, dirs, files in os.walk(self.directory):
            for name in dirs:
                fname = os.path.join(root,name)
                if not os.listdir(fname): #to check wither the dir is empty
                    liste.append(fname)
        return liste

    def get_T1_images_sizes(self):
        def verif_ext_file(path_file):
            prefix, ext = os.path.splitext(path_file)
            if ext == ".gz":
                pref, exte = os.path.splitext(prefix)
                if exte == ".nii":
                   return True
            return False

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

    def check_subjects_unicity(self):
        ''' return a list of subjects whose ID is found multiple times in a database directory '''
        subjects = self.get_flat_subjects()
        return len(set(subjects)) == len(subjects)
