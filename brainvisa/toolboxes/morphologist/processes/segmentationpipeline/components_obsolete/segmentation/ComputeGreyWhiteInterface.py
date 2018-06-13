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
from brainvisa import shelltools
from brainvisa import registration

name = '5 - Compute Grey white Interface Mesh'
userLevel = 2

# Argument declaration
signature = Signature(
    'Side', Choice("Both", "Left", "Right"),
    'left_hemi_cortex', ReadDiskItem('Left CSF+GREY Mask',
                                     'Aims writable volume formats'),
    'right_hemi_cortex', ReadDiskItem('Right CSF+GREY Mask',
                                      'Aims writable volume formats'),
    'left_white_mesh', WriteDiskItem('Left Hemisphere White Mesh',
                                     'Aims mesh formats'),
    'right_white_mesh', WriteDiskItem('Right Hemisphere White Mesh',
                                      'Aims mesh formats'),
    'left_white_mesh_fine', WriteDiskItem('Left Fine Hemisphere White Mesh',
                                          'Aims mesh formats'),
    'right_white_mesh_fine', WriteDiskItem('Right Fine Hemisphere White Mesh',
                                           'Aims mesh formats'),

    'iterations', Integer(),
    'rate', Float(),
)
# Default values


def initialization(self):
    self.linkParameters('right_hemi_cortex', 'left_hemi_cortex')
    self.linkParameters('left_white_mesh', 'left_hemi_cortex')
    self.linkParameters('right_white_mesh', 'right_hemi_cortex')
    self.linkParameters('left_white_mesh_fine', 'left_hemi_cortex')
    self.linkParameters('right_white_mesh_fine', 'right_hemi_cortex')
    self.Side = "Both"
    self.iterations = 10
    self.rate = 0.2
#


def execution(self, context):
    tm = registration.getTransformationManager()
    if self.Side in ('Left', 'Both'):

        if os.path.exists(self.left_white_mesh.fullName() + '.loc'):
            context.write("Left Hemisphere White Mesh Locked")
        else:
            context.write("Reconstructing left hemisphere white surface...")
            white = context.temporary('GIS Image')
            context.system("VipSingleThreshold", "-i", self.left_hemi_cortex,
                           "-o", white, "-t", "0", "-c", "b", "-m",
                           "ne", "-w", "t")
            context.system("AimsMeshWhite", "-i", white, "-o",
                           self.left_white_mesh)
            context.system("AimsMeshWhite", "-i", white, "-o",
                           self.left_white_mesh_fine,
                           "--deciMaxClearance",  "1",
                           "--deciMaxError", "1")
            del white

            context.write("Smoothing mesh...")
            context.runProcess('meshSmooth', mesh=self.left_white_mesh,
                               iterations=self.iterations, rate=self.rate)
            context.runProcess('meshSmooth', mesh=self.left_white_mesh_fine,
                               iterations=20, rate=self.rate)
            tm.copyReferential(self.left_hemi_cortex, self.left_white_mesh)
            tm.copyReferential(self.left_hemi_cortex,
                               self.left_white_mesh_fine)

    if self.Side in ('Right', 'Both'):

        if os.path.exists(self.right_white_mesh.fullName() + '.loc'):
            context.write("Right Hemisphere White Mesh Locked")
        else:
            context.write("Reconstructing right hemisphere white surface...")
            white = context.temporary('GIS Image')
            context.system("VipSingleThreshold", "-i", self.right_hemi_cortex,
                           "-o", white, "-t", "0", "-c", "b", "-m",
                           "ne", "-w", "t")
            context.system("AimsMeshWhite", "-i", white, "-o",
                           self.right_white_mesh)
            context.system("AimsMeshWhite", "-i", white, "-o",
                           self.right_white_mesh_fine,
                           "--deciMaxClearance",  "1",
                           "--deciMaxError", "1")
            del white

            context.write("Smoothing mesh...")
            context.runProcess('meshSmooth', mesh=self.right_white_mesh,
                               iterations=self.iterations, rate=self.rate)
            context.runProcess('meshSmooth', mesh=self.right_white_mesh_fine,
                               iterations=20, rate=self.rate)
            tm.copyReferential(self.left_hemi_cortex, self.right_white_mesh)
            tm.copyReferential(self.left_hemi_cortex,
                               self.right_white_mesh_fine)
