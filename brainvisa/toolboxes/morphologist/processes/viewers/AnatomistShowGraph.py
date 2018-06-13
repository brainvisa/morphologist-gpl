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

name = 'Anatomist Show Graph'
roles = ('viewer',)
userLevel = 0


def validation():
    anatomist.validation()


signature = Signature(
    'graph', ReadDiskItem('Data Graph', 'Graph'),
    'nomenclature', ReadDiskItem('Nomenclature', 'Hierarchy'),
    'anatomy', ReadDiskItem('T1 MRI', 'anatomist Volume Formats'),
    'meshes', ListOf(ReadDiskItem('Mesh',
                                  'anatomist Mesh Formats')),
    'head_mesh', ReadDiskItem('Head mesh',
                              'anatomist Mesh Formats'),
)


def initialization(self):
    def change_meshes(self, proc):
        meshes = []
        m = ReadDiskItem('Hemisphere mesh',
                         'anatomist Mesh Formats'). \
            findValue(self.graph)
        if m is not None:
            meshes.append(m)
        return meshes

    self.setOptional('nomenclature')
    self.setOptional('anatomy')
    self.setOptional('meshes')
    self.setOptional('head_mesh')
    self.linkParameters('anatomy', 'graph')
    self.nomenclature = self.signature['nomenclature'].findValue({})
    self.linkParameters('head_mesh', 'graph')
    self.linkParameters('meshes', 'graph', change_meshes)


def execution(self, context):
    a = anatomist.Anatomist()
    selfdestroy = []
    obj = []
    if self.nomenclature is not None:
        (hie, br) = context.runProcess('AnatomistShowNomenclature',
                                       read=self.nomenclature)
        selfdestroy += (hie, br)
    obj.append(a.loadObject(self.graph))
    if self.anatomy is not None:
        obj.append(a.loadObject(self.anatomy))
    if self.meshes is not None:
        msh = map(lambda x: a.loadObject(x), self.meshes)
        obj += msh
    if self.head_mesh is not None:
        hd = a.loadObject(self.head_mesh)
        obj.append(hd)
        hd.setMaterial(a.Material(diffuse=[1, 0.85, 0.5, 0.5]))
    win3 = a.createWindow('3D')
    win3.addObjects(obj, add_graph_nodes=True)
    selfdestroy.append(win3)

    return selfdestroy + obj
