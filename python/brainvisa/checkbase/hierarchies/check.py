# -*- coding: utf-8 -*-

from __future__ import print_function
from brainvisa.checkbase.check import studies_list, users_dict, users_dir

def perform_checks_hierarchy(directory, hierarchy_type = 'Morphologist'):
    ''' Runs a series of tests on a given dictionary returned from
    checkbase.detect_hierarchies. These tests are performed according to the
    type of the hierarchy.
    - lists key steps of the production pipeline associated to the hierarchy
    - lists subjects (or just directories at the subject level) detected in the hierarchy
    - sorts out subjects whose ID appear multiple times (in distinct groups e.g)
    - identifies all existing files in the hierarchy and collects the unidentified ones.
    - lists subjects with complete datasets according to the previous key items
    - lists subjects with no identified items (possibly mistaken folders)
    All the results are returned as a dictionary.
      checks['all_subjects'] : {'/neurospin/cati/Users/dubois/' : ['toto', 'tata', ...], ...}
      checks['existing_files'] :
         {'/neurospin/cati/Memento/' : ( {'toto' : {'subject': toto,
                                                    'group': 'temoins',
                                                    'acquisition': 'default',
                                                    'modality' : 't1mri',
                                                    'extension' : 'nii'}, ...},
                                         {'tata' : ['i_am_an_unidentified_file.xxx', ...], ...} ), ...}
      checks['complete_subjects']
      checks['multiple_subjects']
      checks['empty_subjects']
      checks['checkbase']

    '''
    from brainvisa.checkbase.hierarchies import morphologist as morpho
    from brainvisa.checkbase.hierarchies import freesurfer as free
    from brainvisa.checkbase.hierarchies import snapshots as snap

    if hierarchy_type == 'morphologist':
        m = morpho.MorphologistCheckbase(directory)
        m.perform_checks()
    elif hierarchy_type == 'freesurfer':
        m = free.FreeSurferCheckbase(directory)
        m.perform_checks()
    elif hierarchy_type == 'snapshots':
        m = snap.SnapshotsCheckbase(directory)
        m.perform_checks()


#    # extracting results and storing them in checks
#    results = extract_results(db, m)
#    for check, d in results.items():
#       checks.setdefault(check, {})
#       for db, res in results[check].items():
#           checks[check].setdefault(db, {})
#
#       checks[check].update(results[check])

    return m


#def extract_results(db, checkbase):
#     from brainvisa.checkbase.hierarchies import morphologist as morpho
#     from brainvisa.checkbase.hierarchies import freesurfer as free
#     from brainvisa.checkbase.hierarchies import snapshots as snap
#     checks = {}
#     for each in ['hierarchies', 'existing_files', 'all_subjects', 'key_items', 'complete_subjects',
#      'multiple_subjects', 'empty_subjects', 'checkbase']:
#        checks[each] = {}
#     if isinstance(checkbase, morpho.MorphologistCheckbase):
#        checks['key_items'][db] = morpho.keyitems
#        checks['existing_files'][db] = checkbase.check_database_for_existing_files()
#        checks['multiple_subjects'][db] = checkbase.get_multiple_subjects()
#        checks['complete_subjects'][db] = checkbase.get_complete_subjects()
#        checks['empty_subjects'][db] = checkbase.get_empty_subjects()
#     elif isinstance(checkbase, free.FreeSurferCheckbase):
#        checks['key_items'][db] = free.keyitems
#        checks['multiple_subjects'][db] = checkbase.get_multiple_subjects()
#     elif isinstance(checkbase, snap.SnapshotsCheckbase):
#        checks['key_items'][db] = snap.keyitems
#
#     checks['all_subjects'][db] = checkbase.get_flat_subjects()
#
#     return checks


def _check_directories(rootdirectory, dirlist, verbose = True):
   from brainvisa import checkbase as c
   import os
   checks = {}
   hierarchies = {}

   for eachdir in dirlist:
       # process each directory
       if verbose: print(eachdir, 'in progress')
       db_dir = os.path.join(rootdirectory, eachdir)
       h = c.detect_hierarchies(db_dir, maxdepth=3)
       assert(not hierarchies.has_key(eachdir))
       hierarchies[eachdir] = h
       dir_checks = perform_checks_hierarchy(h)

       # update big directory
       for each in dir_checks.keys():
          checks.setdefault(each, {})
          for db, res in dir_checks[each].items():
             checks[each].setdefault(db, {})
          checks[each].update(dir_checks[each])
   return checks, hierarchies


def check_hierarchies(input_dir, studies_list = studies_list, users_dir = users_dir, users_list = users_dict.keys(), verbose = True):

   from brainvisa.checkbase import DatabaseChecker
   import os, time

   # build a list of directories contained in '/neurospin/cati'
   # with "users" (in './Users/') and studies (in '.')
   users_dir = os.path.join(input_dir, users_dir)

   checks = {}
   hierarchies = {}
   start_time = time.time()

   # processing users folders
   if verbose: print('Processing users...')
   users_checks, users_hierarchies = _check_directories(users_dir, users_list, verbose = verbose)

   # processing studies folders
   if verbose: print('Processing studies...')
   studies_checks, studies_hierarchies = _check_directories(input_dir, studies_list, verbose = verbose)

   # update big dictionary
   for each in users_checks.keys():
       checks.setdefault(each, {})
       for db, res in users_checks[each].items():
          checks[each].setdefault(db, {})
       checks[each].update(users_checks[each])
   for each in studies_checks.keys():
       checks.setdefault(each, {})
       for db, res in studies_checks[each].items():
          checks[each].setdefault(db, {})
       checks[each].update(studies_checks[each])

   # update hierarchies
   hierarchies.update(users_hierarchies)
   hierarchies.update(studies_hierarchies)

   # compiling results as attributes of an object
   database_checker = DatabaseChecker()
   database_checker.rootdirectory = input_dir
   database_checker.hierarchies =  hierarchies
   database_checker.checks = checks
   database_checker.execution_time = time.time() - start_time
   return database_checker


