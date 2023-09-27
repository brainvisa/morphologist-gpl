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
from brainvisa.validation import ValidationError
from soma.wip.application.api import Application

import os.path


configuration = Application().configuration


def validation():
    try:
        from soma.spm.spm_launcher import SPM8, SPM8Standalone
    except ImportError:
        raise ValidationError('The SPM toolbox for BrainVISA is not available')
    try:
        spm = SPM8Standalone(configuration.SPM.spm8_standalone_command,
                             configuration.SPM.spm8_standalone_mcr_path,
                             configuration.SPM.spm8_standalone_path)
    except:
        spm = SPM8(configuration.SPM.spm8_path,
                   configuration.matlab.executable,
                   configuration.matlab.options)


name = 'Anatomy Normalization (using SPM8)'
userLevel = 2

signature = Signature(
    'anatomy_data', ReadDiskItem("Raw T1 MRI", ['NIFTI-1 image', 'SPM image']),
    'anatomical_template', ReadDiskItem("anatomical Template",
                                        ['NIFTI-1 image', 'MINC image',
                                         'SPM image']),
    'voxel_size', Choice('[1 1 1]'),
    'cutoff_option', Integer(),
    'nbiteration', Integer(),
    'transformations_informations', WriteDiskItem("SPM2 normalization matrix",
                                                  'Matlab file'),
    'normalized_anatomy_data', WriteDiskItem("Raw T1 MRI",
                                             ['NIFTI-1 image', 'SPM image'],
                                             {"normalization": "SPM"})
)


capsul_param_options = {
    'anatomical_template': ['dataset="shared"'],
}


def initialization(self):
    configuration.SPM.spm8_path  # trigger the spmpathcheck process if needed
    self.linkParameters("transformations_informations", "anatomy_data")
    self.linkParameters("normalized_anatomy_data", "anatomy_data")
    self.voxel_size = "[1 1 1]"
    self.cutoff_option = "25"
    self.nbiteration = 16
    self.setOptional("anatomical_template")
    # Link parameters
    self.anatomical_template = self.signature['anatomical_template'].findValue({'databasename': 'spm',
                                                                                'skull_stripped': 'no'})


def execution(self, context):
    vs = [float(x) for x in self.voxel_size[1:-1].split(' ')]
    # The directory containing the batch-file is used as working directory for
    # SPM; by allocating a temporary directory instead of a temporary Matlab
    # script we ensure that the working directory will be different for each
    # run (this avoids clobbering intermediate results during parallel runs).
    tmpdir = context.temporary('Directory')
    matfile_path = os.path.join(tmpdir.fullPath(), "batch.m")
    # we must instantiate SPM8NormaliseEandW_generic and change the type of
    # its sn_mat parameter
    p = getProcessInstance('SPM8NormaliseEandW_generic')
    p.signature['sn_mat'] = self.signature['transformations_informations']
    context.runProcess(p,
                       source=self.anatomy_data,
                       images_to_write=[self.anatomy_data],
                       template=self.anatomical_template,
                       frequency_cutoff=self.cutoff_option,
                       iterations=self.nbiteration,
                       voxel_size=vs,
                       images_written=[self.normalized_anatomy_data],
                       sn_mat=self.transformations_informations,
                       batch_location=matfile_path)
