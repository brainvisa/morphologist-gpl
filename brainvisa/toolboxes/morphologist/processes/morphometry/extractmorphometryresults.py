# -*- coding: utf-8 -*-

from brainvisa.processes import *
import numpy as np
import os

name = 'Extract one measure from the morphometry statistics table'
userLevel = 2

signature = Signature(
    'morpho_stat_files', ListOf(ReadDiskItem('CSV File', 'CSV File')),
    'measures', OpenChoice('opening', 'GM_thickness', 'surface_native',
                           ('length', 'hullJunctionsLength'),
                           ('depthMean', 'geodesicDepthMean'),
                           ('depthMax', 'geodesicDepthMax')),
    'output_file', WriteDiskItem('CSV File', 'CSV File'),
    'pipeline_mode', Boolean()
)


def initialization(self):
    self.measures = 'opening'
    self.pipeline_mode = False
    self.signature['pipeline_mode'].userLevel = 3

    def find_database():
        #Find database and add to choice
        databases = [None]
        databases.extend([dbs.directory for dbs in neuroConfig.dataPath \
                          if not dbs.builtin])
        self.signature['database'].setChoices(*databases)
        self.database = databases[0]


    def link_pipeline_mode(model, names, parameterized):
        if self.pipeline_mode:
            process = parameterized[0]
            signature = process.signature
            self.signature['database'] = Choice()
            self.signature['timepoint'] = String()
            self.signature['history_file'] = WriteDiskItem('History Sulcal Openings Table',
                                                           'Text file',
                                                           requiredAttributes={'software': 'morphologist'})
            self.signature['output_file'] = WriteDiskItem('Sulcal Openings Table',
                                                          'CSV File',
                                                          requiredAttributes={'software': 'morphologist'})
            self.addLink(None, 'timepoint', link_files)
            process.changeSignature(signature)
            find_database()

    def link_files(model, names, parameterized):
        if self.pipeline_mode and self.timepoint:
            d = {}
            d['_database'] = self.database
            d['acquisition'] = self.timepoint
            self.output_file = self.signature['output_file'].findValue(d)
            if self.output_file:
                self.history_file = self.signature['history_file'].findValue(d)

    self.addLink(None, 'pipeline_mode', link_pipeline_mode)
    self.addLink(None, 'output_file', link_files)


def execution(self, context):
    #Recuperation des mesures pour chaque sillons
    measures_by_sulci = {}

    if self.pipeline_mode and os.path.exists(str(self.output_file)):
        self.file_measures = '/tmp/tmp_sulcalopenings_morphologist.csv'
        need_concatenated = True
    else:
        self.file_measures = self.output_file
        need_concatenated = False

    sub_list_global = []
    for f in self.morpho_stat_files:
        #Lecture des csv
        csv = np.recfromtxt(f.fullPath(), delimiter=';', names=True, dtype='S12,S32,S6,f8,f8,f8,f8,f8,f8,f8,f8,f8,f8')
        subjects_list = list(csv['subject'])
        subject_arr = csv['subject']

        measures_by_sub = {}
        for sub in subjects_list:
            if sub not in sub_list_global:
                sub_list_global.append(sub)
            meas = csv[subject_arr == sub][self.measures][0]
            measures_by_sub[sub] = meas
        sulcus = os.path.basename(f.fullPath()).split('_')[-2] + '_' + \
                            os.path.basename(f.fullPath()).split('_')[-1][:-4]
        measures_by_sulci[sulcus] = measures_by_sub

    outf = open(str(self.file_measures), "w")
    outf.write("subject")
    for sulcus in sorted(measures_by_sulci.keys()):
        outf.write(";" + sulcus)
    outf.write("\n")

    for sub in sub_list_global:
        outf.write(str(sub))
        for sulcus in sorted(measures_by_sulci.keys()):
            if sub in measures_by_sulci[sulcus].keys():
                outf.write(";" + str(measures_by_sulci[sulcus][sub]))
            else:
                outf.write(";X")
        outf.write("\n")
    outf.close()

    if self.pipeline_mode:
        from catidb import catidb_axon
        if need_concatenated:
            catidb_axon.concatenated_csv(context, str(self.output_file),
                                   str(self.file_measures), str(self.history_file))
            # detete tmp file measure
            os.remove(self.file_measures)
        else:
            catidb_axon.write_history(True, subjects_list, [], str(self.history_file))
