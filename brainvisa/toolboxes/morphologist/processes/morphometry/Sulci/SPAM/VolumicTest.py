# -*- coding: iso-8859-1 -*-

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

from __future__ import absolute_import
from brainvisa import shelltools

from brainvisa.processes import *
name = 'Volumic T Test'
userLevel = 2

signature = Signature(
    'Images_group1', ListOf(ReadDiskItem('3D Volume',
                                         'Aims readable volume formats')),
    'Images_group2', ListOf(ReadDiskItem('3D Volume',
                                         'Aims readable volume formats')),
    'Average_group1', WriteDiskItem('3D Volume',
                                    'Aims writable volume formats'),
    'Average_group2', WriteDiskItem('3D Volume',
                                    'Aims writable volume formats'),
    'Mean_difference', WriteDiskItem('3D Volume',
                                     'Aims writable volume formats'),
    'Deviation', WriteDiskItem('3D Volume',
                               'Aims writable volume formats'),
    'T_test', WriteDiskItem('3D Volume', 'Aims writable volume formats'),
    'data_smoothing', Choice('Yes', 'No'),
    'smoothing_parameter', Float(),
)


def initialization(self):
    self.smoothing = 'Yes'
    self.smoothing_parameter = 1.0


def execution(self, context):

    NbImages1 = len(self.Images_group1)
    NbImages2 = len(self.Images_group2)
    NbImages = NbImages1 + NbImages2

    if NbImages1 * NbImages2 == 0:
        raise Exception(_t_('arguments <em>images_group1</em> and<em>images_group2</em> should not be '
                            'empty'))
    context.write('Computing group 1 mean image')
    context.runProcess('VolumicAverage',
                       Images=self.Images_group1,
                       Average=self.Average_group1,
                       data_smoothing=self.smoothing,
                       smoothing_parameter=self.smoothing_parameter)

    context.write('')
    context.write('Computing group 2 mean image')
    context.runProcess('VolumicAverage',
                       Images=self.Images_group2,
                       Average=self.Average_group2,
                       data_smoothing=self.smoothing,
                       smoothing_parameter=self.smoothing_parameter)

    Images = self.Images_group1 + self.Images_group2
    meanTot = context.temporary('GIS Image')

    context.pythonSystem('cartoLinearComb.py', '-o', meanTot,
                         '-i', self.Average_group1.fullPath(),
                         '-i', self.Average_group2.fullPath(),
                         '-f', 'I1.astype("FLOAT") * %d / %d '
                         '+ I2.astype("FLOAT") * %d / %d'
                         % (NbImages1, NbImages, NbImages2, NbImages))

    context.write('')
    context.write('Computing whole group deviation image')
    context.runProcess('VolumicDeviation',
                       Images=Images,
                       Reference=meanTot,
                       Deviation=self.Deviation.fullPath(),
                       data_smoothing=self.smoothing,
                       smoothing_parameter=self.smoothing_parameter)

    context.pythonSystem('cartoLinearComb.py',
                         '-o', self.Mean_difference.fullPath(),
                         '-i', self.Average_group1.fullPath(),
                         '-i', self.Average_group2.fullPath(),
                         '-f', 'I1.astype("FLOAT") - I2')

    context.pythonSystem('cartoLinearComb.py',
                         '-o', self.Mean_difference.fullPath(),
                         '-i', self.Mean_difference.fullPath(),
                         '-f', 'I1 ** 2')

    context.pythonSystem('cartoLinearComb.py',
                         '-o', self.Mean_difference.fullPath(),
                         '-i', self.Mean_difference.fullPath(),
                         '-f', 'I1 ** 0.5')

    context.pythonSystem('cartoLinearComb.py', '-o', self.T_test.fullPath(),
                         '-i', self.Mean_difference.fullPath(),
                         '-i', self.Deviation.fullPath(),
                         '-f', 'I1 / I2')
