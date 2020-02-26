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

#
# MeshCurvatureEstimation process declaration
#
from __future__ import absolute_import
from brainvisa.processes import *

name = 'White Mesh Curvature Estimation'
userLevel = 2

# Argument declaration
signature = Signature(
    'Side', Choice("Both", "Left", "Right"),
    'Method', Choice("fem", "barycenter", "boix"),
    'left_white_mesh', ReadDiskItem(
        'Left Hemisphere White Mesh', 'aims Mesh Formats'),
    'right_white_mesh', ReadDiskItem(
        'Right Hemisphere White Mesh', 'aims Mesh Formats'),
    'left_white_curvature', WriteDiskItem(
        'White Curvature Texture', 'Texture', requiredAttributes={'side': 'left'}),
    'right_white_curvature', WriteDiskItem(
        'White Curvature Texture', 'Texture', requiredAttributes={'side': 'right'}),
    'Threshold_ratio', Float()
)


# Default values
def initialization(self):
    self.linkParameters('right_white_mesh', 'left_white_mesh')
    self.linkParameters('left_white_curvature', 'left_white_mesh')
    self.linkParameters('right_white_curvature', 'right_white_mesh')
    self.Threshold_ratio = 0.95

# process


def execution(self, context):
    if self.Side in ('Left', 'Both'):
        context.system('AimsMeshCurvature', '-i', self.left_white_mesh.fullPath(), '-o', self.left_white_curvature.fullPath(),
                       '-m', self.Method, '-r', self.Threshold_ratio)
    if self.Side in ('Right', 'Both'):
        context.system('AimsMeshCurvature', '-i', self.right_white_mesh.fullPath(), '-o', self.right_white_curvature.fullPath(),
                       '-m', self.Method, '-r', self.Threshold_ratio)
