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
from brainvisa import shelltools
import os
from brainvisa import registration

name = 'Cortical Fold Arg (3.0)'
userLevel = 2

# Argument declaration
signature = Signature(
    'Side', Choice("Both", "Left", "Right"),
    'mri_corrected', ReadDiskItem('T1 MRI Bias Corrected',
                                  'Aims readable volume formats'),
    'histo_analysis', ReadDiskItem('Histo Analysis', 'Histo Analysis'),
    'split_mask', ReadDiskItem('Split Brain Mask',
                               'Aims readable volume formats'),
    'left_hemi_cortex', WriteDiskItem('Left CSF+GREY Mask',
                                      'Aims writable volume formats'),
    'right_hemi_cortex', WriteDiskItem('Right CSF+GREY Mask',
                                       'Aims writable volume formats'),
    'Lskeleton', WriteDiskItem('Left Cortex Skeleton',
                               'Aims writable volume formats'),
    'Rskeleton', WriteDiskItem('Right Cortex Skeleton',
                               'Aims writable volume formats'),
    'Lroots', WriteDiskItem('Left Cortex Catchment Bassins',
                            'Aims writable volume formats'),
    'Rroots', WriteDiskItem('Right Cortex Catchment Bassins',
                            'Aims writable volume formats'),
    'Lgraph', WriteDiskItem('Cortical folds graph', 'Graph',
                            requiredAttributes={'side': 'left', 'labelled': 'No', 'graph_version': '3.0'}),
    'Rgraph', WriteDiskItem('Cortical folds graph', 'Graph',
                            requiredAttributes={'side': 'right', 'labelled': 'No',  'graph_version': '3.0'}),
    'Commissure_coordinates', ReadDiskItem('Commissure coordinates',
                                           'Commissure coordinates'),
    'compute_fold_meshes', Choice("Yes", "No")
)
# Default values


def initialization(self):
    self.linkParameters('histo_analysis', 'mri_corrected')
    self.linkParameters('split_mask', 'histo_analysis')
    self.linkParameters('left_hemi_cortex', 'split_mask')
    self.linkParameters('right_hemi_cortex', 'left_hemi_cortex')
    self.linkParameters('Lgraph', 'Lroots')
    self.linkParameters('Rgraph', 'Rroots')
    self.linkParameters('Lskeleton', 'left_hemi_cortex')
    self.linkParameters('Rskeleton', 'right_hemi_cortex')
    self.linkParameters('Lroots', 'Lskeleton')
    self.linkParameters('Rroots', 'Rskeleton')
    self.linkParameters('Commissure_coordinates', 'mri_corrected')
    self.Side = "Both"
    self.compute_fold_meshes = "Yes"
#
#


