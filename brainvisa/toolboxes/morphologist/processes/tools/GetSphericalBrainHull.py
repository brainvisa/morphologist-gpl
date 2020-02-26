# -*- coding: utf-8 -*-
from __future__ import absolute_import
from brainvisa.processes import *
from brainvisa import registration

name = 'Get Spherical Brain Hull'
userLevel = 0

# Argument declaration
signature = Signature(
    'split_mask', ReadDiskItem('Split Brain Mask',
                               'Aims readable volume formats'),
    'left_hemi_cortex', ReadDiskItem('Left CSF+GREY Mask',
                                     'Aims readable volume formats'),
    'right_hemi_cortex', ReadDiskItem('Right CSF+GREY Mask',
                                      'Aims readable volume formats'),
    'left_hemi_hull', WriteDiskItem('Hemisphere Hull Mesh',
                                    'Aims mesh formats', requiredAttributes={"side": "left"}),
    'right_hemi_hull', WriteDiskItem('Hemisphere Hull Mesh',
                                     'Aims mesh formats', requiredAttributes={"side": "right"}),
    'both_hemi_hull', WriteDiskItem('Hemisphere Hull Mesh',
                                    'Aims mesh formats', requiredAttributes={"side": "both"}),
    'brain_hull', WriteDiskItem('Brain Hull Mesh',
                                'Aims mesh formats'),
)

# Default values


def initialization(self):
    self.linkParameters('left_hemi_cortex', 'split_mask')
    self.linkParameters('right_hemi_cortex', 'split_mask')
    self.linkParameters('left_hemi_hull', 'split_mask')
    self.linkParameters('right_hemi_hull', 'split_mask')
    self.linkParameters('both_hemi_hull', 'split_mask')
    self.linkParameters('brain_hull', 'split_mask')

# Main function


def execution(self, context):
    tm = registration.getTransformationManager()

    context.write("Extracting left hemisphere hull...")
    Lhull = context.temporary('NIFTI-1 Image')

    context.system("AimsThreshold",
                   "-i", self.left_hemi_cortex, "-o", Lhull,
                   "-t", "11", "-m", "eq", "-b")

    context.system("AimsMeshBrain",
                   "-i", Lhull, "-o", self.left_hemi_hull,
                   "--smoothIt", 50, "--smoothRate", 0.5,
                   "--deciMaxClearance", 5., "--internalinterface")
    context.system("meshCleaner",
                   "-i", self.left_hemi_hull,
                   "-o", self.left_hemi_hull,
                   "-maxCurv", "0.5")

    tm.copyReferential(self.split_mask, self.left_hemi_hull)
    del Lhull

    context.write("Extracting right hemisphere hull...")
    Rhull = context.temporary('NIFTI-1 Image')

    context.system("AimsThreshold",
                   "-i", self.right_hemi_cortex, "-o", Rhull,
                   "-t", "11", "-m", "eq", "-b")

    context.system("AimsMeshBrain",
                   "-i", Rhull, "-o", self.right_hemi_hull,
                   "--smoothIt", 50, "--smoothRate", 0.5,
                   "--deciMaxClearance", 5., "--internalinterface")
    context.system("meshCleaner",
                   "-i", self.right_hemi_hull,
                   "-o", self.right_hemi_hull,
                   "-maxCurv", "0.5")

    tm.copyReferential(self.split_mask, self.right_hemi_hull)
    del Rhull

    context.write("Extracting hemispheres hull...")
    Hhull = context.temporary('NIFTI-1 Image')

    context.system("VipDoubleThreshold",
                   "-i", self.split_mask, "-o", Hhull,
                   "-tl", "1", "-th", "2", "-m", "be",
                   "-c", "b", "-w", "t")
    context.system("VipClosing",
                   "-i", Hhull, "-o", Hhull,
                   "-s", "10", "-w", "t")
    context.system("VipSingleThreshold",
                   "-i", Hhull, "-o", Hhull,
                   "-t", "0", "-m", "eq",
                   "-c", "b", "-w", "t")

    context.system("AimsMeshBrain",
                   "-i", Hhull, "-o", self.both_hemi_hull,
                   "--smoothIt", 50, "--smoothRate", 0.5,
                   "--deciMaxClearance", 5., "--internalinterface")
    context.system("meshCleaner",
                   "-i", self.both_hemi_hull,
                   "-o", self.both_hemi_hull,
                   "-maxCurv", "0.5")

    tm.copyReferential(self.split_mask, self.both_hemi_hull)
    del Hhull

    context.write("Extracting brain hull...")
    Bhull = context.temporary('NIFTI-1 Image')

    context.system("VipSingleThreshold",
                   "-i", self.split_mask, "-o", Bhull,
                   "-t", "0", "-m", "gt",
                   "-c", "b", "-w", "t")
    context.system("VipClosing",
                   "-i", Bhull, "-o", Bhull,
                   "-s", "10", "-w", "t")
    context.system("VipSingleThreshold",
                   "-i", Bhull, "-o", Bhull,
                   "-t", "0", "-m", "eq",
                   "-c", "b", "-w", "t")

    context.system("AimsMeshBrain",
                   "-i", Bhull, "-o", self.brain_hull,
                   "--smoothIt", 50, "--smoothRate", 0.5,
                   "--deciMaxClearance", 5., "--internalinterface")
    context.system("meshCleaner",
                   "-i", self.brain_hull,
                   "-o", self.brain_hull,
                   "-maxCurv", "0.5")

    tm.copyReferential(self.split_mask, self.brain_hull)
    del Bhull
