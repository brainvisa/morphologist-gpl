# -*- coding: utf-8 -*-

from brainvisa.checkbase.check import studies_list, users_dict

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

def check_free_disk(directory, get_sizes = True, studies_list = studies_list, users_dir = 'Users', users_list = users_dict.keys(), excludelist = ['.snapshot', 'Users']):
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
   import os, subprocess, time, string
   from brainvisa.checkbase import DatabaseChecker
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
            #continue
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
           #continue
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
