# -*- coding: utf-8 -*-
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
from brainvisa.processes import *
import os

name = 'CSF Classif'
userLevel = 2

signature = Signature(
    'left_grey_white', ReadDiskItem('Left Grey White Mask',
                                    'Aims readable volume formats'),
    'right_grey_white', ReadDiskItem('Right Grey White Mask',
                                     'Aims readable volume formats'),
    'left_csf', WriteDiskItem('Left CSF Mask', 'Aims writable volume formats'),
    'right_csf', WriteDiskItem('Right CSF Mask',
                               'Aims writable volume formats'),
    'split_mask', ReadDiskItem('Split Brain Mask',
                               'Aims readable volume formats'),
)


def link_split(self, proc, dummy):
    if self.left_grey_white is not None:
        atts = self.left_grey_white.hierarchyAttributes()
        if 'side' in atts:
            del atts['side']
        return proc.signature['split_mask'].findValue(atts)


def initialization(self):
    self.linkParameters('right_grey_white', 'left_grey_white')
    self.linkParameters('left_csf', 'left_grey_white')
    self.linkParameters('right_csf', 'right_grey_white')
    self.linkParameters('split_mask', 'left_grey_white', self.link_split)


def execution(self, context):

    im1 = context.temporary('GIS image')
    im2 = context.temporary('GIS image')
    im3 = context.temporary('GIS image')
    im4 = context.temporary('GIS image')
    im5 = context.temporary('GIS image')
    im6 = context.temporary('GIS image')

    brainL = im1.fullPath()
    brainR = im2.fullPath()
    brain = im3.fullPath()
    brain_closed = im4.fullPath()
    brainLR_closed = im5.fullPath()
    cerebelum = im6.fullPath()

    brainL_closed = self.left_csf.fullPath()

    # Extract cerebelum mask
    context.system('AimsThreshold', '-i', self.split_mask.fullPath(),
                   '-o', cerebelum, '-m', 'eq', '-t', '3')
    # context.system('AimsReplaceLevel', '-i', cerebelum ,
    #               '-o', '/tmp/cerebelum.ima', '-g', '0','3', '-n', '1', '0')
    context.system('AimsReplaceLevel', '-i', cerebelum,
                   '-o', cerebelum, '-g', '0', '3', '-n', '1', '0')

    # Extract left brain mask
    context.system('AimsThreshold', '-i', self.left_grey_white.fullPath(),
                   '-o', brainL, '-m', 'ge', '-t', '100', '-b')

    # Extract right brain mask
    context.system('AimsThreshold', '-i', self.right_grey_white.fullPath(),
                   '-o', brainR, '-m', 'ge', '-t', '100', '-b')

    # Define brain mask
    # context.pythonSystem('cartoLinearComb.py', '-i', brainL , '-i', brainR ,
    #'-o', brain, '-f', 'I1 + I2')
    context.system('AimsMerge', '-i', brainL, '-M', brainR,
                   '-o', brain, '-m', 'sv')

    # Close left and right brain
    brainR_closed = brainR
    context.system('AimsMorphoMath', '-m', 'clo', '-i', brainR,
                   '-o', brainR_closed, '-r',  '20')
    brainL_closed = brainL
    context.system('AimsMorphoMath', '-m', 'clo', '-i', brainL,
                   '-o', brainL_closed, '-r',  '20')
    context.system('AimsMorphoMath', '-m', 'clo', '-i', brain,
                   '-o', brain_closed, '-r',  '20')

    context.pythonSystem('cartoLinearComb.py', '-i', brainL_closed,
                         '-i', brainR_closed, '-o', brainLR_closed,
                         '-f', 'I1 / 32767 * 2 + I2 / 32767 * 4')

    brain_merge = brainR_closed
    context.pythonSystem('cartoLinearComb.py', '-i', brain_closed,
                         '-i', brainLR_closed, '-o', brain_merge,
                         '-f', 'I1 / 32767 + I2')

    voronoi = brainLR_closed
    voronoi = self.right_csf.fullPath()
    context.system('AimsVoronoi', '-i', brain_merge,
                   '-o', voronoi, '-d', '1', '-f', '0')

    context.pythonSystem('cartoLinearComb.py', '-i', voronoi, '-i', brain,
                         '-o', voronoi, '-f', 'I1 + I2 / 32767')

    # context.system( 'AimsLinearComb', '-i', voronoi ,
    #                '-j', brain , '-o', '/tmp/vor.ima' , '-d', '32767' )

    # Remove cerebelum
    context.system('AimsThreshold', '-i', voronoi,
                   '-o', self.left_csf.fullPath(), '-m', 'eq', '-t', '3', '-b')
    context.system('AimsPowerComb', '-i', self.left_csf.fullPath(),
                   '-j', cerebelum, '-o', self.left_csf.fullPath())
    # Remove cerebelum
    context.system('AimsThreshold', '-i', voronoi,
                   '-o', self.right_csf.fullPath(), '-m', 'eq', '-t', '5', '-b')
    context.system('AimsPowerComb', '-i', self.right_csf.fullPath(),
                   '-j', cerebelum, '-o', self.right_csf.fullPath())
