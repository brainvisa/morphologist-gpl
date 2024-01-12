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


name = 'Concatenate both hemisphere textures'
userLevel = 0

signature = Signature(
    'left_texture', ReadDiskItem('Texture', 'aims texture formats',
                                 requiredAttributes={'side': 'left'}),
    'right_texture', ReadDiskItem('Texture', 'aims texture formats',
                                  requiredAttributes={'side': 'right'}),
    'both_texture', WriteDiskItem('Texture', 'aims texture formats',
                                  requiredAttributes={'side': 'both'}),
    'left_offset', Float(),
    'right_offset', Float(),
)


def initialization(self):
    self.linkParameters('right_texture', 'left_texture')
    self.linkParameters('both_texture', 'left_texture')
    self.left_offset = 0
    self.right_offset = 0


def execution(self, context):
    from soma import aims
    import numpy as np
    left = aims.read(self.left_texture.fullPath())
    right = aims.read(self.right_texture.fullPath())
    dtype = left[0].np.dtype
    both = aims.TimeTexture(dtype=dtype)
    loff = type(left[0][0])(self.left_offset)
    roff = type(left[0][0])(self.right_offset)
    for t in range(max(len(left), len(right))):
        if t >= len(left):
            l = np.zeros((len(left[0]), ), dtype=dtype)
        else:
            l = left[t].np
        if t >= len(right):
            r = np.zeros((len(right[0]), ), dtype=dtype)
        else:
            r = right[t].np

        b = np.hstack((l + loff, r + roff))
        both[t].assign(b)
    aims.write(both, self.both_texture.fullPath())
