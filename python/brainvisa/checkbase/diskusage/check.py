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


def check_free_disk(directory, get_sizes = False):
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
   global start_time

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
   users_dir = os.path.join(directory, 'Users')
   all_users_list = [each for each in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, each))]
   all_studies_list = [ each for each in os.listdir(directory) if os.path.isdir(os.path.join(directory, each))]

   excludelist = ['.snapshot', 'Users']
   for each in excludelist:
      if each in all_studies_list:
         all_studies_list.pop(all_studies_list.index(each))

   # processing users folders
   print 'Processing users...'
   for user in all_users_list:
       print user, 'in progress'
       if user in users_dict.keys():
            s = 0
            if get_sizes: s = get_size(os.path.join(users_dir, user))
            users_space[user] = s
            print user, users_space[user], 'identified', time.time() - start_time
       else:
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

    '''
    from brainvisa.checkbase.hierarchies import morphologist as morpho
    from brainvisa.checkbase.hierarchies import freesurfer as free
    from brainvisa.checkbase.hierarchies import snapshots as snap
    checks = {}
    for each in ['hierarchies', 'existing_files', 'all_subjects', 'key_items', 'complete_subjects',
      'multiple_subjects', 'empty_subjects']:
        checks[each] = {}

    for db, hiertype in h.items():
        if hiertype == 'morphologist':
           m = morpho.MorphologistCheckbase(db)
           checks['key_items'][db] = morpho.keyitems
        elif hiertype == 'freesurfer':
           m = free.FreeSurferCheckbase(db)
           checks['key_items'][db] = free.keyitems
        elif hiertype == 'snapshots':
           m = snap.SnapshotsCheckbase(db)
           checks['key_items'][db] = snap.keyitems

        checks['all_subjects'][db] = m.get_flat_subjects()
        if hiertype == 'morphologist':
           checks['existing_files'][db] = m.check_database_for_existing_files()
           checks['multiple_subjects'][db] = m.get_multiple_subjects()
           checks['complete_subjects'][db] = m.get_complete_subjects()
           checks['empty_subjects'][db] = m.get_empty_subjects()

    return checks

def check_hierarchies(input_dir, do_it = False):

   from brainvisa import checkbase as c

   # create some lists/directories
   checks = {}
   hierarchies = {}
   for each in ['existing_files', 'all_subjects', 'key_items', 'complete_subjects',
         'multiple_subjects', 'empty_subjects']:
      checks[each] = {}
   all_studies_list = []
   all_users_list = []

   # build a list of directories contained in '/neurospin/cati'
   # with "users" (in './Users/') and studies (in '.')
   users_dir = os.path.join(input_dir, 'Users')
   all_users_list = [each for each in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, each))]
   all_studies_list = [ each for each in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, each))]

   identified_users_list = users_dict.keys()

   # processing users folders
   print 'Processing users...'
   for user in all_users_list:
       print user, 'in progress'
       if user in identified_users_list:
              if do_it:
                db_dir = os.path.join(users_dir, user)
                h = c.detect_hierarchies(db_dir, maxdepth=3)
                hierarchies[user] = h
                user_checks = perform_checks_hierarchy(h)
                for each in checks.keys():
                   checks[each].update(user_checks[each])
                #print checks['all_subjects']


   # processing studies folders
   print 'Processing studies...'
   for study in studies_list:
       print study, 'in progress'
       if study in studies_list:
            if do_it:
                db_dir = os.path.join(input_dir, study)
                h = c.detect_hierarchies(db_dir, maxdepth=3)
                hierarchies[user] = h
                study_checks = perform_checks_hierarchy(h)
                for each in checks.keys():
                    checks[each].update(study_checks[each])

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


def perform_check(input_dir, logdir = '/neurospin/cati/Users/operto/logs'):

    import sys, time
    global start_time
    # initialize time
    start_time = time.time()
    print 'Checking free disk............................................'
    database_checker = check_free_disk(input_dir, get_sizes = True)
    print ''
    print 'Checking hierarchies............................................'
    try:
       dbcheck_hierachies = check_hierarchies(input_dir, True)
       database_checker.hierarchies = dbcheck_hierachies.hierarchies
       database_checker.checks = dbcheck_hierachies.checks
       print 'checks'
       print database_checker.checks
    except Exception as e:
       print e
       pass

    database_checker.execution_time = time.time() - start_time
    # generating report
    import pdf, report, time
    datetime_string = str(time.strftime('%d%m%Y-%H%M%S', time.gmtime()))
    reportgen = report.HTMLReportGenerator(database_checker)
    html = reportgen.generate_html_report()
    html_file = os.path.join(logdir, 'report-%s.html'%datetime_string)
    pdf_file =  os.path.join(logdir, 'report-%s.pdf'%datetime_string)

    # saving csv
    save_csv(database_checker)
    with open(html_file, 'wb') as f:
        f.write(html)
