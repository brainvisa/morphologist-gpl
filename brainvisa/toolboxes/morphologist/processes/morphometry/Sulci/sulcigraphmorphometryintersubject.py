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

from __future__ import absolute_import
from brainvisa.processes import *
import numpy as np
import os
from six.moves import zip

name = 'Sulci graph morphometry inter subject'
userLevel = 0

signature = Signature(
    'sulcal_morpho_measures', ListOf(ReadDiskItem(
        'Sulcal morphometry measurements',
        'CSV File')),
    'subjects', ListOf(String()),
    'sort_by', Choice(('one file by measure', 'measure'),
                      ('one file by sulcus', 'sulcus')),
    'measure', OpenChoice('opening',
                          'surface_talairach',
                          'GM_thickness',
                          'hull_junction_length_talairach',
                          'meandepth_talairach',
                          'maxdepth_talairach'),
    'output_directory', WriteDiskItem('Directory', 'Directory'),
)


def link_subjects(self, proc, dummy):
    subjects = []
    for item in self.sulcal_morpho_measures:
        subjects.append(item.get('subject'))
    return subjects


def updateSignature(self, proc):
    if self.sort_by == 'measure':
        self.signature['measure'].userLevel = 0
        self.signature['measure'].mandatory = True
    elif self.sort_by == 'sulcus':
        self.signature['measure'].userLevel = 100
        self.signature['measure'].mandatory = False
    self.changeSignature(self.signature)


def initialization(self):
    self.linkParameters('subjects',
                        'sulcal_morpho_measures',
                        self.link_subjects)
    self.addLink(None, 'sort_by', self.updateSignature)
    self.sort_by = 'measure'
    self.measure = 'opening'


def execution(self, context):

    if self.sort_by == 'measure':
        measure_file = self.output_directory.fullPath() + '/' + self.measure + '.csv'
        fi = open(measure_file, 'w')

    meas_by_sulcus = {}
    first = True
    for item, subject in zip(self.sulcal_morpho_measures, self.subjects):
        # lecture des csv
        csv = np.recfromtxt(item.fullPath(), delimiter=';', names=True)
        header = csv.dtype.names
        sulci = [x.decode() for x in csv['sulcus']]
        sulci_arr = csv['sulcus']

        if self.sort_by == 'measure' and first:
            fi.write('subject;' + ';'.join(sulci) + '\n')
            first_header = header
            first_sulci = sulci
            first = False
        elif self.sort_by == 'sulcus' and first:
            first_header = header
            first_sulci = sulci
            first = False
        elif header != first_header:
            context.error('Subjects CSV headers do not match. First:\n%s\nSubject %s:\n%s' % (
                first_header, subject, header))
            raise ValueError('subjects CSV headers do not match')
        elif sulci != first_sulci:
            context.error('Subjects sulci list do not match. First:\n%s\nSubject %s:\n%s' % (
                first_sulci, subject, sulci))
            raise ValueError('subjects sulci list do not match')

        if self.sort_by == 'measure':
            column = [str(i) for i in csv[self.measure]]
            fi.write(subject + ';' + ';'.join(column) + '\n')
        elif self.sort_by == 'sulcus':
            for sulcus in sulci:
                if sulcus in meas_by_sulcus:
                    meas_by_sulcus[sulcus][subject] = list(
                        csv[sulci_arr == sulcus.encode()][0])[1:]
                else:
                    # if the sulci doesn't exist yet, we create it.
                    meas_by_sulcus[sulcus] = {subject: list(
                        csv[sulci_arr == sulcus.encode()][0])[1:]}

    if self.sort_by == 'measure':
        fi.close()
    elif self.sort_by == 'sulcus':
        for sulcus in sorted(meas_by_sulcus.keys()):
            sulci_file = self.output_directory.fullPath() + '/' + sulcus + '.csv'
            sfi = open(sulci_file, 'w')
            sfi.write('subject;' + ';'.join(first_header[1:]) + '\n')
            for subject in sorted(self.subjects):
                line = [str(i) for i in meas_by_sulcus[sulcus][subject]]
                sfi.write(subject + ';' + ';'.join(line) + '\n')
            sfi.close()
