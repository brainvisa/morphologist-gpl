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
from brainvisa import shelltools

name = 'Create Sulcus Label Volume'
userLevel = 2

signature = Signature(
    'graph', ReadDiskItem('Cortical folds graph', 'Graph'),
    'mri', ReadDiskItem('T1 MRI Bias Corrected',
                        'aims readable Volume Formats'),
    'transformation_matrix', ReadDiskItem('Transformation matrix',
                                          'Transformation matrix'),
    'transformation_template', ReadDiskItem('3D Volume',
                                            'aims readable Volume Formats'),
    'transformation', Choice('No', 'Yes'),
    'binarize', Choice('No', 'Yes'),
    'sulci', WriteDiskItem('Sulci Volume', 'Aims writable volume formats'),
    'simple_surface', WriteDiskItem('Simple Surface Volume',
                                    'Aims writable volume formats'),
    'bottom', WriteDiskItem('Bottom Volume', 'Aims writable volume formats'),
    'hull_junction', WriteDiskItem('Hull Junction Volume',
                                   'Aims writable volume formats'),
    'compress', Choice('Yes', 'No'),
    'bucket', Choice('custom', 'Sulci', 'Simple Surfaces', 'Bottoms',
                     'Junctions with brain hull'),
    'custom_buckets', String(),
    'label_translation', ReadDiskItem(
        'Label Translation', 'Label Translation'),
    'input_int_to_label_translation', ReadDiskItem('log file', 'text file'),
    'int_to_label_translation', WriteDiskItem('log file', 'text file'),
    'label_attributes', Choice('custom', '(label, name)', 'label', 'name'),
    'custom_label_attributes', String(),
    'node_edge_types', Choice('All', 'custom',
                              'Nodes (fold, cluster, roi, nucleus)',
                              'Relations (junction, cortical, etc.)'),
    'custom_node_edge_types', String(),
    'label_values', String(),
)


def initialization(self):
    self.linkParameters('mri', 'graph')
    self.linkParameters('sulci', 'graph')
    self.linkParameters('transformation_matrix', 'mri')
    self.linkParameters('simple_surface', 'graph')
    self.linkParameters('hull_junction', 'graph')
    self.linkParameters('bottom', 'graph')
    self.linkParameters('input_int_to_label_translation', 'graph')
    self.linkParameters('int_to_label_translation', 'graph')
    self.bucket = 'Sulci'
    self.compress = 'No'
#     self.transformation_template = '/home/spm/spm/spm2/templates/T1.mnc'
    self.label_attributes = '(label, name)'
    self.setOptional('mri')
    self.setOptional('transformation_template')
    self.setOptional('transformation_matrix')
    self.setOptional('label_translation')
    self.setOptional('simple_surface')
    self.setOptional('hull_junction')
    self.setOptional('bottom')
    self.setOptional('input_int_to_label_translation')
    self.setOptional('int_to_label_translation')
    self.setOptional('custom_buckets')
    self.setOptional('custom_node_edge_types')
    self.setOptional('custom_label_attributes')
    self.setOptional('label_values')
    self.setOptional('binarize')
    self.setOptional('transformation')