def execution(self, context):
    context.write("Masking Bias corrected image with hemisphere masks...")
    Lbraing = context.temporary('GIS Image')
    context.system('AimsMask', '-i', self.mri_corrected, "-m",
                   self.split_mask, "-o", Lbraing, "-l", "2")
    Rbraing = context.temporary('GIS Image')
    context.system("AimsMask", "-i", self.mri_corrected, "-m",
                   self.split_mask, "-o", Rbraing, "-l", "1")

    trManager = registration.getTransformationManager()
    if self.Side in ('Left', 'Both'):

        if os.path.exists(self.left_hemi_cortex.fullName() + '.loc'):
            context.write("Left grey/white locked")
        else:
            context.write("Detecting left grey/white interface...")
            context.system("VipHomotopicSnake", "-i", Lbraing, "-h",
                           self.histo_analysis, "-o",
                           self.left_hemi_cortex, "-w", "t")
        trManager.copyReferential(self.split_mask, self.left_hemi_cortex)

        context.write("Computing skeleton and buried gyrus watershed...")
        context.system("VipSkeleton", "-i", self.left_hemi_cortex,
                       "-so", self.Lskeleton, "-vo",
                       self.Lroots, "-g", Lbraing,
                       "-ve", "1", "-w", "t")
        trManager.copyReferential(self.split_mask, self.Lroots)
        trManager.copyReferential(self.split_mask, self.Lskeleton)

        context.write("Building Attributed Relational Graph...")
        context.system("VipFoldArg", "-i", self.Lskeleton, "-v",
                       self.Lroots, "-o", self.Lgraph)
        if self.compute_fold_meshes == "Yes":
            context.system("VipFoldArgAtt", "-i", self.Lskeleton, "-lh",
                           Lbraing, "-rh", Rbraing, "-a",
                           self.Lgraph, "-P",
                           self.Commissure_coordinates, "-t", "y")

        else:
            context.system("VipFoldArgAtt", "-i", self.Lskeleton, "-lh",
                           Lbraing, "-rh", Rbraing, "-a",
                           self.Lgraph, "-P",
                           self.Commissure_coordinates, "-t", "n")

        context.system("VipFoldArg", "-a", self.Lgraph, "-o",
                       self.Lgraph.fullName() + "local", "-w", "g")
        context.system("AimsGraphConvert", "-i",
                       self.Lgraph.fullName() + "local.arg", "-o",
                       self.Lgraph.fullPath(0), "-b",
                       os.path.basename(self.Lgraph.fullName()) + '.data',
                       "-g")
        trManager.copyReferential(self.split_mask, self.Lgraph)
        context.write('computing additional attributes')
        context.system('AimsGraphComplete', '-i', self.Lgraph.fullPath(),
                       '--dversion', '3.0', '--mversion', '3.0')
        shelltools.rm(self.Lgraph.fullName() + "local*")
        shelltools.rm(self.Lgraph.fullName() + ".data/Tmtk")
        shelltools.rm(self.Lgraph.fullName() + "*.Vip")

    if self.Side in ('Right', 'Both'):

        if os.path.exists(self.right_hemi_cortex.fullName() + '.loc'):
            context.write("Right grey/white locked")
        else:
            context.write("Detecting right grey/white interface...")
            context.system("VipHomotopicSnake", "-i", Rbraing, "-h",
                           self.histo_analysis, "-o",
                           self.right_hemi_cortex, "-w", "t")
        trManager.copyReferential(self.split_mask, self.right_hemi_cortex)

        context.write("Computing skeleton and buried gyrus watershed...")
        context.system("VipSkeleton", "-i", self.right_hemi_cortex,
                       "-so", self.Rskeleton, "-vo",
                       self.Rroots, "-g", Rbraing,
                       "-ve", "1", "-w", "t")
        trManager.copyReferential(self.split_mask, self.Rroots)
        trManager.copyReferential(self.split_mask, self.Rskeleton)

        context.write("Building Attributed Relational Graph...")
        context.system("VipFoldArg", "-i", self.Rskeleton, "-v",
                       self.Rroots, "-o", self.Rgraph)
        if self.compute_fold_meshes == "Yes":
            context.system("VipFoldArgAtt", "-i", self.Rskeleton,
                           "-lh", Lbraing, "-rh", Rbraing,
                           "-a", self.Rgraph, "-P",
                           self.Commissure_coordinates, "-t", "y")
        else:
            context.system("VipFoldArgAtt", "-i", self.Rskeleton, "-lh",
                           Lbraing, "-rh", Rbraing, "-a",
                           self.Rgraph, "-P",
                           self.Commissure_coordinates, "-t", "n")

        context.system("VipFoldArg", "-a", self.Rgraph, "-o",
                       self.Rgraph.fullName() + "local", "-w", "g")
        context.system("AimsGraphConvert", "-i",
                       self.Rgraph.fullName() + "local.arg", "-o",
                       self.Rgraph.fullPath(0), "-b",
                       os.path.basename(self.Rgraph.fullName()) + ".data",
                       "-g")
        trManager.copyReferential(self.split_mask, self.Rgraph)
        context.write('computing additional attributes')
        context.system('AimsGraphComplete', '-i', self.Rgraph.fullPath(),
                       '--dversion', '3.0', '--mversion', '3.0')
        shelltools.rm(self.Rgraph.fullName() + "local*")
        shelltools.rm(self.Rgraph.fullName() + ".data/Tmtk")
        shelltools.rm(self.Rgraph.fullName() + "*.Vip")

    del Lbraing
    del Rbraing
