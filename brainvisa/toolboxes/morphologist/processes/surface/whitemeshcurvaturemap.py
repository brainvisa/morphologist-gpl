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
import os
from brainvisa import anatomist

name = 'White Mesh Curvature Map'
userLevel = 0

signature = Signature(
    "white_mesh", ReadDiskItem("Hemisphere White Mesh", "Aims mesh formats"),
    "curvature_texture", WriteDiskItem("White Curvature Texture", "Aims texture formats"),
    "curvature_method", Choice(('Finite Elements', 'fem'), ('Boix', 'boix'),
                               ('Barycenter', 'barycenter'), ('Boix Gaussian', 'boixgaussian')),
)


def initialization(self):
    self.linkParameters("curvature_texture", "white_mesh")


def execution(self, context):
    context.system('AimsMeshCurvature', '-i', self.white_mesh, '-o',
                   self.curvature_texture, '-m', self.curvature_method)
