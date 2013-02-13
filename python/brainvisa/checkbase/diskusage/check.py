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
                'DICOM',
                'Imagen',
                'Lilly',
                'MAPT',
                'N4U',
                'NIMH_Gogtay'
                ]


def get_size(start_path = '.', fastmode=True):
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


def check_free_disk(input_dir, get_sizes=False):

   import subprocess, time
   start_time = time.time()

   df = subprocess.Popen(["df", input_dir], stdout=subprocess.PIPE)
   output = df.communicate()[0]
   device, size, used, available, percent, mountpoint = \
   output.split("\n")[1].split()
   global_disk_space =  string.join([device, size, used, available, percent[:-1]], ' ')

   studies_space = {}
   other_studies = {}


   users_space = {}
   other_users = {}

   all_studies_list = []
   all_users_list = []

   if get_sizes:
       users_dir = os.path.join(input_dir, 'Users')
       for each in os.listdir(users_dir):
            if os.path.isdir(os.path.join(users_dir, each)):
                all_users_list.append(each)
       for each in os.listdir(input_dir):
            if os.path.isdir(os.path.join(input_dir, each)):
                all_studies_list.append(each)

       identified_users_list = users_dict.keys()

       print 'Processing users...'
       for user in all_users_list:
           print user, 'in progress'
           if user in identified_users_list:
                users_space[user] = get_size(os.path.join(users_dir, user))
                print user, users_space[user], 'identified', time.time() - start_time
           else:
                pass
                #other_users[user] = get_size(os.path.join(users_dir, user))
                #print user, other_users[user], 'undeclared', time.time() - start_time

       print 'Processing studies...'
       for study in studies_list:
           print study, 'in progress'
           if study in studies_list:
               studies_space[study] = get_size(os.path.join(input_dir, study))
               print study, studies_space[study], 'identified', time.time() - start_time
           else:
               pass#other_studies[study] = get_size(os.path.join(input_dir, study))
               #print study, other_studies[study], 'undeclared', time.time() - start_time


   database_checker = DatabaseChecker()
   database_checker.database = input_dir
   database_checker.global_disk_space =  global_disk_space
   database_checker.studies_space = studies_space
   database_checker.users_space = users_space
   database_checker.other_studies = other_studies
   database_checker.other_users = other_users
   database_checker.execution_time = time.time() - start_time

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

    from PyQt4 import Qt, QtCore, QtGui
    import sys
    qt_app = Qt.QApplication(sys.argv)
    database_checker = check_free_disk(input_dir, True)
    import pdf, report, time
    datetime_string = str(time.strftime('%d%m%Y-%H%M%S', time.gmtime()))
    reportgen = report.HTMLReportGenerator(database_checker)
    html = reportgen.generate_html_report()
    printer = pdf.PDFReportPrinter(os.path.join(logdir, 'report-%s.pdf'%datetime_string), 'Report', html)
    printer.print_()
    save_csv(database_checker)
