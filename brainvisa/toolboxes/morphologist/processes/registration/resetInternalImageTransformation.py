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
import soma.subprocess
import re
from six.moves import zip


def validation():
    try:
        from soma import aims
    except Exception as e:
        raise ValidationError(_t_('soma.aims module cannot be imported: ')
                              + str(e))


name = 'Reset internal image transformation'
userLevel = 1

signature = Signature(
    'input_image', ReadDiskItem("4D Volume",
                                'aims readable volume formats'),
    'output_image', WriteDiskItem("4D Volume",
                                  'aims writable volume formats'),
    'origin', Choice(('Center of the image', 0), ('Gravity center', 1)),
    'roi_image', ReadDiskItem("4D Volume",
                              'aims readable volume formats'),
)


def initialization(self):
    self.linkParameters('output_image', 'input_image')

    self.addLink(None, 'origin', self._update_roi_by_origin)
    self.setOptional('roi_image')
    self.setUserLevel(2, 'roi_image')


def execution(self, context):
    from soma import aims
    vol = aims.read(self.input_image.fullPath())
    h = vol.header()
    refs = ['Scanner-based anatomical coordinates']
    vs = h['voxel_size'][:3]
    tr = -aims.AffineTransformation3d()
    if self.origin == 0:
        tr.setTranslation([vol.getSizeX() * vs[0] / 2,
                           vol.getSizeY() * vs[1] / 2, vol.getSizeZ() * vs[2] / 2, ])
    else:
        cmd = ['AimsMassCenter',
               self.input_image.fullPath()]
        if self.roi_image:
            cmd.extend(['-r', self.roi_image.fullPath()])
        p = soma.subprocess.Popen(cmd,
                                  stdout=soma.subprocess.PIPE,
                                  shell=False)
        pout = p.communicate()[0].decode('utf-8')
        if p.returncode != 0:
            raise RuntimeError('AimsMassCenter failed')
        m = re.search('^General:\t([^\t]+)\t([^\t]+)\t([^\t]+)', pout, re.M)
        tr.setTranslation([float(x) for x in m.groups()])
    trans = [tr.toVector()]
    h['referentials'] = refs
    h['transformations'] = trans
    aims.write(vol, self.output_image.fullPath())


def _update_roi_by_origin(self, proc):
    if self.origin:
        self.setEnable('roi_image')
        self.setOptional('roi_image')
    else:
        self.setDisable('roi_image')
    self.changeSignature(self.signature)
