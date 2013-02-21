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


def get_size(start_path = '.', fastmode=True):
    global do_get_size
    if not do_get_size: return 0
    total_size = 0
    if fastmode:
        return fast_get_size(start_path)
    for dirpath, dirnames, filenames in os.walk(start_path):
      if not os.path.islink(dirpath):
        for f in filenames:
          if not os.path.islink(os.path.join(dirpath, f)):
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def fast_get_size(path = '.'):
    import subprocess
    df = subprocess.Popen(['du', '-sb', path], stdout=subprocess.PIPE)
    output = df.communicate()[0]
    #print output
    size, directory = output.rstrip('\n').split('\t')
    return size


class DatabaseChecker():
    def __init__(self):
        pass


def check_free_disk(input_dir, get_sizes = False):
   import subprocess, time
   global do_get_size, do_get_hierarchies
   do_get_size = get_sizes

   # initialize time
   start_time = time.time()

   # get df output
   df = subprocess.Popen(["df", input_dir], stdout=subprocess.PIPE)
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
   users_dir = os.path.join(input_dir, 'Users')
   all_users_list = [each for each in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, each))]
   all_studies_list = [ each for each in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, each))]

   excludelist = ['.snapshot', 'Users']
   for each in excludelist:
      if each in all_studies_list:
         all_studies_list.pop(all_studies_list.index(each))

   # processing users folders
   print 'Processing users...'
   for user in all_users_list:
       print user, 'in progress'
       if user in users_dict.keys():
            users_space[user] = get_size(os.path.join(users_dir, user))
            print user, users_space[user], 'identified', time.time() - start_time
       else:
            other_users[user] = get_size(os.path.join(users_dir, user))
            print user, other_users[user], 'undeclared', time.time() - start_time

   # processing studies folders
   print 'Processing studies...'
   for study in all_studies_list:
       print study, 'in progress'
       if study in studies_list:
           studies_space[study] = get_size(os.path.join(input_dir, study))
           print study, studies_space[study], 'identified', time.time() - start_time
       else:
           other_studies[study] = get_size(os.path.join(input_dir, study))
           print study, other_studies[study], 'undeclared', time.time() - start_time

   # compiling results as attributes of an object
   database_checker = DatabaseChecker()
   database_checker.rootdirectory = input_dir
   database_checker.global_disk_space =  global_disk_space
   database_checker.studies_space = studies_space
   database_checker.users_space = users_space
   database_checker.other_studies = other_studies
   database_checker.other_users = other_users
   database_checker.execution_time = time.time() - start_time

   return database_checker


def check_hierarchies(input_dir, do_it = False):

   from brainvisa import checkbase as c
   from brainvisa.checkbase import morphologist as morpho

   # create some lists/directories
   databases = {}
   for each in ['hierarchies', 'existing_files', 'all_subjects', 'key_items', 'complete_subjects']:
      databases[each] = {}
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
              db_dir = os.path.join(users_dir, user)
              if do_it:
                h = c.detect_hierarchies(db_dir, maxdepth=1)
                print h
                databases['hierarchies'][user] = h
                for db, hiertype in h.items():
                    if hiertype == 'morphologist': m = c.morpho.MorphologistCheckbase(db)

                    databases['existing_files'][db] = m.check_database_for_existing_files()
                    databases['all_subjects'][db] = m.get_all_subjects(db)
                    databases['key_items'][db] = m.keyitems
                    #databases['complete_subjects'][db] =


   # processing studies folders
   do_it = False
   print 'Processing studies...'
   for study in studies_list:
       print study, 'in progress'
       if study in studies_list:
             if do_it:
               h = c.detect_hierarchies(os.path.join(input_dir, study), maxdepth=2)
               print h
               hierarchies[study] = h

   # compiling results as attributes of an object
   database_checker = DatabaseChecker()
   database_checker.rootdirectory = input_dir
   database_checker.databases =  databases
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

    import sys
    print 'Checking free disk............................................'
    database_checker = check_free_disk(input_dir, get_sizes = True)
    #print ''
    #print 'Checking hierarchies............................................'
    #dbcheck_hierachies = check_hierarchies(input_dir, True)
    #database_checker.databases = dbcheck_hierachies.databases

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
