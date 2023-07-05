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
from brainvisa.tools import aimsGlobals
from brainvisa import registration

name = 'Ana Get Spherical Cortical Surface'
userLevel = 2

# Argument declaration
signature = Signature(
    'Side', Choice("Both", "Left", "Right"),
    'mri_corrected', ReadDiskItem('T1 MRI Bias Corrected',
                                  'Aims readable volume formats'),
    'histo_analysis', ReadDiskItem('Histo Analysis', 'Histo Analysis'),
    'split_mask', ReadDiskItem('Split Brain Mask',
                               'Aims readable volume formats'),
    'left_white_mesh', WriteDiskItem('Left Hemisphere White Mesh',
                                     'Aims mesh formats'),
    'right_white_mesh', WriteDiskItem('Right Hemisphere White Mesh',
                                      'Aims mesh formats'),
    'left_white_mesh_fine', WriteDiskItem('Left Fine Hemisphere White Mesh',
                                          'Aims mesh formats'),
    'right_white_mesh_fine', WriteDiskItem('Right Fine Hemisphere White Mesh',
                                           'Aims mesh formats'),

    'oversampling', Choice("none", "best resolution in each direction", "1.0x1.0x1.0mm",
                           "0.9x0.9x0.9mm", "0.8x0.8x0.8mm", "0.7x0.7x0.7mm", "0.6x0.6x0.6mm", "0.5x0.5x0.5mm"),
    'pressure', Choice("0", "25", "50", "75", "100", "125", "150"),
    'iterations', Integer(),
    'rate', Float(),
)
# Default values


def initialization(self):
    self.linkParameters('histo_analysis', 'mri_corrected')
    self.linkParameters('left_white_mesh', 'mri_corrected')
    self.linkParameters('right_white_mesh', 'mri_corrected')
    self.linkParameters('left_white_mesh_fine', 'mri_corrected')
    self.linkParameters('right_white_mesh_fine', 'mri_corrected')
    self.linkParameters('split_mask', 'mri_corrected')
    self.Side = "Both"
    self.oversampling = "best resolution in each direction"
    self.pressure = "100"
    self.iterations = 10
    self.rate = 0.2


