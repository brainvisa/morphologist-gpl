
from __future__ import absolute_import
from morphologist.capsul.axon.spmnormalizationpipeline \
    import SPMnormalizationPipeline
from traits.api import Undefined, Bool, File, Set
import six

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
        self.add_link(
            'ConvertSPMnormalizationToAIMS.write->transformation')

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
        self.on_trait_change(self.change_flip, 'allow_flip_initial_MRI')
        self.nodes['converter'].process.trait('write').allowed_extensions \
            = ['.nii']
        self.nodes['converter'].process.trait('write').optional = False
        self.nodes['converter'].process.trait('removeSource').optional = True
        self.nodes['converter'].process.trait('ascii').optional = True
        self.nodes['converter'].process.trait('rescaleDynamic').optional = True
        self.nodes['converter'].process.trait('useInputTypeLimits').optional = True
        self.nodes['converter'].plugs['removeSource'].optional = True
        self.nodes['converter'].plugs['ascii'].optional = True
        self.nodes['converter'].plugs['rescaleDynamic'].optional = True
        self.nodes['converter'].plugs['useInputTypeLimits'].optional = True

        if not self.get_study_config().use_spm:
            self.nodes['normalization_t1_spm12_reinit'].enabled = False
            self.nodes['normalization_t1_spm8_reinit'].enabled = False
        else:
            if self.get_study_config().spm_version in ('12', None):
                self.nodes['normalization_t1_spm8_reinit'].enabled = False
                self.NormalizeSPM = 'normalization_t1_spm12_reinit'
            else:
                self.nodes['normalization_t1_spm12_reinit'].enabled = False
                self.NormalizeSPM = 'normalization_t1_spm8_reinit'

        self.node_position = {
            'ConvertSPMnormalizationToAIMS': (1302., 99.),
            'NormalizeSPM': (863., 195.),
            'ReorientAnatomy': (1587., 9.),
            'converter': (417., 206.),
            'inputs': (0.0, 0.0),
            'normalization_t1_spm12_reinit': (598., 172.),
            'normalization_t1_spm8_reinit': (599., 424.),
            'outputs': (1876., 153.)}

    def change_flip(self, value):
        self.nodes_activation.ReorientAnatomy = value

