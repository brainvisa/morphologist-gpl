# -*- coding: utf-8 -*-
from __future__ import with_statement # allow python 2.5 to work

users_dir = 'Users'

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
                'NIMH_Gogtay',
                '3C'
                ]

def csv2html(csvfile, with_head_tags=True):
   '''csvfile can be a list of comma separated strings or a csv textfile'''
   html = ''
   import re, os
   import cgi
   import sys
   import string
   import codecs

   #file = codecs.open(sys.argv[1], encoding='utf-8', mode='r')
   if isinstance(csvfile, basestring) and os.path.exists(csvfile):
      file = open(csvfile, 'r')
   elif isinstance(csvfile, list):
      file = csvfile
   if with_head_tags:
      html += """
      <!DOCTYPE html>
      <html>
       <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>Results</title>
      """
   html += """
     <style>
       .b-table {
         width: 100%;
         border-spacing : 2px;
         border-collapse: separate;
         cellspacing : 3px;
       }

       .b-table__cell {
         border: 1px solid;
       }

       .b-table__cell_min {
         background: #DFFCD8;
       }

       .b-table__cell_max {
         background: #F7D6D6;
       }
     </style>"""
   if with_head_tags:
      html += """
    </head>
    <body>
      """
   html += """
    <table class="b-table" style="font-size:6px">
   """
   color = {'0':'#FFFFFF', '1':'#000000'}
   for line in file:
       line = string.strip(line)
       line_chunks = re.split("[ ,;]", line)
       html += "       <tr class='b-table__row'>"
       for chunk in line_chunks:
           chunk = chunk.strip()
           chunk = cgi.escape(chunk)
           chunk = re.sub(r'\\n', '<br />', chunk)
           if not chunk or chunk == '""':
               chunk = "&nbsp;"
           bgcolor = '#FFFFFF'
           if chunk in ['1', '0']:
              bgcolor = color[chunk]
              chunk = '&nbsp;'
           if chunk in ['n/a']:
              bgcolor = color['1']
           html += "   <td bgcolor=%s class='b-table__cell'>"%bgcolor + chunk + "</td>"
       html += "      </tr>"
   html += "</table>"
   if with_head_tags:
      html += """
       </body>
      </html>
      """
   return html

def save_volumes(volumes, logdir = '/neurospin/cati/Users/operto/logs/volumes/', datetime_string = ''):

    import csv, time, string, os
    fields_names = ['subject']
    # selection of volumes
    fields_names.extend(['tivol', 'grey', 'white', 'csf', 'brainmask', 'left_grey', 'right_grey', 'left_white', 'right_white', 'spm_greymap', 'spm_whitemap'])
    if not os.path.exists(logdir):
       os.makedirs(logdir)
    csv_path = os.path.join(logdir, ('volumes-%s.csv'%datetime_string).lstrip('.'))
    with open(csv_path, 'wb',) as csvfile:
      mywriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
      mywriter.writerow(fields_names)
      for subject, vol in volumes.items():
         subject_row = [unicode(subject).encode("utf-8")]
         for k in fields_names[1:]:
            if vol.has_key(k):
               subject_row.append('%3.2f'%vol[k])
            else:
               subject_row.append('n/a')

         mywriter.writerow(subject_row)

    html = csv2html(csv_path)
    f = open(csv_path[:-4] + '.html', 'w')
    f.write(html)
    f.close()


def save_volumes_as_csv(volumes, csvfile):

    import csv, os, string
    with open(csvfile, 'wb',) as csvfile:
        mywriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        mywriter.writerow(volumes.items()[0][1].keys())
        for i, (subject, vol) in enumerate(volumes.items()):
            row = [subject]
            row.extend(vol.values())
            mywriter.writerow(row )

def save_thicknesses_as_csv(volumes, csvfile):
    import csv, os, string
    with open(csvfile, 'wb',) as csvfile:
        mywriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        f1 = volumes.items()[0][1].items()[0][1]
        fields = ['%s_%s'%(volumes.items()[0][1].keys()[0][0], each) for each in f1]
        fields.extend(['%s_%s'%(volumes.items()[0][1].keys()[1][0], each) for each in f1])
        mywriter.writerow(fields)
        for i, (subject, vol) in enumerate(volumes.items()):
            row = [subject]
            for side, values in vol.items():
                for name, v in values.items():
                    if name == 'average':
                        row.append(v)
                    else:
                        row.append(v[4])
            mywriter.writerow(row)

def save_csv(database_checker, logdir = '/neurospin/cati/Users/operto/logs', datetime_string = ''):

    import csv, os, string
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

