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

def csv2html(csvfile):
   html = ''
   import re
   import cgi
   import sys
   import string
   import codecs

   #file = codecs.open(sys.argv[1], encoding='utf-8', mode='r')
   file = open(csvfile, 'r')

   html += """
   <!DOCTYPE html>
   <html>
    <head>
     <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
     <title>Results</title>
     <style>
       body {
         font: .8em Arial, sans-serif;
         background: #fff;
         color: #000;
       }

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
     </style>
    </head>
    <body>
    <table class="b-table">
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
           html += "   <td bgcolor=%s class='b-table__cell'>"%bgcolor + chunk + "</td>"
       html += "      </tr>"

   html += """
     </table>
    </body>
   </html>
   """
   return html


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


def save_table(checkbase, logdir = '/neurospin/cati/Users/operto/logs/existingfiles', datetime_string = ''):
    import csv, time, string, os
    database_id = checkbase.directory
    changed_database_id = string.replace(database_id, os.path.sep, '_')
    fields_names = ['subject']
    fields_names.extend(checkbase.keyitems)
    csv_path = os.path.join(logdir, ('%s-%s.csv'%(changed_database_id, datetime_string)).lstrip('.'))
    with open(csv_path, 'wb',) as csvfile:
      print csv_path
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

def save_tables(checks, logdir = '/neurospin/cati/Users/operto/logs/existingfiles', datetime_string = ''):
   for db, checkbase in checks.items():
      if hasattr(checkbase, 'existingfiles'):
         save_table(checkbase, logdir, datetime_string)


def run_disk_check(directory = '/neurospin/cati', logdir = '/neurospin/cati/Users/operto/logs'):

    import sys, time, os
    from brainvisa.checkbase import DatabaseChecker
    from brainvisa.checkbase.diskusage.check import check_free_disk
    studies_list = ['Projet_X_050213'] #['MEMENTO_fevrier2013']
    users_list = [] #'operto']
    users_dir = ''

    print 'Checking free disk............................................'
    database_checker = check_free_disk(directory) #, get_sizes = True, studies_list = studies_list, users_dir = users_dir, users_list = users_list)

    datetime_string = str(time.strftime('%d%m%Y-%H%M%S', time.gmtime()))
    try:
       if hasattr(database_checker, 'studies_space'):
          # saving csv
          save_csv(database_checker, datetime_string = datetime_string)
    except Exception as e:
       print e
       pass

    # generating report
    import report
    reportgen = report.HTMLReportGenerator(database_checker)
    html = reportgen.generate_html_report()
    html_file = os.path.join(logdir, 'diskreport-%s.html'%datetime_string)
    pdf_file =  os.path.join(logdir, 'diskreport-%s.pdf'%datetime_string)
    with open(html_file, 'wb') as f:
        f.write(html)


def run_hierarchies_check(directory = '/neurospin/cati', logdir = '/neurospin/cati/Users/operto/logs'):
    import sys, time, os
    from brainvisa.checkbase import DatabaseChecker
    from brainvisa.checkbase.hierarchies.check import check_hierarchies
    studies_list = ['Projet_X_050213'] #['MEMENTO_fevrier2013']
    users_list = [] #'operto']

    print 'Checking hierarchies............................................'
    database_checker = check_hierarchies(directory) #, studies_list = studies_list, users_dir = 'Users', users_list = users_list)

    # generating report
    import report
    datetime_string = str(time.strftime('%d%m%Y-%H%M%S', time.gmtime()))
    reportgen = report.HTMLReportGenerator(database_checker)
    html = reportgen.generate_html_report()
    html_file = os.path.join(logdir, 'hierarchiesreport-%s.html'%datetime_string)
    pdf_file =  os.path.join(logdir, 'hierarchiesreport-%s.pdf'%datetime_string)
    with open(html_file, 'wb') as f:
        f.write(html)

    try:
      if hasattr(database_checker, 'checks'):
          # save tables
          save_tables(database_checker.checks['checkbase'], os.path.join(logdir, 'existingfiles'), datetime_string = datetime_string)
    except Exception as e:
       print e
       pass


