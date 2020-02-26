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
from brainvisa import anatomist

name = 'Show Models With Sulci For Manual Labeling'
userLevel = 0

signature = Signature(
    'graphs', ListOf(ReadDiskItem('Labelled Cortical folds graph',
                                  'Graph and Data')),
    'max_views_per_block', Integer(),
    'show_first_mesh_alone', Boolean(),
    'spam_model', ReadDiskItem('Sulci Segments Model', 'Text data table'),
    'levels', Choice((_t_('1: High probability (70% rejected)'), 1),
                     (_t_('2: Intermediate probability (40% rejected)'), 2),
                     (_t_('3: Low probability (20% rejected)'), 4),
                     (_t_('1-2: High-inter probabilities'), 3),
                     (_t_('1-3: All 3 probabilities thesholds'), 7)),
    'show_unknown', Boolean(),
    'nomenclature', ReadDiskItem('Nomenclature', 'Hierarchy'),
    'show_mesh', Boolean(),
    'white_mesh', ReadDiskItem('White SPAM mesh', 'anatomist mesh formats'),
    'mesh_TO_spam', ReadDiskItem('Transformation', 'Transformation Matrix'),
)


def initialization(self):
    def linkTrans(self, proc):
        if self.spam_model is not None and self.white_mesh is not None:
            x = ReadDiskItem('Transformation', 'Transformation Matrix',
                             requiredAttributes={'source_referential':
                                                 self.white_mesh.get(
                                                     'referential'),
                                                 'destination_referential':
                                                 self.spam_model.get(
                                                     'referential')
                                                 }
                             ).findValue({})
            return x

    def linkSide(self, proc):
        if self.spam_model is not None:
            return self.signature['white_mesh'].findValue(
                {'side': self.spam_model.get('side')})

    def linkSpam(self, proc):
        if len(self.graphs) != 0:
            return ReadDiskItem('Sulci Segments Model', 'Text data table',
                                requiredAttributes={'sulci_segments_model_type':
                                                    'locally_from_global_registred_spam'}). \
                findValue(self.graphs[0])
    self.setOptional('nomenclature')
    self.levels = 2
    self.show_unknown = False
    self.nomenclature = self.signature['nomenclature'].findValue({})
    self.linkParameters('white_mesh', 'spam_model', linkSide)
    self.linkParameters('mesh_TO_spam', ('white_mesh', 'spam_model'),
                        linkTrans)
    self.setOptional('white_mesh')
    self.setOptional('mesh_TO_spam')
    self.linkParameters('spam_model', 'graphs', linkSpam)
    self.max_views_per_block = 12


def execution(self, context):
    a = anatomist.Anatomist()
    objlist = context.runProcess('AnatomistShowDescriptiveModel',
                                 read=self.spam_model, levels=self.levels,
                                 show_unknown=self.show_unknown, nomenclature=self.nomenclature,
                                 show_mesh=self.show_mesh, white_mesh=self.white_mesh,
                                 mesh_TO_spam=self.mesh_TO_spam)
    oldwins = [x for x in objlist if isinstance(x, a.AWindow)]
    objlist = [x for x in objlist if isinstance(x, a.AObject)]
    # clean windows used by AnatomistShowDescriptiveModel in case they are
    # reusable
    a.removeObjects(objects=objlist, windows=oldwins, remove_children=True)
    del oldwins
    bk = a.createWindowsBlock(nbRows=2, nbCols=0)
    w = a.createWindow('3D', block=bk)
    w.setControl('SelectionControl')
    w.addObjects([x for x in objlist if x.objectType != 'NOMENCLATURE'],
                 add_graph_nodes=True)

    if not self.show_unknown and self.nomenclature is not None:
        # temporarily make a windows group to have a separate selection
        g = a.linkWindows([w])
        hie = [x for x in objlist if isinstance(x, a.AObject)
               and x.objectType == 'NOMENCLATURE'][0]
        a.execute('SelectByNomenclature', nomenclature=hie,
                  names='unknown', modifiers='remove', group=g)
        a.linkWindows([w], group=0)
    wins = [w, bk]
    del w
    nv = 1
    first = True

    for g in self.graphs:
        vres = context.runProcess('AnatomistShowFoldGraph', graph=g,
                                  nomenclature=self.nomenclature)
        if self.nomenclature is not None:
            vres = vres[2:]
        oldwins = [x for x in vres if isinstance(x, a.AWindow)]
        vres = [x for x in vres if isinstance(x, a.AObject)]
        # clean windows used by AnatomistShowDescriptiveModel in case they are
        # reusable
        a.removeObjects(objects=vres, windows=oldwins, remove_children=True)
        del oldwins
        if first:
            first = False
            if self.show_first_mesh_alone:
                mesh = [x for x in vres if x.objectType == 'SURFACE']
                if len(mesh) >= 1:
                    mesh = mesh[0]
                    w = a.createWindow('3D', block=bk)
                    w.addObjects(mesh)
                    wins.append(w)
                    nv += 1
                del mesh
        if nv >= self.max_views_per_block:
            bk.arrangeInRect()
            bk = a.createWindowsBlock(nbRows=2, nbCols=None)
            wins.append(bk)
            nv = 0
        w = a.createWindow('3D', block=bk)
        w.setControl('SelectionControl')
        nv += 1
        w.addObjects(vres, add_graph_nodes=True)
        objlist += vres
        wins.append(w)

    bk.arrangeInRect()
    return objlist + wins
