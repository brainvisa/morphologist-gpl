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
from brainvisa import registration

name = 'Split Brain Mask'
userLevel = 0

signature = Signature(
    'brain_mask', ReadDiskItem('T1 Brain Mask',
                               'Aims readable volume formats'),
    't1mri_nobias', ReadDiskItem('T1 MRI Bias Corrected',
                                 'Aims readable volume formats'),
    'histo_analysis', ReadDiskItem('Histo Analysis', 'Histo Analysis'),
    'commissure_coordinates', ReadDiskItem('Commissure coordinates',
                                           'Commissure coordinates'),
    'use_ridges', Boolean(),
    'white_ridges', ReadDiskItem('T1 MRI White Matter Ridges',
                                 'Aims readable volume formats'),
    'use_template', Boolean(),
    'split_template', ReadDiskItem('Hemispheres Template',
                                   'Aims readable volume formats'),
    'mode', Choice('Watershed (2011)', 'Voronoi'),
    'variant', Choice('regularized', 'GW Barycentre', 'WM Standard Deviation'),
    'bary_factor', Choice(0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1),
    'mult_factor', Choice(0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4),
    'initial_erosion', Float(),
    'cc_min_size', Integer(),
    'split_brain', WriteDiskItem('Split Brain Mask',
                                 'Aims writable volume formats'),
    'fix_random_seed', Boolean(),
)


def updateSignatureAboutVariant(self, proc):
    if self.variant == 'GW Barycentre':
        self.showAndMandadesSignatureFieldList(['bary_factor'])
        self.hideAndMakeOptionalSignatureFieldList(['mult_factor'])
    elif self.variant == 'WM Standard Deviation':
        self.showAndMandadesSignatureFieldList(['mult_factor'])
        self.hideAndMakeOptionalSignatureFieldList(['bary_factor'])
    elif self.variant == 'regularized':
        self.hideAndMakeOptionalSignatureFieldList(['bary_factor'])
        self.hideAndMakeOptionalSignatureFieldList(['mult_factor'])


def updateSignatureAboutRidges(self, proc):
    if self.use_ridges == True:
        self.showAndMandadesSignatureFieldList(['white_ridges'])
    else:
        self.hideAndMakeOptionalSignatureFieldList(['white_ridges'])


def updateSignatureAboutTemplate(self, proc):
    if self.use_template == True:
        self.showAndMandadesSignatureFieldList(['split_template'])
    else:
        self.hideAndMakeOptionalSignatureFieldList(['split_template'])


def initialization(self):
    self.addLink(None, 'variant', self.updateSignatureAboutVariant)
    self.addLink(None, 'use_ridges', self.updateSignatureAboutRidges)
    self.addLink(None, 'use_template', self.updateSignatureAboutTemplate)
    self.linkParameters('t1mri_nobias', 'brain_mask')
    self.linkParameters('histo_analysis', 't1mri_nobias')
    self.linkParameters('commissure_coordinates', 't1mri_nobias')
    self.linkParameters('white_ridges', 't1mri_nobias')
    self.linkParameters('split_brain', 'brain_mask')
    self.split_template = self.signature['split_template'].findValue({})

    self.signature['commissure_coordinates'].mandatory = False
    self.signature['fix_random_seed'].userLevel = 3

    self.use_ridges = 'True'
    self.use_template = 'True'
    self.mode = 'Watershed (2011)'
    self.variant = 'GW Barycentre'
    self.bary_factor = 0.6
    self.mult_factor = 2
    self.initial_erosion = 2
    self.cc_min_size = 500
    self.fix_random_seed = False


def execution(self, context):
    if os.path.exists(self.split_brain.fullName() + '.loc'):
        context.write(self.split_brain.fullName(), ' has been locked')
        context.write('Remove', self.split_brain.fullName(),
                      '.loc if you want to trigger a new segmentation')
    else:
        command = ['VipSplitBrain',
                   '-input',  self.t1mri_nobias,
                   '-brain', self.brain_mask,
                   '-analyse', 'r',
                   '-hname', self.histo_analysis,
                   '-output', self.split_brain,
                   '-mode', self.mode,
                   '-erosion', self.initial_erosion,
                   '-ccsize', self.cc_min_size]
        if self.commissure_coordinates:
            command += ['-Points', self.commissure_coordinates]
        if self.variant == 'regularized':
            command += ['-walgo', 'r']
        elif self.variant == 'GW Barycentre':
            command += ['-walgo', 'b', '-Bary', self.bary_factor]
        elif self.variant == 'WM Standard Deviation':
            command += ['-walgo', 'c', '-Coef', self.mult_factor]
        if self.use_template:
            command += ['-template', self.split_template, '-TemplateUse', 'y']
        else:
            command += ['-TemplateUse', 'n']
        if self.use_ridges:
            command += ['-Ridge', self.white_ridges]
        if self.fix_random_seed:
            command += ['-srand', '10']

        context.system(*command)

        tm = registration.getTransformationManager()
        tm.copyReferential(self.t1mri_nobias, self.split_brain)


def showAndMandadesSignatureFieldList(self, field_list):
    for field in field_list:
        self.signature[field].userLevel = 0
        self.signature[field].mandatory = True
    self.changeSignature(self.signature)


def hideAndMakeOptionalSignatureFieldList(self, field_list):
    for field in field_list:
        self.signature[field].userLevel = 10
        self.signature[field].mandatory = False
    self.changeSignature(self.signature)
