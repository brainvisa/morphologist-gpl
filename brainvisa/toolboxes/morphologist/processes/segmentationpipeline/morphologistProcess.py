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
from six.moves import zip


name = 'Simplified Morphologist 2015'
userLevel = 0

signature = Signature(
    't1mri', ReadDiskItem(
        'Raw T1 MRI',
        'Aims readable volume formats'),
    'perform_segmentation', Boolean(),
    'perform_bias_correction', Boolean(),

    # Commissures Coordinates
    'method_ACPC', Choice('Manually',
                          'With SPM12 Normalization',
                          'Already done'),
    'commissure_coordinates', WriteDiskItem(
        'Commissure coordinates',
        'Commissure coordinates'),
    'anterior_commissure', Point3D(),
    'posterior_commissure', Point3D(),
    'interhemispheric_point', Point3D(),
    'left_hemisphere_point', Point3D(),
    'older_MNI_normalization', ReadDiskItem(
        'Transform Raw T1 MRI to Talairach-MNI template-SPM',
        'Transformation matrix'),
    # SPM Normalization
    'anatomical_template', ReadDiskItem(
        'anatomical Template',
        ['NIFTI-1 image', 'MINC image', 'SPM image']),
    #'job_file', WriteDiskItem( 'SPM2 parameters', 'Matlab file' ),
    'transformations_information', WriteDiskItem(
        'SPM2 normalization matrix',
        'Matlab file'),
    'normalized_t1mri', WriteDiskItem(
        'Raw T1 MRI',
        ['NIFTI-1 image', 'SPM image'], {'normalization': 'SPM'}),
    'talairach_MNI_transform', WriteDiskItem(
        'Transform Raw T1 MRI to Talairach-MNI template-SPM',
        'Transformation matrix', ),
    # Talairach Transformation
    'source_referential', ReadDiskItem(
        'Referential of Raw T1 MRI', 'Referential'),
    'normalized_referential', ReadDiskItem('Referential', 'Referential'),
    'tal_to_normalized_transform', ListOf(ReadDiskItem('Transformation',
                                                       'Transformation matrix')),
    # Bias Correction
    't1mri_nobias', WriteDiskItem('T1 MRI Bias Corrected',
                                  'Aims writable volume formats'),
    'hfiltered', WriteDiskItem('T1 MRI Filtered For Histo',
                               'Aims writable volume formats'),
    'white_ridges', WriteDiskItem('T1 MRI White Matter Ridges',
                                  'Aims writable volume formats', exactType=1),
    'variance', WriteDiskItem('T1 MRI Variance',
                              'Aims writable volume formats'),
    'edges', WriteDiskItem('T1 MRI Edges',
                           'Aims writable volume formats'),
    'field', WriteDiskItem('T1 MRI Bias Field',
                           'Aims writable volume formats'),
    'meancurvature', WriteDiskItem('T1 MRI Mean Curvature',
                                   'Aims writable volume formats'),
    # Histogram Analysis
    'histo_analysis', WriteDiskItem('Histo Analysis',
                                    'Histo Analysis'),
    'histo', WriteDiskItem('Histogram',
                           'Histogram'),
    # Brain Mask Segmentation
    'brain_mask', WriteDiskItem('T1 Brain Mask',
                                'Aims writable volume formats'),
    # Re Commissures Coordinates
    'skull_stripped', WriteDiskItem('Raw T1 MRI Brain Masked',
                                    'Aims writable volume formats'),
    'anatomical_template_skull_stripped', ReadDiskItem('anatomical Template',
                                                       ['NIFTI-1 image', 'MINC image', 'SPM image'], requiredAttributes={'skull_stripped': 'yes'}),
    # Split Brain Mask
    'split_brain', WriteDiskItem('Split Brain Mask',
                                 'Aims writable volume formats'),
    'split_template', ReadDiskItem('Hemispheres Template',
                                   'Aims readable volume formats'),
    # Talairach Transformation
    'talairach_ACPC_transform', WriteDiskItem('Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
                                              'Transformation matrix'),
    # Grey/White Classification
    'left_grey_white', WriteDiskItem('Left Grey White Mask',
                                     'Aims writable volume formats'),
    'right_grey_white', WriteDiskItem('Right Grey White Mask',
                                      'Aims writable volume formats'),
    # Grey/White Topology
    'perform_meshes_and_graphs', Boolean(),
    'left_hemi_cortex', WriteDiskItem('Left CSF+GREY Mask',
                                      'Aims writable volume formats'),
    'right_hemi_cortex', WriteDiskItem('Right CSF+GREY Mask',
                                       'Aims writable volume formats'),
    # Grey/White Mesh
    'left_white_mesh', WriteDiskItem('Left Hemisphere White Mesh',
                                     'Aims mesh formats'),
    'right_white_mesh', WriteDiskItem('Right Hemisphere White Mesh',
                                      'Aims mesh formats'),
    # Sulci Skeleton
    'left_skeleton', WriteDiskItem('Left Cortex Skeleton',
                                   'Aims writable volume formats'),
    'left_roots', WriteDiskItem('Left Cortex Catchment Bassins',
                                'Aims writable volume formats'),
    'right_skeleton', WriteDiskItem('Right Cortex Skeleton',
                                    'Aims writable volume formats'),
    'right_roots', WriteDiskItem('Right Cortex Catchment Bassins',
                                 'Aims writable volume formats'),
    # Pial Mesh
    'left_pial_mesh', WriteDiskItem('Left Hemisphere Mesh',
                                    'Aims mesh formats'),
    'right_pial_mesh', WriteDiskItem('Right Hemisphere Mesh',
                                     'Aims mesh formats'),
    # Cortical Folds Graph
    # Left
    'left_graph', WriteDiskItem('Cortical folds graph',
                                'Graph', requiredAttributes={'side': 'left', 'labelled': 'No', 'graph_version': '3.1'}),
    'left_sulci_voronoi', WriteDiskItem('Sulci Voronoi',
                                        'Aims writable volume formats', requiredAttributes={'side': 'left'}),
    'left_cortex_mid_interface', WriteDiskItem('Grey White Mid-Interface Volume',
                                               'Aims writable volume formats', requiredAttributes={'side': 'left'}),
    # Right
    'right_graph', WriteDiskItem('Cortical folds graph',
                                 'Graph', requiredAttributes={'side': 'right', 'labelled': 'No', 'graph_version': '3.1'}),
    'right_sulci_voronoi', WriteDiskItem('Sulci Voronoi',
                                         'Aims writable volume formats', requiredAttributes={'side': 'right'}),
    'right_cortex_mid_interface', WriteDiskItem('Grey White Mid-Interface Volume',
                                                'Aims writable volume formats', requiredAttributes={'side': 'right'}),
    # Sulci Recognition
    'perform_sulci_recognition', Choice('No',
                                        'SPAM',
                                        'DeepCNN'),
    'labels_translation_map', ReadDiskItem('Label Translation',
                                           ['Label Translation', 'DEF Label translation']),
    # Left
    'left_labelled_graph', WriteDiskItem('Labelled Cortical folds graph',
                                         'Graph and data', requiredAttributes={'side': 'left', 'labelled': 'Yes', 'automatically_labelled': 'Yes'}),
    'left_posterior_probabilities', WriteDiskItem('Sulci Labels Segmentwise Posterior Probabilities',
                                                  'CSV file', requiredAttributes={'side': 'left'}),
    'left_labels_priors', ReadDiskItem('Sulci Labels Priors',
                                       'Text Data Table', requiredAttributes={'side': 'left'}),
    'left_model_file', ReadDiskItem('Any Type', 'mdsm file'),
    'left_param_file', ReadDiskItem('Any Type', 'JSON file'),
    # Global
    'left_global_model', ReadDiskItem('Sulci Segments Model',
                                      'Text Data Table', requiredAttributes={'side': 'left'}),
    'left_tal_to_global_transform', WriteDiskItem('Sulci Talairach to Global SPAM transformation',
                                                  'Transformation matrix', requiredAttributes={'side': 'left'}),
    'left_t1_to_global_transform', WriteDiskItem('Raw T1 to Global SPAM transformation',
                                                 'Transformation matrix', requiredAttributes={'side': 'left'}),
    # Local
    'left_local_model', ReadDiskItem('Sulci Segments Model',
                                     'Text Data Table', requiredAttributes={'side': 'left'}),
    'left_local_referentials', ReadDiskItem('Sulci Local referentials',
                                            'Text Data Table', requiredAttributes={'side': 'left'}),
    'left_direction_priors', ReadDiskItem('Sulci Direction Transformation Priors',
                                          'Text Data Table', requiredAttributes={'side': 'left'}),
    'left_angle_priors', ReadDiskItem('Sulci Angle Transformation Priors',
                                      'Text Data Table', requiredAttributes={'side': 'left'}),
    'left_translation_priors', ReadDiskItem('Sulci Translation Transformation Priors',
                                            'Text Data Table', requiredAttributes={'side': 'left'}),
    'left_global_to_local_transforms', WriteDiskItem('Sulci Local SPAM transformations Directory',
                                                     'Directory', requiredAttributes={'side': 'left'}),
    # Right
    'right_labelled_graph', WriteDiskItem('Labelled Cortical folds graph',
                                          'Graph and data', requiredAttributes={'side': 'right', 'labelled': 'Yes', 'automatically_labelled': 'Yes'}),
    'right_posterior_probabilities', WriteDiskItem('Sulci Labels Segmentwise Posterior Probabilities',
                                                   'CSV file', requiredAttributes={'side': 'right'}),
    'right_labels_priors', ReadDiskItem('Sulci Labels Priors',
                                        'Text Data Table', requiredAttributes={'side': 'right'}),
    'right_model_file', ReadDiskItem('Any Type', 'mdsm file'),
    'right_param_file', ReadDiskItem('Any Type', 'JSON file'),
    # Global
    'right_global_model', ReadDiskItem('Sulci Segments Model',
                                       'Text Data Table', requiredAttributes={'side': 'right'}),
    'right_tal_to_global_transform', WriteDiskItem('Sulci Talairach to Global SPAM transformation',
                                                   'Transformation matrix', requiredAttributes={'side': 'right'}),
    'right_t1_to_global_transform', WriteDiskItem('Raw T1 to Global SPAM transformation',
                                                  'Transformation matrix', requiredAttributes={'side': 'right'}),
    # Local
    'right_local_model', ReadDiskItem('Sulci Segments Model',
                                      'Text Data Table', requiredAttributes={'side': 'right'}),
    'right_local_referentials', ReadDiskItem('Sulci Local referentials',
                                             'Text Data Table', requiredAttributes={'side': 'right'}),
    'right_direction_priors', ReadDiskItem('Sulci Direction Transformation Priors',
                                           'Text Data Table', requiredAttributes={'side': 'right'}),
    'right_angle_priors', ReadDiskItem('Sulci Angle Transformation Priors',
                                       'Text Data Table', requiredAttributes={'side': 'right'}),
    'right_translation_priors', ReadDiskItem('Sulci Translation Transformation Priors',
                                             'Text Data Table', requiredAttributes={'side': 'right'}),
    'right_global_to_local_transforms', WriteDiskItem('Sulci Local SPAM transformations Directory',
                                                      'Directory', requiredAttributes={'side': 'right'}),
    # Sulcal Morphometry
    'sulci_file', ReadDiskItem('Sulci groups list', 'JSON file'),
    'sulcal_morpho_measures', WriteDiskItem(
        'Sulcal morphometry measurements', 'CSV File'),
    'left_csf', WriteDiskItem('Left CSF Mask',
                              'Aims writable volume formats'),
    'right_csf', WriteDiskItem('Right CSF Mask',
                               'Aims writable volume formats'),
    'subject', String(),
    'sulci_label_attribute', String(),
    'brain_volumes_file', WriteDiskItem(
        'Brain volumetry measurements', 'CSV file'),
    'report', WriteDiskItem('Morphologist report', 'PDF file'),
)


