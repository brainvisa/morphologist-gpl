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

name = 'Hemisphere Grey White Topological Correction'
userLevel = 0

# Argument declaration
signature = Signature(
    'grey_white', ReadDiskItem('Grey White Mask',
                               'Aims readable volume formats'),
    't1mri_nobias', ReadDiskItem('T1 MRI Bias Corrected',
                                 'Aims readable volume formats'),
    'histo_analysis', ReadDiskItem('Histo Analysis', 'Histo Analysis'),
    'hemi_cortex', WriteDiskItem('CSF+GREY Mask',
                                 'Aims writable volume formats'),
    'version', Choice('1', '2'),
    'fix_random_seed', Boolean(),
)

# Default values


def initialization(self):
    self.linkParameters('t1mri_nobias', 'grey_white')
    self.linkParameters('histo_analysis', 't1mri_nobias')
    self.linkParameters('hemi_cortex', 'grey_white')
    self.signature['version'].userLevel = 3
    self.signature['fix_random_seed'].userLevel = 3
    self.version = '2'
    self.fix_random_seed = False


def execution(self, context):
    tm = registration.getTransformationManager()

    side = self.grey_white.get('side')
    if side is not None:
        context.write("Detecting " + side +
                      " hemisphere spherical inner cortical interface...")
    else:
        context.write("Detecting spherical inner cortical interface...")

    command = ["VipHomotopic",
               "-i", self.t1mri_nobias,
               "-cl", self.grey_white,
               "-h", self.histo_analysis,
               "-o", self.hemi_cortex,
               "-m", "C", "-v", self.version,
               "-w", "t"]
    if self.fix_random_seed:
        command.extend(['-srand', '10'])
    context.system(*command)

    tm.copyReferential(self.grey_white, self.hemi_cortex)
