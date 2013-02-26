# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui, Qt, QtWebKit
import os, sys, string

users_dict = {'operto' : 'go231605',
              'champseix': 'cc233590',
              'fischer' : 'cf227350',
              'lecomte' : 'sl226881',
              'longodossantos' : 'cl228633',
              'mangin' : 'jm135268',
              'cointepas' : 'yc176684',
              'perrot' : 'mp210984',
              'reynal' : 'mr231721',
              'roca' : 'pr216633',
              'sun': 'zs213040',
              'thoprakarn' : 'ut229786'
                }


studies_list = ['Memento',
                'ADNI',
                'CATI_MIRROR',
                'Imagen',
                'Lilly',
                'MAPT',
                'N4U',
                'NIMH_Gogtay'
                ]


def get_size(directory = '.', fastmode=True):
    ''' Returns the size of a directory.
    By default, the size is computed using du Unix command.
    If fastmode is set to False, it uses os.walk and returns the
    sum of sizes of all the files recursively contained in the directory'''

    def fast_get_size(path = '.'):
       import subprocess
       df = subprocess.Popen(['du', '-sb', path], stdout=subprocess.PIPE)
       output = df.communicate()[0]
       size, directory = output.rstrip('\n').split('\t')
       return size

    total_size = 0
    if fastmode:
        return fast_get_size(directory)
    for dirpath, dirnames, filenames in os.walk(directory):
      if not os.path.islink(dirpath):
        for f in filenames:
          if not os.path.islink(os.path.join(dirpath, f)):
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


class DatabaseChecker():
    ''' DatabaseChecker objects are only intended to store as attributes a collection
    of database-related information. '''
    def __init__(self):
        pass


def check_free_disk(directory, get_sizes = False, studies_list = studies_list, users_dir = 'Users', users_list = users_dict.keys(), excludelist = ['.snapshot', 'Users']):
   ''' Disk usage controlling procedure, originally for /neurospin/cati
   - gets the output of df Unix function
   - estimates the size of every folder under the given directory
   Processes './Users' folder in a distinct way (intended to contain personal
   folders).
   Filters '/neurospin/cati/.snapshot' out of being processed.
   If get_sizes is set to False, skips size estimation and assumes every folder
   has null size (debug).
   The procedure uses two lists of identified users/studies (users_dict and
   studies_list) defined in brainvisa.checkbase.diskusage.check module. Any
   other folder will still be processed but notified as undeclared.

   At the end, results are stored as attributes in a DatabaseChecker object.
   database_checker.rootdirectory : directory
   database_checker.global_disk_space : df output
   database_checker.studies_space = {'Memento' : 98765432, ...}
   database_checker.users_space = {'broca' : 12345678, ...}
   database_checker.other_studies = {'JUNKDIR' : 5413213, ...}
   database_checker.other_users = {'datajunkie1337' : 12223, ...}
   '''
   import subprocess, time
   start_time = time.time()

   # get df output
   df = subprocess.Popen(["df", directory], stdout=subprocess.PIPE)
   output = df.communicate()[0]
   device, size, used, available, percent, mountpoint = \
   output.split("\n")[1].split()
   global_disk_space =  string.join([device, size, used, available, percent[:-1]], ' ')

   # initialize some list and dictionaries
   studies_space = {}
   other_studies = {}

   users_space = {}
   other_users = {}

   all_studies_list = []
   all_users_list = []

   # build a list of directories contained in '/neurospin/cati'
   # with "users" (in './Users/') and studies (in '.')
   users_dir = os.path.join(directory, users_dir)
   all_users_list = [each for each in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, each))]
   all_studies_list = [ each for each in os.listdir(directory) if os.path.isdir(os.path.join(directory, each))]

   for each in excludelist:
      if each in all_studies_list:
         all_studies_list.pop(all_studies_list.index(each))

   # processing users folders
   print 'Processing users...'
   for user in all_users_list:
       print user, 'in progress'
       if user in users_list:
            s = 0
            if get_sizes: s = get_size(os.path.join(users_dir, user))
            users_space[user] = s
            print user, users_space[user], 'identified', time.time() - start_time
       else:
            continue
            s = 0
            if get_sizes: s = get_size(os.path.join(users_dir, user))
            other_users[user] = s
            print user, other_users[user], 'undeclared', time.time() - start_time

   # processing studies folders
   print 'Processing studies...'
   for study in all_studies_list:
       print study, 'in progress'
       if study in studies_list:
           s = 0
           if get_sizes: s = get_size(os.path.join(directory, study))
           studies_space[study] = s
           print study, studies_space[study], 'identified', time.time() - start_time
       else:
           continue
           s = 0
           if get_sizes: s = get_size(os.path.join(directory, study))
           other_studies[study] = s
           print study, other_studies[study], 'undeclared', time.time() - start_time

   # compiling results as attributes of an object
   database_checker = DatabaseChecker()
   database_checker.rootdirectory = directory
   database_checker.global_disk_space =  global_disk_space
   database_checker.studies_space = studies_space
   database_checker.users_space = users_space
   database_checker.other_studies = other_studies
   database_checker.other_users = other_users
   database_checker.execution_time = time.time() - start_time

   return database_checker