def execution(self, context):
    if self.oversampling == "none":
        over_nobias = self.mri_corrected
        over_split = self.split_mask
    else:
        attrs = aimsGlobals.aimsVolumeAttributes(self.mri_corrected,
                                                 forceFormat=1)
        dimx = attrs['volume_dimension'][0]
        dimy = attrs['volume_dimension'][1]
        dimz = attrs['volume_dimension'][2]
        voxx = attrs['voxel_size'][0]
        voxy = attrs['voxel_size'][1]
        voxz = attrs['voxel_size'][2]
        if self.oversampling == "best resolution in each direction":
            minvox = 100
            if minvox > voxx:
                minvox = voxx
            if minvox > voxy:
                minvox = voxy
            if minvox > voxz:
                minvox = voxz
            newvox = minvox
        elif self.oversampling == "1.0x1.0x1.0mm":
            newvox = 1.0
        elif self.oversampling == "0.9x0.9x0.9mm":
            newvox = 0.9
        elif self.oversampling == "0.8x0.8x0.8mm":
            newvox = 0.8
        elif self.oversampling == "0.7x0.7x0.7mm":
            newvox = 0.7
        elif self.oversampling == "0.6x0.6x0.6mm":
            newvox = 0.6
        elif self.oversampling == "0.5x0.5x0.5mm":
            newvox = 0.5
        context.write("New cubic spatial resolution:" + str(newvox))
        over_nobias = context.temporary('GIS Image')
        over_split = context.temporary('GIS Image')
        newdimx = int((dimx+1)*voxx/newvox)
        newdimy = int((dimy+1)*voxy/newvox)
        newdimz = int((dimz+1)*voxz/newvox)
        context.write("Computing oversampled MR image to improve cortical "
                      "surface definition (cubic spline)")
        context.system("AimsApplyTransform", "-i", self.mri_corrected,
                       "-n", "3", "--dx", str(newdimx), "--dy", str(newdimy),
                       "--dz", str(newdimz), "--sx", str(newvox),
                       "--sy", str(newvox), "--sz", str(newvox), "--vol_id",
                       "-o", over_nobias)
        context.write(
            "Computing oversampled split brain mask (nearest neighbor)")
        context.system("AimsApplyTransform", "-i", self.split_mask,
                       "-n", "0", "--dx", str(newdimx), "--dy", str(newdimy),
                       "--dz", str(newdimz), "--sx", str(newvox),
                       "--sy", str(newvox), "--sz", str(newvox), "--vol_id",
                       "-o", over_split)
    trManager = registration.getTransformationManager()
    if self.Side in ('Left', 'Both'):
        if os.path.exists(self.left_white_mesh.fullName() + '.loc'):
            context.write("Left Hemisphere White Mesh Locked")
        else:
            context.write(
                "Masking Bias corrected image with left hemisphere mask...")
            braing = context.temporary('GIS Image')
            context.system("AimsMask", "-i", over_nobias, "-m",
                           over_split, "-o", braing,
                           "-l", "2")

            hemi_cortex = context.temporary('GIS Image')
            context.write("Detecting left grey/white interface...")
            context.system("VipHomotopicSnake", "-i", braing, "-h",
                           self.histo_analysis, "-o",
                           hemi_cortex, "-w", "t", "-p",
                           self.pressure)
            del braing

            context.write("Reconstructing left hemisphere white surface...")
            white = context.temporary('GIS Image')
            context.system("AimsThreshold", "-i", hemi_cortex,
                           "-o", white, "-t", "0", "-b", "-m", "di")
            del hemi_cortex

            context.write("Triangulation and Decimation...")
            context.system("AimsMeshWhite", "-i", white.fullPath(), "-o",
                           self.left_white_mesh.fullPath())
            context.system("AimsMeshWhite", "-i", white.fullPath(), "-o",
                           self.left_white_mesh_fine.fullPath(),
                           "--deciMaxClearance",  "1",
                           "--deciMaxError", "1")
            del white

            context.write("Smoothing mesh...")
            context.runProcess('meshSmooth', mesh=self.left_white_mesh,
                               iterations=self.iterations, rate=self.rate)
            context.runProcess('meshSmooth', mesh=self.left_white_mesh_fine,
                               iterations=20, rate=self.rate)
            trManager.copyReferential(self.mri_corrected, self.left_white_mesh)
            trManager.copyReferential(
                self.mri_corrected, self.left_white_mesh_fine)

    if self.Side in ('Right', 'Both'):
        if os.path.exists(self.right_white_mesh.fullName() + '.loc'):
            context.write("Right Hemisphere White Mesh Locked")
        else:
            context.write(
                "Masking Bias corrected image with right hemisphere mask...")
            braing = context.temporary('GIS Image')
            context.system("AimsMask", "-i", over_nobias, "-m",
                           over_split, "-o", braing,
                           "-l", "1")

            hemi_cortex = context.temporary('GIS Image')
            context.write("Detecting right grey/white interface...")
            context.system("VipHomotopicSnake", "-i", braing, "-h",
                           self.histo_analysis, "-o",
                           hemi_cortex, "-w", "t", "-p",
                           self.pressure)
            del braing

            context.write("Reconstructing right hemisphere white surface...")
            white = context.temporary('GIS Image')
            context.system("AimsThreshold", "-i", hemi_cortex,
                           "-o", white, "-t", "0", "-b", "-m", "di")
            del hemi_cortex

            context.write("Triangulation and Decimation...")
            context.system("AimsMeshWhite", "-i", white.fullPath(), "-o",
                           self.right_white_mesh.fullPath())
            context.system("AimsMeshWhite", "-i", white.fullPath(), "-o",
                           self.right_white_mesh_fine.fullPath(),
                           "--deciMaxClearance",  "1",
                           "--deciMaxError", "1")
            del white

            context.write("Smoothing mesh...")
            context.runProcess('meshSmooth', mesh=self.right_white_mesh,
                               iterations=self.iterations, rate=self.rate)
            context.runProcess('meshSmooth', mesh=self.right_white_mesh_fine,
                               iterations=20, rate=self.rate)
            trManager.copyReferential(
                self.mri_corrected, self.right_white_mesh)
            trManager.copyReferential(
                self.mri_corrected, self.right_white_mesh_fine)

    del over_nobias
    del over_split