def save_action_diskusage(database_checker, logdir = '/neurospin/cati/Users/operto/logs/json', datetime_string = ''):
    import json

    import csv, os, string
    studies_space = database_checker.studies_space
    users_space = database_checker.users_space
    other_studies = database_checker.other_studies
    other_users = database_checker.other_users
    res = {}
    res['action_name'] = 'neurospin_diskusage'
    res['action_date'] = datetime_string
    res['action_desc'] = 'General info about disk usage on /neurospin/cati'
    res['action_vers'] = '1.0'
    for each in ['studies', 'users', 'global']:
       res[each] = {}

    for i, (study, size) in enumerate(studies_space.items()):
        res['studies'][study] = size
    for i, (user, size) in enumerate(users_space.items()):
        res['users'][user] = size

    for i, (study, size) in enumerate(other_studies.items()):
        res['studies'][study] = size
    for i, (user, size) in enumerate(other_users.items()):
        res['users'][user] = size

    s = string.split(database_checker.global_disk_space, ' ')
    for i, each in enumerate([ 'device', 'size', 'used', 'available', 'percent' ]):
        res['global'][each] = s[i]

    res['global']['execution_time'] = database_checker.execution_time
    res['global']['directory'] = database_checker.rootdirectory
    json_file = os.path.join(logdir, 'action_%s.json'%datetime_string)
    while os.path.exists(json_file):
       import time
       time.sleep(2)
       json_file = os.path.join(logdir, 'action_%s.json'%datetime_string)
    json.dump(res, open(json_file, 'wb'))

def get_action_hierarchies(checkbases):
    import time
    from brainvisa.checkbase import MorphologistCheckbase, FreeSurferCheckbase, SnapshotsCheckbase
    import csv, os, string
    res = {}
    res['action_name'] = 'neurospin_folders_inventory'
    datetime_string = str(time.strftime('%d%m%Y-%H%M%S', time.gmtime()))
    res['action_date'] = datetime_string
    res['action_desc'] = 'Index of existing identified files on /neurospin/cati'
    res['action_vers'] = '1.0'
    res['inventory'] = {}
    for db, c in checkbases.items():
       print db
       if hasattr(c, 'existingfiles'):
          res['inventory'][db] = {}
          res['inventory'][db]['key_items'] = c.keyitems
          hiertype = "unknown"
          if isinstance(c, MorphologistCheckbase):
             hiertype = 'Morphologist'
          elif isinstance(c, FreeSurferCheckbase):
             hiertype = 'FreeSurfer'
          elif isinstance(c, SnapshotsCheckbase):
             hiertype = 'Snapshots'
          res['inventory'][db]['hierarchy_type'] = hiertype
          res['inventory'][db]['identified_items'] = c.existingfiles[0]
          res['inventory'][db]['unidentified_items'] = c.existingfiles[1]
          res['inventory'][db]['all_subjects'] = c.get_flat_subjects()

    return res

def save_table(checkbase, logdir = '/neurospin/cati/Users/operto/logs/existingfiles', datetime_string = ''):
    import csv, time, string, os
    database_id = checkbase.directory
    changed_database_id = string.replace(database_id, os.path.sep, '_')
    fields_names = ['subject']
    fields_names.extend(checkbase.keyitems)
    if not os.path.exists(logdir):
       os.makedirs(logdir)
    csv_path = os.path.join(logdir, ('%s-%s.csv'%(changed_database_id, datetime_string)).lstrip('.'))
    with open(csv_path, 'wb',) as csvfile:
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

    html = csv2html(csv_path)
    f = open(csv_path[:-4] + '.html', 'w')
    f.write(html)
    f.close()

def json_to_tables(j):
   tables = {}
   import json, csv, string, os
   assert(j['action_name'] == 'neurospin_folders_inventory')
   for directory, inv in j['inventory'].items():
       fields_names = ['subject']
       fields_names.extend(inv['key_items'])
       csv = []
       csv.append(string.join(fields_names, ';'))
       for subject in inv['identified_items'].keys():
            subject_row = [unicode(subject).encode("utf-8")]
            for each in inv['key_items']:
               if each in inv['identified_items'][subject].keys():
                  subject_row.append('1')
               else:
                  subject_row.append('0')

            csv.append(string.join(subject_row, ';'))

       html = csv2html(csv, with_head_tags=False)
       tables[directory] = html

   return tables

