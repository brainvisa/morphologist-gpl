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
from soma.path import find_in_path
from brainvisa.tools import aimsGlobals
from brainvisa import registration

name = 'Hemisphere Sulci Voronoi'
userLevel = 2


signature = Signature(
    'graph', ReadDiskItem('Cortical folds graph', 'Graph'),
    'hemi_cortex', ReadDiskItem('CSF+GREY Mask',
                                'Aims readable volume formats'),
    'sulci_voronoi', WriteDiskItem('Sulci Voronoi',
                                   'Aims writable volume formats'),
)


def initialization(self):
    def linkVoronoi(self, proc):
        # this function just to link the image format from hemi_cortex
        format = None
        if self.hemi_cortex is not None:
            format = self.hemi_cortex.format
        if format is None:
            return self.signature['sulci_voronoi'].findValue(self.graph)
        di = WriteDiskItem('Sulci Voronoi',
                           [str(format)] + aimsGlobals.aimsWriteVolumeFormats)
        return di.findValue(self.graph)
    self.linkParameters('hemi_cortex', 'graph')
    self.linkParameters('sulci_voronoi', ('graph', 'hemi_cortex'),
                        linkVoronoi)


def execution(self, context):
    context.system(sys.executable, find_in_path('AimsSulciVoronoi.py'),
                   '-f', self.graph, '-g', self.hemi_cortex, '-o', self.sulci_voronoi)
    trManager = registration.getTransformationManager()
    trManager.copyReferential(self.hemi_cortex, self.sulci_voronoi)
