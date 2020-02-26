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

#
# VipGetOpenedHemiSurface process declaration
#

name = 'Ana Get Opened Hemi Surface'
userLevel = 2

# Argument declaration
signature = Signature(
    'Side', Choice("Both", "Left", "Right"),
    'mri_corrected', ReadDiskItem('T1 MRI Bias Corrected',
                                  'Aims readable volume formats'),
    'split_mask', ReadDiskItem('Split Brain Mask',
                               'Aims readable volume formats'),
    'left_hemi_cortex', ReadDiskItem('Left CSF+GREY Mask',
                                     'Aims writable volume formats'),
    'right_hemi_cortex', ReadDiskItem('Right CSF+GREY Mask',
                                      'Aims writable volume formats'),
    'left_hemi_mesh', WriteDiskItem('Left Hemisphere Mesh',
                                    'Aims mesh formats'),
    'right_hemi_mesh', WriteDiskItem('Right Hemisphere Mesh',
                                     'Aims mesh formats'),
)
# Default values


def initialization(self):
    self.linkParameters('split_mask', 'mri_corrected')
    self.linkParameters('left_hemi_cortex', 'split_mask')
    self.linkParameters('right_hemi_cortex', 'left_hemi_cortex')
    self.linkParameters('left_hemi_mesh', 'left_hemi_cortex')
    self.linkParameters('right_hemi_mesh', 'right_hemi_cortex')
    self.Side = "Both"


def execution(self, context):
    trManager = registration.getTransformationManager()
    if self.Side in ('Left', 'Both'):
        if os.path.exists(self.left_hemi_mesh.fullName() + '.loc'):
            context.write("Left Hemisphere Mesh locked")
        else:
            context.write(
                "Masking Bias corrected image with left hemisphere mask...")
            braing = context.temporary('GIS Image')
            context.system("VipMask", "-i", self.mri_corrected, "-m",
                           self.split_mask, "-o",
                           braing, "-w", "t", "-l", "2")

            context.write("Reconstructing left hemisphere surface...")
            white = context.temporary('GIS Image')
            context.system("VipSingleThreshold", "-i",
                           self.left_hemi_cortex, "-o",
                           white, "-t", "0", "-c", "b", "-m", "eq",
                           "-w", "t")
            openbrain = context.temporary('GIS Image')
            context.system("VipOpenFold", "-i", braing, "-s",
                           white, "-o", openbrain,
                           "-a", "i", "-w", "t", "-n", "5")
            del braing
            del white

            context.write("Triangulation and Decimation...")
            context.system("AimsMeshBrain", "-i", openbrain.fullPath(), "-o",
                           self.left_hemi_mesh.fullPath(), "--smoothType", "laplacian",
                           "--smoothIt", 5, "--smoothRate", 0.4,
                           "--deciMaxClearance", 5., "--deciMaxError", 3.)
            trManager.copyReferential(self.mri_corrected, self.left_hemi_mesh)
            del openbrain

    if self.Side in ('Right', 'Both'):
        if os.path.exists(self.right_hemi_mesh.fullName() + '.loc'):
            context.write("Right Hemisphere locked")
        else:
            context.write(
                "Masking Bias corrected image with right hemisphere mask...")
            braing = context.temporary('GIS Image')
            context.system("VipMask", "-i", self.mri_corrected, "-m",
                           self.split_mask, "-o",
                           braing, "-w", "t", "-l", "1")

            context.write("Reconstructing right hemisphere surface...")
            white = context.temporary('GIS Image')
            context.system("VipSingleThreshold", "-i",
                           self.right_hemi_cortex, "-o",
                           white, "-t", "0", "-c", "b", "-m", "eq",
                           "-w", "t")
            openbrain = context.temporary('GIS Image')
            context.system("VipOpenFold", "-i", braing, "-s",
                           white, "-o", openbrain,
                           "-a", "i", "-w", "t")
            del braing
            del white

            context.write("Triangulation and Decimation...")
            context.system("AimsMeshBrain", "-i", openbrain.fullPath(), "-o",
                           self.right_hemi_mesh.fullPath(), "--smoothType", "laplacian",
                           "--smoothIt", 5, "--smoothRate", 0.4,
                           "--deciMaxClearance", 5., "--deciMaxError", 3.)
            trManager.copyReferential(self.mri_corrected, self.right_hemi_mesh)
            del openbrain
