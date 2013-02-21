# -*- coding: utf-8 -*-
import os
image_extensions = '(nii.gz|nii|ima|ima.gz)'
mesh_extensions = '(gii|mesh)'

def parsefilepath(filepath, patterns = None):
  import morphologist as morpho
  import re, os
  for datatype, path in morpho.patterns.items():
    m = re.match(r"%s"%path, filepath)
    if m:
       return datatype, m.groupdict()


def getfilepath(datatype, attributes):
    return processregexp(morpho.patterns[datatype], attributes)


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





#    all_subjects = get_all_subjects(databasedir)

def detect_hierarchy(directory, returnvotes = False, maxvote=50):
    def _get_directories(root, threshold = 1, fullpath = False):
        directories = []
        dirs = []
        for e in os.listdir(root):
            if len(dirs) >= threshold: break
            if os.path.isdir(os.path.join(root, e)) and  not e in ['.', '..']:
                dirs.append(e)
        if fullpath == True:
            return [os.path.join(root, e) for e in dirs]
        else:
            return dirs

    from glob import glob
    import string
    votes = {'morphologist': 0, 'freesurfer': 0, 'snapshots':0}

    if os.path.split(os.path.abspath(directory))[1] in ['snapshots']:
       votes['snapshots'] += 1
    items = [os.path.split(e)[1] for e in glob('%s/*'%directory)]
    for each in items:
      if max(votes.values()) >= maxvote: break
      if os.path.isfile(os.path.join(directory, each)) and each[:9] == 'snapshots' and os.path.splitext(each)[1] == '.png':
        votes['snapshots'] += 1
      if os.path.isdir(os.path.join(directory, each)):
        fs_key_items = set(['surf', 'stats', 'src', 'touch', 'label', 'bem', 'scripts', 'tmp', 'trash', 'mri'])
        directories = _get_directories(os.path.join(directory, each), threshold = len(fs_key_items))
        s = len(set(directories).intersection(fs_key_items))
        if s > len(fs_key_items) / 2:
          votes['freesurfer'] += s

        directories = []
        subjects = _get_directories(os.path.join(directory, each))
        for subject in subjects:
            directories.extend(_get_directories(os.path.join(directory, each, subject)))

        for each_dir in directories:
           if each_dir in ['t1mri']:
                  votes['morphologist'] += 1
                  subdirectories = []
                  g = glob(os.path.join(directory, each, '*', each_dir))
                  for e in g:
                    if os.path.split(e)[1] in ['default_acquisition']:
                        votes['morphologist'] += 1
                    subdirectories.extend(_get_directories(e, fullpath=True))
                  subdir2 = []
                  for e in subdirectories:
                    subdir2.extend(_get_directories(e, fullpath=False))
                  for each_subdir in subdir2:
                     if each_subdir in ['default_analysis', 'whasa_default_analysis', 'registration']:
                        #'spm_preproc', 'segmentation']:
                        votes['morphologist'] += 1
    m = max(votes.values())
    if votes.values().count(m) > 1:
      return None
    if returnvotes:
      return votes.keys()[votes.values().index(m)], votes
    else:
      return votes.keys()[votes.values().index(m)]



def detect_hierarchies(rootdir, maxdepth=3):
   import string
   from glob import glob
   hierarchies = {}
   globpath = rootdir
   dirs = []
   for depth in xrange(maxdepth):
       for i in xrange(depth): globpath = os.path.join(globpath, '*')
       print globpath
       dirs.extend([e for e in glob(globpath) if os.path.isdir(e)])
   print dirs, len(dirs)
   for root in dirs:

      hierarchy = detect_hierarchy(root, True)
      if hierarchy:
        winner, votes = hierarchy
        print root, votes
        hierarchies[root] = winner
   return hierarchies

