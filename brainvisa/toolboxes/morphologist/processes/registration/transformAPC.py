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

name = 'Transform a commissures AC-PC coordinates'
userLevel = 1


def validation():
    try:
        from soma import aims
    except:
        raise ValidationError('aims module not available')


signature = Signature(
    'Commissure_coordinates',
    ReadDiskItem('Commissure coordinates', 'Commissure coordinates'),
    'T1mri', ReadDiskItem("Raw T1 MRI", 'AIMS readable volume formats'),
    'output_coordinates', WriteDiskItem('Commissure coordinates',
                                        'Commissure coordinates'),
    'transformation', ReadDiskItem('Transformation Matrix',
                                   'Transformation matrix'),
    'destination_volume', ReadDiskItem('Raw T1 MRI',
                                       'AIMS readable volume formats'),
)


def initialization(self):
    self.linkParameters('T1mri', 'Commissure_coordinates')
    self.linkParameters('destination_volume', 'output_coordinates')
    self.setOptional('T1mri')


def execution(self, context):
    if not self.T1mri:
        context.write('No T1mri parameter specified - hope the .APC file ',
                      self.Commissure_coordinates, ' contains millimetric information')
    from soma import aims
    from soma.aims import apctools
    mot = aims.read(self.transformation.fullPath())
    mri = None
    if self.T1mri:
        mri = self.T1mri.fullPath()
    apctools.apcFileTransform(self.Commissure_coordinates.fullPath(),
                              self.output_coordinates.fullPath(), mot,
                              self.destination_volume.fullPath(), mri)
