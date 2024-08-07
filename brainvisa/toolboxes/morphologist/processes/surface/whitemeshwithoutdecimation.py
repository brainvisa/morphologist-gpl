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

name = 'White Mesh without decimation'
userLevel = 0

# Argument declaration
signature = Signature(
    'hemi_cortex', ReadDiskItem('CSF+GREY Mask',
                                'Aims readable volume formats'),
    'white_mesh_fine', WriteDiskItem('Fine Hemisphere White Mesh',
                                     'Aims mesh formats'),
    'maxClearance',  Float(),
    'maxError', Float(),
    'maxCurv', Float(),
)

# Default values


def initialization(self):
    self.linkParameters('white_mesh_fine', 'hemi_cortex')
    self.maxClearance = 1
    self.maxError = 2
    self.maxCurv = 1.0


def execution(self, context):
    tm = registration.getTransformationManager()
    white = context.temporary('GIS Image')
    context.system("AimsThreshold", "-i", self.hemi_cortex,
                   "-o", white, "-t", "0", "-b", "-m", "di")

    context.system("AimsMeshBrain", "-i", white, "-o", self.white_mesh_fine, '--internalinterface',
                   "--deciMaxClearance",  self.maxClearance, "--deciMaxError", self.maxError)
    context.system("AimsMeshCleaner", "-i", self.white_mesh_fine,
                   "-o", self.white_mesh_fine, "-maxCurv", self.maxCurv)

    tm.copyReferential(self.hemi_cortex, self.white_mesh_fine)
