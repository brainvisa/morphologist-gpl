
from __future__ import absolute_import
import morphologist.capsul.morphologist
from traits.api import Undefined, Bool, File

class CustomMorphologist(morphologist.capsul.morphologist.morphologist):

    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        super(CustomMorphologist, self).__init__(
            autoexport_nodes_parameters, **kwargs)


        # if this line is in pipeline_definition(), it has no effect...
        #self.GreyWhiteClassification_1_side = 'right'

    def pipeline_definition(self):
        autoexport_nodes_parameters = self._autoexport_nodes_parameters
        self._autoexport_nodes_parameters = False
        super(CustomMorphologist, self).pipeline_definition()
        self._autoexport_nodes_parameters = autoexport_nodes_parameters

        self.add_switch('select_Talairach',
            ['StandardACPC', 'Normalization'],
            ['Talairach_transform'])

        self.add_switch('select_renormalization_commissures',
            ['initial', 'skull_stripped'],
            ['commissure_coordinates'], export_switch=False)
        self.add_switch('select_renormalization_transform',
            ['initial', 'skull_stripped'],
            ['Talairach_transform'], export_switch=False)

        # fix initial values of switches: should be Undefined, not None.
        self.nodes['select_Talairach'].StandardACPC_switch_Talairach_transform = Undefined
        self.nodes['select_Talairach'].Normalization_switch_Talairach_transform = Undefined
        self.nodes['select_renormalization_transform'].skull_stripped_switch_Talairach_transform = Undefined
        self.nodes['select_renormalization_transform'].initial_switch_Talairach_transform = Undefined
        self.nodes['select_renormalization_commissures'].skull_stripped_switch_commissure_coordinates = Undefined
        self.nodes['select_renormalization_commissures'].initial_switch_commissure_coordinates = Undefined

        self.export_parameter('PrepareSubject', 'allow_flip_initial_MRI')
        self.export_parameter('PrepareSubject', 'Normalization_select_Normalization_pipeline')
        self.export_parameter(
            'PrepareSubject',
            'TalairachFromNormalization_normalized_referential',
            'PrepareSubject_TalairachFromNormalization_normalized_referential')
        self.export_parameter(
            'PrepareSubject',
            'TalairachFromNormalization_source_referential',
            'PrepareSubject_TalairachFromNormalization_source_referential')
        self.export_parameter(
            'PrepareSubject',
            'TalairachFromNormalization_acpc_referential',
            'PrepareSubject_TalairachFromNormalization_acpc_referential')
        self.export_parameter(
            'PrepareSubject',
            'TalairachFromNormalization_transform_chain_ACPC_to_Normalized',
            'PrepareSubject_TalairachFromNormalization_transform_chain_ACPC_to_Normalized')

        self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes['Normalization_AimsMIRegister'].process.user_traits()['transformation_to_MNI'].optional = False
        self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes['Normalization_AimsMIRegister'].process.user_traits()['normalized_anatomy_data'].optional = False
        self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes['Normalization_AimsMIRegister'].plugs['transformation_to_MNI'].optional = False
        self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes['Normalization_AimsMIRegister'].plugs['normalized_anatomy_data'].optional = False

        self.nodes['PrepareSubject'].plugs['talairach_transformation'].optional = True
        self.nodes['PrepareSubject'].process.nodes['TalairachFromNormalization'].plugs['Talairach_transform'].optional = True
        self.nodes['PrepareSubject'].process.nodes['TalairachFromNormalization'].plugs['commissure_coordinates'].optional = False

        self.nodes['PrepareSubject'].process.export_parameter(
            'Normalization', 'transformation',
            'normalization_transformation', is_optional=True, weak_link=True)

        self.export_parameter(
            'PrepareSubject', 'normalization_transformation',
            is_optional=True, weak_link=True)
        self.export_parameter(
            'PrepareSubject', 'Normalization_normalized', 'normalized_t1mri',
            is_optional=True, weak_link=True)
        self.add_trait('normalization_allow_retry_initialization', Bool())

        self.nodes['Renorm'].plugs['transformation'].optional = True

        self.add_link('PrepareSubject.commissure_coordinates->Renorm.Normalization_commissures_coordinates')
        self.add_link('allow_flip_initial_MRI->Renorm.Normalization_allow_flip_initial_MRI')
        self.add_link('Normalization_select_Normalization_pipeline->Renorm.Normalization_select_Normalization_pipeline')
        self.add_link('PrepareSubject_TalairachFromNormalization_normalized_referential->Renorm.TalairachFromNormalization_normalized_referential')
        self.add_link('PrepareSubject_TalairachFromNormalization_source_referential->Renorm.TalairachFromNormalization_source_referential')
        self.add_link('PrepareSubject_TalairachFromNormalization_acpc_referential->Renorm.TalairachFromNormalization_acpc_referential')
        self.add_link('PrepareSubject_TalairachFromNormalization_transform_chain_ACPC_to_Normalized->Renorm.TalairachFromNormalization_transform_chain_ACPC_to_Normalized')
        self.add_link('Renorm.transformation->normalization_transformation',
                      weak_link=True)
        self.add_link('Renorm.Normalization_normalized->normalized_t1mri', weak_link=True)

        self.add_link('TalairachTransformation.Talairach_transform->select_Talairach.StandardACPC_switch_Talairach_transform')
        self.add_link('select_Talairach->PrepareSubject.select_AC_PC_Or_Normalization')
        self.remove_link('TalairachTransformation.Talairach_transform->CorticalFoldsGraph.talairach_transform')
        self.remove_link('TalairachTransformation.Talairach_transform->CorticalFoldsGraph_1.talairach_transform')

        self.export_parameter('select_renormalization_commissures',
            'switch', 'perform_skull_stripped_renormalization')
        self.export_parameter('select_renormalization_commissures',
            'commissure_coordinates', 'commissure_coordinates')
        self.export_parameter('select_renormalization_transform',
            'Talairach_transform', 'Talairach_transform')
        self.add_link('perform_skull_stripped_renormalization->select_renormalization_transform.switch')
        self.add_link('PrepareSubject.commissure_coordinates->select_renormalization_commissures.initial_switch_commissure_coordinates')
        self.add_link('PrepareSubject.talairach_transformation->select_Talairach.Normalization_switch_Talairach_transform')
        self.add_link('select_Talairach.Talairach_transform->select_renormalization_transform.initial_switch_Talairach_transform')
        self.add_link('Renorm.commissure_coordinates->select_renormalization_commissures.skull_stripped_switch_commissure_coordinates')
        self.add_link('Renorm.talairach_transformation->select_renormalization_transform.skull_stripped_switch_Talairach_transform')

        self.remove_link('Renorm.commissure_coordinates->Renorm_commissure_coordinates')
        self.remove_trait('Renorm_commissure_coordinates')

        # why does this one exist ? FIXME
        #self.remove_link('PrepareSubject.commissure_coordinates->Renorm_TalairachFromNormalization_commissure_coordinates')

        self.add_link('select_renormalization_transform.Talairach_transform->CorticalFoldsGraph.talairach_transform')
        self.add_link('select_renormalization_transform.Talairach_transform->CorticalFoldsGraph_1.talairach_transform')

        self.remove_link('PrepareSubject.commissure_coordinates->SplitBrain.commissure_coordinates')
        self.add_link('select_renormalization_commissures.commissure_coordinates->SplitBrain.commissure_coordinates')

        # plug commissure_coordinates and Talairach_transform params from
        # switches to other boxes
        self.remove_link('PrepareSubject.commissure_coordinates->GreyWhiteClassification.commissure_coordinates')
        self.add_link('select_renormalization_commissures.commissure_coordinates->GreyWhiteClassification.commissure_coordinates')
        self.remove_link('PrepareSubject.commissure_coordinates->GreyWhiteClassification_1.commissure_coordinates')
        self.add_link('select_renormalization_commissures.commissure_coordinates->GreyWhiteClassification_1.commissure_coordinates')

        self.remove_link('PrepareSubject.commissure_coordinates->CorticalFoldsGraph.commissure_coordinates')
        self.add_link('select_renormalization_commissures.commissure_coordinates->CorticalFoldsGraph.commissure_coordinates')
        self.remove_link('PrepareSubject.commissure_coordinates->CorticalFoldsGraph_1.commissure_coordinates')
        self.add_link('select_renormalization_commissures.commissure_coordinates->CorticalFoldsGraph_1.commissure_coordinates')

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
        self.perform_skull_stripped_renormalization = 'skull_stripped'

        self.nodes_activation.SulciRecognition = True
        self.nodes_activation.SulciRecognition_1 = True

        self.export_parameter(
          'PrepareSubject', 'reoriented_t1mri', is_optional=True)
        self.nodes['PrepareSubject'].process.nodes['select_AC_PC_Or_Normalization'].plugs['talairach_transformation'].optional = True

        #self.add_link('Renorm.Normalization_reoriented_t1mri->reoriented_t1mri')
        #self.remove_link('t1mri->BiasCorrection.t1mri')
        #self.add_link('PrepareSubject.reoriented_t1mri->BiasCorrection.t1mri')
        #self.remove_link('t1mri->Renorm.t1mri')
        #self.add_link('PrepareSubject.reoriented_t1mri->Renorm.t1mri')

        self.do_not_export.add(('Renorm', 'Normalization_reoriented_t1mri'))
        self.nodes['Renorm'].process.nodes['Normalization'].plugs['reoriented_t1mri'].optional = True
        self.nodes['Renorm'].process.nodes['Normalization'].process.nodes['select_Normalization_pipeline'].plugs['reoriented_t1mri'].optional = True

        if self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes.has_key('NormalizeSPM'):
            self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes['NormalizeSPM'].process.nodes_activation.ReorientAnatomy = True
            self.add_link('normalization_allow_retry_initialization->PrepareSubject.Normalization_NormalizeSPM_allow_retry_initialization')
            self.add_link('normalization_allow_retry_initialization->Renorm.Normalization_NormalizeSPM_allow_retry_initialization')
            self.export_parameter('PrepareSubject', 'Normalization_NormalizeSPM_spm_transformation', 'normalization_spm_native_transformation')
            self.add_link('Renorm.Normalization_NormalizeSPM_spm_transformation->normalization_spm_native_transformation')
            self.export_parameter('PrepareSubject', 'Normalization_NormalizeSPM_NormalizeSPM_job_file', 'normalization_spm_native_job_file')
            self.add_link('Renorm.Normalization_NormalizeSPM_NormalizeSPM_job_file->normalization_spm_native_job_file')
            self.do_not_export.add(('Renorm', 'Normalization_NormalizeSPM_ReorientAnatomy_output_t1mri'))

        if self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes.has_key('NormalizeFSL'):
            self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes['NormalizeFSL'].process.nodes_activation.ReorientAnatomy = True
            self.add_link('normalization_allow_retry_initialization->PrepareSubject.Normalization_NormalizeFSL_allow_retry_initialization')
            self.add_link('normalization_allow_retry_initialization->Renorm.Normalization_NormalizeFSL_allow_retry_initialization')
            self.export_parameter('PrepareSubject', 'Normalization_NormalizeFSL_NormalizeFSL_transformation_matrix', 'normalization_fsl_native_transformation')
            self.add_link('Renorm.Normalization_NormalizeFSL_NormalizeFSL_transformation_matrix->normalization_fsl_native_transformation')
            self.do_not_export.add(('Renorm', 'Normalization_NormalizeFSL_ReorientAnatomy_output_t1mri'))

        if self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes.has_key('NormalizeBaladin'):
            self.export_parameter('PrepareSubject', 'Normalization_NormalizeBaladin_NormalizeBaladin_transformation_matrix', 'normalization_baladin_native_transformation')
            self.add_link('Renorm.Normalization_NormalizeBaladin_NormalizeBaladin_transformation_matrix->normalization_baladin_native_transformation')
            self.do_not_export.add(('Renorm', 'Normalization_NormalizeBaladin_ReorientAnatomy_output_t1mri'))

        if self.nodes['PrepareSubject'].process.nodes['Normalization'].process.nodes.has_key('Normalization_AimsMIRegister'):
            self.do_not_export.add(('PrepareSubject', 'Normalization_Normalization_AimsMIRegister_transformation_to_template'))
            self.do_not_export.add(('PrepareSubject', 'Normalization_Normalization_AimsMIRegister_transformation_to_ACPC'))
            self.do_not_export.add(('Renorm', 'Normalization_Normalization_AimsMIRegister_transformation_to_template'))
            self.do_not_export.add(('Renorm', 'Normalization_Normalization_AimsMIRegister_transformation_to_ACPC'))

        if autoexport_nodes_parameters:
            self.autoexport_nodes_parameters()

        self.nodes['GreyWhiteClassification'].plugs['side'].optional = True
        self.nodes['GreyWhiteClassification'].set_plug_value('side', 'left')
        self.nodes['GreyWhiteClassification_1'].plugs['side'].optional = True
        self.nodes['GreyWhiteClassification_1'].set_plug_value('side', 'right')

        # nodes position in Pipeline*View
        self.node_position = {'BiasCorrection': (210.9, 1149.7),
            'BrainSegmentation': (629.2, 1471.2),
            'CorticalFoldsGraph': (2608.3760217599993, 589.6010982399999),
            'CorticalFoldsGraph_1': (2571.6765708800003, 2731.49890176),
            'GreyWhiteClassification': (1775.8776691199998, 565.50128128),
            'GreyWhiteClassification_1': (1663.1811468799995, 2716.6948748799996),
            'GreyWhiteMesh': (2405.1751065599997, 347.00018303999997),
            'GreyWhiteMesh_1': (2278.17949952, 2409.2999999999997),
            'GreyWhiteTopology': (1992.6780352, 369.50183039999996),
            'GreyWhiteTopology_1': (1866.3813299199999, 2481.2999999999997),
            'HeadMesh': (1885.17913344, 1867.2387206399999),
            'HistoAnalysis': (428.8, 1199.2),
            'PialMesh': (2393.77602176, 523.2989017600001),
            'PialMesh_1': (2289.6791334399995, 2557.7003660800005),
            'PrepareSubject': (-489.2, 431.1),
            'Renorm': (845.0725406719996, 62.38973235200024),
            'SplitBrain': (1477.767001599999, 1248.3938124799995),
            'SulciRecognition': (2918.4798655999994, 347.0009151999998),
            'SulciRecognition_1': (2902.67858432, 2615.6968883199993),
            'SulciSkeleton': (2169.7774860799996, 668.39945088),
            'SulciSkeleton_1': (2075.7807808, 2737.89835264),
            'TalairachTransformation': (1961.4688831999997, 1273.5018304),
            'inputs': (-1335.3, 121.7),
            'outputs': (3629.7734591999997, 1029.50073216),
            'select_Talairach': (2231.8330662399985, 1673.9494374399999),
            'select_renormalization': (2429.8292479999996, 1274.2534399999995),
            'select_renormalization_commissures': (1194.6271999999997,
                                                    1119.9775999999997),
            'select_renormalization_transform': (2563.670399999999, 1470.8831999999998)}

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
            'NormalizeBaladin': (-430.384, 908.816),
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

        self.add_pipeline_step('orientation',
                               ['PrepareSubject',  'TalairachTransformation'])
        self.add_pipeline_step('bias_correction',
                               ['BiasCorrection', 'HistoAnalysis'])
        self.add_pipeline_step('brain_extraction',
                               ['BrainSegmentation'])
        self.add_pipeline_step('renormalization', ['Renorm'])
        self.add_pipeline_step('hemispheres_split',
                               ['SplitBrain'])
        self.add_pipeline_step('head_mesh', ['HeadMesh'])
        self.add_pipeline_step('grey_white_segmentation',
                               ['GreyWhiteClassification', 'GreyWhiteTopology',
                                'GreyWhiteMesh', 'PialMesh',
                                'GreyWhiteClassification_1',
                                'GreyWhiteTopology_1', 'GreyWhiteMesh_1',
                                'PialMesh_1'])
        self.add_pipeline_step('sulci_graph',
                               ['SulciSkeleton', 'CorticalFoldsGraph',
                                'SulciSkeleton_1', 'CorticalFoldsGraph_1'])
        self.add_pipeline_step('sulci_recognition',
                               ['SulciRecognition', 'SulciRecognition_1'])

