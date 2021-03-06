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

name = 'AC/PC Or Normalization'
userLevel = 0

signature = Signature(
    'T1mri', ReadDiskItem("Raw T1 MRI", 'aims readable Volume Formats'),
    'commissure_coordinates', WriteDiskItem('Commissure coordinates',
                                            'Commissure coordinates'),
    'allow_flip_initial_MRI', Boolean(),
    'reoriented_t1mri', WriteDiskItem('Raw T1 MRI',
                                      'aims writable volume formats'),
)


def initialization(self):
    try:
        ps = getProcess('preparesubject')
    except:
        ps = None
    try:
        np = getProcess('normalizationPipeline')
        np.validationDelayed()
    except:
        np = None

    self.allow_flip_initial_MRI = False

    eNode = SelectionExecutionNode(self.name, parameterized=self)

    # for "future" pipelines
    self.selection_outputs = []
    self.switch_output = ['commissure_coordinates', 'reoriented_t1mri',
                          'talairach_transformation']

    if ps:
        if np:
            sel = 0
        else:
            sel = 1
        eNode.addChild('StandardACPC',
                       ProcessExecutionNode(ps, selected=sel))
        self.selection_outputs.append(['commissure_coordinates',
                                       'reoriented_t1mri', None])

        eNode.addDoubleLink('StandardACPC.T1mri', 'T1mri')
        eNode.addDoubleLink('StandardACPC.commissure_coordinates',
                            'commissure_coordinates')
        eNode.addDoubleLink('StandardACPC.allow_flip_initial_MRI',
                            'allow_flip_initial_MRI')
        eNode.addDoubleLink('reoriented_t1mri',
                            'StandardACPC.reoriented_t1mri')

    if np:
        eNode1 = SerialExecutionNode('Normalization', selected=1)
        eNode1.addChild('Normalization',
                        ProcessExecutionNode(np))
        eNode1.addChild('TalairachFromNormalization',
                        ProcessExecutionNode('TalairachTransformationFromNormalization'))
        eNode.addChild('Normalization', eNode1)

        # eNode1.Normalization.removeLink( 'commissures_coordinates', 't1mri' )
        # eNode1.addDoubleLink( 'Normalization.commissures_coordinates',
        #   'TalairachFromNormalization.commissure_coordinates' )
        self.selection_outputs.append([
            'TalairachFromNormalization.commissure_coordinates',
            'Normalization.reoriented_t1mri',
            'TalairachFromNormalization.Talairach_transform'])

        eNode.addDoubleLink('Normalization.Normalization.t1mri', 'T1mri')
        eNode.addDoubleLink('Normalization.Normalization.allow_flip_initial_MRI',
                            'allow_flip_initial_MRI')
        eNode.addDoubleLink('reoriented_t1mri',
                            'Normalization.Normalization.reoriented_t1mri')

        if ps:
            eNode1.TalairachFromNormalization.removeLink('commissure_coordinates',
                                                         'Talairach_transform')
        eNode1.TalairachFromNormalization.removeLink('t1mri',
                                                     'commissure_coordinates')

        eNode.addDoubleLink('Normalization.Normalization.reoriented_t1mri',
                            'Normalization.TalairachFromNormalization.t1mri')
        eNode.addDoubleLink(
            'Normalization.TalairachFromNormalization.normalization_transformation',
            'Normalization.Normalization.transformation')
        eNode.addDoubleLink(
            'Normalization.TalairachFromNormalization.commissure_coordinates',
            'commissure_coordinates')

    self.setExecutionNode(eNode)

    self.capsul_do_not_export = [
        ('Normalization', 'output_commissures_coordinates'), ]
