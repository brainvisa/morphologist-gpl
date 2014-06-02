
from __future__ import absolute_import
import morphologist.capsul.morphologist

class CustomMorphologist(morphologist.capsul.morphologist.morphologist):

    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        super(CustomMorphologist, self).__init__(False, **kwargs)
        if autoexport_nodes_parameters:
            self.export_internal_parameters()

        # temporary tuning - should be removed when the pipeline infrastructure
        # is working properly...
        #self.nodes[''].plugs['PrepareSubject_TalairachFromNormalization_source_referential'].activated = True
        #self.nodes[''].plugs['PrepareSubject_TalairachFromNormalization_normalized_referential'].activated = True
        #self.nodes[''].plugs['PrepareSubject_TalairachFromNormalization_transform_chain_ACPC_to_Normalized'].activated = True
        #self.nodes[''].plugs['BiasCorrection_field'].activated = True
        #self.nodes['BiasCorrection'].plugs['field'].activated = True
        #self.nodes[''].plugs['BiasCorrection_hfiltered'].activated = True
        #self.nodes['BiasCorrection'].plugs['hfiltered'].activated = True
        #self.nodes[''].plugs['BiasCorrection_white_ridges'].activated = True
        #self.nodes['BiasCorrection'].plugs['white_ridges'].activated = True
        #self.nodes[''].plugs['BiasCorrection_variance'].activated = True
        #self.nodes['BiasCorrection'].plugs['variance'].activated = True
        #self.nodes[''].plugs['BiasCorrection_edges'].activated = True
        #self.nodes['BiasCorrection'].plugs['edges'].activated = True
        #self.nodes[''].plugs['BiasCorrection_meancurvature'].activated = True
        #self.nodes['BiasCorrection'].plugs['meancurvature'].activated = True
        ##self.nodes[''].plugs['PrepareSubject_commissure_coordinates'].activated = True
        #self.nodes[''].plugs['HistoAnalysis_histo'].activated = True
        #self.nodes['HistoAnalysis'].plugs['histo'].activated = True
        #self.nodes[''].plugs['BrainSegmentation_brain_mask'].activated = True
        #self.nodes[''].plugs['GreyWhiteClassification_grey_white'].activated = True
        #self.nodes[''].plugs['GreyWhiteClassification_1_grey_white'].activated = True
        #self.nodes[''].plugs['GreyWhiteTopology_hemi_cortex'].activated = True
        #self.nodes[''].plugs['GreyWhiteTopology_1_hemi_cortex'].activated = True
        #self.nodes[''].plugs['GreyWhiteMesh_white_mesh'].activated = True
        #self.nodes[''].plugs['GreyWhiteMesh_1_white_mesh'].activated = True
        #self.nodes[''].plugs['SulciSkeleton_skeleton'].activated = True
        #self.nodes[''].plugs['SulciSkeleton_1_skeleton'].activated = True
        #self.nodes[''].plugs['SulciSkeleton_roots'].activated = True
        #self.nodes[''].plugs['SulciSkeleton_1_roots'].activated = True
        #self.nodes[''].plugs['PialMesh_pial_mesh'].activated = True
        #self.nodes[''].plugs['PialMesh_1_pial_mesh'].activated = True
        #self.nodes[''].plugs['CorticalFoldsGraph_sulci_voronoi'].activated \
            #= True
        #self.nodes['CorticalFoldsGraph'].plugs['sulci_voronoi'].activated \
            #= True
        #self.nodes[''].plugs['CorticalFoldsGraph_1_sulci_voronoi'].activated \
            #= True
        #self.nodes['CorticalFoldsGraph_1'].plugs['sulci_voronoi'].activated \
            #= True
        #self.nodes['HeadMesh'].activated = True
        #self.nodes[''].plugs['HeadMesh_head_mesh'].activated = True
        #self.nodes['HeadMesh'].plugs['head_mesh'].activated = True
        #self.nodes['HeadMesh'].plugs['t1mri_nobias'].activated = True
        #self.nodes['HeadMesh'].plugs['histo_analysis'].activated = True
        #self.nodes['HeadMesh'].plugs['keep_head_mask'].activated = True
        #self.nodes['HeadMesh'].plugs['remove_mask'].activated = True
        #self.nodes['HeadMesh'].plugs['first_slice'].activated = True
        #self.nodes['HeadMesh'].plugs['threshold'].activated = True
        #self.nodes['HeadMesh'].plugs['closing'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].\
            #process.nodes['global_recognition'].\
            #plugs['posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].\
            #process.nodes['global_recognition'].\
            #plugs['posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].plugs['global_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].plugs['global_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['global_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['global_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['global_recognition_model'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['global_recognition_model'].activated = True
        #self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_model'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_model'].activated = True
        #self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_labels_priors'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_labels_priors'].activated = True
        #self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_output_transformation'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_output_transformation'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].plugs['global_recognition_output_transformation'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].plugs['global_recognition_output_transformation'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['global_recognition_output_transformation'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['global_recognition_output_transformation'].activated = True
        #self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_output_t1_to_global_transformation'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_global_recognition_output_t1_to_global_transformation'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].plugs['global_recognition_output_t1_to_global_transformation'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].plugs['global_recognition_output_t1_to_global_transformation'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['global_recognition_output_t1_to_global_transformation'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['global_recognition_output_t1_to_global_transformation'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes['global_recognition'].plugs['output_t1_to_global_transformation'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes['global_recognition'].plugs['output_t1_to_global_transformation'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_model'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_model'].activated = True
        #self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_model'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_model'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].\
            #process.nodes['local_recognition'].\
            #plugs['posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].\
            #process.nodes['local_recognition'].\
            #plugs['posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].plugs['local_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].plugs['local_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_local_referentials'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_local_referentials'].activated = True
        #self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_local_referentials'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_local_referentials'].activated = True
        #self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_direction_priors'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_direction_priors'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_direction_priors'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_direction_priors'].activated = True
        #self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_angle_priors'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_angle_priors'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_angle_priors'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_angle_priors'].activated = True
        #self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_translation_priors'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_translation_priors'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_translation_priors'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_translation_priors'].activated = True
        #self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_output_local_transformations'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_local_recognition_output_local_transformations'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].plugs['local_recognition_output_local_transformations'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].plugs['local_recognition_output_local_transformations'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_output_local_transformations'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['local_recognition_output_local_transformations'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes['local_recognition'].plugs['output_local_transformations'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes['local_recognition'].plugs['output_local_transformations'].activated = True
        #self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_markovian_recognition_model'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_markovian_recognition_model'].activated = True
        #self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_markovian_recognition_segments_relations_model'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_markovian_recognition_segments_relations_model'].activated = True
        #self.nodes['SulciRecognition'].process.nodes[''].plugs['SPAM_recognition09_markovian_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes[''].plugs['SPAM_recognition09_markovian_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].plugs['markovian_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].plugs['markovian_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes['markovian_recognition'].plugs['posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes['markovian_recognition'].plugs['posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['markovian_recognition_posterior_probabilities'].activated = True
        #self.nodes['SulciRecognition_1'].process.nodes['SPAM_recognition09'].process.nodes[''].plugs['markovian_recognition_posterior_probabilities'].activated = True

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
        self.add_link('PrepareSubject.TalairachFromNormalization_Talairach_transform->select_Talairach.Normalization_switch_Talairach_transform')
        self.add_link('TalairachTransformation.Talairach_transform->select_Talairach.StandardACPC_switch_Talairach_transform')
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

        self.nodes['SulciRecognition'].enabled = True
        self.nodes['SulciRecognition_1'].enabled = True
        self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes['NormalizeSPM'].process.nodes['ReorientAnatomy'].enabled = True
        self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes['NormalizeFSL'].process.nodes['ReorientAnatomy'].enabled = True
        # self.select_Talairach = 'StandardACPC'

        # nodes position in Pipeline*View
        self.node_position = {
            'BiasCorrection': (210.9, 1149.7),
            'BrainSegmentation': (629.2, 1471.2),
            'CorticalFoldsGraph': (2045.1, 615.4),
            'CorticalFoldsGraph_1': (2021.3, 2705.7),
            'GreyWhiteClassification': (1251.3, 595.6),
            'GreyWhiteClassification_1': (1220.3, 2596.3),
            'GreyWhiteMesh': (1820.4, 351.3),
            'GreyWhiteMesh_1': (1796.6, 2409.3),
            'GreyWhiteTopology': (1476.7, 412.5),
            'GreyWhiteTopology_1': (1427.8, 2481.3),
            'HeadMesh': (1395., 1523.97),
            'HistoAnalysis': (428.8, 1199.2),
            'PialMesh': (1830.5, 497.5),
            'PialMesh_1': (1799.5, 2566.3),
            'PrepareSubject': (-489.2, 431.1),
            'SplitBrain': (933.4, 1356.2),
            'SulciRecognition': (2445.5, 368.5),
            'SulciRecognition_1': (2399.6, 2542.6),
            'SulciSkeleton': (1640.9, 655.5),
            'SulciSkeleton_1': (1624.3, 2699.2),
            'TalairachTransformation': (1230.5, 1316.5),
            'inputs': (-1335.3, 121.7),
            'outputs': (3006.3, 1046.7),
            'select_Talairach': (1525.9, 1425.4)}

        self.nodes['PrepareSubject'].process.node_position = {
            'Normalization': (161.4, 227.6),
            'StandardACPC': (272.8, -169.),
            'TalairachFromNormalization': (684.6, 485.4),
            'inputs': (-510.8, 14.8),
            'outputs': (1185.4, 441.8),
            'select_AC_PC_Or_Normalization': (925.6, 189.4)}

        self.nodes['PrepareSubject'].process.nodes['Normalization'] \
                .process.node_position = {
            'inputs': (-1134.0, 129.0),
            'Normalization_AimsMIRegister': (-410.4, 633.6),
            'outputs': (404.8, 390.4),
            'NormalizeFSL': (-481.6, -231.8),
            'NormalizeSPM': (-488.8, 186.8),
            'select_Normalization_pipeline': (8.6, 231.0)}

        if 'NormalizeFSL' in self.nodes['PrepareSubject'].process \
                .nodes['Normalization'].process.nodes:
            self.nodes['PrepareSubject'].process.nodes['Normalization']  \
                    .process.nodes['NormalizeFSL'].process.node_position = {
                'ReorientAnatomy': (431.0, 179.0),
                'outputs': (626.0, 360.0),
                'ConvertFSLnormalizationToAIMS': (206.0, 341.0),
                'NormalizeFSL': (-45.0, 116.0),
                'inputs': (-492.0, 241.0)}

        if 'NormalizeSPM' in self.nodes['PrepareSubject'].process \
                .nodes['Normalization'].process.nodes:
            self.nodes['PrepareSubject'].process.nodes['Normalization'] \
                    .process.nodes['NormalizeSPM'].process.node_position = {
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


