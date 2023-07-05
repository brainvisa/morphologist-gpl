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
from soma import aims
from brainvisa import registration

name = 'Grey White Surface 2012'
userLevel = 2

# Argument declaration
signature = Signature(
    'Side', Choice("Both", "Left", "Right"),
    'mri_corrected', ReadDiskItem('T1 MRI Bias Corrected',
                                  'Aims readable volume formats'),
    'histo_analysis', ReadDiskItem('Histo Analysis', 'Histo Analysis'),
    'left_grey_white', ReadDiskItem('Left Grey White Mask',
                                    'Aims writable volume formats'),
    'right_grey_white', ReadDiskItem('Right Grey White Mask',
                                     'Aims writable volume formats'),
    'left_hemi_cortex', WriteDiskItem('Left CSF+GREY Mask',
                                      'Aims writable volume formats'),
    'right_hemi_cortex', WriteDiskItem('Right CSF+GREY Mask',
                                       'Aims writable volume formats'),
    'left_white_mesh', WriteDiskItem('Left Hemisphere White Mesh',
                                     'Aims mesh formats'),
    'right_white_mesh', WriteDiskItem('Right Hemisphere White Mesh',
                                      'Aims mesh formats'),
    'fix_random_seed', Boolean(),

)
# Default values


def initialization(self):
    self.linkParameters('histo_analysis', 'mri_corrected')
    self.linkParameters('left_grey_white', 'mri_corrected')
    self.linkParameters('right_grey_white', 'mri_corrected')
    self.linkParameters('left_hemi_cortex', 'mri_corrected')
    self.linkParameters('right_hemi_cortex', 'mri_corrected')
    self.linkParameters('left_white_mesh', 'mri_corrected')
    self.linkParameters('right_white_mesh', 'mri_corrected')
    self.signature['fix_random_seed'].userLevel = 3
    self.Side = "Both"
    self.fix_random_seed = False
#
#


def execution(self, context):
    tm = registration.getTransformationManager()
    if self.Side in ('Left', 'Both'):

        if os.path.exists(self.left_hemi_cortex.fullName() + '.loc'):
            context.write("Left cortex locked")
        else:
            context.write("Detecting left spherical cortex interface...")
            command = ["VipHomotopic",
                       "-i", self.mri_corrected,
                       "-cl", self.left_grey_white,
                       "-h", self.histo_analysis,
                       "-o", self.left_hemi_cortex,
                       "-m", "C", "-v", '1', "-w", "t"]
            if self.fix_random_seed:
                command.extend(['-srand', '10'])
            context.system(*command)
            tm.copyReferential(self.left_grey_white, self.left_hemi_cortex)

        if os.path.exists(self.left_white_mesh.fullName() + '.loc'):
            context.write("Left Hemisphere White Mesh Locked")
        else:
            context.write("Reconstructing left hemisphere white surface...")
            white = context.temporary('NIFTI-1 Image')
            context.system("AimsThreshold", "-i", self.left_hemi_cortex,
                           "-o", white, "-t", "0", "-b", "-m", "di")

            context.system("AimsMeshBrain", "-i", white,
                           "-o", self.left_white_mesh,
                           "--smoothType", "laplacian",
                           "--smoothIt", 5, "--smoothRate", 0.4,
                           "--deciMaxClearance", 5., "--deciMaxError", 3.,
                           "--internalinterface")
            context.system("AimsMeshCleaner", "-i", self.left_white_mesh,
                           "-o", self.left_white_mesh, "-maxCurv", "0.5")

            tm.copyReferential(self.left_grey_white, self.left_white_mesh)

            del white

    if self.Side in ('Right', 'Both'):

        if os.path.exists(self.right_hemi_cortex.fullName() + '.loc'):
            context.write("Right cortex locked")
        else:
            context.write("Detecting right spherical cortex interface...")
            command = ["VipHomotopic",
                       "-i", self.mri_corrected,
                       "-cl", self.right_grey_white,
                       "-h", self.histo_analysis,
                       "-o", self.right_hemi_cortex,
                       "-m", "C", "-v", '1', "-w", "t"]
            if self.fix_random_seed:
                command.extend(['-srand', '10'])
            context.system(*command)
            tm.copyReferential(self.right_grey_white, self.right_hemi_cortex)

        if os.path.exists(self.right_white_mesh.fullName() + '.loc'):
            context.write("Right Hemisphere White Mesh Locked")
        else:
            context.write("Reconstructing right hemisphere white surface...")
            white = context.temporary('NIFTI-1 Image')
            context.system("AimsThreshold", "-i", self.right_hemi_cortex,
                           "-o", white, "-t", "0", "-b", "-m", "di")

            context.system("AimsMeshBrain", "-i", white,
                           "-o", self.right_white_mesh,
                           "--smoothType", "laplacian",
                           "--smoothIt", 5, "--smoothRate", 0.4,
                           "--deciMaxClearance", 5., "--deciMaxError", 3.,
                           "--internalinterface")
            context.system("AimsMeshCleaner", "-i", self.right_white_mesh,
                           "-o", self.right_white_mesh, "-maxCurv", "0.5")

            tm.copyReferential(self.right_grey_white, self.right_white_mesh)

            del white
