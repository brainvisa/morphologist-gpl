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
from brainvisa.tools import aimsGlobals

name = 'T1 mapping maps: build using VFA method'
userLevel = 0

signature = Signature(
    'T1weighted_low_angle',
    ReadDiskItem('Raw T1 MRI', 'aims readable volume formats'),
    'T1weighted_high_angle',
    ReadDiskItem('Raw T1 MRI', 'aims readable volume formats'),
    'BAFI_amplitude_map',
    ReadDiskItem('4D Volume', 'aims readable volume formats'),
    'BAFI_phase_map',
    ReadDiskItem('4D Volume', 'aims readable volume formats'),
    'output_t1_map',
    WriteDiskItem('Raw T1 MRI', 'aims writable volume formats'),
    'invert', Boolean(),
    'BAFI_smoothing', Float(),
)


def initialization(self):
    self.invert = True  # can be discussed...
    self.BAFI_smoothing = 0


def execution(self, context):
    cmdexe = os.path.join(findInPath('AimsT1mapVFA.py'),
                          'AimsT1mapVFA.py')
    command = [sys.executable, cmdexe,
               '-t', self.T1weighted_low_angle,
               '-u', self.T1weighted_high_angle,
               '-a', self.BAFI_amplitude_map,
               '-p', self.BAFI_phase_map,
               '-o', self.output_t1_map,
               '-g', self.BAFI_smoothing,
               '-s', 'median']
    if self.invert:
        command.append('--inv')
    context.system(*command)