class APCReader(object):
    def __init__(self, key):
        self._key = key

    def __call__(self, values, process):
        acp = None
        if values.commissure_coordinates is not None:
            acp = values.commissure_coordinates
        result = None
        key_mm = self._key + 'mm'
        if acp is not None and acp.isReadable():
            f = open(acp.fullPath())
            for l in f.readlines():
                l = l.split(':', 1)
                if len(l) == 2 and l[0] == key_mm:
                    return [float(i) for i in l[1].split()]
                if len(l) == 2 and l[0] == self._key and values.t1mri is not None:
                    vs = values.t1mri.get('voxel_size')
                    if vs:
                        pos = l[1].split()
                        if len(pos) == 3:
                            result = [float(i) * j for i, j in zip(pos, vs)]
        return result


def linkOldNormalization(self, proc, dummy):
        # this forced acquisition is meant to avoid confusion with a different one
        # when there is no older normalization in the same acquisition
    required = {}
    acquisition = self.t1mri.get('acquisition')
    if acquisition:
        required['acquisition'] = acquisition
    return self.signature['older_MNI_normalization'].findValue(
        self.t1mri, requiredAttributes=required)

def linkSubject(self, proc, dummy):
    if self.split_brain is not None:
        subject = self.split_brain.get('subject')
        return subject

