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
from brainvisa import anatomist

name = 'Anatomist Show Hemisphere With MRI'
roles = ('viewer',)
userLevel = 0


def validation():
    anatomist.validation()


signature = Signature(
    'hemi_mesh', ReadDiskItem('Hemisphere Mesh', 'Anatomist mesh formats'),
    'mri_corrected', ReadDiskItem('T1 MRI Bias Corrected',
                                  'Anatomist volume formats'),
)


def initialization(self):
    self.setOptional('mri_corrected')
    self.linkParameters('mri_corrected', 'hemi_mesh')


def execution(self, context):
    a = anatomist.Anatomist()
    mesh = a.loadObject(self.hemi_mesh, duplicate=True)
    mesh.setMaterial(a.Material(diffuse=[0.9, 0.7, 0.0, 1]))
    returned = [mesh]
    if self.mri_corrected is not None:
        anat = a.loadObject(self.mri_corrected)
        returned.append(anat)
    win3 = a.createWindow('Sagittal')
    win3.assignReferential(mesh.referential)
    side = self.hemi_mesh.get('side')
    if side is not None and side == 'right':
        win3.camera(view_quaternion=[0.5, -0.5, -0.5, 0.5])

    if self.mri_corrected is not None:
        win3.addObjects([anat])
    win3.addObjects([mesh])
    returned.append(win3)

    return returned
