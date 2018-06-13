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

from brainvisa.processes import *
name = 'Correction Split Brain from Brain Mask'
userLevel = 0

signature = Signature(
    'mri_corrected', ReadDiskItem('T1 MRI Bias Corrected', 'GIS Image'),
    'variant', Choice("Standard procedure", "Barycentre 0.9", "Barycentre 0.75", "Barycentre 0.5", "Barycentre 0.25",
                      "2 * standard deviation", "2.5 * standard deviation", "3 * standard deviation",
                      "3.5 * standard deviation", "4 * standard deviation"),
    'split_mask', WriteDiskItem('Split Brain Mask', 'GIS Image'),
    'histo_analysis', ReadDiskItem('Histo Analysis', 'Histo Analysis'),
    'brain_mask', ReadDiskItem('T1 Brain Mask', 'GIS Image'),
    'Use_template', Boolean(),
    'split_template', ReadDiskItem('Hemispheres Template', 'GIS Image'),
    'Commissure_coordinates', ReadDiskItem(
        'Commissure coordinates', 'Commissure coordinates'),

)


def initialization(self):
    self.linkParameters('histo_analysis', 'mri_corrected')
    self.linkParameters('brain_mask', 'mri_corrected')
    self.linkParameters('split_mask', 'mri_corrected')
    self.linkParameters('Commissure_coordinates', 'mri_corrected')
    self.variant = "Barycentre 0.25"
    self.split_template = self.signature['split_template'].findValue({})
    self.Use_template = 1
    self.setOptional('split_template')
    self.setOptional('Commissure_coordinates')


def execution(self, context):
    if self.variant == "Standard procedure":
        context.runProcess('VipSplitBrain',
                           mri_corrected=self.mri_corrected,
                           histo_analysis=self.histo_analysis,
                           brain_mask=self.brain_mask,
                           split_mask=self.split_mask,
                           split_template=self.split_template,
                           Use_template=self.Use_template,
                           Commissure_coordinates=self.Commissure_coordinates)
    if self.variant == "Barycentre 0.9":
        context.runProcess('VipSplitBrain',
                           mri_corrected=self.mri_corrected,
                           histo_analysis=self.histo_analysis,
                           brain_mask=self.brain_mask,
                           split_mask=self.split_mask,
                           split_template=self.split_template,
                           Use_template=self.Use_template,
                           Commissure_coordinates=self.Commissure_coordinates,
                           white_algo='b',
                           bary_factor=0.9)
    if self.variant == "Barycentre 0.75":
        context.runProcess('VipSplitBrain',
                           mri_corrected=self.mri_corrected,
                           histo_analysis=self.histo_analysis,
                           brain_mask=self.brain_mask,
                           split_mask=self.split_mask,
                           split_template=self.split_template,
                           Use_template=self.Use_template,
                           Commissure_coordinates=self.Commissure_coordinates,
                           white_algo='b',
                           bary_factor=0.75)
    if self.variant == "Barycentre 0.5":
        context.runProcess('VipSplitBrain',
                           mri_corrected=self.mri_corrected,
                           histo_analysis=self.histo_analysis,
                           brain_mask=self.brain_mask,
                           split_mask=self.split_mask,
                           split_template=self.split_template,
                           Use_template=self.Use_template,
                           Commissure_coordinates=self.Commissure_coordinates,
                           white_algo='b',
                           bary_factor=0.5)
    if self.variant == "Barycentre 0.25":
        context.runProcess('VipSplitBrain',
                           mri_corrected=self.mri_corrected,
                           histo_analysis=self.histo_analysis,
                           brain_mask=self.brain_mask,
                           split_mask=self.split_mask,
                           split_template=self.split_template,
                           Use_template=self.Use_template,
                           Commissure_coordinates=self.Commissure_coordinates,
                           white_algo='b',
                           bary_factor=0.25)
    if self.variant == "2 * standard deviation":
        context.runProcess('VipSplitBrain',
                           mri_corrected=self.mri_corrected,
                           histo_analysis=self.histo_analysis,
                           brain_mask=self.brain_mask,
                           split_mask=self.split_mask,
                           split_template=self.split_template,
                           Use_template=self.Use_template,
                           Commissure_coordinates=self.Commissure_coordinates,
                           white_algo='c',
                           mult_factor=2)
    if self.variant == "2.5 * standard deviation":
        context.runProcess('VipSplitBrain',
                           mri_corrected=self.mri_corrected,
                           histo_analysis=self.histo_analysis,
                           brain_mask=self.brain_mask,
                           split_mask=self.split_mask,
                           split_template=self.split_template,
                           Use_template=self.Use_template,
                           Commissure_coordinates=self.Commissure_coordinates,
                           white_algo='c',
                           mult_factor=2.5)
    if self.variant == "3 * standard deviation":
        context.runProcess('VipSplitBrain',
                           mri_corrected=self.mri_corrected,
                           histo_analysis=self.histo_analysis,
                           brain_mask=self.brain_mask,
                           split_mask=self.split_mask,
                           split_template=self.split_template,
                           Use_template=self.Use_template,
                           Commissure_coordinates=self.Commissure_coordinates,
                           white_algo='c',
                           mult_factor=3)
    if self.variant == "3.5 * standard deviation":
        context.runProcess('VipSplitBrain',
                           mri_corrected=self.mri_corrected,
                           histo_analysis=self.histo_analysis,
                           brain_mask=self.brain_mask,
                           split_mask=self.split_mask,
                           split_template=self.split_template,
                           Use_template=self.Use_template,
                           Commissure_coordinates=self.Commissure_coordinates,
                           white_algo='c',
                           mult_factor=3.5)
    if self.variant == "4 * standard deviation":
        context.runProcess('VipSplitBrain',
                           mri_corrected=self.mri_corrected,
                           histo_analysis=self.histo_analysis,
                           brain_mask=self.brain_mask,
                           split_mask=self.split_mask,
                           split_template=self.split_template,
                           Use_template=self.Use_template,
                           Commissure_coordinates=self.Commissure_coordinates,
                           white_algo='c',
                           mult_factor=4)
