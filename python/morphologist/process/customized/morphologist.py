
import morpho.morphologist

class CustomMorphologist(morpho.morphologist.morphologist):

    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        super(CustomMorphologist, self).__init__(False, **kwargs)
        if autoexport_nodes_parameters:
            self.export_internal_parameters()

        # temporary tuning - should be removed when the pipeline infrastructure
        # is working properly...
        self.nodes[''].plugs['PrepareSubject_TalairachFromNormalization_source_referential'].activated = True
        self.nodes[''].plugs['PrepareSubject_TalairachFromNormalization_normalized_referential'].activated = True
        self.nodes[''].plugs['PrepareSubject_TalairachFromNormalization_transform_chain_ACPC_to_Normalized'].activated = True
        self.nodes[''].plugs['BiasCorrection_field'].activated = True
        self.nodes['BiasCorrection'].plugs['field'].activated = True
        self.nodes[''].plugs['BiasCorrection_hfiltered'].activated = True
        self.nodes['BiasCorrection'].plugs['hfiltered'].activated = True
        self.nodes[''].plugs['BiasCorrection_white_ridges'].activated = True
        self.nodes['BiasCorrection'].plugs['white_ridges'].activated = True
        self.nodes[''].plugs['BiasCorrection_variance'].activated = True
        self.nodes['BiasCorrection'].plugs['variance'].activated = True
        self.nodes[''].plugs['BiasCorrection_edges'].activated = True
        self.nodes['BiasCorrection'].plugs['edges'].activated = True
        self.nodes[''].plugs['BiasCorrection_meancurvature'].activated = True
        self.nodes['BiasCorrection'].plugs['meancurvature'].activated = True
        #self.nodes[''].plugs['PrepareSubject_commissure_coordinates'].activated = True
        self.nodes[''].plugs['HistoAnalysis_histo'].activated = True
        self.nodes['HistoAnalysis'].plugs['histo'].activated = True
        self.nodes[''].plugs['BrainSegmentation_brain_mask'].activated = True
        self.nodes[''].plugs['GreyWhiteClassification_grey_white'].activated = True
        self.nodes[''].plugs['GreyWhiteClassification_1_grey_white'].activated = True
        self.nodes[''].plugs['GreyWhiteTopology_hemi_cortex'].activated = True
        self.nodes[''].plugs['GreyWhiteTopology_1_hemi_cortex'].activated = True
        self.nodes[''].plugs['GreyWhiteMesh_white_mesh'].activated = True
        self.nodes[''].plugs['GreyWhiteMesh_1_white_mesh'].activated = True
        self.nodes[''].plugs['SulciSkeleton_skeleton'].activated = True
        self.nodes[''].plugs['SulciSkeleton_1_skeleton'].activated = True
        self.nodes[''].plugs['SulciSkeleton_roots'].activated = True
        self.nodes[''].plugs['SulciSkeleton_1_roots'].activated = True
        self.nodes[''].plugs['PialMesh_pial_mesh'].activated = True
        self.nodes[''].plugs['PialMesh_1_pial_mesh'].activated = True
        self.nodes[''].plugs['CorticalFoldsGraph_sulci_voronoi'].activated \
            = True
        self.nodes['CorticalFoldsGraph'].plugs['sulci_voronoi'].activated \
            = True
        self.nodes[''].plugs['CorticalFoldsGraph_1_sulci_voronoi'].activated \
            = True
        self.nodes['CorticalFoldsGraph_1'].plugs['sulci_voronoi'].activated \
            = True
        self.nodes['HeadMesh'].activated = True
        self.nodes[''].plugs['HeadMesh_head_mesh'].activated = True
        self.nodes['HeadMesh'].plugs['head_mesh'].activated = True
        self.nodes['HeadMesh'].plugs['t1mri_nobias'].activated = True
        self.nodes['HeadMesh'].plugs['histo_analysis'].activated = True
        self.nodes['HeadMesh'].plugs['keep_head_mask'].activated = True
        self.nodes['HeadMesh'].plugs['remove_mask'].activated = True
        self.nodes['HeadMesh'].plugs['first_slice'].activated = True
        self.nodes['HeadMesh'].plugs['threshold'].activated = True
        self.nodes['HeadMesh'].plugs['closing'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].\
            process.nodes['global_recognition'].\
            plugs['posterior_probabilities'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].\
            process.nodes['global_recognition'].\
            plugs['posterior_probabilities'].activated = True
        self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_posterior_probabilities'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_posterior_probabilities'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].plugs['global_recognition_posterior_probabilities'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].plugs['global_recognition_posterior_probabilities'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['global_recognition_posterior_probabilities'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['global_recognition_posterior_probabilities'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['global_recognition_model'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['global_recognition_model'].activated = True
        self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_model'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_model'].activated = True
        self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_labels_priors'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_labels_priors'].activated = True
        self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_output_transformation'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_output_transformation'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].plugs['global_recognition_output_transformation'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].plugs['global_recognition_output_transformation'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['global_recognition_output_transformation'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['global_recognition_output_transformation'].activated = True
        self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_output_t1_to_global_transformation'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_output_t1_to_global_transformation'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].plugs['global_recognition_output_t1_to_global_transformation'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].plugs['global_recognition_output_t1_to_global_transformation'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['global_recognition_output_t1_to_global_transformation'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['global_recognition_output_t1_to_global_transformation'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes['global_recognition'].plugs['output_t1_to_global_transformation'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes['global_recognition'].plugs['output_t1_to_global_transformation'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_model'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_model'].activated = True
        self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_model'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_model'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].\
            process.nodes['local_recognition'].\
            plugs['posterior_probabilities'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].\
            process.nodes['local_recognition'].\
            plugs['posterior_probabilities'].activated = True
        self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_posterior_probabilities'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_posterior_probabilities'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].plugs['local_recognition_posterior_probabilities'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].plugs['local_recognition_posterior_probabilities'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_posterior_probabilities'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_posterior_probabilities'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_local_referentials'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_local_referentials'].activated = True
        self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_local_referentials'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_local_referentials'].activated = True
        self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_direction_priors'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_direction_priors'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_direction_priors'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_direction_priors'].activated = True
        self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_angle_priors'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_angle_priors'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_angle_priors'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_angle_priors'].activated = True
        self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_translation_priors'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_translation_priors'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_translation_priors'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_translation_priors'].activated = True
        self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_output_local_transformations'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_output_local_transformations'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].plugs['local_recognition_output_local_transformations'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].plugs['local_recognition_output_local_transformations'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_output_local_transformations'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_output_local_transformations'].activated = True
        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes['local_recognition'].plugs['output_local_transformations'].activated = True
        self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes['local_recognition'].plugs['output_local_transformations'].activated = True

        # if this line is in pipeline_definition(), it has no effect...
        self.GreyWhiteClassification_1_side = 'right'

    def pipeline_definition(self):
        super(CustomMorphologist, self).pipeline_definition()

        self.add_switch('select_Talairach',
            ['StandardACPC', 'Normalization'],
            ['Talairach_transform'])

        # export output parameter
        self.export_parameter('select_Talairach', 'Talairach_transform',
            'Talairach_transform')
        self.export_parameter('PrepareSubject', 'commissure_coordinates',
            'commissure_coordinates')
        self.add_link('PrepareSubject.TalairachFromNormalization_Talairach_transform->select_Talairach.StandardACPC_switch_Talairach_transform')
        self.add_link('TalairachTransformation.Talairach_transform->select_Talairach.Normalization_switch_Talairach_transform')
        self.add_link('select_Talairach->PrepareSubject.select_AC_PC_Or_Normalization')
        self.remove_link('TalairachTransformation.Talairach_transform->CorticalFoldsGraph.talairach_transform')
        self.remove_link('TalairachTransformation.Talairach_transform->CorticalFoldsGraph_1.talairach_transform')
        self.add_link('select_Talairach.Talairach_transform->CorticalFoldsGraph.talairach_transform')
        self.add_link('select_Talairach.Talairach_transform->CorticalFoldsGraph_1.talairach_transform')

        # reactivate Talairach node: will be triggered via the normalization 
        # flag
        self.nodes_activation.TalairachTransformation = True

        self.export_parameter('BiasCorrection', 'fix_random_seed', 
            'fix_random_seed' )
        self.add_link('fix_random_seed->HistoAnalysis.fix_random_seed')
        self.add_link('fix_random_seed->BrainSegmentation.fix_random_seed')
        self.add_link('fix_random_seed->SplitBrain.fix_random_seed')
        self.add_link('fix_random_seed->GreyWhiteClassification.fix_random_seed')
        self.add_link('fix_random_seed->GreyWhiteTopology.fix_random_seed')
        self.add_link('fix_random_seed->SulciSkeleton.fix_random_seed')
        self.add_link('fix_random_seed->PialMesh.fix_random_seed')
        self.add_link('fix_random_seed->GreyWhiteClassification_1.fix_random_seed')
        self.add_link('fix_random_seed->GreyWhiteTopology_1.fix_random_seed')
        self.add_link('fix_random_seed->SulciSkeleton_1.fix_random_seed')
        self.add_link('fix_random_seed->PialMesh_1.fix_random_seed')

        self.export_parameter('CorticalFoldsGraph', 'graph_version', 
            'cortical_graph_version')
        self.export_parameter('CorticalFoldsGraph', 'compute_fold_meshes', 
            'compute_fold_meshes')
        self.export_parameter('CorticalFoldsGraph', 'allow_multithreading', 
            'allow_multithreading')
        self.export_parameter('CorticalFoldsGraph', 
            'write_cortex_mid_interface', 
            'CorticalFoldsGraph_write_cortex_mid_interface')

        self.add_link('cortical_graph_version->CorticalFoldsGraph_1.graph_version')
        self.add_link('compute_fold_meshes->CorticalFoldsGraph_1.compute_fold_meshes')
        self.add_link('allow_multithreading->CorticalFoldsGraph_1.allow_multithreading')
        self.add_link('CorticalFoldsGraph_write_cortex_mid_interface->CorticalFoldsGraph_1.write_cortex_mid_interface')

        self.export_parameter('SulciRecognition',
            'SPAM_recognition09_global_recognition_labels_translation_map',
            'SPAM_recognition_labels_translation_map')
        self.add_link('SPAM_recognition_labels_translation_map->SulciRecognition_1.SPAM_recognition09_global_recognition_labels_translation_map')

        # default settings
        self.select_Talairach = 'Normalization'
        self.PrepareSubject_Normalization_NormalizeSPM_allow_retry_initialization = True
        self.compute_fold_meshes = True
        self.HistoAnalysis_use_hfiltered = True
        self.HistoAnalysis_use_wridges = True
        self.SplitBrain_use_ridges = True
        self.SplitBrain_use_template = True
        self.cortical_graph_version = '3.1'
        self.allow_multithreading = True

        # nodes position in Pipeline*View
        self.node_position = {
            'BiasCorrection': (210.94167040000002, 1149.7378048),
            'BrainSegmentation': (629.1590399999998, 1471.2065279999997),
            'CorticalFoldsGraph': (2045.1370751999998, 615.4479360000003),
            'CorticalFoldsGraph_1': (2021.3345536, 2705.7220864),
            'GreyWhiteClassification': (1251.3162495999998, 595.5941632),
            'GreyWhiteClassification_1': (1220.3473664000003, 2596.2887935999997),
            'GreyWhiteMesh': (1820.3838719999999, 351.27974400000016),
            'GreyWhiteMesh_1': (1796.5813503999998, 2409.3052672000003),
            'GreyWhiteTopology': (1476.7275775999997, 412.5228800000002),
            'GreyWhiteTopology_1': (1427.8427904, 2481.2979456000003),
            'HeadMesh': (1394.9725439999997, 1523.9670528000001),
            'HistoAnalysis': (428.8299776, 1199.2138495999998),
            'PialMesh': (1830.4752895999995, 497.5320320000001),
            'PialMesh_1': (1799.5064064, 2566.3070976),
            'PrepareSubject': (-489.2466431999998, 431.06680319999987),
            'SplitBrain': (933.4003455999999, 1356.2156799999996),
            'SulciRecognition': (2445.5270656, 368.47659520000036),
            'SulciRecognition_1': (2399.6282623999996, 2542.3582976),
            'SulciSkeleton': (1640.8957696, 655.5210496000002),
            'SulciSkeleton_1': (1624.2596096000002, 2699.2138496),
            'TalairachTransformation': (1230.4752896, 1316.4716287999995),
            'inputs': (-1335.2975103999997, 121.66361600000005),
            'outputs': (3006.3192832000004, 1046.7175168000006),
            'select_Talairach': (1525.8988800000009, 1425.370752)}

        self.nodes['PrepareSubject'].process.node_position = {
            'Normalization': (161.36, 227.60000000000002),
            'StandardACPC': (272.8, -169.04),
            'TalairachFromNormalization': (684.56, 485.4),
            'inputs': (-510.75999999999993, 14.800000000000068),
            'outputs': (1185.3999999999999, 441.7599999999999),
            'select_AC_PC_Or_Normalization': (925.6399999999999, 189.44000000000005)}

        self.nodes['PrepareSubject'].process.nodes['Normalization'].process.node_position = {
            'inputs': (-1134.0, 129.0),
            'Normalization_AimsMIRegister': (-410.4, 633.6000000000001),
            'outputs': (404.79999999999995, 390.4),
            'NormalizeFSL': (-481.59999999999997, -231.8),
            'NormalizeSPM': (-488.8, 186.80000000000007),
            'select_Normalization_pipeline': (8.600000000000023, 231.0)}

        self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes['NormalizeFSL'].process.node_position = {
            'ReorientAnatomy': (431.0, 179.0),
            'outputs': (626.0, 360.0),
            'ConvertFSLnormalizationToAIMS': (206.0, 341.0),
            'NormalizeFSL': (-45.0, 116.0),
            'inputs': (-492.0, 241.0)}

        self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes['NormalizeSPM'].process.node_position = {
            'ReorientAnatomy': (404.0, 378.0),
            'outputs': (627.0, 232.0),
            'inputs': (-553.0, 218.0),
            'ConvertSPMnormalizationToAIMS': (193.0, 200.0),
            'NormalizeSPM': (-96.0, 365.0)}

        self.nodes['SulciRecognition'].process.node_position = {
            'SPAM_recognition09': (95.0, 340.0),
            'outputs': (756.0, 429.0),
            'recognition2000': (182.0, -5.0),
            'inputs': (-508.0, 245.0),
            'select_Sulci_Recognition': (497.0, 197.0)}

        self.nodes['SulciRecognition_1'].process.node_position \
            = self.nodes['SulciRecognition'].process.node_position

        self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.node_position = {
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