def execution(self, context):
    cmd = ['siGraph2Label', '-g', self.graph.fullPath()]
    if self.mri is not None:
        cmd += ['-tv', self.mri.fullPath()]

    if self.label_translation is not None:
        cmd += ['-tr', self.label_translation.fullPath()]

    if self.label_attributes == 'custom':
        if self.custom_label_attributes:
            la = string.split(self.custom_label_attributes)
        else:
            la = ()
    elif self.label_attributes == '(label, name)':
        la = ()
    else:
        la = (self.label_attributes, )
    for i in la:
        cmd += ['-a', i]

    if self.input_int_to_label_translation is not None:
        cmd += ['-it', self.input_int_to_label_translation.fullPath()]
    if self.int_to_label_translation is not None:
        cmd += ['-ot', self.int_to_label_translation.fullPath()]

    a = ()
    if self.node_edge_types == 'custom':
        if self.custom_node_edge_types:
            a = string.split(self.custom_node_edge_types)
    elif self.node_edge_types == 'Nodes (fold, cluster, roi, nucleus)':
        a = ('fold', 'cluster', 'roi', 'nucleus')
    elif self.node_edge_types == 'Relations (junction, cortical, etc.)':
        a = ('junction', 'cortical', 'hull_junction', 'plidepassage',
             'scalebloblink', 'blob_saddle_link', 'roi_junction', )
    for i in a:
        cmd += ['-s', i]

    if self.label_values:
        a = string.split(self.label_values)
        for i in a:
            cmd += ['-l', i]

    if self.bucket == 'custom':
        if not self.custom_buckets:
            raise Exception('<em>custom_buckets</em> must be non-empty '
                            'in custom bucket mode')
        cmd += ['-o', self.sulci.fullPath()]
        a = string.split(self.custom_buckets)
        for i in a:
            cmd += ['-b', i]
        context.system(*cmd)
        if self.compress == 'Yes':
            context.system('gzip', '--force',
                           self.sulci.fullName() + '*')
    else:
        if self.bucket in ('Sulci'):
            if os.path.exists(self.sulci.fullPath() + '.gz') \
                    or os.path.exists(self.sulci.fullPath()):
                shelltools.rm(self.sulci.fullName() + '.*')
            cmd += ['-o', self.sulci.fullPath(), '-b', 'aims_ss', '-b',
                    'aims_bottom', '-b', 'aims_other']
            context.system(*cmd)
            if self.compress == 'Yes':
                for i in self.sulci.fullPaths():
                    context.system('gzip', '--force', i)
            if self.transformation == 'Yes':
                context.system('AimsResample', '-i', self.sulci.fullPath(),
                               '-o', self.sulci.fullPath(),
                               '-m', self.transformation_matrix.fullPath(),
                               '-t', '0',
                               '-r', self.transformation_template.fullPath())
            if self.binarize == 'Yes':
                context.system('AimsThreshold', '-i', self.sulci.fullPath(),
                               '-m', 'gt', '-t', '0', '-b', '-o', self.sulci.fullPath())
                context.system('AimsReplaceLevel', '-i', self.sulci.fullPath(),
                               '-g', '32767', '-n', '100', '-o', self.sulci.fullPath())

        if self.bucket in ('Bottoms'):
            if os.path.exists(self.bottom.fullPath() + '.gz') \
                    or os.path.exists(self.bottom.fullPath()):
                shelltools.rm(self.bottom.fullName() + '.*')
            cmd += ['-o', self.bottom.fullPath(), '-b', 'aims_bottom']
            context.system(*cmd)
            if self.compress == 'Yes':
                for i in self.bottom.fullPaths():
                    context.system('gzip', '--force', i)
            if self.transformation == 'Yes':
                context.system('AimsResample', '-i', self.bottom.fullPath(),
                               '-o', self.bottom.fullPath(),
                               '-m', self.transformation_matrix.fullPath(),
                               '-t', '0',
                               '-r', self.transformation_template.fullPath())
            if self.binarize == 'Yes':
                context.system('AimsThreshold', '-i', self.bottom.fullPath(),
                               '-m', 'gt', '-t', '0', '-b', '-o', self.bottom.fullPath())
                context.system('AimsReplaceLevel', '-i', self.bottom.fullPath(),
                               '-g', '32767', '-n', '100', '-o', self.bottom.fullPath())

        if self.bucket in ('Junctions with brain hull'):
            if os.path.exists(self.hull_junction.fullPath() + 'a.gz') \
                    or os.path.exists(self.hull_junction.fullPath()):
                shelltools.rm(self.hull_junction.fullName() + '.*')
            cmd += ['-o', self.hull_junction.fullPath(), '-b',
                    'aims_junction', '-s', 'hull_junction']
            context.system(*cmd)
            if self.compress == 'Yes':
                for i in self.hull_junction.fullPaths():
                    context.system('gzip', '--force', i)
            if self.transformation == 'Yes':
                context.system('AimsResample', '-i', self.hull_junction.fullPath(),
                               '-o', self.hull_junction.fullPath(),
                               '-m', self.transformation_matrix.fullPath(),
                               '-t', '0',
                               '-r', self.transformation_template.fullPath())
            if self.binarize == 'Yes':
                context.system('AimsThreshold', '-i', self.hull_junction.fullPath(),
                               '-m', 'gt', '-t', '0', '-b', '-o', self.hull_junction.fullPath())
                context.system('AimsReplaceLevel', '-i', self.hull_junction.fullPath(),
                               '-g', '32767', '-n', '100', '-o', self.hull_junction.fullPath())

        if self.bucket in ('Simple Surfaces'):
            if os.path.exists(self.simple_surface.fullPath() + '.gz') \
                    or os.path.exists(self.simple_surface.fullPath()):
                shelltools.rm(self.simple_surface.fullName() + '.*')
            cmd += ['-o', self.simple_surface.fullPath(), '-b', 'aims_ss']
            context.system(*cmd)
            if self.compress == 'Yes':
                for i in self.simple_surface.fullPaths():
                    context.system('gzip', '--force', i)
            if self.transformation == 'Yes':
                context.system('AimsResample', '-i', self.simple_surface.fullPath(),
                               '-o', self.simple_surface.fullPath(),
                               '-m', self.transformation_matrix.fullPath(),
                               '-t', '0',
                               '-r', self.transformation_template.fullPath())
            if self.binarize == 'Yes':
                context.system('AimsThreshold', '-i', self.simple_surface.fullPath(),
                               '-m', 'gt', '-t', '0', '-b', '-o', self.simple_surface.fullPath())
                context.system('AimsReplaceLevel', '-i', self.simple_surface.fullPath(),
                               '-g', '32767', '-n', '100', '-o', self.simple_surface.fullPath())
