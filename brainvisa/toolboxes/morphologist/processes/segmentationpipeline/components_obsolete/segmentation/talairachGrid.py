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

from __future__ import print_function
from brainvisa.processes import *

name = 'Talairach grid mesh generator'
userLevel = 2

signature = Signature(
    'output_grid', WriteDiskItem('Mesh', 'aims Mesh Formats'),
    'cylinder_facets', Integer()
)


def initialization(self):
    self.cylinder_facets = 6


def genmesh(self, out, p1, p2, context):
    param = out + ".cfg"
    f = open(param, "w")
    print("attributes = ", file=f)
    par = {'type': 'cylinder',
           'point1': p1,
           'point2': p2,
           'radius': 0.5,
           'facets': self.cylinder_facets}
    print(str(par), file=f)
    f.close()
    context.system('AimsMeshGenerate', '-i', param, '-o', out + '.mesh')


def execution(self, context):
    tmp = context.temporary('Directory', 'Directory')
    dir = tmp.fullPath()
    #os.makedirs( dir )

    self.genmesh(os.path.join(dir, 'e1'), [88, 16, 30],
                 [88, 197, 30], context)
    self.genmesh(os.path.join(dir, 'e2'), [88, 16, 159],
                 [88, 197, 159], context)
    self.genmesh(os.path.join(dir, 'e3'), [88, 16, 30],
                 [88, 16, 159], context)
    self.genmesh(os.path.join(dir, 'e4'), [88, 197, 30],
                 [88, 197, 159], context)

    self.genmesh(os.path.join(dir, 'e5'), [159, 16, 30],
                 [159, 197, 30],
                 context)
    self.genmesh(os.path.join(dir, 'e6'), [159, 16, 159],
                 [159, 197, 159], context)
    self.genmesh(os.path.join(dir, 'e7'), [159, 16, 30],
                 [159, 16, 159], context)
    self.genmesh(os.path.join(dir, 'e8'), [159, 197, 30],
                 [159, 197, 159], context)

    self.genmesh(os.path.join(dir, 'e9'), [88, 16, 30],
                 [159, 16, 30], context)
    self.genmesh(os.path.join(dir, 'e10'), [88, 16, 159],
                 [159, 16, 159], context)
    self.genmesh(os.path.join(dir, 'e11'), [88, 197, 30],
                 [159, 197, 30], context)
    self.genmesh(os.path.join(dir, 'e12'), [88, 197, 159],
                 [159, 197, 159], context)

    self.genmesh(os.path.join(dir, 'se1'), [123.5, 16, 30],
                 [123.5, 197, 30], context)
    self.genmesh(os.path.join(dir, 'se2'), [123.5, 16, 159],
                 [123.5, 197, 159], context)
    self.genmesh(os.path.join(dir, 'se3'), [123.5, 16, 30],
                 [123.5, 16, 159], context)
    self.genmesh(os.path.join(dir, 'se4'), [123.5, 197, 30],
                 [123.5, 197, 159], context)

    self.genmesh(os.path.join(dir, 'se5'), [105.75, 16, 30],
                 [105.75, 197, 30], context)
    self.genmesh(os.path.join(dir, 'se6'), [105.75, 16, 159],
                 [105.75, 197, 159], context)
    self.genmesh(os.path.join(dir, 'se7'), [105.75, 16, 30],
                 [105.75, 16, 159], context)
    self.genmesh(os.path.join(dir, 'se8'), [105.75, 197, 30],
                 [105.75, 197, 159], context)

    self.genmesh(os.path.join(dir, 'se9'), [141.25, 16, 30],
                 [141.25, 197, 30], context)
    self.genmesh(os.path.join(dir, 'se10'), [141.25, 16, 159],
                 [141.25, 197, 159], context)
    self.genmesh(os.path.join(dir, 'se11'), [141.25, 16, 30],
                 [141.25, 16, 159], context)
    self.genmesh(os.path.join(dir, 'se12'), [141.25, 197, 30],
                 [141.25, 197, 159], context)

    self.genmesh(os.path.join(dir, 'oe1'), [88, 61.25, 30],
                 [159, 61.25, 30], context)
    self.genmesh(os.path.join(dir, 'oe2'), [88, 61.25, 159],
                 [159, 61.25, 159], context)
    self.genmesh(os.path.join(dir, 'oe3'), [88, 106.50, 30],
                 [159, 106.50, 30], context)
    self.genmesh(os.path.join(dir, 'oe4'), [88, 106.50, 159],
                 [159, 106.50, 159], context)
    self.genmesh(os.path.join(dir, 'oe5'), [88, 151.75, 30],
                 [159, 151.75, 30], context)
    self.genmesh(os.path.join(dir, 'oe6'), [88, 151.75, 159],
                 [159, 151.75, 159], context)

    self.genmesh(os.path.join(dir, 'i1'), [88, 16, 62.25],
                 [159, 16, 62.25], context)
    self.genmesh(os.path.join(dir, 'i2'), [88, 61.25, 62.25],
                 [159, 61.25, 62.25], context)
    self.genmesh(os.path.join(dir, 'i3'), [88, 106.50, 62.25],
                 [159, 106.50, 62.25], context)
    self.genmesh(os.path.join(dir, 'i4'), [88, 151.75, 62.25],
                 [159, 151.75, 62.25], context)
    self.genmesh(os.path.join(dir, 'i5'), [88, 197, 62.25],
                 [159, 197, 62.25], context)
    self.genmesh(os.path.join(dir, 'i6'), [88, 16, 94.50],
                 [159, 16, 94.50], context)
    self.genmesh(os.path.join(dir, 'i7'), [88, 61.25, 94.50],
                 [159, 61.25, 94.50], context)
    self.genmesh(os.path.join(dir, 'i8'), [88, 106.50, 94.50],
                 [159, 106.50, 94.50], context)
    self.genmesh(os.path.join(dir, 'i9'), [88, 151.75, 94.50],
                 [159, 151.75, 94.50], context)
    self.genmesh(os.path.join(dir, 'i10'), [88, 197, 94.50],
                 [159, 197, 94.50], context)
    self.genmesh(os.path.join(dir, 'i11'), [88, 16, 126.75],
                 [159, 16, 126.75], context)
    self.genmesh(os.path.join(dir, 'i12'), [88, 61.25, 126.75],
                 [159, 61.25, 126.75], context)
    self.genmesh(os.path.join(dir, 'i13'), [88, 106.50, 126.75],
                 [159, 106.50, 126.75], context)
    self.genmesh(os.path.join(dir, 'i14'), [88, 151.75, 126.75],
                 [159, 151.75, 126.75], context)
    self.genmesh(os.path.join(dir, 'i15'), [88, 197, 126.75],
                 [159, 197, 126.75], context)

    self.genmesh(os.path.join(dir, 'l16'), [88, 16, 62.25],
                 [88, 197, 62.25], context)
    self.genmesh(os.path.join(dir, 'l17'), [88, 16, 94.50],
                 [88, 197, 94.50], context)
    self.genmesh(os.path.join(dir, 'l18'), [88, 16, 126.75],
                 [88, 197, 126.75], context)
    self.genmesh(os.path.join(dir, 'l19'), [159, 16, 62.25],
                 [159, 197, 62.25], context)
    self.genmesh(os.path.join(dir, 'l20'), [159, 16, 94.50],
                 [159, 197, 94.50], context)
    self.genmesh(os.path.join(dir, 'l21'), [159, 16, 126.75],
                 [159, 197, 126.75], context)

    self.genmesh(os.path.join(dir, 'l1'), [105.75, 16, 30],
                 [105.75, 197, 30], context)
    self.genmesh(os.path.join(dir, 'l2'), [105.75, 16, 62.25],
                 [105.75, 197, 62.25], context)
    self.genmesh(os.path.join(dir, 'l3'), [105.75, 16, 94.50],
                 [105.75, 197, 94.50], context)
    self.genmesh(os.path.join(dir, 'l4'), [105.75, 16, 126.75],
                 [105.75, 197, 126.75], context)
    self.genmesh(os.path.join(dir, 'l5'), [105.75, 16, 159],
                 [105.75, 197, 159], context)
    self.genmesh(os.path.join(dir, 'l6'), [123.5, 16, 30],
                 [123.5, 197, 30], context)
    self.genmesh(os.path.join(dir, 'l7'), [123.5, 16, 62.25],
                 [123.5, 197, 62.25], context)
    self.genmesh(os.path.join(dir, 'l8'), [123.5, 16, 94.50],
                 [123.5, 197, 94.50], context)
    self.genmesh(os.path.join(dir, 'l9'), [123.5, 16, 126.75],
                 [123.5, 197, 126.75], context)
    self.genmesh(os.path.join(dir, 'l10'), [123.5, 16, 159],
                 [123.5, 197, 159], context)
    self.genmesh(os.path.join(dir, 'l11'), [141.25, 16, 30],
                 [141.25, 197, 30], context)
    self.genmesh(os.path.join(dir, 'l12'), [141.25, 16, 62.25],
                 [141.25, 197, 62.25], context)
    self.genmesh(os.path.join(dir, 'l13'), [141.25, 16, 94.50],
                 [141.25, 197, 94.50], context)
    self.genmesh(os.path.join(dir, 'l14'), [141.25, 16, 126.75],
                 [141.25, 197, 126.75], context)
    self.genmesh(os.path.join(dir, 'l15'), [141.25, 16, 159],
                 [141.25, 197, 159], context)

    self.genmesh(os.path.join(dir, 'v1'), [88, 61.25, 30],
                 [88, 61.25, 159], context)
    self.genmesh(os.path.join(dir, 'v2'), [105.75, 61.25, 30],
                 [105.75, 61.25, 159], context)
    self.genmesh(os.path.join(dir, 'v3'), [123.5, 61.25, 30],
                 [123.5, 61.25, 159], context)
    self.genmesh(os.path.join(dir, 'v4'), [141.25, 61.25, 30],
                 [141.25, 61.25, 159], context)
    self.genmesh(os.path.join(dir, 'v5'), [159, 61.25, 30],
                 [159, 61.25, 159], context)
    self.genmesh(os.path.join(dir, 'v6'), [88, 106.5, 30],
                 [88, 106.5, 159], context)
    self.genmesh(os.path.join(dir, 'v7'), [105.75, 106.5, 30],
                 [105.75, 106.5, 159], context)
    self.genmesh(os.path.join(dir, 'v8'), [123.5, 106.5, 30],
                 [123.5, 106.5, 159], context)
    self.genmesh(os.path.join(dir, 'v9'), [141.25, 106.5, 30],
                 [141.25, 106.5, 159], context)
    self.genmesh(os.path.join(dir, 'v10'), [159, 106.5, 30],
                 [159, 106.5, 159], context)
    self.genmesh(os.path.join(dir, 'v11'), [88, 151.75, 30],
                 [88, 151.75, 159], context)
    self.genmesh(os.path.join(dir, 'v12'), [105.75, 151.75, 30],
                 [105.75, 151.75, 159], context)
    self.genmesh(os.path.join(dir, 'v13'), [123.5, 151.75, 30],
                 [123.5, 151.75, 159], context)
    self.genmesh(os.path.join(dir, 'v14'), [141.25, 151.75, 30],
                 [141.25, 151.75, 159], context)
    self.genmesh(os.path.join(dir, 'v15'), [159, 151.75, 30],
                 [159, 151.75, 159], context)

    files = ['e' + str(x) for x in range(1, 13)]
    files += ['se' + str(x) for x in range(1, 13)]
    files += ['oe' + str(x) for x in range(1, 7)]
    files += ['i' + str(x) for x in range(1, 16)]
    files += ['l' + str(x) for x in range(1, 22)]
    files += ['v' + str(x) for x in range(1, 16)]

    context.write(files)

    context.system('AimsZCat', '-o', self.output_grid,
                   *[os.path.join(dir, f + '.mesh') for f in files])
