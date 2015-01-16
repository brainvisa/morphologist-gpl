# -*- coding: utf-8 -*-

from brainvisa.processes import *
import numpy as np
import os

name = 'Extract one measure from the sulcal morphometry table'
userLevel = 1

signature = Signature(
    'morpho_stat_files', ListOf(ReadDiskItem('Data Table', 'Text Data Table')),
    'measures', OpenChoice(('opening', 'fold_opening_full'),
                           'GM_thickness', 'surface',
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

    def link_pipeline_mode(model, names, parameterized):
        if self.pipeline_mode:
            process = parameterized[0]
            signature = process.signature
            self.signature['historical_file'] = \
            WriteDiskItem('Historical Sulcal Openings Table', 'Text file',
                          requiredAttributes={'software': 'morphologist'})
            self.signature['output_file'] = \
            WriteDiskItem('Sulcal Openings Table', 'CSV File',
                          requiredAttributes={'software': 'morphologist'})
            process.changeSignature(signature)

    def link_historical_file(model, names, parameterized):
        if self.pipeline_mode and self.output_file:
            database_found = self.output_file.hierarchyAttributes()['_database']
            d = {}
            d['_database'] = database_found
            self.historical_file = self.signature['historical_file'].findValue(d)

    self.addLink(None, 'pipeline_mode', link_pipeline_mode)
    self.addLink(None, 'output_file', link_historical_file)


def execution(self, context):
    #Recuperation des mesures pour chaque sillons
    measures_by_sulci = {}

    if self.pipeline_mode and os.path.exists(str(self.output_file)):
        self.file_measures = '/tmp/tmp_sulcalopenings_morphologist.csv'
        need_concatenated = True
    else:
        self.file_measures = self.output_file
        need_concatenated = False


    for f in self.morpho_stat_files:
        print f
        #Lecture des csv
        csv = np.recfromtxt(f.fullPath(), delimiter=' ', names=True)
        subjects_list = list(csv['subject'])
        subject_arr = csv['subject']

        measures_by_sub = {}
        for sub in subjects_list:
            meas = csv[subject_arr == sub][self.measures][0]
            measures_by_sub[sub] = meas
        sulcus = os.path.basename(f.fullPath()).split('_')[-2] + '_' + \
                            os.path.basename(f.fullPath()).split('_')[-1][:-4]
        measures_by_sulci[sulcus] = measures_by_sub

    Loutf = open(str(self.file_measures), "w")
    Loutf.write("subject")
    for sulcus in sorted(measures_by_sulci.keys()):
        Loutf.write(";" + sulcus)
    Loutf.write("\n")

    for sub in subjects_list:
        Loutf.write(str(sub))
        for sulcus in sorted(measures_by_sulci.keys()):
            Loutf.write(";" + str(measures_by_sulci[sulcus][sub]))
        Loutf.write("\n")
    Loutf.close()

    if self.pipeline_mode:
        from catidb import catidb_axon
        if need_concatenated:
            catidb_axon.concatenated_csv(context, str(self.output_file),
                                   str(self.file_measures), str(self.historical_file))
            # detete tmp file measure
            os.remove(self.file_measures)
        else:
            catidb_axon.write_historical(True, subjects_list, [], str(self.historical_file))