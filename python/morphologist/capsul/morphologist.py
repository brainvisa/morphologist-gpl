
from __future__ import absolute_import
import distutils.spawn
import morphologist.capsul.axon.axonmorphologist
from traits.api import Undefined, Bool, File, Set
import six


class Morphologist(morphologist.capsul.axon.axonmorphologist.AxonMorphologist):

    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        super(Morphologist, self).__init__(
            autoexport_nodes_parameters, **kwargs)

        # if this line is in pipeline_definition(), it has no effect...
        #self.GreyWhiteClassification_1_side = 'right'

    def pipeline_definition(self):
        autoexport_nodes_parameters = self._autoexport_nodes_parameters
        self._autoexport_nodes_parameters = False
        self.add_process('importation',
                         'morphologist.capsul.axon.importt1mri.ImportT1MRI')
        super(Morphologist, self).pipeline_definition()

        self.add_switch('select_Talairach',
                        ['StandardACPC', 'Normalization'],
                        ['Talairach_transform'], output_types=[File()])

        # WARNING: we must keep 2 switches here, otherwise we introduce a loop
        # in the pipeline graph:
        # - in AC/PC mode, TalairachTransform needs split, which needs
        #   commissure coords, thus transformations are obtained 2 steps
        #   after APC
        # - in renormalization mode, split is using the APC from Renorm.
        self.add_switch('select_renormalization_commissures',
                        ['initial', 'skull_stripped'],
                        ['commissure_coordinates'], export_switch=False,
                        output_types=[File()])
        self.add_switch('select_renormalization_transform',
                        ['initial', 'skull_stripped'],
                        ['Talairach_transform', 'MNI_transform'], export_switch=False,
                        output_types=[File(), File()])

        self.remove_link('t1mri->PrepareSubject.T1mri')
        self.add_link('t1mri->importation.input')
        self.export_parameter('importation', 'output', 'imported_t1mri')
        self.export_parameter('importation', 'referential',
                              't1mri_referential')
        self.add_link('importation.output->PrepareSubject.T1mri')

        self._autoexport_nodes_parameters = autoexport_nodes_parameters

        # fix initial values of switches: should be Undefined, not None.
        self.nodes['select_Talairach'].StandardACPC_switch_Talairach_transform = Undefined
        self.nodes['select_Talairach'].Normalization_switch_Talairach_transform = Undefined
        self.nodes['select_renormalization_transform'].skull_stripped_switch_Talairach_transform = Undefined
        self.nodes['select_renormalization_transform'].initial_switch_Talairach_transform = Undefined
        self.nodes['select_renormalization_transform'].skull_stripped_switch_MNI_transform = Undefined
        self.nodes['select_renormalization_transform'].initial_switch_MNI_transform = Undefined
        self.nodes['select_renormalization_commissures'].skull_stripped_switch_commissure_coordinates = Undefined
        self.nodes['select_renormalization_commissures'].initial_switch_commissure_coordinates = Undefined

        self.export_parameter('PrepareSubject', 'allow_flip_initial_MRI')
        self.export_parameter(
            'PrepareSubject', 'Normalization_select_Normalization_pipeline')
        self.export_parameter(
            'PrepareSubject',
            'TalairachFromNormalization_normalized_referential',
            'PrepareSubject_TalairachFromNormalization_normalized_referential')
        self.add_link(
            'importation.referential->'
            'PrepareSubject.TalairachFromNormalization_source_referential')
        #'PrepareSubject',
        #'TalairachFromNormalization_source_referential',
        #'PrepareSubject_TalairachFromNormalization_source_referential')
        self.export_parameter(
            'PrepareSubject',
            'TalairachFromNormalization_acpc_referential',
            'PrepareSubject_TalairachFromNormalization_acpc_referential')
        self.export_parameter(
            'PrepareSubject',
            'TalairachFromNormalization_transform_chain_ACPC_to_Normalized',
            'PrepareSubject_TalairachFromNormalization_transform_chain_ACPC_to_Normalized')

        self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes['Normalization_AimsMIRegister'].process.user_traits()[
            'transformation_to_MNI'].optional = False
        self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes['Normalization_AimsMIRegister'].process.user_traits()[
            'normalized_anatomy_data'].optional = False
        self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes[
            'Normalization_AimsMIRegister'].plugs['transformation_to_MNI'].optional = False
        self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes[
            'Normalization_AimsMIRegister'].plugs['normalized_anatomy_data'].optional = False

        self.nodes['PrepareSubject'].plugs['talairach_transformation'].optional = True
        self.nodes['PrepareSubject'].process.nodes['TalairachFromNormalization'].plugs['Talairach_transform'].optional = True
        self.nodes['PrepareSubject'].process.nodes['TalairachFromNormalization'].plugs['commissure_coordinates'].optional = False

        self.nodes['PrepareSubject'].process.export_parameter(
            'Normalization', 'transformation',
            'normalization_transformation', is_optional=True, weak_link=True)

        self.export_parameter(
            'PrepareSubject', 'Normalization_normalized', 'normalized_t1mri',
            is_optional=True, weak_link=True)
        self.add_trait('normalization_allow_retry_initialization', Bool())

        self.nodes['Renorm'].plugs['transformation'].optional = True

        self.add_link(
            'PrepareSubject.commissure_coordinates->Renorm.Normalization_commissures_coordinates')
        self.add_link(
            'allow_flip_initial_MRI->Renorm.Normalization_allow_flip_initial_MRI')
        self.add_link(
            'Normalization_select_Normalization_pipeline->Renorm.Normalization_select_Normalization_pipeline')
        self.add_link(
            'PrepareSubject_TalairachFromNormalization_normalized_referential->Renorm.TalairachFromNormalization_normalized_referential')
        self.add_link(
            'importation.referential->Renorm.TalairachFromNormalization_source_referential')
        self.add_link(
            'PrepareSubject_TalairachFromNormalization_acpc_referential->Renorm.TalairachFromNormalization_acpc_referential')
        self.add_link(
            'PrepareSubject_TalairachFromNormalization_transform_chain_ACPC_to_Normalized->Renorm.TalairachFromNormalization_transform_chain_ACPC_to_Normalized')
        self.add_link(
            'Renorm.Normalization_normalized->normalized_t1mri', weak_link=True)

        self.add_link(
            'TalairachTransformation.Talairach_transform->select_Talairach.StandardACPC_switch_Talairach_transform')
        self.add_link(
            'select_Talairach->PrepareSubject.select_AC_PC_Or_Normalization')
        self.remove_link(
            'TalairachTransformation.Talairach_transform->CorticalFoldsGraph.talairach_transform')
        self.remove_link(
            'TalairachTransformation.Talairach_transform->CorticalFoldsGraph_1.talairach_transform')

        self.export_parameter('select_renormalization_commissures',
                              'switch', 'perform_skull_stripped_renormalization')
        self.export_parameter('select_renormalization_commissures',
                              'commissure_coordinates', 'commissure_coordinates')
        self.export_parameter('select_renormalization_transform',
                              'Talairach_transform', 'Talairach_transform')
        self.export_parameter('select_renormalization_transform',
                              'MNI_transform', 'MNI_transform')
        self.add_link(
            'perform_skull_stripped_renormalization->select_renormalization_transform.switch')
        self.add_link(
            'PrepareSubject.commissure_coordinates->select_renormalization_commissures.initial_switch_commissure_coordinates')
        self.add_link(
            'PrepareSubject.talairach_transformation->select_Talairach.Normalization_switch_Talairach_transform')
        self.add_link(
            'select_Talairach.Talairach_transform->select_renormalization_transform.initial_switch_Talairach_transform')
        self.add_link(
            'Renorm.commissure_coordinates->select_renormalization_commissures.skull_stripped_switch_commissure_coordinates')
        self.add_link(
            'Renorm.talairach_transformation->select_renormalization_transform.skull_stripped_switch_Talairach_transform')
        self.add_link(
            'PrepareSubject.normalization_transformation->select_renormalization_transform.initial_switch_MNI_transform')
        self.add_link(
            'Renorm.transformation->select_renormalization_transform.skull_stripped_switch_MNI_transform')

        self.remove_link(
            'Renorm.commissure_coordinates->Renorm_commissure_coordinates')
        self.remove_trait('Renorm_commissure_coordinates')

        # why does this one exist ? FIXME
        # self.remove_link('PrepareSubject.commissure_coordinates->Renorm_TalairachFromNormalization_commissure_coordinates')

        self.add_link(
            'select_renormalization_transform.Talairach_transform->CorticalFoldsGraph.talairach_transform')
        self.add_link(
            'select_renormalization_transform.Talairach_transform->CorticalFoldsGraph_1.talairach_transform')

        self.remove_link(
            'PrepareSubject.commissure_coordinates->SplitBrain.commissure_coordinates')
        self.add_link(
            'select_renormalization_commissures.commissure_coordinates->SplitBrain.commissure_coordinates')

        # plug commissure_coordinates and Talairach_transform params from
        # switches to other boxes
        self.remove_link(
            'PrepareSubject.commissure_coordinates->GreyWhiteClassification.commissure_coordinates')
        self.add_link(
            'select_renormalization_commissures.commissure_coordinates->GreyWhiteClassification.commissure_coordinates')
        self.remove_link(
            'PrepareSubject.commissure_coordinates->GreyWhiteClassification_1.commissure_coordinates')
        self.add_link(
            'select_renormalization_commissures.commissure_coordinates->GreyWhiteClassification_1.commissure_coordinates')

        self.remove_link(
            'PrepareSubject.commissure_coordinates->CorticalFoldsGraph.commissure_coordinates')
        self.add_link(
            'select_renormalization_commissures.commissure_coordinates->CorticalFoldsGraph.commissure_coordinates')
        self.remove_link(
            'PrepareSubject.commissure_coordinates->CorticalFoldsGraph_1.commissure_coordinates')
        self.add_link(
            'select_renormalization_commissures.commissure_coordinates->CorticalFoldsGraph_1.commissure_coordinates')

        # reactivate Talairach node: will be triggered via the normalization
        # flag
        self.nodes_activation.TalairachTransformation = True

        self.export_parameter('BiasCorrection', 'fix_random_seed',
                              'fix_random_seed')
        self.add_link('fix_random_seed->HistoAnalysis.fix_random_seed')
        self.add_link('fix_random_seed->BrainSegmentation.fix_random_seed')
        self.add_link('fix_random_seed->SplitBrain.fix_random_seed')
        self.add_link(
            'fix_random_seed->GreyWhiteClassification.fix_random_seed')
        self.add_link('fix_random_seed->GreyWhiteTopology.fix_random_seed')
        self.add_link('fix_random_seed->SulciSkeleton.fix_random_seed')
        self.add_link('fix_random_seed->PialMesh.fix_random_seed')
        self.add_link(
            'fix_random_seed->GreyWhiteClassification_1.fix_random_seed')
        self.add_link('fix_random_seed->GreyWhiteTopology_1.fix_random_seed')
        self.add_link('fix_random_seed->SulciSkeleton_1.fix_random_seed')
        self.add_link('fix_random_seed->PialMesh_1.fix_random_seed')
        self.add_link('fix_random_seed->SulciRecognition.fix_random_seed')
        self.add_link('fix_random_seed->SulciRecognition_1.fix_random_seed')

        self.export_parameter('GreyWhiteTopology', 'version',
                              'grey_white_topology_version')
        self.add_link('grey_white_topology_version->'
                      'GreyWhiteTopology_1.version')

        self.export_parameter('PialMesh', 'version', 'pial_mesh_version')
        self.add_link('pial_mesh_version->PialMesh_1.version')

        self.export_parameter('SulciSkeleton', 'version',
                              'sulci_skeleton_version')
        self.add_link('sulci_skeleton_version->SulciSkeleton_1.version')

        self.export_parameter('CorticalFoldsGraph', 'compute_fold_meshes',
                              'compute_fold_meshes')
        self.export_parameter('CorticalFoldsGraph', 'allow_multithreading',
                              'allow_multithreading')
        self.export_parameter('CorticalFoldsGraph',
                              'write_cortex_mid_interface',
                              'CorticalFoldsGraph_write_cortex_mid_interface')

        self.add_link(
            'compute_fold_meshes->CorticalFoldsGraph_1.compute_fold_meshes')
        self.add_link(
            'allow_multithreading->CorticalFoldsGraph_1.allow_multithreading')
        self.add_link(
            'CorticalFoldsGraph_write_cortex_mid_interface->CorticalFoldsGraph_1.write_cortex_mid_interface')

        self.export_parameter('SulciRecognition',
                              'SPAM_recognition09_global_recognition_labels_translation_map',
                              'SPAM_recognition_labels_translation_map')
        self.add_link(
            'SPAM_recognition_labels_translation_map->SulciRecognition_1.SPAM_recognition09_global_recognition_labels_translation_map')

        self.export_parameter('SulciRecognition', 'select_Sulci_Recognition',
                              'select_sulci_recognition')
        self.add_link(
            'select_sulci_recognition'
            '->SulciRecognition_1.select_Sulci_Recognition')
        self.export_parameter('SulciRecognition',
                              'recognition2000_forbid_unknown_label',
                              'sulci_recognition2000_forbid_unknown_label')
        self.add_link('sulci_recognition2000_forbid_unknown_label'
                      '->SulciRecognition_1.recognition2000_forbid_unknown_label')
        self.export_parameter('SulciRecognition',
                              'recognition2000_model_hint',
                              'sulci_recognition2000_model_hint')
        self.add_link('sulci_recognition2000_model_hint'
                      '->SulciRecognition_1.recognition2000_model_hint')
        self.export_parameter('SulciRecognition',
                              'recognition2000_rate',
                              'sulci_recognition2000_rate')
        self.add_link('sulci_recognition2000_rate'
                      '->SulciRecognition_1.recognition2000_rate')
        self.export_parameter('SulciRecognition',
                              'recognition2000_stopRate',
                              'sulci_recognition2000_stop_rate')
        self.add_link('sulci_recognition2000_stop_rate'
                      '->SulciRecognition_1.recognition2000_stopRate')
        self.export_parameter('SulciRecognition',
                              'recognition2000_niterBelowStopProp',
                              'sulci_recognition2000_niter_below_stop_prop')
        self.add_link('sulci_recognition2000_niter_below_stop_prop'
                      '->SulciRecognition_1.recognition2000_niterBelowStopProp')
        self.export_parameter('SulciRecognition',
                              'SPAM_recognition09_local_or_markovian',
                              'sulci_recognition_spam_local_or_markovian')
        self.add_link('sulci_recognition_spam_local_or_markovian'
                      '->SulciRecognition_1.SPAM_recognition09_local_or_markovian')
        self.export_parameter(
            'SulciRecognition',
            'SPAM_recognition09_global_recognition_model_type',
            'sulci_recognition_spam_global_model_type')
        self.add_link('sulci_recognition_spam_global_model_type->'
                      'SulciRecognition_1.'
                      'SPAM_recognition09_global_recognition_model_type')
        if 'CNN_recognition19' in self.nodes['SulciRecognition'].process.nodes:
          self.add_link(
              'allow_multithreading->SulciRecognition.CNN_recognition19_allow_multithreading')
          self.export_parameter(
              'SulciRecognition',
              'CNN_recognition19_rebuild_attributes',
              'rebuild_graph_attributes_after_split')
          self.add_link(
              'allow_multithreading->SulciRecognition_1.CNN_recognition19_allow_multithreading')
          self.add_link(
              'rebuild_graph_attributes_after_split->SulciRecognition_1.CNN_recognition19_rebuild_attributes')

        self.export_parameter('SulcalMorphometry', 'sulcal_morpho_measures')
        self.export_parameter('SulcalMorphometry', 'sulci_file',
                              'sulcal_morphometry_sulci_file')
        self.nodes['SulcalMorphometry'].enabled = True

        self.export_parameter(
            'PrepareSubject', 'reoriented_t1mri', is_optional=True)
        self.nodes['PrepareSubject'].process.nodes['select_AC_PC_Or_Normalization'].plugs['talairach_transformation'].optional = True

        # self.add_link('Renorm.Normalization_reoriented_t1mri->reoriented_t1mri')
        # self.remove_link('t1mri->BiasCorrection.t1mri')
        # self.add_link('PrepareSubject.reoriented_t1mri->BiasCorrection.t1mri')
        # self.remove_link('t1mri->Renorm.t1mri')
        # self.add_link('PrepareSubject.reoriented_t1mri->Renorm.t1mri')

        self.do_not_export.add(('Renorm', 'Normalization_reoriented_t1mri'))
        self.nodes['Renorm'].process.nodes['Normalization'].plugs['reoriented_t1mri'].optional = True
        self.nodes['Renorm'].process.nodes['Normalization'].process.nodes[
            'select_Normalization_pipeline'].plugs['reoriented_t1mri'].optional = True

        if 'NormalizeSPM' \
                in self.nodes['PrepareSubject'].process.nodes[
                    'Normalization'].process.nodes:
            self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes[
                'NormalizeSPM'].process.nodes_activation.ReorientAnatomy = True
            self.nodes['Renorm'].process.nodes['Normalization'].process.nodes['NormalizeSPM'].process.nodes_activation.ReorientAnatomy = True
            self.add_link(
                'normalization_allow_retry_initialization->PrepareSubject.Normalization_NormalizeSPM_allow_retry_initialization')
            self.add_link(
                'normalization_allow_retry_initialization->Renorm.Normalization_NormalizeSPM_allow_retry_initialization')
            self.export_parameter(
                'PrepareSubject',
                'Normalization_NormalizeSPM_spm_transformation',
                'normalization_spm_native_transformation_pass1')
            self.export_parameter(
                'Renorm', 'Normalization_NormalizeSPM_spm_transformation',
                'normalization_spm_native_transformation')
            self.do_not_export.add(
                ('Renorm', 'Normalization_NormalizeSPM_ReorientAnatomy_output_t1mri'))
            self.export_parameter('PrepareSubject',
                                  'Normalization_NormalizeSPM_NormalizeSPM',
                                  'spm_normalization_version')
            self.add_link('spm_normalization_version->'
                          'Renorm.Normalization_NormalizeSPM_NormalizeSPM')

        if 'NormalizeFSL' \
                in self.nodes['PrepareSubject'].process.nodes[
                    'Normalization'].process.nodes:
            self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes[
                'NormalizeFSL'].process.nodes_activation.ReorientAnatomy = True
            self.nodes['Renorm'].process.nodes['Normalization'].process.nodes['NormalizeFSL'].process.nodes_activation.ReorientAnatomy = True
            self.add_link(
                'normalization_allow_retry_initialization->PrepareSubject.Normalization_NormalizeFSL_allow_retry_initialization')
            self.add_link(
                'normalization_allow_retry_initialization->Renorm.Normalization_NormalizeFSL_allow_retry_initialization')
            self.export_parameter(
                'PrepareSubject',
                'Normalization_NormalizeFSL_NormalizeFSL_transformation_matrix',
                'normalization_fsl_native_transformation_pass1')
            self.export_parameter(
                'Renorm',
                'Normalization_NormalizeFSL_NormalizeFSL_transformation_matrix',
                'normalization_fsl_native_transformation')
            self.do_not_export.add(
                ('Renorm', 'Normalization_NormalizeFSL_ReorientAnatomy_output_t1mri'))

        if 'NormalizeBaladin' \
                in self.nodes['PrepareSubject'].process.nodes[
                    'Normalization'].process.nodes:
            self.export_parameter(
                'PrepareSubject',
                'Normalization_NormalizeBaladin_NormalizeBaladin_transformation_matrix',
                'normalization_baladin_native_transformation_pass1')
            self.export_parameter(
                'Renorm',
                'Normalization_NormalizeBaladin_NormalizeBaladin_transformation_matrix',
                'normalization_baladin_native_transformation')
            self.do_not_export.add(
                ('Renorm', 'Normalization_NormalizeBaladin_ReorientAnatomy_output_t1mri'))
            # disable it if baladin is not in the path
            if not distutils.spawn.find_executable('baladin'):
                self.nodes['PrepareSubject'].process.nodes['Normalization'].\
                    process.nodes['NormalizeBaladin'].enabled = False

        if 'Normalization_AimsMIRegister' \
                in self.nodes['PrepareSubject'].process.nodes[
                    'Normalization'].process.nodes:
            self.do_not_export.add(
                ('PrepareSubject', 'Normalization_Normalization_AimsMIRegister_transformation_to_template'))
            self.do_not_export.add(
                ('PrepareSubject', 'Normalization_Normalization_AimsMIRegister_transformation_to_ACPC'))
            self.do_not_export.add(
                ('Renorm', 'Normalization_Normalization_AimsMIRegister_transformation_to_template'))
            self.do_not_export.add(
                ('Renorm', 'Normalization_Normalization_AimsMIRegister_transformation_to_ACPC'))

        if autoexport_nodes_parameters:
            self.autoexport_nodes_parameters()

        self.nodes['GreyWhiteClassification'].plugs['side'].optional = True
        self.nodes['GreyWhiteClassification'].set_plug_value('side', 'left')
        self.nodes['GreyWhiteClassification_1'].plugs['side'].optional = True
        self.nodes['GreyWhiteClassification_1'].set_plug_value('side', 'right')

        # check normalization type
        self.on_trait_change(self.ensure_use_allowed_normalization,
                             'Normalization_select_Normalization_pipeline')
        self.on_trait_change(self._check_renormalization, 'select_Talairach')

        # default settings
        self.select_Talairach = 'Normalization'
        self.normalization_allow_retry_initialization = True
        self.compute_fold_meshes = True
        self.HistoAnalysis_use_hfiltered = True
        self.HistoAnalysis_use_wridges = True
        self.SplitBrain_use_ridges = True
        self.SplitBrain_use_template = True
        self.CorticalFoldsGraph_graph_version = '3.1'
        self.allow_multithreading = True
        self.perform_skull_stripped_renormalization = 'skull_stripped'

        self.nodes_activation.SulciRecognition = True
        self.nodes_activation.SulciRecognition_1 = True

        # nodes position in Pipeline*View
        self.node_position = {'BiasCorrection': (2149., 1157.),
                              'BrainSegmentation': (2746., 2089.),
                              'CorticalFoldsGraph': (6470., 2061.),
                              'CorticalFoldsGraph_1': (6470., 608.),
                              'GreyWhiteClassification': (4973., 1982.),
                              'GreyWhiteClassification_1': (4973., 1012.),
                              'GreyWhiteMesh': (6234., 1785.),
                              'GreyWhiteMesh_1': (6234., 530.),
                              'GreyWhiteTopology': (5397., 1911.),
                              'GreyWhiteTopology_1': (5397., 573.),
                              'HeadMesh': (2767., 565.),
                              'HistoAnalysis': (2472., 1040.),
                              'PialMesh': (6222., 1910.),
                              'PialMesh_1': (6222., 690.),
                              'PrepareSubject': (1062., 2159.),
                              'Renorm': (3048., 2368.),
                              'SplitBrain': (4649., 1261.),
                              'SulcalMorphometry': (7843., 2278.),
                              'SulciRecognition': (6854., 1954.),
                              'SulciRecognition_1': (6854., 636.),
                              'SulciSkeleton': (5873., 2387.),
                              'SulciSkeleton_1': (5873., 875.),
                              'TalairachTransformation': (4943., 3313.),
                              'importation': (703., 2820.),
                              'inputs': (0.0, 0.0),
                              'outputs': (8179., 700.),
                              'select_Talairach': (5297., 3419.),
                              'select_renormalization_commissures': (4134., 2217.),
                              'select_renormalization_transform': (5762., 3201.)}

        self.nodes['PrepareSubject'].process.node_position = {
            'Normalization': (161.4, 227.6),
            'StandardACPC': (272.8, -169.),
            'TalairachFromNormalization': (684.6, 485.4),
            'inputs': (-510.8, 14.8),
            'outputs': (1185.4, 441.8),
            'select_AC_PC_Or_Normalization': (925.6, 189.4)}

        self.nodes['PrepareSubject'].process.nodes['Normalization'] \
            .process.node_position = {
            'Normalization_AimsMIRegister': (538., 1375.),
            'NormalizeBaladin': (479., 1041.),
            'NormalizeFSL': (475., 0.0),
            'NormalizeSPM': (479., 489.5),
            'inputs': (0.0, 660.),
            'outputs': (1212., 855.),
            'select_Normalization_pipeline': (846., 764.)}

        if 'NormalizeBaladin' in self.nodes['PrepareSubject'].process \
                .nodes['Normalization'].process.nodes:
            self.nodes['PrepareSubject'].process.nodes['Normalization'] \
                .process.nodes['NormalizeBaladin'].process.node_position \
                = {
                    'ConvertBaladinNormalizationToAIMS': (318.0, 104.0),
                    'NormalizeBaladin': (108.0, 393.0),
                    'ReorientAnatomy': (435.0, 299.0),
                    'inputs': (-208.0, 127.0),
                    'outputs': (699.0, 241.0)}

        self.nodes['Renorm'].process.node_position = {
            'Normalization': (832.0799999999998, 384.39999999999986),
            'SkullStripping': (672.1599999999999, 248.68),
            'TalairachFromNormalization': (1363.9600000000003, 79.84),
            'inputs': (50.0, 50.0),
            'outputs': (1646.84, 315.48)}

        self.nodes['Renorm'].process.nodes['Normalization'] \
            .process.node_position \
            = self.nodes['PrepareSubject'].process.nodes['Normalization'] \
            .process.node_position

        self.nodes['SulciRecognition'].process.node_position = {
            'SPAM_recognition09': (95.0, 340.0),
            'outputs': (756.0, 429.0),
            'recognition2000': (182.0, -5.0),
            'inputs': (-508.0, 245.0),
            'select_Sulci_Recognition': (497.0, 197.0)}

        self.nodes['SulciRecognition_1'].process.node_position \
            = self.nodes['SulciRecognition'].process.node_position

        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'] \
            .process.node_position = {
            'inputs': (-517.0, 255.0),
            'markovian_recognition': (238.0, 72.0),
            'outputs': (652.0, 510.0),
            'global_recognition': (-101.0, 60.0),
            'local_or_markovian': (456.0, 341.0),
            'local_recognition': (155.0, 404.0)}

        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'] \
            .process.node_position \
            = self.nodes['SulciRecognition'].process \
            .nodes['SPAM_recognition09'].process.node_position

        self.add_pipeline_step('importation', ['importation'])
        self.add_pipeline_step('orientation',
                               ['PrepareSubject', 'TalairachTransformation'])
        self.add_pipeline_step('bias_correction', ['BiasCorrection'])
        self.add_pipeline_step('histogram_analysis', ['HistoAnalysis'])
        self.add_pipeline_step('brain_extraction', ['BrainSegmentation'])
        self.add_pipeline_step('renormalization', ['Renorm'])
        self.add_pipeline_step('hemispheres_split',
                               ['SplitBrain'])
        self.add_pipeline_step('head_mesh', ['HeadMesh'])
        self.add_pipeline_step('grey_white_segmentation',
                               ['GreyWhiteClassification', 'GreyWhiteTopology',
                                'GreyWhiteClassification_1',
                                'GreyWhiteTopology_1'])
        self.add_pipeline_step('white_mesh',
                               ['GreyWhiteMesh', 'GreyWhiteMesh_1'])
        self.add_pipeline_step('pial_mesh', ['PialMesh', 'PialMesh_1'])
        self.add_pipeline_step('sulci',
                               ['SulciSkeleton', 'CorticalFoldsGraph',
                                'SulciSkeleton_1', 'CorticalFoldsGraph_1'])
        self.add_pipeline_step('sulci_labelling',
                               ['SulciRecognition', 'SulciRecognition_1'])
        self.add_pipeline_step('sulcal_morphometry', ['SulcalMorphometry'])

        # customize params order for nicer user GUI
        self.reorder_traits([
            't1mri', 'imported_t1mri', 'select_Talairach',
            'Normalization_select_Normalization_pipeline',
            'commissure_coordinates',
            'anterior_commissure', 'posterior_commissure',
            'interhemispheric_point', 'left_hemisphere_point',
            'normalized_t1mri', 'Talairach_transform', 't1mri_nobias',
            'histo_analysis', 'BrainSegmentation_brain_mask', 'split_brain',
            'HeadMesh_head_mesh', 'GreyWhiteClassification_grey_white',
            'GreyWhiteClassification_1_grey_white',
            'GreyWhiteTopology_hemi_cortex', 'GreyWhiteTopology_1_hemi_cortex',
            'GreyWhiteMesh_white_mesh', 'GreyWhiteMesh_1_white_mesh',
            'SulciSkeleton_skeleton', 'SulciSkeleton_1_skeleton',
            'PialMesh_pial_mesh', 'PialMesh_1_pial_mesh',
            'left_graph', 'right_graph', 'left_labelled_graph',
            'right_labelled_graph', 'sulcal_morpho_measures',
        ])

        # setup groups
        self.define_groups_as_steps()
        ungroup = ('t1mri', 'imported_t1mri', 'select_Talairach',
                   'Normalization_select_Normalization_pipeline',
                   'allow_flip_initial_MRI', 'fix_random_seed',
                   't1mri_nobias', 'histo_analysis',
                   'BrainSegmentation_brain_mask', 'split_brain',
                   'GreyWhiteClassification_grey_white',
                   'GreyWhiteClassification_1_grey_white',
                   'GreyWhiteTopology_hemi_cortex',
                   'GreyWhiteTopology_1_hemi_cortex',
                   'PialMesh_pial_mesh', 'PialMesh_1_pial_mesh',
                   'GreyWhiteMesh_white_mesh', 'GreyWhiteMesh_1_white_mesh',
                   'HeadMesh_head_mesh',
                   'left_graph', 'right_graph', 'left_labelled_graph',
                   'right_labelled_graph', 'select_sulci_recognition',
                   'sulcal_morpho_measures')
        for param in ungroup:
            del self.trait(param).groups
        self.trait('grey_white_topology_version').groups = ['segmentation']
        self.trait('pial_mesh_version').groups = ['segmentation']
        self.on_trait_change(self._change_graph_version,
                             'CorticalFoldsGraph_graph_version')
        self._change_graph_version(self.CorticalFoldsGraph_graph_version)
        self.visible_groups = set()

    def attach_config_activations(self):
        '''
        Set notification handlers on study_config variables use_spm, use_fsl
        to adapt activation of SPM and FSL nodes in the normalization steps,
        and the normalization switches values.
        Any previous notification will be removed first.
        '''
        study_config = self.get_study_config()
        self.detach_config_activation()
        study_config.on_trait_change(self._change_spm_activation, 'use_spm')
        study_config.on_trait_change(self._change_fsl_activation, 'use_fsl')
        self._change_spm_activation(study_config.use_spm)
        self._change_fsl_activation(study_config.use_fsl)

    def detach_config_activation(self):
        '''
        Remove SPM and FSL notification handlers, and release the reference to
        the study config.
        '''
        study_config = self.study_config
        study_config.on_trait_change(self._change_spm_activation, 'use_spm',
                                     remove=True)
        study_config.on_trait_change(self._change_fsl_activation, 'use_fsl',
                                     remove=True)

    def _change_spm_activation(self, dummy):
        '''
        Callback for study_config.use_spm state change
        '''
        enabled = self.study_config.use_spm
        if 'NormalizeSPM' in self.nodes['PrepareSubject'].process \
                .nodes['Normalization'].process.nodes:
            self.nodes['PrepareSubject'].process \
                .nodes['Normalization'].process.nodes['NormalizeSPM'].enabled \
                = enabled
            self.nodes['Renorm'].process \
                .nodes['Normalization'].process.nodes['NormalizeSPM'].enabled \
                = enabled
        self.ensure_use_allowed_normalization()

    def _change_fsl_activation(self, dummy):
        '''
        Callback for study_config.use_fsl state change
        '''
        enabled = self.study_config.use_fsl
        if 'NormalizeFSL' in self.nodes['PrepareSubject'].process \
                .nodes['Normalization'].process.nodes:
            self.nodes['PrepareSubject'].process \
                .nodes['Normalization'].process.nodes['NormalizeFSL'].enabled \
                = enabled
            self.nodes['Renorm'].process \
                .nodes['Normalization'].process.nodes['NormalizeFSL'].enabled \
                = enabled
        self.ensure_use_allowed_normalization()

    def ensure_use_allowed_normalization(self):
        '''
        If the currently selected normalization method is not enabled,
        changes the normalization switch value to take the first allowed one.
        SPM is the highest priority, other values are tested in the switch
        values order.
        '''
        nodes = self.nodes['PrepareSubject'].process.nodes[
            'Normalization'].process.nodes
        if nodes[self.Normalization_select_Normalization_pipeline].enabled:
            return  # OK, nothing to change.
        values = self.trait(
            'Normalization_select_Normalization_pipeline').trait_type.values
        # reorder: spm first
        if 'NormalizeSPM' in values:
            values = list(values)
            values.remove('NormalizeSPM')
            values = ['NormalizeSPM'] + values
        for value in values:
            if nodes[value].enabled:
                self.Normalization_select_Normalization_pipeline = value
                break

    def _check_renormalization(self):
        # if not using normalization renormalization should be disabled too.
        if self.select_Talairach == 'StandardACPC':
            self.perform_skull_stripped_renormalization = 'initial'

    def _change_graph_version(self, value):
        try:
            from capsul.attributes.completion_engine \
                import ProcessCompletionEngine
        except ImportError:
            return
        compl = ProcessCompletionEngine.get_completion_engine(self)
        if compl is not None:
            attributes = compl.get_attribute_values()
            if attributes.trait('graph_version') is not None \
                    and attributes.graph_version != value:
                attributes.graph_version = value
                compl.complete_parameters()
