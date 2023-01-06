# -*- coding: iso-8859-1 -*-

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
from brainvisa import shelltools

from brainvisa.processes import *
from six.moves import zip
name = 'Volumic Sulcus SPAM'
userLevel = 1

signature = Signature(
    'graphs', ListOf(ReadDiskItem('Cortical folds graph', 'Graph')),
    'mri', ReadDiskItem('3D Volume', 'Aims readable volume formats'),
    'SPAM', WriteDiskItem('3D Volume', 'Aims writable volume formats'),
    'smoothing', Choice('Yes', 'No'),
    'smoothing_parameter', Float(),
    'bucket', Choice('custom', 'Sulci', 'Simple Surfaces', 'Bottoms',
                     'Junctions with brain hull'),
    'custom_buckets', String(),
    'label_translation', ReadDiskItem(
        'Label Translation', 'Label Translation'),
    'int_to_label_translation', WriteDiskItem('log file', 'log file'),
    'label_attributes', Choice('custom', '(label, name)', 'label', 'name'),
    'custom_label_attributes', String(),
    'node_edge_types', Choice('All', 'custom',
                              'Nodes (fold, cluster, roi, nucleus)',
                              'Relations (junction, cortical, etc.)'),
    'custom_node_edge_types', String(),
    'label_values', String(),
)


def initialization(self):
    self.bucket = 'Sulci'
    self.smoothing = 'Yes'
    self.label_attributes = '(label, name)'
    self.setOptional('mri')
    self.setOptional('label_translation')
    self.setOptional('int_to_label_translation')
    self.setOptional('custom_buckets')
    self.setOptional('custom_node_edge_types')
    self.setOptional('custom_label_attributes')
    self.setOptional('label_values')
    self.smoothing_parameter = 0.25


def execution(self, context):

    NbGraph = len(self.graphs)
    inc = 1
    context.write('Number of graphs: ', NbGraph)
    if NbGraph == 0:
        raise Exception(_t_('argument <em>graph</em> should not be '
                            'empty'))

    temp = context.temporary('NIFTI-1 Image')
    ok = 0
    if self.mri is not None:
        f = aims.Finder()
        f.check(self.mri.fullPath())
        hdr = f.header()
        dim = hdr['volume_dimension'][:3]
        vs = hdr['voxel_size'][:3]
    else:
        dim = [256, 256, 124]
        vs = [1., 1., 1.]
    sizes = [x * y for x, y in zip(dim, vs)]
    context.write('ref vol sizes:', sizes)
    translation = aims.AffineTransformation3d()
    translation.setTranslation([float(sizes[0])/2, float(sizes[1])/2,
                                float(sizes[2])*0.75])

    for graph in self.graphs:

        context.write('Subject : ', graph.get('subject'), '(', inc, '/',
                      NbGraph, ')')

        cmd = ['siGraph2Label', '-g', graph.fullPath()]

        # if self.mri is not None:
        #cmd += [ '-tv', self.mri.fullPath() ]

        if self.label_translation is not None:
            cmd += ['-tr', self.label_translation.fullPath()]

        if self.label_attributes == 'custom':
            if self.custom_label_attributes:
                la = self.custom_label_attributes.split()
            else:
                la = ()
        elif self.label_attributes == '(label, name)':
            la = ()
        else:
            la = (self.label_attributes, )
        for i in la:
            cmd += ['-a', i]

        if self.int_to_label_translation is not None:
            cmd += ['-ot', self.int_to_label_translation.fullPath()]

        a = ()
        if self.node_edge_types == 'custom':
            if self.custom_node_edge_types:
                a = self.custom_node_edge_types.split()
        elif self.node_edge_types == 'Nodes (fold, cluster, roi, nucleus)':
            a = ('fold', 'cluster', 'roi', 'nucleus')
        elif self.node_edge_types == 'Relations (junction, cortical, etc.)':
            a = ('junction', 'cortical', 'hull_junction', 'plidepassage',
                 'scalebloblink', 'blob_saddle_link', 'roi_junction', )
        for i in a:
            cmd += ['-s', i]

        if self.label_values:
            a = self.label_values.split()
            for i in a:
                cmd += ['-l', i]

        if self.bucket == 'custom':
            if not self.custom_buckets:
                raise Exception('<em>custom_buckets</em> must be non-empty '
                                'in custom bucket mode')
            cmd += ['-o', self.temp]
            a = self.custom_buckets.split()
            for i in a:
                cmd += ['-b', i]
        else:
            if self.bucket in ('Sulci',):
                cmd += ['-o', temp, '-b', 'aims_ss', '-b', 'aims_bottom',
                        '-b', 'aims_other']
            if self.bucket in ('Bottoms',):
                cmd += ['-o', temp, '-b', 'aims_bottom']
            if self.bucket in ('Junctions with brain hull',):
                cmd += ['-o', temp, '-b',
                        'aims_junction', '-s', 'hull_junction']
            if self.bucket in ('Simple Surfaces',):
                cmd += ['-o', temp, '-b', 'aims_ss']
        context.system(*cmd)
        context.system('AimsThreshold', '-i', temp, '-m', 'gt', '-t', '0',
                       '-b', '-o', temp)
        context.system('AimsReplaceLevel', '-i', temp, '-g', '32767', '-n', '1',
                       '-o', temp)
        # Talairach transform
        aims_graph = aims.read(graph.fullPath())
        trans = aims.GraphManip.talairach(aims_graph)
        trans = translation * trans
        temp_tr = context.temporary('Transformation matrix')
        aims.write(trans, temp_tr.fullPath())

        if ok == 0:
            context.system('AimsApplyTransform', '-i', temp,
                           '-o', self.SPAM.fullPath(), '-m', temp_tr,
                           '--dx', dim[0], '--dy', dim[1], '--dz', dim[2],
                           '--sx', vs[0], '--sy', vs[1], '--sz', vs[2],
                           '-t', 'n')
            ok = 1
        else:
            context.system('AimsApplyTransform', '-i', temp,
                           '-o', temp, '-m', temp_tr,
                           '--dx', dim[0], '--dy', dim[1], '--dz', dim[2],
                           '--sx', vs[0], '--sy', vs[1], '--sz', vs[2],
                           '-t', 'n')
            context.system('cartoLinearComb.py', '-i', temp,
                           '-i', self.SPAM.fullPath(),
                           '-f', 'I1+I2',
                           '-o', self.SPAM.fullPath())

        inc = inc + 1

    context.system('cartoLinearComb.py', '-i', self.SPAM.fullPath(),
                   '-f', 'I1 * 100. / %f' % NbGraph,
                   '-o', self.SPAM.fullPath())
    if self.smoothing == 'Yes':
        context.system('AimsFileConvert', '-i', self.SPAM.fullPath(),
                       '-o', self.SPAM.fullPath(), '-t', 'FLOAT')
        context.system('AimsImageSmoothing', '-i', self.SPAM.fullPath(),
                       '-o', self.SPAM.fullPath(),
                       '-t', self.smoothing_parameter, '-s', '0')
    res_vol = aims.read(self.SPAM.fullPath())
    res_vol.header()['referentials'] \
        = [aims.StandardReferentials.acPcReferentialID()]
    res_vol.header()['transformations'] \
        = [list(translation.inverse().toVector())]
    aims.write(res_vol, self.SPAM.fullPath())
