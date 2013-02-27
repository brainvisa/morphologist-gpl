# -*- coding: utf-8 -*-
import os, sys, string, time
import datetime
import sys

class size( long ):
    """ define a size class to allow custom formatting
        Implements a format specifier of S for the size class - which displays a human readable in b, kb, Mb etc
    """
    def __format__(self, fmt):
        import math
        if fmt == "" or fmt[-1] != "S":
            if fmt[-1].tolower() in ['b','c','d','o','x','n','e','f','g','%']:
                # Numeric format.
                return long(self).__format__(fmt)
            else:
                return str(self).__format__(fmt)

        val, s = float(self), ["b ","Kb","Mb","Gb","Tb","Pb"]
        if val<1:
            # Can't take log(0) in any base.
            i,v = 0,0
        else:
            i = int(math.log(val,1024))+1
            v = val / math.pow(1024,i)
            v,i = (v,i) if v > 0.5 else (v*1024,i-1)
        return ("{0:{1}f}"+s[i]).format(v, fmt[:-1])


def revision_number(filepath):
   import subprocess, string

   print filepath
   df = subprocess.Popen(['svn', 'info', filepath], stdout=subprocess.PIPE)
   output = df.communicate()[0]
   rev_number = string.atoi(output.split('\n')[4].split(' ')[1])
   return rev_number


