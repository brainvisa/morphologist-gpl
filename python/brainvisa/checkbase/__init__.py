# -*- coding: utf-8 -*-
import os 

from diskusage.check import perform_check
from diskusage.check import check_free_disk

def get_centres(databasedir, excludelist = ['history_book']):
    centres = []
    if os.path.isdir(databasedir):
        for centre in os.listdir(databasedir):
            path = os.path.join(databasedir, centre)
            if os.path.isdir(path) and centre not in excludelist:
               centres.append(centre)
        return centres
    return centres

def get_subjects(databasedir, excludelist = ['sacha_log_files', 'whasa_log_files']):
    centres = get_centres(databasedir)
    centres_dic = {}
    for centre in centres:
        centres_dic[centre] = []
        subjects = os.listdir(os.path.join(databasedir, centre))
        for subject in subjects:
            if os.path.isdir(os.path.join(databasedir, centre, subject)) and \
                    subject not in excludelist:
                centres_dic[centre].append(subject)
    return centres_dic

def get_all_subjects(databasedir):
    all_subjects = []
    subjects = get_subjects(databasedir)
    for each in subjects.values():
      all_subjects.extend(each)
    return all_subjects

def check_empty_directories(databasedir):
    liste = []
    for root, dirs, files in os.walk(databasedir):
        for name in dirs:
            fname = join(root,name)
            if not os.listdir(fname): #to check wither the dir is empty
                liste.append(fname)
    return liste

def get_T1_images_sizes(databasedir):
    def verif_ext_file(path_file):
        prefix, ext = os.path.splitext(path_file)
        if ext == ".gz":
            pref, exte = os.path.splitext(prefix)
        if exte == ".nii":
            return True
        return False

    dic_image_T1 = {}
    for root, dirs, files in os.walk(databasedir):
        for fic in files:
            if verif_ext_file(fic):
                dic_image_T1[os.path.join(root,fic)] = os.path.getsize(os.path.join(root,fic))
    return dic_image_T1

def check_T1_images_sizes(databasedir, min_size = 9, max_size = 18):
    liste = []
    nii = get_T1_images_sizes(databasedir)
    for im in nii:
        if not (nii[im] < (max_size*1000000) and nii[im] > (min_size*1000000)):
            liste.append(im)
    return liste

morphologist_patterns = { 'raw': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P=subject).nii.gz'),
                 'acpc': os.path.join('(?P<database>[\w -/]+)' ,'(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P=subject).APC'),
                 'nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'nobias_(?P=subject).nii.gz'),
                 'greywhite': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', '(?P<side>[LR]?)grey_white_(?P=subject).nii.gz'),
                 'brainmask': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'brain_(?P=subject).nii.gz'),
                 'split': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'voronoi_(?P=subject).nii.gz'),
                 'whitemeshes': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[LR]?)white.gii'),
                 'hemimeshes': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[LR]?)hemi.gii'),
                 'sulci': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'folds', '(?P<graph_version>[\d.]+)', '(?P<side>[LR]?)(?P=subject).arg'),
                 'spm_nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'nobias_(?P=subject).nii'),
                 'spm_greymap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_grey_probamap.nii'),
                 'spm_whitemap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_white_probamap.nii')}

snapshots_patterns = {'sulci' : os.path.join('(?P<database>[\w -/]+)', 'snapshots_sulci_(?P<side>[LR]?)_(?P<mode>\w+)_(?P<group>\w+)_(?P<subject>\w+)_(?P<acquisition>[\w -/]+).png') }

freesurfer_patterns = { }

def parsefilepath(filepath, patterns = morphologist_patterns):
  import re, os
  for datatype, path in patterns.items():
    m = re.match(r"%s"%path, filepath)
    if m:
       return datatype, m.groupdict()


def getfilepath(datatype, attributes):
    return processregexp(morphologist_patterns[datatype], attributes)


def processregexp(regexp, attributes):
    import string, re
    s = string.split(regexp, '(?P')
    res = []
    for each in s: 
        m = re.match('^[=<](?P<field>\w+)', each)
        if m:
            field = m.groupdict()['field']
            t = string.split(each, ')')
            res.append('%s%s'%(attributes[field], t[1]))
    return string.join(res, '')


def get_subject_hierarchy_files(databasedir, subject):
    from glob import glob
    key_items = ['raw', 'acpc', 'nobias', 'greywhite', 'brainmask', 'split', 'whitemeshes', 'hemimeshes', 'sulci', 'spm_greymap', 'spm_whitemap']
    attributes = {'subject': subject, 'group': '*', 'database': databasedir, 'modality': '*', 
                'acquisition': '*', 'analysis':'*', 'side':'*', 'graph_version':'*', 'whasa_analysis':'*'}
    items = {}
    for each in key_items:
        items[each] = glob(processregexp(morphologist_patterns[each], attributes))
        if len(items[each]) == 0:
            items.pop(each)
    return items

