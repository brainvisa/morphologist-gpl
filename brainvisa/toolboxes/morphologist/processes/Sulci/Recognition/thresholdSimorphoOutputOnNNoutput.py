#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
#
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.

from __future__ import print_function
from brainvisa.processes import *
import re
import os
import os.path
import glob
import string
name = 'Select folds & relations with good recognition percentage'
userLevel = 0

usualSelectedFoldsCols = [
    'extremity1x', 'extremity1y', 'extremity1z', 'extremity2x', 'extremity2y', 'extremity2z', 'gravityCenter_x', 'gravityCenter_y', 'gravityCenter_z', 'normal_x', 'normal_y', 'normal_z', 'direction_x', 'direction_y', 'direction_z', 'volume', 'geodesicDepthMax', 'hullJunctionsSize', 'surface']

usualSelectedRelCols = [
    'corticalSize', 'distanceMin', 'direction_x', 'direction_y', 'direction_z', 'distanceToExtremity1', 'distanceToExtremity2', 'gravityCenter_x', 'gravityCenter_y', 'gravityCenter_z', 'corticalDotProduct']


def filter(srcdir, destdir, prop, remove_non_valid, select_all_descriptors, selectedDesciptors):
    if prop > 1:
        prop = float(prop)/100
    exp = os.path.join(srcdir, '*')
    files = glob.glob(exp)

    # 1. Count the number of subjects
    nbSubjects = 0
    for f in files:
        fd = open(f, 'r')
        lines = fd.readlines()
        fd.close()
        if len(lines) > nbSubjects:
            nbSubjects = len(lines)
    nbSubjects = nbSubjects-1

    # 2. Filter
    for f in files:
        fd = open(f, 'r')
        lines = fd.readlines()
        header = lines[0]
        colNames = header.split()
        fd.close()

        # find the neural net output & valid col
        # find the index of selected columns
        selectedDesciptorsIndex = []
        nn_re = re.compile('\w+_descriptor\d_output')
        nnoutCol = -1
        validCol = -1
        subjectCol = -1
        for i in xrange(len(colNames)):
            if nn_re.match(colNames[i]):
                nnoutCol = i
            if colNames[i] == 'valid':
                validCol = i
            if colNames[i] == 'subject':
                subjectCol = i
            if selectedDesciptors.count(colNames[i]):
                selectedDesciptorsIndex += [i]

        if nnoutCol == -1:
            sys.exit("Neural net output not found")
        if validCol == -1:
            sys.exit("column <valid> not found")
        if subjectCol == -1:
            sys.exit("column <subject> not found")

        # store the header
        if select_all_descriptors:
            strLineOut = string.strip(lines[0])
        else:
            strLineOut = colNames[subjectCol]
            for j in selectedDesciptorsIndex:
                strLineOut += ' '+colNames[j]
        outLines = [strLineOut+'\n']
        # count the number of negative neural net output
        # select feature
        # where line are valid => put everything in outLines
        nbNeg = 0
        for i in xrange(1, len(lines)):
            # print('\nline',i,'--', end='')
            strLineOut = ''
            items = lines[i].split()
            nnout = float(items[nnoutCol])
            if nnout < 0:
                nbNeg += 1
            if not remove_non_valid or int(items[validCol]):
                if select_all_descriptors:
                    strLineOut = string.strip(lines[i])
                else:
                    strLineOut = items[subjectCol]
                    for j in selectedDesciptorsIndex:
                        strLineOut += ' '+items[j]
# print(strLineOut)
                outLines.append(strLineOut+'\n')

        propNeg = float(nbNeg)/float(nbSubjects)

        if propNeg >= prop:
            destFile = os.path.join(destdir, os.path.basename(f))
            fo = open(destFile, 'w')
            for line in outLines:
                ##        print('\n print line -----------------------')
                # print(line)
                fo.write(line)
            fo.close()
        else:
            print('Dont select', f, 'Because less than ',
                  prop, ' of neural output are negative')


signature = Signature(
    'input_directory', ReadDiskItem('Directory', 'Directory'),
    'good_regonition_percentage', Integer(),
    'remove_non_valid', Boolean(),
    'select_all_descriptors', Boolean(),
    'sulci_descriptors', ListOf(String()),
    'relations_descriptors', ListOf(String()),
    'output_directory', WriteDiskItem('Directory', 'Directory'),
)


def initialization(self):
    self.good_regonition_percentage = 50
    self.remove_non_valid = True
    self.select_all_descriptors = False

    self.sulci_descriptors = usualSelectedFoldsCols
    self.relations_descriptors = usualSelectedRelCols


def execution(self, context):
    selectedDesciptors = self.sulci_descriptors+self.relations_descriptors
    print(selectedDesciptors)
    filter(srcdir=self.input_directory.fullPath(),
           destdir=self.output_directory.fullPath(),
           prop=self.good_regonition_percentage,
           remove_non_valid=self.remove_non_valid,
           select_all_descriptors=self.select_all_descriptors,
           selectedDesciptors=selectedDesciptors)
