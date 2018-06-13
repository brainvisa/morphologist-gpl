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
import glob
from brainvisa import registration

name = 'Anatomist Show Descriptive Model'
userLevel = 0
roles = ('viewer',)


def validation():
    anatomist.validation()


signature = Signature(
    'read', ReadDiskItem('Sulci Segments Model', 'Text data table'),
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
        if self.read is not None and self.white_mesh is not None:
            x = ReadDiskItem('Transformation', 'Transformation Matrix',
                             requiredAttributes={'source_referential':
                                                 self.white_mesh.get(
                                                     'referential'),
                                                 'destination_referential': self.read.get('referential')
                                                 }
                             ).findValue({})
            return x

    def linkSide(self, proc):
        if self.read is not None:
            return self.signature['white_mesh'].findValue(
                {'side': self.read.get('side')})
    self.setOptional('nomenclature')
    self.levels = 2
    self.show_unknown = False
    self.nomenclature = self.signature['nomenclature'].findValue({})
    self.linkParameters('white_mesh', 'read', linkSide)
    self.linkParameters('mesh_TO_spam', ('white_mesh', 'read'), linkTrans)
    self.setOptional('white_mesh')
    self.setOptional('mesh_TO_spam')


def execution(self, context):
    a = anatomist.Anatomist()
    meshdir = os.path.join(os.path.dirname(self.read.fullPath()), 'meshes')
    graphs = glob.glob(os.path.join(meshdir, '*.arg'))
    objlist = []
    aref = None
    if len(graphs) != 0:
        if self.nomenclature is not None:
            (hie, br) = context.runProcess('AnatomistShowNomenclature',
                                           read=self.nomenclature)
        tm = registration.getTransformationManager()
        ref = tm.referential(self.read.get('referential'))
        if ref:
            aref = a.createReferential(ref.fullPath())
        for graphname in graphs:
            level = int(graphname[-5]) + 1
            if level == 3:
                level = 4  # make level a binary mask
            if level & self.levels:
                graph = a.loadObject(graphname)
                objlist.append(graph)
                if self.levels not in (1, 2, 4):
                    if level == 2:
                        graph.setMaterial(diffuse=[1., 1., 1., 0.5])
                    elif level == 4:
                        graph.setMaterial(diffuse=[1., 1., 1., 0.2])
        w = a.createWindow('3D')
        if ref:
            a.assignReferential(aref, objlist + [w])
        w.addObjects(objlist, add_graph_nodes=True)
        objlist += [w, br, hie]
        if not self.show_unknown:
            # temporarily make a windows group to have a separate selection
            g = a.linkWindows([w])
            a.execute('SelectByNomenclature', nomenclature=hie,
                      names='unknown', modifiers='remove', group=g)
            a.linkWindows([w], group=0)
    else:
        for meshname in glob.glob(os.path.join(meshdir, '*.mesh')):
            level = int(os.path.splitext(meshname)[0][-1]) + 1
            if level == 3:
                level = 4  # make level a binary mask
            if (level & self.levels) \
                    and (self.show_unknown or meshname.find('unknown') < 0):
                objlist.append(a.loadObject(meshname,
                                            loadReferential=False))
        tm = registration.getTransformationManager()
        ref = tm.referential(self.read.get('referential'))
        w = a.createWindow('3D')
        if ref:
            aref = a.createReferential(ref.fullPath())
            a.assignReferential(aref, objlist + [w])
        w.addObjects(objlist)
        objlist.append(w)

    if self.show_mesh and self.white_mesh is not None:
        mesh = a.loadObject(self.white_mesh)
        objlist.append(mesh)
        w.addObjects(mesh)
        if self.mesh_TO_spam is not None and aref is not None:
            sr = tm.referential(
                self.mesh_TO_spam.get('source_referential'))
            r = a.createReferential(sr)
            a.loadTransformation(self.mesh_TO_spam.fullPath(),
                                 origin=r, destination=aref)

    # set an identity transform between the SPAM model and Talairach AC/PC
    # it is temporary until we handle SPAMs refs correctly
    if aref is not None:
        tr = a.newId()
        #tr = a.Transformation(a)
        a.execute('LoadTransformation', origin=aref, destination=a.centralRef,
                  matrix=[0, 0, 0,  1, 0, 0, 0, 1, 0, 0, 0, 1],
                  res_pointer=tr)
    else:
        context.write('no transfo')
    #context.write( 'objlist:', objlist )
    return objlist