def perform_checks_hierarchy(h):
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
    checks = {}

    for db, hiertype in h.items():
        if hiertype == 'morphologist':
           m = morpho.MorphologistCheckbase(db)
           m.perform_checks()
        elif hiertype == 'freesurfer':
           m = free.FreeSurferCheckbase(db)
        elif hiertype == 'snapshots':
           m = snap.SnapshotsCheckbase(db)

           checks.setdefault('checkbase', {})
           checks['checkbase'][db] = m

        # extracting results and storing them in checks
        results = extract_results(db, m)
        for check, d in results.items():
           checks.setdefault(check, {})
           for db, res in results[check].items():
               checks[check].setdefault(db, {})

           checks[check].update(results[check])

    return checks


def extract_results(db, checkbase):
     from brainvisa.checkbase.hierarchies import morphologist as morpho
     from brainvisa.checkbase.hierarchies import freesurfer as free
     from brainvisa.checkbase.hierarchies import snapshots as snap
     checks = {}
     for each in ['hierarchies', 'existing_files', 'all_subjects', 'key_items', 'complete_subjects',
      'multiple_subjects', 'empty_subjects', 'checkbase']:
        checks[each] = {}
     if isinstance(checkbase, morpho.MorphologistCheckbase):
        checks['key_items'][db] = morpho.keyitems
        checks['existing_files'][db] = checkbase.check_database_for_existing_files()
        checks['multiple_subjects'][db] = checkbase.get_multiple_subjects()
        checks['complete_subjects'][db] = checkbase.get_complete_subjects()
        checks['empty_subjects'][db] = checkbase.get_empty_subjects()
     elif isinstance(checkbase, free.FreeSurferCheckbase):
        checks['key_items'][db] = free.keyitems
     elif isinstance(checkbase, snap.SnapshotsCheckbase):
        checks['key_items'][db] = snap.keyitems

     checks['all_subjects'][db] = checkbase.get_flat_subjects()

     return checks


def _check_directories(rootdirectory, dirlist):
   from brainvisa import checkbase as c
   checks = {}
   hierarchies = {}

   for eachdir in dirlist:
       # process each directory
       print eachdir, 'in progress'
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


def check_hierarchies(input_dir, studies_list = studies_list, users_dir = 'Users', users_list = users_dict.keys()):

   from brainvisa import checkbase as c

   # build a list of directories contained in '/neurospin/cati'
   # with "users" (in './Users/') and studies (in '.')
   users_dir = os.path.join(input_dir, users_dir)

   checks = {}
   hierarchies = {}

   # processing users folders
   print 'Processing users...'
   users_checks, users_hierarchies = _check_directories(users_dir, users_list)

   # processing studies folders
   print 'Processing studies...'
   studies_checks, studies_hierarchies = _check_directories(input_dir, studies_list)

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
   return database_checker


