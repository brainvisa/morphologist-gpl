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

from brainvisa.processes import (
    Signature, ReadDiskItem, WriteDiskItem, String, Choice,
)
from brainvisa.morphologist.morphometry import global_sulc_morpho
from morphologist.qc import morpho_qc
from soma import aims
import os
import os.path as osp


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
    'split_template', ReadDiskItem('Hemispheres template',
                                   'aims readable volume formats'),
    'icbm_brain_mask_template', ReadDiskItem(
        'Anatomical template', 'aims readable volume formats',
        requiredAttributes={'skull_stripped': 'yes', 'Size': '1 mm'}),
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

    def linkBrainVolumes(self, proc):
        if self.left_labelled_graph is not None:
            return self.signature['brain_volumes_file'].findValue(
                self.left_labelled_graph)
        if self.split_brain is not None:
            return self.signature['brain_volumes_file'].findValue(
                self.split_brain)
        return None

    self.split_template = self.signature['split_template'].findValue({})
    self.icbm_brain_mask_template \
        = self.signature['icbm_brain_mask_template'].findValue({})

    self.sulci_label_attribute = 'label'
    self.setOptional('left_labelled_graph', 'right_labelled_graph',
                     'left_gm_mesh', 'right_gm_mesh',
                     'left_wm_mesh', 'right_wm_mesh', 'split_template',
                     'icbm_brain_mask_template')
    self.linkParameters('subject', 'split_brain', linkSubject)
    self.linkParameters('left_grey_white', 'split_brain')
    self.linkParameters('right_grey_white', 'split_brain')
    self.linkParameters('left_csf', 'split_brain')
    self.linkParameters('right_csf', 'split_brain')
    self.linkParameters('left_labelled_graph', 'split_brain')
    self.linkParameters('right_labelled_graph', 'left_labelled_graph')
    self.linkParameters('brain_volumes_file',
                        ('left_labelled_graph', 'split_brain'),
                        linkBrainVolumes)
    self.linkParameters('left_gm_mesh', 'split_brain')
    self.linkParameters('right_gm_mesh', 'split_brain')
    self.linkParameters('left_wm_mesh', 'split_brain')
    self.linkParameters('right_wm_mesh', 'split_brain')

    self.linkParameters('sulci_label_attribute',
                        ('left_labelled_graph', 'right_labelled_graph'),
                        linkSulciLabelAtt)


def execution(self, context):
    context.write('Extracting left and right CSF inside sulci.\n')
    do_csf = False
    if not osp.exists(self.left_csf.fullPath()) \
            or not osp.exists(self.right_csf.fullPath()):
        do_csf = True
    if not do_csf and (
            os.stat(self.left_grey_white.fullPath()).st_mtime
            >= os.stat(self.left_csf.fullPath()).st_mtime
            or os.stat(self.right_grey_white.fullPath()).st_mtime
            >= os.stat(self.right_csf.fullPath()).st_mtime):
        do_csf = True

    if not do_csf:
        context.write('CSF masks are up-to-date.')
    else:
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
    rwm = None
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
          'left.hull_area': 'left.hull_area',
          'right.hull_area': 'right.hull_area',
          'left.skel_points': 'left_skel_points',
          'right.skel_points': 'right_skel_points',
          'left.skel_labelled_points': 'left_skel_labelled_points',
          'right.skel_labelled_points': 'right_skel_labelled_points',
        }
        vols_cm3 = [k for k in col_names.keys()
                    if k not in ('subject', 'left.skel_points',
                                 'right.skel_points',
                                 'left.skel_labelled_points',
                                 'right.skel_labelled_points',
                                 'left.hull_area', 'right.hull_area')]

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

    if self.split_template is not None \
            and self.icbm_brain_mask_template is not None:
        split_template = aims.read(self.split_template.fullPath())
        icbm_template = aims.read(self.icbm_brain_mask_template.fullPath())
        qc_sb_res = morpho_qc.split_brain_overlaps(
            self.split_brain.fullPath(), split_template, icbm_template)
        qc_fold_res = morpho_qc.graphs_overlaps(
            self.left_labelled_graph.fullPath(),
            self.right_labelled_graph.fullPath(),
            split_template, icbm_template)
        ncols = ['brain_template_overlap', 'brain_template_out',
                 'brain_template_missing',
                 'left.template_overlap', 'left.template_out',
                 'left.template_missing',
                 'right.template_overlap', 'right.template_out',
                 'right.template_missing',
                 'left.sulci_template_overlap', 'left.sulci_template_out',
                 'left.sulci_template_missing',
                 'right.sulci_template_overlap', 'right.sulci_template_out',
                 'right.sulci_template_missing',]
        csvh += ncols
        th += [f'<td>{x}</td>' for x in ncols]
        gb = qc_sb_res['global']
        nv = [gb['jaccard'],
              gb['outside'] / gb['template_size'],
              gb['missing'] / gb['template_size']]
        gb = qc_sb_res['left_hemi']
        nv += [gb['jaccard'],
               gb['outside'] / gb['template_size'],
               gb['missing'] / gb['template_size']]
        gb = qc_sb_res['right_hemi']
        nv += [gb['jaccard'],
               gb['outside'] / gb['template_size'],
               gb['missing'] / gb['template_size']]
        gb = qc_fold_res['left_hemi']
        nv += [gb['jaccard'],
               gb['outside'] / gb['template_size'],
               gb['missing'] / gb['template_size']]
        gb = qc_fold_res['right_hemi']
        nv += [gb['jaccard'],
               gb['outside'] / gb['template_size'],
               gb['missing'] / gb['template_size']]
        nv = [f'{x:.3}' for x in nv]
        csvt += nv
        table += [f'<td>{x}</td>' for x in nv]

    context.write('<table style="border: 1px"><th>' + ''.join(th)
                  + '</th><tr>' + ''.join(table) + '</tr></table>')

    if self.brain_volumes_file is not None:
        with open(self.brain_volumes_file.fullPath(), 'w') as f:
            f.write(';'.join(csvh) + '\n')
            f.write(';'.join(csvt))
