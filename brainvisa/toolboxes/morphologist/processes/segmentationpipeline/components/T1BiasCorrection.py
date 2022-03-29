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
from brainvisa import registration

name = 'T1 Bias Correction'
userLevel = 0

signature = Signature(
    't1mri', ReadDiskItem('Raw T1 MRI', 'Aims readable volume formats'),
    'commissure_coordinates', ReadDiskItem('Commissure coordinates',
                                           'Commissure coordinates'),
    'sampling', Float(),
    'field_rigidity', Float(),
    'zdir_multiply_regul', Float(),
    'wridges_weight', Float(),
    'ngrid', Integer(),
    'background_threshold_auto', Choice('no',
                                        ('c', 'corners'),
                                        ('o', 'otsu')),
    'delete_last_n_slices', OpenChoice(
        'auto (AC/PC Points needed)', '0', '10', '20', '30'),
    't1mri_nobias', WriteDiskItem('T1 MRI Bias Corrected',
                                  'Aims writable volume formats'),
    'mode', Choice('write_minimal', 'write_all',
                   'delete_useless', 'write_minimal without correction'),
    'write_field', Choice('yes', 'no'),
    'field', WriteDiskItem('T1 MRI Bias Field',
                           'Aims writable volume formats'),
    'write_hfiltered', Choice('yes', 'no'),
    'hfiltered', WriteDiskItem('T1 MRI Filtered For Histo',
                               'Aims writable volume formats'),
    'write_wridges', Choice('yes', 'no', 'read'),
    'white_ridges', WriteDiskItem('T1 MRI White Matter Ridges',
                                  'Aims writable volume formats', exactType=1),
    'variance_fraction', Integer(),
    'write_variance', Choice('yes', 'no'),
    'variance', WriteDiskItem('T1 MRI Variance',
                              'Aims writable volume formats'),
    'edge_mask', Choice('yes', 'no'),
    'write_edges', Choice('yes', 'no'),
    'edges', WriteDiskItem('T1 MRI Edges',
                           'Aims writable volume formats'),
    'write_meancurvature', Choice('yes', 'no'),
    'meancurvature', WriteDiskItem('T1 MRI Mean Curvature',
                                   'Aims writable volume formats'),
    'fix_random_seed', Boolean(),
    'modality', Choice('T1', 'T2'),
    'use_existing_ridges', Boolean(),
)


def change_wridges_io(self, use_existing_ridges):
    if use_existing_ridges:
        self.signature['white_ridges'] = ReadDiskItem(
            'T1 MRI White Matter Ridges',
            'Aims writable volume formats', exactType=1)
    else:
        self.signature['white_ridges'] = WriteDiskItem(
            'T1 MRI White Matter Ridges',
            'Aims writable volume formats', exactType=1)
    self.changeSignature(self.signature)


# Default values
def initialization(self):
    self.linkParameters('commissure_coordinates', 't1mri')
    self.linkParameters('t1mri_nobias', 't1mri')
    self.linkParameters('field', 't1mri_nobias')
    self.linkParameters('hfiltered', 'field')
    self.linkParameters('white_ridges', 'hfiltered')
    self.linkParameters('variance', 'white_ridges')
    self.linkParameters('edges', 'variance')
    self.linkParameters('meancurvature', 'edges')
    self.setOptional('commissure_coordinates')
    self.setOptional('field')
    self.setOptional('meancurvature')

    self.signature['ngrid'].userLevel = 2
    self.signature['zdir_multiply_regul'].userLevel = 2
    self.signature['variance_fraction'].userLevel = 2
    self.signature['fix_random_seed'].userLevel = 3

    self.mode = 'write_minimal'
    self.write_wridges = 'yes'
    self.write_field = 'no'
    self.write_hfiltered = 'yes'
    self.write_variance = 'yes'
    self.write_edges = 'yes'
    self.write_meancurvature = 'no'
    self.field_rigidity = 20
    self.wridges_weight = 20.
    self.sampling = 16
    self.ngrid = 2
    self.zdir_multiply_regul = 0.5
    self.variance_fraction = 75
    self.background_threshold_auto = 'c'
    self.edge_mask = 'yes'
    self.delete_last_n_slices = 'auto (AC/PC Points needed)'
    self.fix_random_seed = False
    self.modality = 'T1'
    self.use_existing_ridges = False
    # self.linkParameters('white_ridges', 'use_existing_ridges',
    # change_wridges_io)
    self.addLink(None, 'use_existing_ridges', self.change_wridges_io)


