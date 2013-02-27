# -*- coding: utf-8 -*-


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



def save_csv(database_checker, logdir = '/neurospin/cati/Users/operto/logs'):

    import csv, os, time, string
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
      if hasattr(checkbase, 'existingfiles'):
         save_table(checkbase)


def perform_check(directory = '/neurospin/cati', logdir = '/neurospin/cati/Users/operto/logs'):

    import sys, time
    from brainvisa.checkbase import DatabaseChecker
    from brainvisa.checkbase.diskusage.check import check_free_disk
    from brainvisa.checkbase.hierarchies.check import check_hierarchies
    database_checker = DatabaseChecker()
    studies_list = []#'CATI_MIRROR']
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
    print database_checker.checks['checkbase'].keys()

    # generating report
    import report
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