class HTMLReportGenerator():

    def __init__(self, database_checker):
        '''
    An HTMLReportGenerator instance is in charge of compiling the analysis
    results stored in a DatabaseChecker in order to generate an HTML report
    describing these.
    As a DatabaseChecker may contain several instances of Quality Check, the
    ``_qcid`` argument is here to specify which of these must be processed
    when the function ``generate_html_report`` is called.
        '''

        self.database_checker = database_checker

    def _convert_from_template(self, template_id, conversion_hashtable):
        '''
    This command takes an HTML template, converts its tags (starting with a
    dollar character) using a hashtable ``conversion_hashtable`` provided as
    argument, and returns the converted string.
        '''

        html_report = ''
        templates = { 'DISKUSAGE' : 'diskusage_template.html',
            'MORPHOLOGIST_HIERARCHY' : 'hierarchy_template.html',
            'FREESURFER_HIERARCHY' : 'freesurfer_hierarchy_template.html',
            'SNAPSHOTS_HIERARCHY' : 'snapshots_hierarchy_template.html',
            'DIRECTORIES' : 'directories_template.html',
            'GENERALINFO' : 'generalinformation_template.html',
        }
        m = sys.modules['brainvisa.checkbase']
        report_template_path = os.path.join(os.path.split(m.__file__)[0], 'templates',
                templates[template_id])
        parent_path = os.path.realpath(report_template_path) #os.path.split(os.path.realpath(report_template_path))[0]
        conversion_hashtable.update( {'$REVISION_NUMBER' : str(revision_number(parent_path)), })

        template_file = open(report_template_path, 'rb')

        for line in template_file:
            for tag in conversion_hashtable.keys():
                if string.find(line, tag) != -1:
                    #value = conversion_hashtable.pop(tag)
                    value = conversion_hashtable[tag]
                    line = line.replace(tag, value)
            html_report += line + '\n'

        return html_report

    def _generate_summary_on_directories(self):
        summary = ''
        for study, study_size in self.database_checker.studies_space.items():
            summary = summary + '%s: %s<br>'%(study, str("{0:.2S}".format(size(study_size))))
        return summary

    def _generate_summary_on_users(self):
        summary = ''
        for user, user_size in self.database_checker.users_space.items():
            summary = summary + '%s: %s<br>'%(user, str("{0:.2S}".format(size(user_size))))
        return summary

    def _generate_summary_on_undeclared_directories(self):
        summary = ''
        if len(self.database_checker.other_studies.keys()) > 0:
            summary += '<br><b><h3>Detailed information on undeclared directories :</h3></b><br>'

            for study, study_size in self.database_checker.other_studies.items():
                gecos, name = self._get_owner_username(os.path.join(self.database_checker.rootdirectory, study))
                summary = summary + '%s: %s (%s - %s)<br>'%(study, str("{0:.2S}".format(size(study_size))), gecos, name)
            summary += '<br>'
        return summary

    def _get_owner_username(self, filename):
        import pwd
        file_uid = os.stat(str(filename)).st_uid
        for each in pwd.getpwall():
            if each.pw_uid == file_uid:
                break
        return each.pw_gecos, each.pw_name

    def _generate_summary_on_undeclared_users(self):
        summary = ''
        if len(self.database_checker.other_users.keys()) > 0:
            summary += '<br><b><h3>Detailed information on undeclared directories :</h3></b><br>'
            for user, user_size in self.database_checker.other_users.items():
                summary = summary + '%s: %s<br>'%(user, str("{0:.2S}".format(size(user_size))))
            summary += '<br>'
        return summary

    def _generate_detailed_directories(self):
        summary = ''
        for key, hierarchies in self.database_checker.hierarchies.items():
            summary += 'Results for directory %s<br><br>'%key
            if hierarchies :
                for hieradir, hieratype in hierarchies.items():
                    subjects = self.database_checker.checks['all_subjects'][hieradir]
                    conversion_hashtable = {'$HIERARCHY_DIR': str('%s'%hieradir),
                        '$HIERARCHY_DETECTED_TYPE' : str(hieratype),
                        '$HIERARCHY_SUBJECTSDIRECTORY' : str('%s (%i)'%(subjects, len(subjects))),
                        '$HIERARCHY_SUBJECT_KEY_ITEMS' : str('%s'%(self.database_checker.checks['key_items'][hieradir])),
                        '$HIERARCHY_INVALID_SUBJECTS' : str(''),
                        '$BIOMARKERS' : str(''),
                        '$HIERARCHY_EMPTY_SUBJECTS' : str(''),
                        '$HIERARCHY_COMPLETE_SUBJECTS' : str(''),
                        '$HIERARCHY_INVALID_SUBJECTS' : str(''),
                        '$HIERARCHY_UNIDENTIFIED_FILES' : str(''),
                    }
                    if hieratype == 'morphologist':
                      conversion_hashtable.update({
                        '$HIERARCHY_MULTIPLE_SUBJECTS' : str('%s'%self.database_checker.checks['multiple_subjects'][hieradir]),
                        '$HIERARCHY_EMPTY_SUBJECTS' : str('%s'%self.database_checker.checks['empty_subjects'][hieradir]),
                        '$HIERARCHY_COMPLETE_SUBJECTS' : str('%s'%self.database_checker.checks['complete_subjects'][hieradir]),
                        '$HIERARCHY_INVALID_SUBJECTS' : str(''),
                        '$HIERARCHY_UNIDENTIFIED_FILES' : str(''),
                        '$BIOMARKERS' : str(''),
                      })
                      summary += self._convert_from_template('MORPHOLOGIST_HIERARCHY', conversion_hashtable)
                    elif hieratype == 'snapshots':
                      summary += self._convert_from_template('SNAPSHOTS_HIERARCHY', conversion_hashtable)
                    elif hieratype == 'freesurfer':
                      conversion_hashtable.update({
                        })
                      summary += self._convert_from_template('FREESURFER_HIERARCHY', conversion_hashtable)

        ht = {'$DIRECTORIES_DETAILED_HIERARCHIES' : summary,
              '$HIERARCHIES' : self.database_checker.hierarchies,
              }

        return self._convert_from_template('DIRECTORIES', ht)

    def generate_html_report(self):
        '''
    This command generates an exhaustive HTML report with results from various
    quality checks (files existence, data ambiguity, existence of forbidden
    values) and from the estimation of various features, jointly performed with
    outliers detection.

    The result is a string containing HTML code.
        '''
        from glob import glob
        db_id = '/neurospin/cati/'
        datetime_string = str(time.strftime('%d %m %Y %H:%M:%S', time.gmtime()))
        nb_previous_checks = len(glob('/neurospin/cati/Users/operto/logs/report*.*'))

        conversion_hashtable = {
            '$DATABASE_ID' : str(db_id),
            '$DATETIME_GENERATED' : str(datetime_string),
            '$DATETIME_STRING' : str(datetime_string),
            '$DETAILED_DIRECTORIES' : '',
            '$GENERAL_INFORMATION' : '',
        }

        # Information on disk usage
        if hasattr(self.database_checker, 'studies_space'):
           device, total_size, used, available, percent = string.split(self.database_checker.global_disk_space, ' ')
           percent = 100.0 - float(percent)
           hours, remainder = divmod(int(self.database_checker.execution_time), 3600)
           minutes, seconds = divmod(remainder, 60)
           execution_time=  '%s:%s:%s' % (hours, minutes, seconds)
           ht = {'$NUMBER_OF_STUDIES' : str('%i'%len(self.database_checker.studies_space.keys())),
            '$DATABASE_DIR' : str(db_id),
            '$NUMBER_OF_PREVIOUS_CHECKS' : str(nb_previous_checks),
            '$STUDIES' : str(self.database_checker.studies_space.keys()),
            '$NUMBER_OF_USERS' : str('%i'%len(self.database_checker.users_space.keys())),
            '$USERS' : str(self.database_checker.users_space.keys()),
            '$UNIDENTIFIED_DIRS' : str('%s (%i studies)'%(str(self.database_checker.other_studies.keys()), len(self.database_checker.other_studies.keys()))),
            '$TOTAL_SPACE' : str("{0:.2S}".format(size(int(total_size) * 1024.0))),
            '$USED_SPACE' : str("{0:.2S}".format(size(int(used) * 1024.0))),
            '$FREE_SPACE' : str("{0:.2S}".format(size(int(available) * 1024.0))),
            '$PERCENT' : '%s %%'%str(percent),
            '$SUMMARY_ON_DIRECTORIES' : str(self._generate_summary_on_directories()),
            '$SUMMARY_ON_USERS' : str(self._generate_summary_on_users()),
            '$SUMMARY_ON_UNDECLARED_DIRS' : str(self._generate_summary_on_undeclared_directories()),
            '$SUMMARY_ON_UNDECLARED_USERS' : str(self._generate_summary_on_undeclared_users()),
            '$EXECUTION_TIME' : str(execution_time),
           }
           conversion_hashtable['$GENERAL_INFORMATION'] = self._convert_from_template('GENERALINFO', ht)


        # Information on hierarchies
        if hasattr(self.database_checker, 'hierarchies'):
            conversion_hashtable['$DETAILED_DIRECTORIES'] = self._generate_detailed_directories()

        return self._convert_from_template('DISKUSAGE', conversion_hashtable)
