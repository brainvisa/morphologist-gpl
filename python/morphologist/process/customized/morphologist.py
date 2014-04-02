
import morpho.morphologist

class CustomMorphologist(morpho.morphologist.morphologist):

    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        super(CustomMorphologist, self).__init__(False, **kwargs)
        self.set_autoexport_parameters(autoexport_nodes_parameters)
        self.export_internal_parameters()


    def pipeline_definition(self):
        super(CustomMorphologist, self).pipeline_definition()

        self.add_switch('select_Talairach',
            ['StandardACPC', 'Normalization'],
            ['Talairach_transform'])

        # export output parameter
        self.export_parameter('select_Talairach', 'Talairach_transform',
            'Talairach_transform')
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

