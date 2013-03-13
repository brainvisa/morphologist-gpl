# -*- coding: utf-8 -*-
import os
from brainvisa.checkbase.hierarchies import *
from brainvisa.checkbase.hierarchies.checkbase import Checkbase

patterns = {'spm_nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'nobias_(?P=subject).(?P<extension>%s)'%image_extensions),
                 'spm_greymap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_grey_probamap.(?P<extension>%s)'%image_extensions),
                 'spm_whitemap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_white_probamap.(?P<extension>%s)'%image_extensions)}

keyitems = ['spm_greymap', 'spm_whitemap']

class SPMCheckbase(Checkbase):
   def __init__(self, directory):
        from brainvisa.checkbase.hierarchies import spm
        self.patterns = morpho.patterns
        self.keyitems = morpho.keyitems
        Checkbase.__init__(self, directory)

   def check_database_for_existing_files(self, patterns = None, save = True):
      from brainvisa.checkbase.hierarchies import spm
      if not patterns: patterns = spm.patterns
      return self._check_database_for_existing_files(patterns, save)

   def get_complete_subjects(self, keyitems = None, save = True):
      from brainvisa.checkbase.hierarchies import spm
      if not keyitems: keyitems = spm.keyitems
      return self._get_complete_subjects(keyitems, save)

#   def compute_volumes(self):

