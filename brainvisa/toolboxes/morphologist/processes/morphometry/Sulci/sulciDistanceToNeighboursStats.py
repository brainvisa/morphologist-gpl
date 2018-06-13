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
from brainvisa.data.labelSelection import LabelSelection
from brainvisa import registration

name = 'Sulci Distance to Neighbours Stats'
userLevel = 0


signature = Signature(
    'graphs', ListOf(ReadDiskItem('Labelled Cortical Folds Graph',
                                  'Graph and data')),
    'output_csv', WriteDiskItem('CSV file', 'CSV file'),
    'nomenclature', ReadDiskItem('Nomenclature', 'Hierarchy'),
    'model', ReadDiskItem('Model graph', 'Graph'),
    'region_selection', LabelSelection(),
    'label_attribute', Choice('auto', 'label', 'name'),
)


def initialization(self):
    def change_region(self, proc):
        if self.model:
            mod = self.model.fullPath()
        else:
            mod = None
        if self.nomenclature:
            nom = self.nomenclature.fullPath()
        else:
            nom = None
        sel = self.region_selection
        if sel is None:
            sel = LabelSelection(mod, nom)
        else:
            sel.value['model'] = mod
            sel.value['nomenclature'] = nom
        return sel

    def linkModel(self, proc):
        if self.graphs is not None and len(self.graphs) != 0:
            return self.signature['model'].findValue(self.graphs[0])
        return None

    self.nomenclature = self.signature['nomenclature'].findValue({})
    self.setOptional('model', 'nomenclature', 'region_selection')
    self.linkParameters('model', 'graphs', linkModel)
    self.linkParameters('region_selection', ('model', 'nomenclature'),
                        change_region)


def execution(self, context):
    self.region_selection.writeSelection(context)
    if self.region_selection.isValid():
        sfile = self.region_selection.file
    else:
        sfile = None
    tmpcsv = context.temporary('CSV file')
    open(self.output_csv.fullPath(), 'w')
    first = True
    ns = len(self.graphs)
    n = 0
    for g in self.graphs:
        subject = g.get('subject', None)
        cmd = ['sulciDistanceToNeighbours.py', '-i', g, '-o', tmpcsv]
        if subject:
            cmd += ['-s', subject]
        if self.label_attribute == 'auto':
            if g.get('manually_labelled', 'No') == 'Yes':
                cmd += ['-l', 'name']
            else:
                cmd += ['-l', 'label']
        else:
            cmd += ['-l', self.label_attribute]
        if sfile is not None:
            cmd += ['-t', sfile]
        elif self.nomenclature is not None and self.model is not None:
            cmd += ['-t', self.nomenclature]
            if self.model is not None:
                cmd += ['--modeltrans', self.model]
        context.progress(n, ns, process=self)
        context.write('processing subject', n+1, '/', ns, ':', g, '...')
        context.system(*cmd)
        of = open(self.output_csv.fullPath(), 'a')
        f = open(tmpcsv.fullPath())
        if first:
            first = False
        else:
            l = f.readline()  # skip header line
            l[:-1]  # force using iterator
        rem = f.read()
        of.write(rem)
        of.close()
        f.close()
        n += 1

    context.progress(ns, ns, process=self)