def linkSulciLabelAtt(self, proc, dummy):
    auto = 'Yes'
    if self.left_labelled_graph is not None:
        auto = self.left_labelled_graph.get('automatically_labelled',
                                            'Yes')
    elif self.right_labelled_graph is not None:
        auto = self.right_labelled_graph.get('automatically_labelled',
                                              'Yes')
    return {'Yes': 'label', 'No': 'name'}.get(auto, 'label')


def initialization(self):
    self.perform_segmentation = True
    self.perform_bias_correction = True

    # Commissures Coordinates
    self.method_ACPC = 'With SPM12 Normalization'
    self.linkParameters('commissure_coordinates', 't1mri')
    self.linkParameters('anterior_commissure',
                        'commissure_coordinates', APCReader('AC'))
    self.linkParameters('posterior_commissure',
                        'commissure_coordinates', APCReader('PC'))
    self.linkParameters('interhemispheric_point',
                        'commissure_coordinates', APCReader('IH'))
    self.linkParameters('older_MNI_normalization',
                        't1mri', self.linkOldNormalization)

    self.setOptional('anterior_commissure')
    self.setOptional('posterior_commissure')
    self.setOptional('interhemispheric_point')
    self.setOptional('left_hemisphere_point')
    self.setOptional('older_MNI_normalization')

    self.signature['anterior_commissure'].add3DLink(self, 't1mri')
    self.signature['posterior_commissure'].add3DLink(self, 't1mri')
    self.signature['interhemispheric_point'].add3DLink(self, 't1mri')
    self.signature['left_hemisphere_point'].add3DLink(self, 't1mri')
    self.signature['older_MNI_normalization'].userLevel = 100

    # SPM Normalization
    def linkNormRef(proc, param):
        trManager = registration.getTransformationManager()
        if proc.talairach_MNI_transform:
            s = proc.talairach_MNI_transform.get(
                'destination_referential', None)
            if s:
                return trManager.referential(s)
        return trManager.referential(registration.talairachMNIReferentialId)

    def linkACPC_to_norm(proc, param):
        trManager = registration.getTransformationManager()
        if proc.normalized_referential:
            _mniToACPCpaths = trManager.findPaths(registration.talairachACPCReferentialId,
                                                  self.normalized_referential.uuid())
            for x in _mniToACPCpaths:
                return x
            else:
                return []
    self.anatomical_template = self.signature['anatomical_template'].findValue(
        {'databasename': 'spm', 'skull_stripped': 'no'})
    #self.linkParameters( 'job_file', 't1mri' )
    self.linkParameters('transformations_information', 't1mri')
    self.linkParameters('normalized_t1mri', 't1mri')
    self.linkParameters('talairach_MNI_transform',
                        'transformations_information')

    self.linkParameters('source_referential', 't1mri')
    self.linkParameters('normalized_referential',
                        'talairach_MNI_transform', linkNormRef)
    self.linkParameters('tal_to_normalized_transform',
                        'normalized_referential', linkACPC_to_norm)

    self.setOptional('normalized_t1mri')
    self.setOptional('source_referential')

    self.setOptional('anatomical_template')
    #self.setOptional( 'job_file' )

    self.signature['anatomical_template'].userLevel = 100
    #self.signature[ 'job_file' ].userLevel = 100
    self.signature['transformations_information'].userLevel = 100
    self.signature['normalized_t1mri'].userLevel = 100
    self.signature['talairach_MNI_transform'].userLevel = 100
    self.signature['source_referential'].userLevel = 100
    self.signature['normalized_referential'].userLevel = 100
    self.signature['tal_to_normalized_transform'].userLevel = 100

    # Bias Correction
    self.linkParameters('t1mri_nobias', 't1mri')
    self.linkParameters('hfiltered', 't1mri_nobias')
    self.linkParameters('white_ridges', 't1mri_nobias')
    self.linkParameters('variance', 't1mri_nobias')
    self.linkParameters('edges', 't1mri_nobias')
    self.linkParameters('field', 't1mri_nobias')
    self.linkParameters('meancurvature', 't1mri_nobias')
    self.signature['hfiltered'].userLevel = 100
    self.signature['white_ridges'].userLevel = 100
    self.signature['variance'].userLevel = 100
    self.signature['edges'].userLevel = 100
    self.signature['field'].userLevel = 100
    self.signature['meancurvature'].userLevel = 100

    # Histogram Analysis
    self.linkParameters('histo_analysis', 't1mri_nobias')
    self.linkParameters('histo', 't1mri_nobias')
    self.signature['histo'].userLevel = 100

    # Brain Mask Segmentation
    self.linkParameters('brain_mask', 't1mri_nobias')

    # Re Commissures Coordinates
    self.linkParameters('skull_stripped', 't1mri')
    self.anatomical_template_skull_stripped = self.signature[
        'anatomical_template_skull_stripped'].findValue(
            {'_ontology': 'shared',
             'skull_stripped': 'yes', 'Size': '2 mm',
             '_database': neuroConfig.sharedDatabasePath()})
    self.setOptional('anatomical_template_skull_stripped')

    self.signature['skull_stripped'].userLevel = 100
    self.signature['anatomical_template_skull_stripped'].userLevel = 100

    # Split Brain Mask
    self.linkParameters('split_brain', 'brain_mask')
    self.split_template = self.signature['split_template'].findValue({})
    self.signature['split_template'].userLevel = 100

    # Talairach Transformation
    self.linkParameters('talairach_ACPC_transform', 't1mri')
    self.signature['talairach_ACPC_transform'].userLevel = 100

    # Grey/White Classification
    self.linkParameters('left_grey_white', 'split_brain')
    self.linkParameters('right_grey_white', 'split_brain')

    # Grey/White Topology
    self.linkParameters('left_hemi_cortex', 't1mri_nobias')
    self.linkParameters('right_hemi_cortex', 't1mri_nobias')
    self.signature['left_hemi_cortex'].userLevel = 100
    self.signature['right_hemi_cortex'].userLevel = 100

    self.perform_meshes_and_graphs = True
    # Grey/White Mesh
    self.linkParameters('left_white_mesh', 't1mri_nobias')
    self.linkParameters('right_white_mesh', 't1mri_nobias')

    # Sulci Skeleton
    self.linkParameters('left_skeleton', 't1mri_nobias')
    self.linkParameters('left_roots', 't1mri_nobias')
    self.linkParameters('right_skeleton', 't1mri_nobias')
    self.linkParameters('right_roots', 't1mri_nobias')
    self.signature['left_skeleton'].userLevel = 100
    self.signature['left_roots'].userLevel = 100
    self.signature['right_skeleton'].userLevel = 100
    self.signature['right_roots'].userLevel = 100

    # Pial Mesh
    self.linkParameters('left_pial_mesh', 'left_hemi_cortex')
    self.linkParameters('right_pial_mesh', 'right_hemi_cortex')

    # Cortical Folds Graph
    # Left
    self.linkParameters('left_graph', 't1mri_nobias')
    self.linkParameters('left_sulci_voronoi', 'left_graph')
    self.linkParameters('left_cortex_mid_interface', 't1mri_nobias')
    self.signature['left_sulci_voronoi'].userLevel = 100
    self.signature['left_cortex_mid_interface'].userLevel = 100
    # Right
    self.linkParameters('right_graph', 't1mri_nobias')
    self.linkParameters('right_sulci_voronoi', 'right_graph')
    self.linkParameters('right_cortex_mid_interface', 't1mri_nobias')
    self.signature['right_sulci_voronoi'].userLevel = 100
    self.signature['right_cortex_mid_interface'].userLevel = 100

    # Sulci Recognition
    self.perform_sulci_recognition = 'No'
    self.labels_translation_map = self.signature['labels_translation_map'].findValue(
        {'filename_variable': 'sulci_model_2008'})
    self.signature['labels_translation_map'].userLevel = 100
    # Left
    self.linkParameters('left_labelled_graph', 'left_graph')
    self.linkParameters('left_posterior_probabilities', 'left_labelled_graph')
    self.linkParameters('left_labels_priors', 'left_graph')
    self.signature['left_posterior_probabilities'].userLevel = 100
    self.signature['left_labels_priors'].userLevel = 100
    
    self.left_model_file = os.path.normpath(os.path.join(
        neuroConfig.sharedDatabasePath(),
        'models', 'models_2019', 'cnn_models', 'sulci_unet_model_left.mdsm'))
    self.signature['left_model_file'].userLevel = 100
    self.left_param_file = os.path.normpath(os.path.join(
        neuroConfig.sharedDatabasePath(),
        'models', 'models_2019', 'cnn_models',
        'sulci_unet_model_params_left.json'))
    self.signature['left_param_file'].userLevel = 100
    # Global
    self.left_global_model = self.signature['left_global_model'].findValue(
        {'sulci_segments_model_type': 'global_registered_spam'})
    self.linkParameters('left_tal_to_global_transform', 'left_labelled_graph')
    self.linkParameters('left_t1_to_global_transform', 'left_labelled_graph')
    self.signature['left_global_model'].userLevel = 100
    self.signature['left_tal_to_global_transform'].userLevel = 100
    self.signature['left_t1_to_global_transform'].userLevel = 100
    # Local
    self.left_local_model = self.signature['left_local_model'].findValue(
        {'sulci_segments_model_type': 'locally_from_global_registred_spam'})
    self.linkParameters('left_local_referentials', 'left_graph')
    self.linkParameters('left_direction_priors', 'left_graph')
    self.linkParameters('left_angle_priors', 'left_graph')
    self.linkParameters('left_translation_priors', 'left_graph')
    self.linkParameters('left_global_to_local_transforms', 'left_labelled_graph')
    self.signature['left_local_model'].userLevel = 100
    self.signature['left_local_referentials'].userLevel = 100
    self.signature['left_direction_priors'].userLevel = 100
    self.signature['left_angle_priors'].userLevel = 100
    self.signature['left_translation_priors'].userLevel = 100
    self.signature['left_global_to_local_transforms'].userLevel = 100
    # Right
    self.linkParameters('right_labelled_graph', 'left_labelled_graph')
    self.linkParameters('right_posterior_probabilities', 'right_labelled_graph')
    self.linkParameters('right_labels_priors', 'right_graph')
    self.signature['right_posterior_probabilities'].userLevel = 100
    self.signature['right_labels_priors'].userLevel = 100

    self.right_model_file = os.path.normpath(os.path.join(
        neuroConfig.sharedDatabasePath(),
        'models', 'models_2019', 'cnn_models', 'sulci_unet_model_right.mdsm'))
    self.signature['right_model_file'].userLevel = 100
    self.right_param_file = os.path.normpath(os.path.join(
        neuroConfig.sharedDatabasePath(),
        'models', 'models_2019', 'cnn_models',
        'sulci_unet_model_params_right.json'))
    self.signature['right_param_file'].userLevel = 100
    # Global
    self.right_global_model = self.signature['right_global_model'].findValue(
        {'sulci_segments_model_type': 'global_registered_spam'})
    self.linkParameters('right_tal_to_global_transform', 'right_labelled_graph')
    self.linkParameters('right_t1_to_global_transform', 'right_labelled_graph')
    self.signature['right_global_model'].userLevel = 100
    self.signature['right_tal_to_global_transform'].userLevel = 100
    self.signature['right_t1_to_global_transform'].userLevel = 100
    # Local
    self.right_local_model = self.signature['right_local_model'].findValue(
        {'sulci_segments_model_type': 'locally_from_global_registred_spam'})
    self.linkParameters('right_local_referentials', 'right_graph')
    self.linkParameters('right_direction_priors', 'right_graph')
    self.linkParameters('right_angle_priors', 'right_graph')
    self.linkParameters('right_translation_priors', 'right_graph')
    self.linkParameters('right_global_to_local_transforms', 'right_labelled_graph')
    self.signature['right_local_model'].userLevel = 100
    self.signature['right_local_referentials'].userLevel = 100
    self.signature['right_direction_priors'].userLevel = 100
    self.signature['right_angle_priors'].userLevel = 100
    self.signature['right_translation_priors'].userLevel = 100
    self.signature['right_global_to_local_transforms'].userLevel = 100

    # Sulcal Morphometry
    self.sulci_file = self.signature['sulci_file'].findValue(
        {'version': 'default'})
    self.linkParameters('sulcal_morpho_measures', 'left_labelled_graph')
    self.linkParameters('left_csf', 't1mri')
    self.linkParameters('right_csf', 't1mri')
    self.linkParameters('subject', 't1mri', self.linkSubject)
    self.linkParameters('sulci_label_attribute',
                        ('left_labelled_graph', 'right_labelled_graph'),
                        self.linkSulciLabelAtt)
    self.linkParameters('brain_volumes_file', 't1mri')
    self.linkParameters('report', 't1mri')


