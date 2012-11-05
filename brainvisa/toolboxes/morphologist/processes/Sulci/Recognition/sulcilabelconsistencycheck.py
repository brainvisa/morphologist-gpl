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

from brainvisa.processes import *
from soma.path import find_in_path
name = 'Sulci Labels consistency check'
userLevel = 0


signature = Signature(
    'sulci_graph', ReadDiskItem( 'Labelled Cortical folds graph', 'Graph' ),
    'side', Choice( 'left', 'right', None ),
    'labeling_type', Choice( ( 'Manual', 'name' ), ( 'Auto', 'label' ), None ),
)


def initialization( self ):
    def linkSide( self, dummy ):
        if self.sulci_graph is not None:
            return self.sulci_graph.get( 'side' )
    def linkLabelAtt( self, dummy ):
        if self.sulci_graph is not None:
            a = self.sulci_graph.get( 'automatically_labelled' )
            if a is not None:
                if a == 'Yes':
                    return 'label'
                elif a == 'No':
                    return 'name'

    self.linkParameters( 'side', 'sulci_graph', linkSide )
    self.linkParameters( 'labeling_type', 'sulci_graph', linkLabelAtt )


def execution( self, context ):
    cmd = [ sys.executable, find_in_path( 'sulciLabelConsistencyCheck.py' ),
        '-i', self.sulci_graph ]
    if self.side:
        cmd += [ '-s', self.side ]
    if self.labeling_type is not None:
        cmd += [ '-l', self.labeling_type ]
    context.system( *cmd )



