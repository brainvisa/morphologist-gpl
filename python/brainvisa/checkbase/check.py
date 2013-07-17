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

def hierarchies_to_action(checkbase):
    import time
    from brainvisa.checkbase import MorphologistCheckbase, FreeSurferCheckbase, SnapshotsCheckbase
    import csv, os, string
    res = {}
    res['action_name'] = 'neurospin_folders_inventory'
    datetime_string = str(time.strftime('%d%m%Y-%H%M%S', time.gmtime()))
    res['action_date'] = datetime_string
    res['action_desc'] = 'Index of existing identified files on /neurospin/cati'
    res['action_vers'] = '1.0'
    res['directory'] = checkbase.directory
    res['key_items'] = checkbase.keyitems
    hiertype = "unknown"
    if isinstance(checkbase, MorphologistCheckbase):
       hiertype = 'Morphologist'
    elif isinstance(checkbase, FreeSurferCheckbase):
       hiertype = 'FreeSurfer'
    elif isinstance(checkbase, SnapshotsCheckbase):
       hiertype = 'Snapshots'
    res['hierarchy_type'] = hiertype
    res['inventory'] = {}
    res['inventory']['all_subjects'] = checkbase.get_flat_subjects()

    if hasattr(checkbase, 'existingfiles'):
          res['inventory']['identified_items'] = checkbase.existingfiles[0]
          res['inventory']['unidentified_items'] = checkbase.existingfiles[1]
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

def json_to_html_table(j):
   import json, csv, string, os
   assert(j['action_name'] == 'simple_neurospin_folders_inventory')
   directory = j['directory']
   inv = j['inventory']
   fields_names = ['subject']
   fields_names.extend(j['key_items'])
   csv = []
   t = {True: '1', False:'0'}
   csv.append(string.join(fields_names, ';'))
   for subject in inv.keys():
      subject_row = [unicode(subject).encode("utf-8")]
      for each in j['key_items']:
         subject_row.append(t[inv[subject][each]])

      csv.append(string.join(subject_row, ';'))
rrivée des resca
   html = csv2html(csv, with_head_tags=False)
   return html

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

#def save_tables(checks, logdir = '/neurospin/cati/Users/operto/logs/existingfiles', datetime_string = ''):
#   for db, checkbase in checks.items():
#      if hasattr(checkbase, 'existingfiles'):
#         save_table(checkbase, logdir, datetime_string)


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
          save_action_diskusage(database_checker, os.path.join(logdir, 'json', 'diskusage'), datetime_string = datetime_string)
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


def jsons_for_web(json, _type='existence'):

   import os, time
   simple = {}
   from brainvisa.checkbase import getfilepath
   if _type == 'existence':
      simple['key_items'] = json['key_items']
      simple['directory'] = json['directory']
      simple['action_name'] = 'simple_neurospin_folders_inventory'
      datetime_string = str(time.strftime('%d%m%Y-%H%M%S', time.gmtime()))
      simple['action_date'] = datetime_string
      simple['action_desc'] = 'Index of existing identified files on /neurospin/cati (simple version)'
      simple['action_vers'] = '1.0'
      inv = {}
      for subject, items in json['inventory']['identified_items'].items():
         inv[subject] = {}
         for each in simple['key_items']:
            inv[subject][each] = each in items.keys()
      simple['inventory'] = inv
      simple['hierarchy_type'] = json['hierarchy_type']
      simple['all_subjects'] = json['inventory']['all_subjects']

   elif _type == 'dates':
      simple['key_items'] = json['key_items']
      simple['directory'] = json['directory']
      simple['action_name'] = 'simple_neurospin_folders_inventory'
      datetime_string = str(time.strftime('%d%m%Y-%H%M%S', time.gmtime()))
      simple['action_date'] = datetime_string
      simple['action_desc'] = 'Index of existing identified files on /neurospin/cati (simple version)'
      simple['action_vers'] = '1.0'
      inv = {}
      for subject, items in json['inventory']['identified_items'].items():
         inv[subject] = {}
         for each in simple['key_items']:
            if each in items.keys():
               print type(json['inventory']['identified_items'][subject])
               inv[subject][each] = os.path.getmtime(getfilepath(each, json['inventory']['identified_items'][subject][each]))
            else:
               inv[subject][each] = False

      simple['inventory'] = inv




   return simple



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

    import os, time, json

    dbindexfile = 'db_indexes.json'
    start_time = time.time()

    # processing users folders
    if verbose: print 'Processing directories...'
    directories = [os.path.join(directory, each) for each in studies_list]
    directories = []
    directories.extend([os.path.join(directory, users_dir, each) for each in users_list])
    print directories
    for db_dir in directories:
       # process each directory
       if verbose: print db_dir, 'in progress'
       h = c.detect_hierarchies(db_dir, maxdepth=3)
       databases = []
       for db, db_type in h.items():
            dir_checks = check.perform_checks_hierarchy(db, hierarchy_type=db_type)
            dbj = json.load(open(os.path.join(logdir, 'json', dbindexfile), 'rb'))
            dbdirs = [each['directory'] for each in dbj]
            if db in dbdirs:
                h_index = dbdirs.index(db)
            else:
                h_index = len(dbdirs)
                dbj.append({'directory' : db, 'filename': 'db_%s.json'%h_index, 'hierarchy_type': db_type})

            json.dump(dbj, open(os.path.join(logdir, 'json', dbindexfile), 'wb'))
            action_json = hierarchies_to_action(dir_checks)
#            # save tables
#            datetime_string = str(time.strftime('%d%m%Y-%H%M%S', time.gmtime()))
            json_file = os.path.join(logdir, 'json', 'databases', 'db_%s.json'%h_index)
            print 'writing', json_file
            json.dump(action_json, open(json_file, 'wb'))

            # simple json existing files
            simple_existing_json = jsons_for_web(action_json, _type='existence')
            simple_jsonfile = os.path.join(logdir, 'json', 'json_for_web', 'existing_%s.json'%h_index)
            print 'writing', simple_jsonfile
            json.dump(simple_existing_json, open(simple_jsonfile, 'wb'))

            # dates json
            simple_existing_json = jsons_for_web(action_json, _type='dates')
            simple_jsonfile = os.path.join(logdir, 'json', 'json_for_web', 'dates_%s.json'%h_index)
            print 'writing', simple_jsonfile
            json.dump(simple_existing_json, open(simple_jsonfile, 'wb'))

    #execution_time = time.time() - start_time
