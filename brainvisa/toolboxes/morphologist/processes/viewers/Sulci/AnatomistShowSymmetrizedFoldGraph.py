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
from brainvisa import anatomist

name = 'Anatomist Show Symmetrized Folds Graph'
#roles = ('viewer',)
userLevel = 2


def validation():
    anatomist.validation()


signature = Signature(
    'graph', ReadDiskItem('Cortical folds graph', 'Graph'),
    'nomenclature', ReadDiskItem('Nomenclature', 'Hierarchy'),
    'white_mesh', ReadDiskItem('Hemisphere White Mesh',
                               'Anatomist mesh formats'),
)


def initialization(self):
    self.setOptional('nomenclature')
    self.setOptional('white_mesh')
    self.linkParameters('white_mesh', 'graph')
    self.nomenclature = self.signature['nomenclature'].findValue({})


def execution(self, context):
    toload = [self.graph]
    if self.white_mesh is not None:
        toload.append(self.white_mesh)
    selfdestroy = []
    if self.nomenclature is not None:
        (hie, br) = context.runProcess('AnatomistShowNomenclature',
                                       read=self.nomenclature)
        selfdestroy += (hie, br)
    objs = context.runProcess('AnatomistShowSymmetrizedData', items=toload)
    a = anatomist.Anatomist()
    l = self.graph.get('automatically_labelled')
    context.write('automatically_labelled:', l)
    nomenclatureprop = 'default'
    if l and l == 'Yes':
        nomenclatureprop = 'label'
        #a.setGraphParams( label_attribute='label', use_nomenclature=1 )
    else:
        l = self.graph.get('manually_labelled')
        context.write('manually_labelled:', l)
        if l and l == 'Yes':
            nomenclatureprop = 'name'
            #a.setGraphParams( label_attribute='name', use_nomenclature=1 )
    graph = objs[0]
    win = objs[-1]
    win.addObjects(graph, add_graph_nodes=True)
    context.write('nomenclature_property:', nomenclatureprop)
    a.execute('GraphDisplayProperties', objects=[graph],
              nomenclature_property=nomenclatureprop)
    selfdestroy += objs
    return selfdestroy
