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
            'TEST' : 'test_template.html',
            'FEATURE' : 'feature_template.html',
            'PROTOCOL_TEST' : 'protocol_test_template.html',
            'PROTOCOL_FEATURE' : 'protocol_feature_template.html' }
        m = sys.modules['brainvisa.checkbase.diskusage.check']
        report_template_path = os.path.join(os.path.split(m.__file__)[0],
                templates[template_id])
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
                gecos, name = self._get_owner_username(os.path.join(self.database_checker.database, study))
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
        device, total_size, used, available, percent = string.split(self.database_checker.global_disk_space, ' ')
        nb_previous_checks = len(glob('/neurospin/cati/Users/operto/logs/*.pdf'))
        percent = 100.0 - float(percent)
        hours, remainder = divmod(int(self.database_checker.execution_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        execution_time=  '%s:%s:%s' % (hours, minutes, seconds)

        conversion_hashtable = {
            '$DATABASE_ID' : str(db_id),
            '$DATETIME_GENERATED' : str(datetime_string),
            '$DATETIME_STRING' : str(datetime_string),
            '$DATABASE_DIR' : str(db_id),
            '$NUMBER_OF_STUDIES' : str('%i'%len(self.database_checker.studies_space.keys())),
            '$STUDIES' : str(self.database_checker.studies_space.keys()),
            '$NUMBER_OF_USERS' : str('%i'%len(self.database_checker.users_space.keys())),
            '$USERS' : str(self.database_checker.users_space.keys()),
            '$UNIDENTIFIED_DIRS' : str('%s (%i studies)'%(str(self.database_checker.other_studies.keys()), len(self.database_checker.other_studies.keys()))),
            '$NUMBER_OF_PREVIOUS_CHECKS' : str(nb_previous_checks),
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

        return self._convert_from_template('DISKUSAGE', conversion_hashtable)