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

include('base')
include('anatomy')


insert('{center}/{subject}',
    'volBrain', SetWeakAttr('processing', 'volBrain'), SetContent(
        '{acquisition}', SetType('Acquisition'),
        SetDefaultAttributeValue('acquisition', default_acquisition), SetContent(
            'native', SetWeakAttr('space', 'native'), SetContent(
                '<subject>_native_crisp', SetType('T1 MRI intracranial labels'),
                '<subject>_native_hemi', SetType('Split Brain Mask'),
                '<subject>_native_lab', SetType('Subcortical labels'),
                '<subject>_native_mask', SetType('Intracranial mask'),
                '<subject>_native_filtered', SetType('T1 MRI Denoised'),
                '<subject>_native_normalised', SetType('T1 MRI Denoised and Bias Corrected'),
                '<subject>_native_readme', SetType('Text file'),
            ),
            'mni', SetWeakAttr('space', 'mni'), SetContent(
                '<subject>_mni_crisp', SetType('T1 MRI intracranial labels'),
                '<subject>_mni_hemi', SetType('Split Brain Mask'),
                '<subject>_mni_lab', SetType('Subcortical labels'),
                '<subject>_mni_mask', SetType('Intracranial mask'),
                '<subject>_mni_csf', SetType('T1 MRI tissue probability map'),
                SetWeakAttr('tissue_class', 'csf'),
                '<subject>_mni_gm', SetType('T1 MRI tissue probability map'),
                SetWeakAttr('tissue_class', 'grey'),
                '<subject>_mni_wm', SetType('T1 MRI tissue probability map'),
                SetWeakAttr('tissue_class', 'white'),
                '<subject>_mni_normalised', SetType('T1 MRI Denoised and Bias Corrected'),
                '<subject>_mni_readme', SetType('Text file'),
                '<subject>_affine_transformation', SetType('Transformation'),
            ),
            '<subject>_report', SetType('Text file'),
        ),
    ),
)