def execution(self, context):
    if self.mode == 'write_all':
        self.write_wridges = 'yes'
        self.write_field = 'yes'
        self.write_hfiltered = 'yes'
        self.write_variance = 'yes'
        self.write_meancurvature = 'yes'
        self.write_edges = 'yes'
    if self.edge_mask == 'yes':
        edge = '3'
    else:
        edge = 'n'
    if self.mode in ('write_minimal', 'write_all', 'write_minimal without correction'):
        if os.path.exists(self.t1mri_nobias.fullName() + '.loc'):
            context.write(self.t1mri_nobias.fullName(), ' has been locked')
            context.write('Remove', self.t1mri_nobias.fullName(),
                          '.loc if you want to trigger a new correction')
        else:
            command = ['VipT1BiasCorrection', '-i', self.t1mri,
                       '-o', self.t1mri_nobias,
                       '-Fwrite', self.write_field,
                       '-field', self.field,
                       '-wridge', self.white_ridges,
                       '-Kregul', self.field_rigidity,
                       '-sampling', self.sampling,
                       '-Kcrest', self.wridges_weight,
                       '-Grid', self.ngrid,
                       '-ZregulTuning', self.zdir_multiply_regul,
                       '-vp', self.variance_fraction,
                       '-e', edge,
                       '-eWrite', self.write_edges,
                       '-ename', self.edges,
                       '-vWrite', self.write_variance,
                       '-vname', self.variance,
                       '-mWrite', self.write_meancurvature,
                       '-mname', self.meancurvature,
                       '-hWrite', self.write_hfiltered,
                       '-hname', self.hfiltered,
                       '-Last', self.delete_last_n_slices,
                       '-Cw', self.modality,
                       '-tauto', self.background_threshold_auto]
            if self.commissure_coordinates is not None:
                command += ['-Points', self.commissure_coordinates]
            if self.mode == 'write_minimal without correction':
                command += ['-Dcorrect', 'n']
            if self.fix_random_seed:
                command += ['-srand', '10']
            if self.use_existing_ridges:
                command += ['-Wwrite', 'r']
            else:
                command += ['-Wwrite', self.write_wridges]

            context.system(*command)

            tm = registration.getTransformationManager()
            tm.copyReferential(self.t1mri, self.t1mri_nobias)
            if self.write_field:
                tm.copyReferential(self.t1mri, self.field)
            if self.write_hfiltered:
                tm.copyReferential(self.t1mri, self.hfiltered)
            if self.write_wridges:
                tm.copyReferential(self.t1mri, self.white_ridges)
            if self.write_variance:
                tm.copyReferential(self.t1mri, self.variance)
            if self.write_edges:
                tm.copyReferential(self.t1mri, self.edges)
            if self.write_meancurvature:
                tm.copyReferential(self.t1mri, self.meancurvature)

    elif self.mode == 'delete_useless':
        if os.path.exists(self.field.fullName() + '.ima') or os.path.exists(self.field.fullName() + '.ima.gz'):
            shelltools.rm(self.field.fullName() + '.*')
        if os.path.exists(self.variance.fullName() + '.ima') or os.path.exists(self.variance.fullName() + '.ima.gz'):
            shelltools.rm(self.variance.fullName() + '.*')
        if os.path.exists(self.edges.fullName() + '.ima') or os.path.exists(self.edges.fullName() + '.ima.gz'):
            shelltools.rm(self.edges.fullName() + '.*')
        if os.path.exists(self.meancurvature.fullName() + '.ima') or os.path.exists(self.meancurvature.fullName() + '.ima.gz'):
            shelltools.rm(self.meancurvature.fullName() + '.*')
