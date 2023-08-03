
from morphologist.capsul.axon.spmnormalizationpipeline \
    import SPMnormalizationPipeline


class SPMNormalization(SPMnormalizationPipeline):

    def pipeline_definition(self):
        super(SPMNormalization, self).pipeline_definition()
        # fix link from switch
        self.remove_link(
            'normalization_t1_spm12_reinit.transformations_informations'
            '->ConvertSPMnormalizationToAIMS.read')
        self.add_link(
            'NormalizeSPM.spm_transformation'
            '->ConvertSPMnormalizationToAIMS.read')

        # add converter as 1st step
        self.remove_link('t1mri->normalization_t1_spm12_reinit.anatomy_data')
        self.remove_link('t1mri->normalization_t1_spm8_reinit.anatomy_data')
        self.add_process(
            'converter',
            'morphologist.capsul.axon.aimsconverter.AimsConverter')
        self.add_link('t1mri->converter.read')
        self.add_link('converter.write->'
                      'normalization_t1_spm12_reinit.anatomy_data')
        self.add_link('converter.write->'
                      'normalization_t1_spm8_reinit.anatomy_data')

        self.nodes_activation.ReorientAnatomy = True
        self.on_attribute_change.add(self.change_flip,
                                     'allow_flip_initial_MRI')
        self.nodes['converter'].field('write').extensions = ['.nii']
        self.nodes['converter'].field('write').optional = False
        self.nodes['converter'].field('removeSource').optional = True
        self.nodes['converter'].field('ascii').optional = True
        self.nodes['converter'].field('rescaleDynamic').optional = True
        self.nodes['converter'].field('useInputTypeLimits').optional = True
        self.nodes['converter'].plugs['write'].optional = False
        self.nodes['converter'].plugs['removeSource'].optional = True
        self.nodes['converter'].plugs['ascii'].optional = True
        self.nodes['converter'].plugs['rescaleDynamic'].optional = True
        self.nodes['converter'].plugs['useInputTypeLimits'].optional = True

        #if not True:  ### FIXME self.get_study_config().use_spm:
            #self.nodes['normalization_t1_spm12_reinit'].enabled = False
            #self.nodes['normalization_t1_spm8_reinit'].enabled = False
        #else:
            #if True:  ## FIXME self.get_study_config().spm_version in ('12', None, Undefined):
                #self.nodes['normalization_t1_spm8_reinit'].enabled = False
                #self.NormalizeSPM = 'normalization_t1_spm12_reinit'
            #else:
                #self.nodes['normalization_t1_spm12_reinit'].enabled = False
                #self.NormalizeSPM = 'normalization_t1_spm8_reinit'

        self.node_position = {
            'ConvertSPMnormalizationToAIMS':
                (1813.678349526814, 93.33386790220817),
            'NormalizeSPM': (1178.4839657334387, 220.82146790220816),
            'ReorientAnatomy': (2168.1605009069403, 134.07556419558358),
            'converter': (341.7590504731861, 224.84488395110424),
            'inputs': (-263.40589132492113, -2.842170943040401e-14),
            'normalization_t1_spm12_reinit': (674.1066, 193.56869999999992),
            'normalization_t1_spm8_reinit': (672.6066, 526.7061),
            'outputs': (2740.6161075315463, 303.35412961356474)
        }

    def change_flip(self, value):
        self.nodes_activation.ReorientAnatomy = value
