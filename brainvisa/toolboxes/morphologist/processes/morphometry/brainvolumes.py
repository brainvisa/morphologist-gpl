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
from soma import aims
from brainvisa.morphologist.morphometry import global_sulc_morpho
import os

name = 'Brain Volumes'
userLevel = 1

signature = Signature(
    'split_brain', ReadDiskItem('Split brain mask',
                                'Aims readable volume formats'),
    'left_grey_white', ReadDiskItem('Left Grey White Mask',
                                    'Aims readable volume formats'),
    'right_grey_white', ReadDiskItem('Right Grey White Mask',
                                     'Aims readable volume formats'),
    'left_csf', WriteDiskItem('Left CSF Mask',
                              'Aims writable volume formats'),
    'right_csf', WriteDiskItem('Right CSF Mask',
                               'Aims writable volume formats'),
    'left_labelled_graph', ReadDiskItem(
        'labelled Cortical Folds Graph', 'Graph and data',
        requiredAttributes={'side': 'left'}),
    'right_labelled_graph', ReadDiskItem(
        'labelled Cortical Folds Graph', 'Graph and data',
        requiredAttributes={'side': 'right'}),
    'left_gm_mesh', ReadDiskItem('Hemisphere mesh', 'aims mesh formats',
                                 requiredAttributes={'side': 'left'}),
    'right_gm_mesh', ReadDiskItem('Hemisphere mesh', 'aims mesh formats',
                                 requiredAttributes={'side': 'right'}),
    'left_wm_mesh', ReadDiskItem('Hemisphere white mesh', 'aims mesh formats',
                                 requiredAttributes={'side': 'left'}),
    'right_wm_mesh', ReadDiskItem('Hemisphere white mesh', 'aims mesh formats',
                                 requiredAttributes={'side': 'right'}),
    'subject', String(),
    'sulci_label_attribute', String(),
    'table_format', Choice('2023', 'old'),
    'brain_volumes_file', WriteDiskItem(
        'Brain volumetry measurements', 'CSV file'),
)


capsul_param_options = {
    'subject': ['dataset="output"'],
}


def initialization(self):
    def linkSubject(self, proc):
        if self.split_brain is not None:
            subject = self.split_brain.get('subject')
            return subject

    def linkSulciLabelAtt(self, proc):
        auto = 'Yes'
        if self.left_labelled_graph is not None:
            auto = self.left_labelled_graph.get('automatically_labelled',
                                                'Yes')
        elif self.right_labelled_graph is not None:
            auto = self.right_labelled_graph.get('automatically_labelled',
                                                 'Yes')
        return {'Yes': 'label', 'No': 'name'}.get(auto, 'label')

    self.sulci_label_attribute = 'label'
    self.setOptional('left_labelled_graph', 'right_labelled_graph',
                     'left_gm_mesh', 'right_gm_mesh',
                     'left_wm_mesh', 'right_wm_mesh')
    self.linkParameters('subject', 'split_brain', linkSubject)
    self.linkParameters('left_grey_white', 'split_brain')
    self.linkParameters('right_grey_white', 'split_brain')
    self.linkParameters('left_csf', 'split_brain')
    self.linkParameters('right_csf', 'split_brain')
    self.linkParameters('brain_volumes_file', 'split_brain')
    self.linkParameters('left_labelled_graph', 'split_brain')
    self.linkParameters('right_labelled_graph', 'split_brain')
    self.linkParameters('left_gm_mesh', 'split_brain')
    self.linkParameters('right_gm_mesh', 'split_brain')
    self.linkParameters('left_wm_mesh', 'split_brain')
    self.linkParameters('right_wm_mesh', 'split_brain')
    self.linkParameters('sulci_label_attribute',
                        ('left_labelled_graph', 'right_labelled_graph'),
                        linkSulciLabelAtt)


def execution(self, context):
    context.write('Extracting left and right CSF inside sulci.\n')
    context.runProcess('AnaComputeLCRClassif',
                       left_grey_white=self.left_grey_white,
                       right_grey_white=self.right_grey_white,
                       left_csf=self.left_csf,
                       right_csf=self.right_csf,
                       split_mask=self.split_brain)
    context.write('Computing volumes.\n')

    lg = None
    rg = None
    lgm = None
    rgm = None
    lwm = None
    rlm = None
    if self.left_labelled_graph is not None:
        lg = self.left_labelled_graph.fullPath()
    if self.right_labelled_graph is not None:
        rg = self.right_labelled_graph.fullPath()
    if self.left_gm_mesh is not None:
        lgm = self.left_gm_mesh.fullPath()
    if self.right_gm_mesh is not None:
        rgm = self.right_gm_mesh.fullPath()
    if self.left_wm_mesh is not None:
        lwm = self.left_wm_mesh.fullPath()
    if self.right_wm_mesh is not None:
        rwm = self.right_wm_mesh.fullPath()

    res = global_sulc_morpho.sulcal_and_brain_morpho(
        lg, rg,
        self.split_brain.fullPath(),
        self.left_grey_white.fullPath(),
        self.right_grey_white.fullPath(),
        self.left_csf.fullPath(),
        self.right_csf.fullPath(),
        lgm, rgm, lwm, rwm,
        remove_nonfold=True, label_att=self.sulci_label_attribute)

    res['subject'] = self.subject

    table = []
    th = []
    csvh = []
    csvt = []
    col_names = {'subject': 'subject'}
    vols_cm3 = []
    if self.table_format == 'old':
        col_names = {
          'subject': 'subject',
          'left.WM': 'left_wm',
          'right.WM': 'right_wm',
          'left.GM': 'left_gm',
          'right.GM': 'right_gm',
          'left.CSF': 'left_csf',
          'right.CSF': 'right_csf',
          'left.hemi_volume': 'lh',
          'right.hemi_volume': 'rh',
          'both.brain_volume': 'brain',
          'both.hemi_closed_volume': 'bothhemi_closed',
          'both.eTIV': 'eTIV',
          'both.WM': 'both_wm',
          'both.GM': 'both_gm',
          'both.CSF': 'both_csf',
          'both.cerebellum_stem_volume': 'cereb_stem',
          'left.brain_volume': 'left_filled_brain',
          'right.brain_volume': 'right_filled_brain',
        }
        vols_cm3 = [k for k in col_names.keys() if k != 'subject']

    for k, cn in col_names.items():
        th.append('<td>' + cn + '</td>')
        csvh.append(cn)
        v = res[k]
        if not isinstance(v, str):
            if k in vols_cm3:
                v = str(round(v / 1000., 3))
            else:
                v = str(round(v, 3))
        table.append('<td>' + v + '</td>')
        csvt.append(v)

    for k, v in res.items():
        if k not in col_names:
            th.append('<td>' + k + '</td>')
            csvh.append(k)
            if not isinstance(v, str):
                if k in vols_cm3:
                    v = str(round(v / 1000., 3))
                else:
                    v = str(round(v, 3))
            table.append('<td>' + v + '</td>')
            csvt.append(v)

    context.write('<table style="border: 1px"><th>' + ''.join(th)
                  + '</th><tr>' + ''.join(table) + '</tr></table>')

    if self.brain_volumes_file is not None:
        f = open(self.brain_volumes_file.fullPath(), 'w')
        f.write(';'.join(csvh) + '\n')
        f.write(';'.join(csvt))
        f.close()
