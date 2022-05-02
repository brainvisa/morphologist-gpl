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
import os
from soma.wip.application.api import Application


def validation():
    configuration = Application().configuration
    import distutils.spawn
    if not distutils.spawn.find_executable(
            configuration.FSL.fsl_commands_prefix + 'flirt'):
        raise ValidationError(_t_('FSL flirt commandline could not be found'))


name = 'Anatomy Normalization (using FSL) with Re-initialization'
userLevel = 0

signature = Signature(
    'anatomy_data', ReadDiskItem(
        "Raw T1 MRI", ['NIFTI-1 image', 'gz compressed NIFTI-1 image']),
    'anatomical_template', ReadDiskItem(
        "anatomical Template", ['NIFTI-1 image', 'gz compressed NIFTI-1 image']),
    'Alignment', Choice('Already Virtually Aligned',
                        'Not Aligned but Same Orientation', 'Incorrectly Oriented'),
    'transformation_matrix', WriteDiskItem(
        "FSL Transformation", 'Matlab file'),
    'normalized_anatomy_data', WriteDiskItem(
        "Raw T1 MRI", ['gz compressed NIFTI-1 image']),
    'cost_function', Choice(('Correlation ration', 'corratio'),
                            ('Mutual information', 'mutualinfo'),
                            'normcorr', 'normmi', ('Least square', 'leastsq'), 'labeldiff'),
    'search_cost_function', Choice(('Correlation ration', 'corratio'),
                                   ('Mutual information', 'mutualinfo'),
                                   'normcorr', 'normmi', ('Least square', 'leastsq'), 'labeldiff'),
    'allow_retry_initialization', Boolean(),
    'init_translation_origin', Choice(
        ('Center of the image', 0), ('Gravity center', 1)),
)


def initialization(self):
    def anat2results(self, process):
        if self.anatomy_data != None:
            process.signature["normalized_anatomy_data"].requiredAttributes["normalized"] = "yes"
            process.signature["normalized_anatomy_data"].requiredAttributes["normalization"] = "FSL"
        return self.anatomy_data
    self.linkParameters("transformation_matrix", "anatomy_data")
    self.linkParameters("normalized_anatomy_data",
                        "anatomy_data", anat2results)
    #self.linkParameters("normalized_anatomy_data", "anatomy_data")
    self.Alignment = 'Not Aligned but Same Orientation'
    self.anatomical_template = self.signature['anatomical_template'].findValue(
        {'database': os.path.join(os.getenv('FSLDIR', 'data')),
         'skull_stripped': 'no'})
    self.cost_function = 'corratio'
    self.search_cost_function = 'corratio'
    self.linkParameters("search_cost_function", "cost_function")
    self.allow_retry_initialization = False


def execution(self, context):
    context.write(_t_('Trying 1st pass of normalization...'))
    if os.path.exists(self.transformation_matrix.fullPath()):
        os.unlink(self.transformation_matrix.fullPath())
    failed = False
    normproc = {'anatomy_data': self.anatomy_data,
                'anatomical_template': self.anatomical_template,
                'Alignment': self.Alignment,
                'transformation_matrix': self.transformation_matrix,
                'normalized_anatomy_data': self.normalized_anatomy_data,
                'cost_function': self.cost_function,
                'search_cost_function': self.search_cost_function,
                }
    try:
        context.runProcess('Normalization_FSL', **normproc)
        if not os.path.exists(self.transformation_matrix.fullPath()):
            failed = True
    except:
        failed = True
        if not self.allow_retry_initialization:
            raise
    if failed:
        context.write(
            _t_('1st pass failed, changing internal transformation initialization'))
        if not self.allow_retry_initialization:
            raise RuntimeError('Normalization failed')
        context.runProcess('resetInternalImageTransformation',
                           input_image=self.anatomy_data, output_image=self.anatomy_data,
                           origin=self.init_translation_origin)
        context.write(
            _t_('Retrying normalization after changing initialization...'))
        context.runProcess('Normalization_FSL', **normproc)
