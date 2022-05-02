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
from brainvisa.tools import aimsGlobals
from brainvisa import registration
import os
from soma.wip.application.api import Application


def validation():
    configuration = Application().configuration
    import distutils.spawn
    if not distutils.spawn.find_executable(
            configuration.FSL.fsl_commands_prefix + 'flirt'):
        raise ValidationError(_t_('FSL flirt commandline could not be found'))


name = 'Anatomy Normalization (using FSL)'
userLevel = 2

# copied from fmri python/neurospy/bvfunc/FSL_pre_processing.py


def NormalizeAnat(context, anat, templatet1, normAnat, norm_matrix,
                  searcht1="NASO", cost='corratio', searchcost='corratio'):
    """
    Form the normalization of anatomical images using FSL
    """
    if searcht1 == "AVA":
        s1 = ["-searchrx", '-0', '0', '-searchry', '-0', '0', '-searchrz',
              '-0', "0"]
    elif (searcht1 == "NASO"):
        s1 = ["-searchrx", -90, 90, '-searchry', -90, 90, '-searchrz',
              -90, 90]
    elif (searcht1 == "IO"):
        s1 = ["-searchrx", -180, 180, '-searchry', -180, 180, '-searchrz',
              -180, 180]
    else:
        s1 = []
    if normAnat is not None:
        s1 += ['-out', normAnat]
    configuration = Application().configuration
    cmd = [configuration.FSL.fsl_commands_prefix + 'flirt',
           '-in', anat, '-ref', templatet1, '-omat', norm_matrix, '-bins', 1024,
           '-cost', cost, '-searchcost', searchcost] + s1 + ['-dof', 12]
    context.system(*cmd)


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
    self.linkParameters("normalized_anatomy_data", "anatomy_data")
    self.Alignment = 'Not Aligned but Same Orientation'
    self.anatomical_template = self.signature['anatomical_template'].findValue(
        {'database': os.path.join(os.getenv('FSLDIR', 'data')),
         'skull_stripped': 'no'})
    self.cost_function = 'corratio'
    self.search_cost_function = 'corratio'
    self.linkParameters("search_cost_function", "cost_function")


def execution(self, context):
    anat = self.anatomy_data.fullPath()
    template = self.anatomical_template.fullPath()
    snmat = self.transformation_matrix.fullPath()
    normanat = self.normalized_anatomy_data.fullPath()
    if self.Alignment == 'Already Virtually Aligned':
        s1 = 'AVA'
    elif self.Alignment == 'Not Aligned but Same Orientation':
        s1 = 'NASO'
    elif self.Alignment == 'Incorrectly Oriented':
        s1 = 'IO'
    NormalizeAnat(context, anat, template, normanat, snmat, s1,
                  cost=self.cost_function, searchcost=self.search_cost_function)
    # get image orientations in current formats
    srcatts = aimsGlobals.aimsVolumeAttributes(self.anatomy_data)
    srcs2m = srcatts.get('storage_to_memory', None)
    if srcs2m:
        self.transformation_matrix.setMinf('source_storage_to_memory', srcs2m)
    dstatts = aimsGlobals.aimsVolumeAttributes(self.anatomical_template)
    dsts2m = dstatts.get('storage_to_memory', None)
    if dsts2m:
        self.transformation_matrix.setMinf('destination_storage_to_memory',
                                           dsts2m)
    self.transformation_matrix.saveMinf()
    tm = registration.getTransformationManager()
    tm.copyReferential(self.anatomical_template, self.normalized_anatomy_data)
