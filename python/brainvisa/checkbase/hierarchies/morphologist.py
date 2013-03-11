# -*- coding: utf-8 -*-
import os
from brainvisa.checkbase.hierarchies import *
from brainvisa.checkbase.hierarchies.checkbase import Checkbase

patterns = { 'raw': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P=subject)\.(?P<extension>%s)'%image_extensions),
                 'acpc': os.path.join('(?P<database>[\w -/]+)' ,'(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P=subject)\.APC'),
                 'nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'nobias_(?P=subject)\.(?P<extension>%s)'%image_extensions),
                 'greywhite': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', '(?P<side>[LR]?)grey_white_(?P=subject)\.(?P<extension>%s)'%image_extensions),
                 'brainmask': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'brain_(?P=subject)\.(?P<extension>%s)'%image_extensions),
                 'split': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'voronoi_(?P=subject)\.(?P<extension>%s)'%image_extensions),
                 'left_white': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[L]?)white\.(?P<extension>%s)'%mesh_extensions),
                 'right_white': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[R]?)white\.(?P<extension>%s)'%mesh_extensions),
                 'left_hemi': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[L]?)hemi\.(?P<extension>%s)'%mesh_extensions),
                 'right_hemi': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[R]?)hemi\.(?P<extension>%s)'%mesh_extensions),
                 'left_sulci': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'folds', '(?P<graph_version>[\d.]+)', '(?P<side>[L]?)(?P=subject)\.arg'),
                 'right_sulci': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'folds', '(?P<graph_version>[\d.]+)', '(?P<side>[R]?)(?P=subject)\.arg'),
                 'spm_nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'nobias_(?P=subject)\.(?P<extension>%s)'%image_extensions),
                 'spm_greymap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_grey_probamap\.(?P<extension>%s)'%image_extensions),
                 'spm_whitemap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_white_probamap\.(?P<extension>%s)'%image_extensions),
                 'spm_csfmap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_csf_probamap\.(?P<extension>%s)'%image_extensions),
                 'spm_greymap_warped': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_csf_probamap_warped\.(?P<extension>%s)'%image_extensions),
                 'spm_whitemap_warped': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_white_probamap_warped\.(?P<extension>%s)'%image_extensions),
                 'spm_csfmap_warped': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_csf_probamap_warped\.(?P<extension>%s)'%image_extensions),
                 'spm_greymap_modulated': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_grey_probamap_modulated\.(?P<extension>%s)'%image_extensions),
                 'spm_whitemap_modulated': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_white_probamap_modulated\.(?P<extension>%s)'%image_extensions),
                 'spm_csfmap_modulated': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_csf_probamap_modulated\.(?P<extension>%s)'%image_extensions),

}

keyitems = ['raw', 'acpc', 'nobias', 'greywhite', 'brainmask', 'split', 'whitemeshes', 'hemimeshes', 'sulci',
            'spm_greymap', 'spm_whitemap', 'spm_csfmap', 'spm_greymap_warped', 'spm_whitemap_warped',
            'spm_csfmap_warped', 'spm_greymap_modulated', 'spm_whitemap_modulated','spm_csfmap_modulated']

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

    def compute_volumes(self):
       assert(len(self.get_multiple_subjects()) == 0)
       if not hasattr(self, 'subjects'): self.get_subjects()
       if not hasattr(self, 'existingfiles'): self.check_database_for_existing_files()
       self.volumes = {}
       for subject in self.get_flat_subjects():
          self.volumes[subject] = {}
          spm_wc_vols = ['spm_greymap_warped', 'spm_whitemap_warped', 'spm_csfmap_warped',
                'spm_greymap_modulated', 'spm_whitemap_modulated', 'spm_csfmap_modulated']
          if set(spm_wc_vols).issubset(set(self.existingfiles[0][subject].keys())):
            volumes = get_volumes(*spm_wc_vols)
            for v, each in zip(volumes, ['tivol', 'grey', 'white', 'csf']):
               self.volumes[subject][each] = v

          for key in ['spm_greymap', 'spm_whitemap']:
                if key in self.existingfiles[0][subject].keys():
                   from soma import aims
                   from brainvisa.checkbase.hierarchies import getfilepath
                   import numpy as np
                   data = aims.read(getfilepath(key, self.existingfiles[0][subject][key]))
                   n = data.arraydata()
                   r = n.ravel()
                   self.volumes[subject][key] = r.sum()

# compute the total intre cranial volume (Clara Fischer - Olivier Colliot)
def get_volumes( wc_gray, wc_white, wc_csf, mwc_gray, mwc_white, mwc_csf ):
  #Compute an approximate intracranial mask from unmodulated segmentations
  from soma import aims
  wc_gm_im = aims.read(wc_gray)
  wc_wm_im = aims.read(wc_white)
  wc_csf_im = aims.read(wc_csf)
  wc_gm_arr = wc_gm_im.arraydata()
  wc_wm_arr = wc_wm_im.arraydata()
  wc_csf_arr = wc_csf_im.arraydata()

  wc_sum_arr = wc_gm_arr + wc_wm_arr + wc_csf_arr
  mask = (wc_sum_arr > 0.5)

  #Compute volumes by masking the modulated segmentations with the previous mask
  mwc_gm_im = aims.read(mwc_gray)
  mwc_wm_im = aims.read(mwc_white)
  mwc_csf_im = aims.read(mwc_csf)
  mwc_gm_arr = mwc_gm_im.arraydata()
  mwc_wm_arr = mwc_wm_im.arraydata()
  mwc_csf_arr = mwc_csf_im.arraydata()
  mwc_gm_arr = mwc_gm_arr.astype('float64')
  mwc_wm_arr = mwc_wm_arr.astype('float64')
  mwc_csf_arr = mwc_csf_arr.astype('float64')

  mwc_sum_arr = mwc_gm_arr + mwc_wm_arr + mwc_csf_arr
  mwc_sum_arr[mask == False] = 0.
  mwc_gm_arr[mask == False] = 0.
  mwc_wm_arr[mask == False] = 0.
  mwc_csf_arr[mask == False] = 0.
  mwc_sum_arr[mwc_sum_arr < 0] = 0.
  mwc_gm_arr[mwc_gm_arr < 0] = 0.
  mwc_wm_arr[mwc_wm_arr < 0] = 0.
  mwc_csf_arr[mwc_csf_arr < 0] = 0.

  vox_sizes = mwc_gm_im.header()['voxel_size'].arraydata()
  vox_vol = vox_sizes[0]*vox_sizes[1]*vox_sizes[2]

  mwc_sum_arr_mm3 = mwc_sum_arr*vox_vol
  mwc_gm_arr_mm3 = mwc_gm_arr*vox_vol
  mwc_wm_arr_mm3 = mwc_wm_arr*vox_vol
  mwc_csf_arr_mm3 = mwc_csf_arr*vox_vol

  tivol = mwc_sum_arr_mm3.sum()/1000.
  gmvol = mwc_gm_arr_mm3.sum()/1000.
  wmvol = mwc_wm_arr_mm3.sum()/1000.
  csfvol = mwc_csf_arr_mm3.sum()/1000.
  volumes = [tivol, gmvol, wmvol, csfvol]
  return volumes

def pixelsOfValue( data, value ):
    '''
    Returns the number of pixels/voxels of a particular value in the data
    value can be a float or a list of float

    '''

    n = data.arraydata()
    r = n.ravel()
    if ( type(value) == type(float()) ):
        s = r[r==value]
        return s.size
    elif (type(value) == type(list())):
        res = {}
        for val in value:
            s = r[r==float(val)]
            res[val] = s.size
        return res
    else:
        raise TypeError