def save_csv(database_checker, logdir = '/neurospin/cati/Users/operto/logs'):

    import csv
    import time
    datetime_string = str(time.strftime('%d%m%Y-%H%M%S', time.gmtime()))
    studies_space = database_checker.studies_space
    users_space = database_checker.users_space

    with open(os.path.join(logdir, 'directoryusage-%s.csv'%datetime_string), 'wb',) as csvfile:
        mywriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        mywriter.writerow([ 'directory', 'size'])
        for i, (study, size) in enumerate(studies_space.items()):
            mywriter.writerow([ unicode(study).encode("utf-8"), size] )
        for i, (user, size) in enumerate(users_space.items()):
            mywriter.writerow([ unicode(user).encode("utf-8"), size] )
    with open(os.path.join(logdir, 'globalusage-%s.csv'%datetime_string), 'wb',) as csvfile:
        mywriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        mywriter.writerow([ 'device', 'size', 'used', 'available', 'percent', 'computation time'])
        device, size, used, available, percent = string.split(database_checker.global_disk_space, ' ')
        mywriter.writerow([ device, size, used, available, percent, database_checker.execution_time])


def save_table(checkbase, logdir = '/neurospin/cati/Users/operto/logs/existingfiles'):
    import csv, time, string, os
    datetime_string = str(time.strftime('%d%m%Y-%H%M%S', time.gmtime()))
    database_id = checkbase.directory
    changed_database_id = string.replace(database_id, os.path.sep, '_')
    fields_names = ['subject']
    fields_names.extend(checkbase.keyitems)

    with open(os.path.join(logdir, '%s-%s.csv'%(changed_database_id, datetime_string)), 'wb',) as csvfile:
      mywriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
      mywriter.writerow(fields_names)
      for subject in checkbase.existingfiles[0].keys():
         subject_row = [unicode(subject).encode("utf-8")]
         for each in checkbase.keyitems:
            if each in checkbase.existingfiles[0][subject].keys():
               subject_row.append(1)
            else:
               subject_row.append(0)

         mywriter.writerow(subject_row)

def save_tables(checks):
   for db, checkbase in checks.items():
      print db, checkbase.directory
      if hasattr(checkbase, 'existingfiles'):
         save_table(checkbase)


def perform_check(directory = '/neurospin/cati', logdir = '/neurospin/cati/Users/operto/logs'):

    import sys, time
    database_checker = DatabaseChecker()
    studies_list = ['CATI_MIRROR']
    users_list = ['operto']

    print 'Checking free disk............................................'
    dbdisk_checker = check_free_disk(directory, get_sizes = True, studies_list = studies_list, users_dir = 'Users', users_list = users_list)
    for each in ['users_space', 'studies_space', 'other_users', 'other_studies', 'rootdirectory', 'global_disk_space', 'execution_time']:
        setattr(database_checker, each, getattr(dbdisk_checker, each))

    print ''
    print 'Checking hierarchies............................................'
    dbhierarchies_checker = check_hierarchies(directory, studies_list = studies_list, users_dir = 'Users', users_list = users_list)
    for each in ['hierarchies', 'checks']:
        setattr(database_checker, each, getattr(dbhierarchies_checker, each))

    # generating report
    import pdf, report, time
    datetime_string = str(time.strftime('%d%m%Y-%H%M%S', time.gmtime()))
    reportgen = report.HTMLReportGenerator(database_checker)
    html = reportgen.generate_html_report()
    html_file = os.path.join(logdir, 'report-%s.html'%datetime_string)
    pdf_file =  os.path.join(logdir, 'report-%s.pdf'%datetime_string)

    try:
       if hasattr(database_checker, 'studies_space'):
          # saving csv
          save_csv(database_checker)
    except Exception as e:
       print e
       pass
    try :
       if hasattr(database_checker, 'checks'):
          # save tables
          save_tables(database_checker.checks['checkbase'])
    except Exception as e:
       print e
       pass

    with open(html_file, 'wb') as f:
        f.write(html)