def json_to_measures_tables(j):
   tables = {}
   import json, csv, string, os
   assert(j['action_name'] == 'measures')
   for directory, inv in j['inventory'].items():
       fields_names = ['subject']
       fields_names.extend(inv['key_items'])
       csv = []
       csv.append(string.join(fields_names, ';'))
       for subject in inv['identified_items'].keys():
            subject_row = [unicode(subject).encode("utf-8")]
            for each in inv['key_items']:
               if each in inv['identified_items'][subject].keys():
                  subject_row.append('1')
               else:
                  subject_row.append('0')

            csv.append(string.join(subject_row, ';'))

       html = csv2html(csv, with_head_tags=False)
       tables[directory] = html

   return tables

def save_tables(checks, logdir = '/neurospin/cati/Users/operto/logs/existingfiles', datetime_string = ''):
   for db, checkbase in checks.items():
      if hasattr(checkbase, 'existingfiles'):
         save_table(checkbase, logdir, datetime_string)


def run_disk_check(directory = '/neurospin/cati', logdir = '/neurospin/cati/Users/operto/logs', studies_list = None,
                   users_list = None, users_dir = None, get_sizes = True, verbose = True):

    import sys, time, os
    from brainvisa.checkbase import DatabaseChecker
    from brainvisa.checkbase.diskusage.check import check_disk_usage
    from brainvisa.checkbase import check as ch
    if not studies_list: studies_list = ch.studies_list
    if users_list is None: users_list = ch.users_dict.keys()
    if not users_dir: users_dir = ch.users_dir
    if len(users_list) == 0: users_dir = ''
    assert(os.path.exists(logdir))

    if verbose: print 'Checking free disk............................................'
    database_checker = check_disk_usage(directory, get_sizes = get_sizes, studies_list = studies_list, users_dir = users_dir, users_list = users_list, verbose = verbose, process_undeclared = True)

    datetime_string = str(time.strftime('%d%m%Y-%H%M%S', time.gmtime()))
    try:
       if hasattr(database_checker, 'studies_space'):
          # saving csv
          #save_csv(database_checker, logdir, datetime_string = datetime_string)
          save_action_diskusage(database_checker, os.path.join(logdir, 'json'), datetime_string = datetime_string)
    except Exception as e:
       if verbose: print e
       pass

    # generating report
    #import report
    #reportgen = report.HTMLReportGenerator(database_checker)
    #html = reportgen.generate_html_report()
    #html_file = os.path.join(logdir, 'diskreport-%s.html'%datetime_string)
    #pdf_file =  os.path.join(logdir, 'diskreport-%s.pdf'%datetime_string)
    #with open(html_file, 'wb') as f:
    #    f.write(html)


def run_hierarchies_check(directory = '/neurospin/cati', logdir = '/neurospin/cati/Users/operto/logs', studies_list = None, users_list = None, users_dir = None, verbose = True):
    ''' Ex:
    run_hierarchies_check(directory = '/neurospin/cati', logdir = '/neurospin/cati/Users/operto/logs')
    If studies_list is None, it is then reset to ['Memento', 'ADNI', ...]
    If users_list is None, it is then reset to ['operto', 'champseix', 'mangin', ...]
    '''
    import sys, time, os
    from brainvisa.checkbase.hierarchies import check
    from brainvisa.checkbase import check as ch
    from brainvisa import checkbase as c
    if not studies_list: studies_list = ch.studies_list
    if not users_list: users_list = ch.users_dict.keys()
    if not users_dir: users_dir = ch.users_dir
    if len(users_list) == 0: users_dir = ''

    assert(os.path.exists(logdir))

    import os, time

    start_time = time.time()

    # processing users folders
    if verbose: print 'Processing directories...'
    directories = [os.path.join(directory, each) for each in studies_list]
    #directories.extend([os.path.join(directory, users_dir, each) for each in users_list])
    print directories
    for db_dir in directories:
       # process each directory
       if verbose: print db_dir, 'in progress'
       h = c.detect_hierarchies(db_dir, maxdepth=3)
       print h
       dir_checks = check.perform_checks_hierarchy(h)
       if dir_checks.has_key('checkbase'):
          action_json = get_action_hierarchies(dir_checks['checkbase'])
          # save tables
          datetime_string = str(time.strftime('%d%m%Y-%H%M%S', time.gmtime()))
          json_file = os.path.join(logdir, 'json', 'action_%s.json'%datetime_string)
          while os.path.exists(json_file):
             import time
             time.sleep(2)
             json_file = os.path.join(logdir, 'json', 'action_%s.json'%datetime_string)

          import json
          print 'writing', json_file
          json.dump(action_json, open(json_file, 'wb'))


    #execution_time = time.time() - start_time