def execution(self, context):
    if self.perform_segmentation:
        # Commissures Coordinates
        context.write('<b>' + 'Computing AC/PC Coordinates...' + '</b>')
        if self.method_ACPC == 'Manually':
            context.runProcess('preparesubject',
                               T1mri=self.t1mri,
                               commissure_coordinates=self.commissure_coordinates,
                               Anterior_Commissure=self.anterior_commissure,
                               Posterior_Commissure=self.posterior_commissure,
                               Interhemispheric_Point=self.interhemispheric_point,
                               Left_Hemisphere_Point=self.left_hemisphere_point,
                               older_MNI_normalization=self.older_MNI_normalization)
        elif self.method_ACPC == 'With SPM12 Normalization':
            context.runProcess('normalization_t1_spm12_reinit',
                                anatomy_data=self.t1mri,
                                anatomical_template=self.anatomical_template,
                                transformations_informations=self.transformations_information,
                                normalized_anatomy_data=self.normalized_t1mri,
                                allow_retry_initialization=True)
            context.runProcess('SPMsn3dToAims',
                               read=self.transformations_information,
                               write=self.talairach_MNI_transform,
                               source_volume=self.t1mri,
                               normalized_volume=None)
            context.runProcess('TalairachTransformationFromNormalization',
                               normalization_transformation=self.talairach_MNI_transform,
                               Talairach_transform=self.talairach_ACPC_transform,
                               commissure_coordinates=self.commissure_coordinates,
                               t1mri=self.t1mri,
                               source_referential=self.source_referential,
                               normalized_referential=self.normalized_referential,
                               transform_chain_ACPC_to_Normalized=self.tal_to_normalized_transform)

        # Bias Correction
        if self.perform_bias_correction:
            context.write('<b>' + 'Computing T1 Bias Correction...' + '</b>')
            context.runProcess('T1BiasCorrection',
                               t1mri=self.t1mri,
                               commissure_coordinates=self.commissure_coordinates,
                               t1mri_nobias=self.t1mri_nobias,
                               field=self.field,
                               hfiltered=self.hfiltered,
                               white_ridges=self.white_ridges,
                               variance=self.variance,
                               edges=self.edges,
                               meancurvature=self.meancurvature)
        else:

            # > Perform bias correction and create intermediate outputs
            # > without actually applying the correction
            # > the t1mri_nobias will be the actual t1 input
            context.write('<b>' + 'Computing T1 Bias Correction intermediate outputs without applying the correction...' + '</b>')
            context.runProcess('T1BiasCorrection',
                               t1mri=self.t1mri,
                               commissure_coordinates=self.commissure_coordinates,
                               t1mri_nobias=self.t1mri_nobias,
                               mode='write_minimal without correction',
                               field=self.field,
                               hfiltered=self.hfiltered,
                               white_ridges=self.white_ridges,
                               variance=self.variance,
                               edges=self.edges,
                               meancurvature=self.meancurvature)

        # Histogram Analysis
        context.write('<b>' + 'Computing Histogram Analysis...' + '</b>')
        context.runProcess('NobiasHistoAnalysis',
                           t1mri_nobias=self.t1mri_nobias,
                           hfiltered=self.hfiltered,
                           white_ridges=self.white_ridges,
                           histo_analysis=self.histo_analysis,
                           histo=self.histo)
        # Brain Mask Segmentation
        context.write('<b>' + 'Computing Brain Segmentation...' + '</b>')
        context.runProcess('BrainSegmentation',
                           t1mri_nobias=self.t1mri_nobias,
                           histo_analysis=self.histo_analysis,
                           variance=self.variance,
                           edges=self.edges,
                           white_ridges=self.white_ridges,
                           commissure_coordinates=self.commissure_coordinates,
                           lesion_mask=None,
                           brain_mask=self.brain_mask)
        # Re Commissures Coordinates
        if self.method_ACPC == 'With SPM8 Normalization' or self.method_ACPC == 'With SPM12 Normalization':
            context.runProcess('skullstripping',
                               t1mri=self.t1mri,
                               brain_mask=self.brain_mask,
                               skull_stripped=self.skull_stripped)
            if self.method_ACPC == 'With SPM8 Normalization':
                context.runProcess('normalization_t1_spm8_reinit',
                                   anatomy_data=self.skull_stripped,
                                   anatomical_template=self.anatomical_template_skull_stripped,
                                   transformations_informations=self.transformations_information,
                                   normalized_anatomy_data=self.normalized_t1mri)
            elif self.method_ACPC == 'With SPM12 Normalization':
                context.runProcess('normalization_t1_spm12_reinit',
                                   anatomy_data=self.skull_stripped,
                                   anatomical_template=self.anatomical_template_skull_stripped,
                                   transformations_informations=self.transformations_information,
                                   normalized_anatomy_data=self.normalized_t1mri)
            context.runProcess('SPMsn3dToAims',
                               read=self.transformations_information,
                               write=self.talairach_MNI_transform,
                               source_volume=self.skull_stripped,
                               normalized_volume=None)
            context.runProcess('TalairachTransformationFromNormalization',
                               normalization_transformation=self.talairach_MNI_transform,
                               Talairach_transform=self.talairach_ACPC_transform,
                               commissure_coordinates=self.commissure_coordinates,
                               t1mri=self.t1mri,
                               source_referential=self.source_referential,
                               normalized_referential=self.normalized_referential,
                               transform_chain_ACPC_to_Normalized=self.tal_to_normalized_transform)

        # Split Brain Mask
        context.write('<b>' + 'Computing Split Brain...' + '</b>')
        context.runProcess('SplitBrain',
                           brain_mask=self.brain_mask,
                           t1mri_nobias=self.t1mri_nobias,
                           histo_analysis=self.histo_analysis,
                           commissure_coordinates=self.commissure_coordinates,
                           white_ridges=self.white_ridges,
                           split_template=self.split_template,
                           split_brain=self.split_brain)
        # Talairach Transformation
        if self.method_ACPC == 'Manually' or self.method_ACPC == 'Already done':
            context.write(
                '<b>' + 'Computing Talairach Transformation...' + '</b>')
            context.runProcess('TalairachTransformation',
                               split_mask=self.split_brain,
                               commissure_coordinates=self.commissure_coordinates,
                               Talairach_transform=self.talairach_ACPC_transform)
        # Grey/White Classification
        context.write(
            '<b>' + 'Computing Grey/White Classification...' + '</b>')
        context.runProcess('GreyWhiteClassificationHemi',
                           side='left',
                           t1mri_nobias=self.t1mri_nobias,
                           histo_analysis=self.histo_analysis,
                           split_brain=self.split_brain,
                           edges=self.edges,
                           commissure_coordinates=self.commissure_coordinates,
                           grey_white=self.left_grey_white)
        context.runProcess('GreyWhiteClassificationHemi',
                           side='right',
                           t1mri_nobias=self.t1mri_nobias,
                           histo_analysis=self.histo_analysis,
                           split_brain=self.split_brain,
                           edges=self.edges,
                           commissure_coordinates=self.commissure_coordinates,
                           grey_white=self.right_grey_white)

    if self.perform_meshes_and_graphs:
        context.write('<b>' + 'Computing Grey/White Surface...' + '</b>')
        # Grey/White Topology
        context.runProcess('GreyWhiteTopology',
                           grey_white=self.left_grey_white,
                           t1mri_nobias=self.t1mri_nobias,
                           histo_analysis=self.histo_analysis,
                           hemi_cortex=self.left_hemi_cortex)
        context.runProcess('GreyWhiteTopology',
                           grey_white=self.right_grey_white,
                           t1mri_nobias=self.t1mri_nobias,
                           histo_analysis=self.histo_analysis,
                           hemi_cortex=self.right_hemi_cortex)
        # Grey/White Mesh
        context.runProcess('GreyWhiteMesh',
                           hemi_cortex=self.left_hemi_cortex,
                           white_mesh=self.left_white_mesh)
        context.runProcess('GreyWhiteMesh',
                           hemi_cortex=self.right_hemi_cortex,
                           white_mesh=self.right_white_mesh)
        # Sulci Skeleton
        context.write('<b>' + 'Computing Sulci Skeleton and Roots...' + '</b>')
        context.runProcess('sulciskeleton',
                           hemi_cortex=self.left_hemi_cortex,
                           grey_white=self.left_grey_white,
                           t1mri_nobias=self.t1mri_nobias,
                           skeleton=self.left_skeleton,
                           roots=self.left_roots)
        context.runProcess('sulciskeleton',
                           hemi_cortex=self.right_hemi_cortex,
                           grey_white=self.right_grey_white,
                           t1mri_nobias=self.t1mri_nobias,
                           skeleton=self.right_skeleton,
                           roots=self.right_roots)
        # Pial Surface
        context.write('<b>' + 'Computing Pial Surface...' + '</b>')
        context.runProcess('hemispheremesh',
                           hemi_cortex=self.left_hemi_cortex,
                           grey_white=self.left_grey_white,
                           t1mri_nobias=self.t1mri_nobias,
                           skeleton=self.left_skeleton,
                           pial_mesh=self.left_pial_mesh)
        context.runProcess('hemispheremesh',
                           hemi_cortex=self.right_hemi_cortex,
                           grey_white=self.right_grey_white,
                           t1mri_nobias=self.t1mri_nobias,
                           skeleton=self.right_skeleton,
                           pial_mesh=self.right_pial_mesh)
        # Cortical Folds Graph
        context.write('<b>' + 'Computing Cortical Folds Graph...' + '</b>')
        context.runProcess('corticalfoldsgraph',
                           skeleton=self.left_skeleton,
                           roots=self.left_roots,
                           grey_white=self.left_grey_white,
                           hemi_cortex=self.left_hemi_cortex,
                           split_brain=self.split_brain,
                           white_mesh=self.left_white_mesh,
                           pial_mesh=self.left_pial_mesh,
                           commissure_coordinates=self.commissure_coordinates,
                           talairach_transform=self.talairach_ACPC_transform,
                           graph=self.left_graph,
                           sulci_voronoi=self.left_sulci_voronoi,
                           cortex_mid_interface=self.left_cortex_mid_interface)
        context.runProcess('corticalfoldsgraph',
                           skeleton=self.right_skeleton,
                           roots=self.right_roots,
                           grey_white=self.right_grey_white,
                           hemi_cortex=self.right_hemi_cortex,
                           split_brain=self.split_brain,
                           white_mesh=self.right_white_mesh,
                           pial_mesh=self.right_pial_mesh,
                           commissure_coordinates=self.commissure_coordinates,
                           talairach_transform=self.talairach_ACPC_transform,
                           graph=self.right_graph,
                           sulci_voronoi=self.right_sulci_voronoi,
                           cortex_mid_interface=self.right_cortex_mid_interface)

    # Sulci Recognition
    if self.perform_sulci_recognition=='SPAM':
        context.write(
            '<b>' + 'Computing Sulci Recognition with SPAM global+local...' + '</b>')
        # Left
        # Global
        context.runProcess('spam_recognitionglobal',
                           data_graph=self.left_graph,
                           output_graph=self.left_labelled_graph,
                           model=self.left_global_model,
                           posterior_probabilities=self.left_posterior_probabilities,
                           labels_translation_map=self.labels_translation_map,
                           labels_priors=self.left_labels_priors,
                           output_transformation=self.left_tal_to_global_transform,
                           initial_transformation=None,
                           output_t1_to_global_transformation=self.left_t1_to_global_transform)
        # Local
        context.runProcess('spam_recognitionlocal',
                           data_graph=self.left_graph,
                           output_graph=self.left_labelled_graph,
                           model=self.left_local_model,
                           posterior_probabilities=self.left_posterior_probabilities,
                           labels_translation_map=self.labels_translation_map,
                           labels_priors=self.left_labels_priors,
                           local_referentials=self.left_local_referentials,
                           direction_priors=self.left_direction_priors,
                           angle_priors=self.left_angle_priors,
                           translation_priors=self.left_translation_priors,
                           output_local_transformations=self.left_global_to_local_transforms,
                           initial_transformation=None,
                           global_transformation=self.left_tal_to_global_transform)
        # Right
        # Global
        context.runProcess('spam_recognitionglobal',
                           data_graph=self.right_graph,
                           output_graph=self.right_labelled_graph,
                           model=self.right_global_model,
                           posterior_probabilities=self.right_posterior_probabilities,
                           labels_translation_map=self.labels_translation_map,
                           labels_priors=self.right_labels_priors,
                           output_transformation=self.right_tal_to_global_transform,
                           initial_transformation=None,
                           output_t1_to_global_transformation=self.right_t1_to_global_transform)
        # Local
        context.runProcess('spam_recognitionlocal',
                           data_graph=self.right_graph,
                           output_graph=self.right_labelled_graph,
                           model=self.right_local_model,
                           posterior_probabilities=self.right_posterior_probabilities,
                           labels_translation_map=self.labels_translation_map,
                           labels_priors=self.right_labels_priors,
                           local_referentials=self.right_local_referentials,
                           direction_priors=self.right_direction_priors,
                           angle_priors=self.right_angle_priors,
                           translation_priors=self.right_translation_priors,
                           output_local_transformations=self.right_global_to_local_transforms,
                           initial_transformation=None,
                           global_transformation=self.right_tal_to_global_transform)
    
    elif self.perform_sulci_recognition=='DeepCNN':
        context.runProcess('capsul://deepsulci.sulci_labeling.capsul.labeling',
                           graph=self.left_graph,
                           model_file=self.left_model_file,
                           param_file=self.left_param_file,
                           roots=self.left_roots,
                           skeleton=self.left_skeleton,
                           labeled_graph=self.left_labelled_graph)
        context.runProcess('capsul://deepsulci.sulci_labeling.capsul.labeling',
                           graph=self.right_graph,
                           model_file=self.right_model_file,
                           param_file=self.right_param_file,
                           roots=self.right_roots,
                           skeleton=self.right_skeleton,
                           labeled_graph=self.right_labelled_graph)
    if self.perform_sulci_recognition!='No':
        # Sulcal Morphometry
        context.runProcess('sulcigraphmorphometrybysubject',
                           left_sulci_graph=self.left_labelled_graph,
                           right_sulci_graph=self.right_labelled_graph,
                           sulci_file=self.sulci_file,
                           use_attribute='label',
                           sulcal_morpho_measures=self.sulcal_morpho_measures)
    # global stats
    context.runProcess('brainvolumes',
                       split_brain=self.split_brain,
                       left_grey_white=self.left_grey_white,
                       right_grey_white=self.right_grey_white,
                       left_csf=self.left_csf,
                       right_csf=self.right_csf,
                       left_labelled_graph=self.left_labelled_graph,
                       right_labelled_graph=self.right_labelled_graph,
                       left_gm_mesh=self.left_pial_mesh,
                       right_gm_mesh=self.right_pial_mesh,
                       left_wm_mesh=self.left_white_mesh,
                       right_wm_mesh=self.right_white_mesh,
                       subject=self.subject,
                       sulci_label_attribute=self.sulci_label_attribute,
                       brain_volumes_file=self.brain_volumes_file)
    # report
    context.runProcess('morpho_report',
                       t1mri=self.t1mri,
                       left_grey_white=self.left_grey_white,
                       right_grey_white=self.right_grey_white,
                       left_gm_mesh=self.left_pial_mesh,
                       right_gm_mesh=self.right_pial_mesh,
                       left_wm_mesh=self.left_white_mesh,
                       right_wm_mesh=self.right_white_mesh,
                       left_labelled_graph=self.left_labelled_graph,
                       right_labelled_graph=self.right_labelled_graph,
                       brain_volumes_file=self.brain_volumes_file,
                       report=self.report,
                       subject=self.subject)
