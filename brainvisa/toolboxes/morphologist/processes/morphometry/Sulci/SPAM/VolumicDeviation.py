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
name = 'Volumic Deviation'
userLevel = 2

signature = Signature(
    'Images', ListOf(ReadDiskItem('3D Volume',
                                  'Aims readable volume formats')),
    'Reference', ReadDiskItem('3D Volume', 'Aims readable volume formats'),
    'Deviation', WriteDiskItem('3D Volume', 'Aims writable volume formats'),
    'data_smoothing', Choice('Yes', 'No'),
    'smoothing_parameter', Float()
)


def initialization(self):
    self.data_smoothing = 'Yes'
    self.smoothing_parameter = 0.25


def execution(self, context):

    NbImages = len(self.Images)

    #context.write('WARNING : This process works with normalized data having the SAME SPATIAL RESOLUTION')
    # context.write('')
    context.write('Number of images: ', NbImages)
    if NbImages == 0:
        raise Exception(_t_('arguments <em>images</em> should not be '
                            'empty'))

    inc = 1
    ok = 0

    temp = context.temporary('GIS Image')
    ima = context.temporary('GIS Image')
    ref = context.temporary('GIS Image')

    for image in self.Images:

        context.write('Subject : ', image.get('subject'),
                      '(', inc, '/', NbImages, ')')

        context.system('AimsFileConvert', '-i', image,
                       '-o', ima, '-t', 'FLOAT')

        if self.data_smoothing == 'Yes':
            context.system('AimsImageSmoothing', '-i', ima,
                           '-o', ima, '-t', self.smoothing_parameter, '-s', '0')

        context.system('AimsFileConvert', '-i',
                       self.Reference.fullPath(), '-o', ref, '-t', 'FLOAT')

        if ok == 0:
            context.pythonSystem('cartoLinearComb.py', '-o', temp, '-i', ima,
                                 '-i', ref, '-f', 'I2 - I1')
            context.pythonSystem('cartoLinearComb.py',
                                 '-o', self.Deviation.fullPath(), '-i', temp,
                                 '-f', 'I1 ** 2')
            ok = 1
        else:
            context.pythonSystem('cartoLinearComb.py', '-o', temp, '-i', ima,
                                 '-i', ref, '-f', 'I2 - I1')
            context.pythonSystem('cartoLinearComb.py', '-o', temp, '-i',
                           temp, '-f', 'I1 ** 2')
            context.pythonSystem('cartoLinearComb.py', '-i', temp,
                                 '-o', self.Deviation.fullPath(),
                                 '-i', self.Deviation.fullPath(),
                                 '-f', 'I1 + I2')

        inc = inc + 1

    context.pythonSystem('cartoLinearComb.py', '-i', self.Deviation.fullPath(),
                         '-o', self.Deviation.fullPath(),
                         '-f',  '(I1 ** 0.5) / %f' % (NbImages - 1))