def get_files(databasedir):
  ''' Returns a list of the files contained in the directory and subdirectories '''
  all_files = []
  for root, dirs, files in os.walk(databasedir):
    for f in files:
      all_files.append(os.path.join(root, f))
  return all_files

def get_subject_files(databasedir, subject):
  ''' Returns a list of files whose path match a specific subject.
  If the database directory matches a 'BrainVisa'-like structure with dedicated levels 
  for groups and subjects, then the whole collection of files under that subject 
  level is returned.
  For hierarchies like the one used by SnapBase, only files with name matching the
  subject's one are returned. ''' 

  from glob import glob
  import re
  subject_dir = glob(os.path.join(databasedir, '*', subject))
  subject_files = []
  if len(subject_dir) == 0:
    files = get_files(databasedir)
    for f in files:
      m = re.match('[\w -/]*%s\w*'%subject, f)
      if m:
        subject_files.append(f)
    #raise Exception('Subject directory not found')
  else:
    assert(len(subject_dir) == 1)
    subject_dir = subject_dir[0]
    for root, dirs, files in os.walk(subject_dir):
      for f in files:
        subject_files.append(os.path.join(root,f))
  return subject_files 

def missingsubjectfiles(databasedir, subject):
    items = get_subject_hierarchy_files(databasedir, subject)
    missing = []
    for key, value in items.items():
        if len(value) == 0:
            missing.append(key)
    return missing

def check_database_for_missing_files(databasedir):
    all_subjects = get_all_subjects(databasedir)
    missingsubjects = {}
    for subject in all_subjects:
        missing = missingsubjectfiles(databasedir, subject)
        if len(missing) > 0:
            missingsubjects[subject] = missing
    return missingsubjects

def check_database_for_existing_files(databasedir):
   all_subjects = get_all_subjects(databasedir)
   all_subjects_files = {}
   not_recognized = {}
   for subject in all_subjects:
     subject_files = get_subject_files(databasedir, subject)
     for each in subject_files:
        m = parsefilepath(each, morphologist_patterns) #snapshots_patterns)
        if m:
          datatype, attributes = m
          all_subjects_files.setdefault(subject, {})
          all_subjects_files[subject][datatype] = attributes
        else:
          not_recognized.setdefault(subject, []).append(each)
   return all_subjects_files, not_recognized
    
def detect_hierarchy(directory, returnvotes=False):
    from glob import glob
    import string
    votes = {'morphologist': 0, 'freesurfer': 0, 'snapshots':0}
    
    if os.path.split(os.path.abspath(directory))[1] in ['snapshots']:
       votes['snapshots'] += 1
    items = [os.path.split(e)[1] for e in glob('%s/*'%directory)]
    for each in items:
      if os.path.isfile(os.path.join(directory, each)) and each[:9] == 'snapshots' and os.path.splitext(each)[1] == '.png':
        votes['snapshots'] += 1
      if os.path.isdir(os.path.join(directory, each)): 
        directories = [os.path.split(e)[1] for e in glob('%s/*'%os.path.join(directory, each)) if os.path.isdir(e)]
        fs_key_items = ['surf', 'stats', 'src', 'touch', 'label', 'bem', 'scripts', 'tmp', 'trash']
        s = len(set(directories).intersection(set(fs_key_items)))
        if s == len(fs_key_items):
          votes['freesurfer'] += len(fs_key_items)
        
#        for root, directories, files in os.walk(each):
#          if len(string.split(root, os.path.sep)) > 7:
#            break
        directories = [os.path.split(e)[1] for e in glob('%s/*/*'%os.path.join(directory, each)) if os.path.isdir(e)]
        
        for each_dir in directories:
           if each_dir in ['t1mri']: #, 'default_analysis', 'whasa_default_analysis', 
              #'spm_preproc', 'segmentation']:
                  subdirectories = [os.path.split(e)[1] for e in glob('%s/*/%s/*/*'%(os.path.join(directory, each), each_dir)) if os.path.isdir(e)]
                  for each_subdir in subdirectories:
                     if each_subdir in ['default_analysis', 'whasa_default_analysis']:  
                        #'spm_preproc', 'segmentation']:
                        votes['morphologist'] += 1
    m = max(votes.values())
    if votes.values().count(m) > 1:
      return None
    if returnvotes:
      return votes.keys()[votes.values().index(m)], votes
    else:
      return votes.keys()[votes.values().index(m)]



def detect_hierarchies(rootdir):
   hierarchies = {}
   for root, dirs, files in os.walk(rootdir): #, topdown=False):
      hierarchy = detect_hierarchy(root, True)
      if hierarchy:
        winner, votes = hierarchy
        print root, votes
        hierarchies[root] = winner
   return hierarchies
