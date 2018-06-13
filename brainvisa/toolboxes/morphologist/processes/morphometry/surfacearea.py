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
import os

name = "Surface Area and Volume"
userLevel = 0

signature = Signature(
    'surfaces', ListOf(ReadDiskItem('Mesh', 'Aims mesh formats')),
    'output_csv', WriteDiskItem('CSV file', 'CSV file'),
)


def initialization(self):
    self.output_csv = os.path.join(os.getcwd(),
                                   'surface_area_vol.csv')


def execution(self, context):
    def areaVolSurface(context, surface):
        cmd = 'AimsMeshArea ' + surface.fullPath()
        f = os.popen(cmd)
        output = f.readlines()
        res = f.close()
        if res is not None and res != 0:
            raise RuntimeError('failure in execution of command ' + cmd)
        a = float(output[0].split()[1])
        v = float(output[1].split()[1])
        return [a, v]

    f = open(self.output_csv.fullPath(), 'w')
    f.write('subject;surface;area_mm2;volume_mm3\n')

    for surface in self.surfaces:
        subject = surface.get('subject')
        side = surface.get('side')
        surf = (os.path.basename(surface.fullPath()).split(
            '.')[0]).replace(subject+"_", "")

        [a, v] = areaVolSurface(context, surface)

        f.write(subject + ';' + surf + ';' + str(a) + ';' + str(v) + '\n')
    f.close()
