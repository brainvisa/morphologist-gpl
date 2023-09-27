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


name = 'Anatomy Normalization (using AimsMIRegister)'
userLevel = 2

signature = Signature(
    'anatomy_data', ReadDiskItem("Raw T1 MRI", 'aims readable volume formats'),
    'anatomical_template', ReadDiskItem("anatomical Template",
                                        'aims readable volume formats'),
    'transformation_to_template', WriteDiskItem("Transformation matrix",
                                                'Transformation matrix'),
    'normalized_anatomy_data', WriteDiskItem("Raw T1 MRI",
                                             'aims writable volume formats'),
    'transformation_to_MNI', WriteDiskItem(
        "Transform Raw T1 MRI to Talairach-MNI template-SPM",
        'Transformation matrix'),
    'transformation_to_ACPC', WriteDiskItem(
        "Transform Raw T1 MRI to Talairach-AC/PC-Anatomist",
        'Transformation matrix'),
    'mni_to_acpc', ReadDiskItem("Transformation matrix",
                                'Transformation matrix'),
    'smoothing', Float(),
)


capsul_param_options = {
    'anatomical_template': ['dataset="shared"'],
    'mni_to_acpc': ['dataset="shared"'],
}


def initialization(self):
    def anat2results(self, process):
        if self.anatomy_data != None:
            process.signature["normalized_anatomy_data"].requiredAttributes["normalized"] = "yes"
            process.signature["normalized_anatomy_data"].requiredAttributes["normalization"] = "AimsMIRegister"
        return self.anatomy_data
    self.linkParameters("transformation_to_template", "anatomy_data")
    self.linkParameters("normalized_anatomy_data",
                        "anatomy_data", anat2results)
    self.linkParameters("transformation_to_MNI", "anatomy_data")
    self.linkParameters("transformation_to_ACPC", "anatomy_data")
    tplval = {'skull_stripped': 'no', 'Size': '2 mm'}
    if len(neuroHierarchy.databases._databases) != 0:
        tplval['_database'] = list(neuroHierarchy.databases._databases.keys())[0]
    self.anatomical_template = self.signature['anatomical_template'].findValue(
        tplval)
    try:
        self.mni_to_acpc = neuroHierarchy.databases.getDiskItemFromUuid(
            '9b26135b-e608-041a-9e2c-d66043f797cc')
    except:
        self.mni_to_acpc = None
    self.smoothing = 1.
    self.setOptional('normalized_anatomy_data')
    self.setOptional('transformation_to_template')
    self.setOptional('transformation_to_MNI')
    self.setOptional('transformation_to_ACPC')
    self.setOptional('mni_to_acpc')


def execution(self, context):
    smoothanat = self.anatomy_data
    if self.smoothing != 0:
        context.write('smoothing anatomy_data...')
        smoothanat = context.temporary('GIS image')
        context.system('AimsGaussianSmoothing', '-i', self.anatomy_data,
                       '-o', smoothanat, '-x', self.smoothing, '-y', self.smoothing,
                       '-z', self.smoothing)
    invtrans = context.temporary('Transformation matrix')
    if self.transformation_to_template is None:
        totemplate = context.temporary('Transformation matrix')
    else:
        totemplate = self.transformation_to_template
    context.write('Registering to the template...')
    context.runProcess('Register3DMutualInformation',
                       source_image=smoothanat, reference_image=self.anatomical_template,
                       source_to_reference=totemplate,
                       reference_to_source=invtrans,
                       resampled_image=self.normalized_anatomy_data)
    context.write('Managing transformations chain...')
    tm = registration.getTransformationManager()
    tomni = self.transformation_to_MNI
    if self.transformation_to_ACPC is not None and tomni is None:
        tomni = context.temporary('Transformation matrix')
    if tomni is not None:
        atts = aimsGlobals.aimsVolumeAttributes(self.anatomical_template)
        trs = atts.get('transformations')
        if not trs:
            raise ValueError('The template has no transformation information.')
        tplToMni = aims.AffineTransformation3d(trs[-1])
        anatToTpl = aims.read(totemplate.fullPath())
        anatToMni = tplToMni * anatToTpl
        aims.write(anatToMni, tomni.fullPath())
        tm.setNewTransformationInfo(tomni, source_referential=self.anatomy_data,
                                    destination_referential=tm.referential(
                                        registration.talairachMNIReferentialId),
                                    description='Normalized using AimsMIRegister')
        if self.transformation_to_ACPC is not None \
                and self.mni_to_acpc is not None:
            acpcToMni = aims.read(self.mni_to_acpc.fullPath())
            anattoAcpc = acpcToMni.inverse() * anatToMni
            aims.write(anattoAcpc, self.transformation_to_ACPC.fullPath())
            tm.setNewTransformationInfo(self.transformation_to_ACPC,
                                        source_referential=self.anatomy_data,
                                        destination_referential=tm.referential(
                                            registration.talairachACPCReferentialId),
                                        description='Normalized using AimsMIRegister')
    if self.transformation_to_template is not None:
        tm.setNewTransformationInfo(self.transformation_to_template,
                                    source_referential=self.anatomy_data,
                                    destination_referential=self.anatomical_template,
                                    description='Normalized using AimsMIRegister')
    if self.normalized_anatomy_data is not None:
        tm.copyReferential(self.anatomical_template,
                           self.normalized_anatomy_data)
    context.write('done.')
