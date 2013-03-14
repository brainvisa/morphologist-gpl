# -*- coding: utf-8 -*-
image_extensions = '(nii.gz|nii|ima|ima.gz)$'
mesh_extensions = '(gii|mesh)$'

def parsefilepath(filepath, patterns = None):
  ''' Matches a filepath with a set of regex given as a dictionary named patterns (default : checkbase.hierarchies.morphologist.patterns).
  Returns the key name of the successfully matched pattern, and the identified attributes
  ex : c.parsefilepath('/neurospin/cati/Users/reynal/BVdatabase/Paris/CHBR/t1mri/raw/CHBR.nii')
  ('raw',
     {'acquisition': 'raw',
     'database': '/neurospin/cati/Users/reynal/BVdatabase',
     'extension': 'nii',
     'group': 'Paris',
     'modality': 't1mri',
     'subject': 'CHBR'}) '''
  import morphologist as morpho
  if not patterns: patterns = morpho.patterns
  import re, os
  for datatype, path in patterns.items():
    m = re.match(r"%s"%path, filepath)
    if m:
       return datatype, m.groupdict()


def getfilepath(datatype, attributes, patterns = None):
    ''' Returns a filepath built on a given datatype and a dictionary of attributes. For now based on Morpho patterns'''
    import morphologist as morpho
    if not patterns: patterns = morpho.patterns
    assert(isinstance(attributes, dict))
    return processregexp(patterns[datatype], attributes)


def processregexp(regexp, attributes, wildcards = True):
    ''' From a regexp and a dictionary of attributes, returns a string where all the regexp fields have been replaced by values given by the dictionary.
        If wildcards is True, then if a regexp field misses in the dictionary, it is replaced by a wildcard.
    ex : r = '(?P<database>[\\w -/]+)/(?P<group>[\\w -]+)/(?P<subject>\\w+)/(?P<modality>\\w+)/(?P<acquisition>[\\w -]+)/(?P=subject).(nii.gz|nii|ima|ima.gz)'
         att = {'database' : 'basedonnees', 'group' : 'groupe', 'subject' : 'mr_toto', 'modality' : 't1mri', 'acquisition' : 'default_acquisition', 'inutile' : 'useless'}
         processregexp(morpho.patterns['raw'], att)

         'basedonnees/groupe/mr_toto/t1mri/default_acquisition/mr_toto.(nii.gz|nii|ima|ima.gz)'
    '''

    def _findmatchingparenthesis(s):
       opening = []
       closing = []
       i = 0
       while i != -1:
         i = s.find('(', i+1)
         if i>-1: opening.append(i)
       i = 0
       while i != -1:
         i = s.find(')', i+1)
         if i>-1: closing.append(i)
       both = []
       both.extend(opening)
       both.extend(closing)
       score = 1
       both = set(both)
       assert(len(both) == len(opening) + len(closing))
       for each in both:
          if each in opening:
             score += 1
          elif each in closing:
             score -= 1
          if score == 0: return each

    import string, re
    s = string.split(regexp, '(?P')
    res = []
    for each in s:
        m = re.match('^[=<](?P<field>\w+)', each)
        if m:
            field = m.groupdict()['field']
            #print field, attributes[field], each[_findmatchingparenthesis(each)+1:]
            if wildcards:
               if not attributes.has_key(field):
                  attributes[field] = '*'
            res.append('%s%s'%(attributes[field], each[_findmatchingparenthesis(each)+1:].rstrip('$)')) )

    return string.join(res, '')

def get_files(databasedir):
  ''' Returns a list of the files contained in the directory and subdirectories '''
  import os
  all_files = []
  for root, dirs, files in os.walk(databasedir):
    for f in files:
      all_files.append(os.path.join(root, f))
  return all_files


def detect_hierarchy(directory, returnvotes = False, maxvote=50):
    ''' Detects if a file tree matches those created/used by Morphologist, FreeSurfer or SnapBase.
    If returnvotes is True, the votes that let the decision are also returned. maxvotes is a
    threshold to end the process once consensus is assumedly reached.
    ex: c.detect_hierarchy('/neurospin/cati/Memento/BVdatabase')
        'morphologist'
    '''
    def _get_directories(root, threshold = 1, fullpath = False):
        import os
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
    import string, os
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



def detect_hierarchies(directory, maxdepth=3):
   ''' Browses a directory (the maximum depth is given by maxdepth) in search for
   hierarchies matching Morphologist, FreeSurfer or SnapBase.
   Calls c.detect_hierarchy for any subdir of 'directory'.
    '''
   import os, string
   from glob import glob
   hierarchies = {}
   globpath = directory
   dirs = []
   for depth in xrange(maxdepth):
       for i in xrange(depth): globpath = os.path.join(globpath, '*')
       dirs.extend([e for e in glob(globpath) if os.path.isdir(e)])
   for root in dirs:
      hierarchy = detect_hierarchy(root, True)
      if hierarchy:
        winner, votes = hierarchy
        hierarchies[root] = winner
   return hierarchies

