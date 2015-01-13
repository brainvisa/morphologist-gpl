# -*- coding: utf-8 -*-
from brainvisa.processes import *
import numpy as np
import os

name = 'Extract one measure from the sulcal morphometry table'
userLevel = 3

signature = Signature(
    'morpho_stat_files', ListOf(ReadDiskItem('Data Table', 'Text Data Table')),
    #'morpho_stat_files_right', ListOf(ReadDiskItem('Data Table', 'Text Data Table')),
    'measures', OpenChoice(('opening', 'fold_opening_full'), 'GM_thickness', 'surface', ('length', 'hullJunctionsLength'), ('depthMean', 'geodesicDepthMean'), ('depthMax', 'geodesicDepthMax')),
    'output_file', WriteDiskItem('CSV File', 'CSV File'),
    #'output_files_right', WriteDiskItem('CSV File', 'CSV File'),
)


def initialization(self):
    self.measures = 'opening'


def execution(self, context):
    
    #Recuperation des mesures pour chaque sillons
    measures_by_sulci = {}
    
    for f in self.morpho_stat_files:
        print f
        #Lecture des csv
        csv = np.recfromtxt(f.fullPath(), delimiter=' ', names=True)
        subjects_list = list(csv['subject'])
        subject_arr = csv['subject']
            
        measures_by_sub = {}
        for sub in subjects_list:
            meas = csv[subject_arr==sub][self.measures][0]
            measures_by_sub[sub] = meas
        sulcus = os.path.basename(f.fullPath()).split('_')[-2] + '_' +os.path.basename(f.fullPath()).split('_')[-1][:-4]
        measures_by_sulci[sulcus] = measures_by_sub
    
    Loutf = open(self.output_file.fullPath(), "w")
    Loutf.write("subject")
    for sulcus in measures_by_sulci.keys():
        Loutf.write(";"+sulcus)
    Loutf.write("\n")
    
    for sub in subjects_list:
        Loutf.write(str(sub))
        for sulcus in measures_by_sulci.keys():
            Loutf.write(";"+str(measures_by_sulci[sulcus][sub]))
        Loutf.write("\n")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    Loutf.close()
    #Routf.close()

