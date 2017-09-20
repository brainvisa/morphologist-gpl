
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
        self.nodes_activation.ReorientAnatomy = True
        self.on_trait_change(self.change_flip, 'allow_flip_initial_MRI')

    def change_flip(self, value):
        self.nodes_activation.ReorientAnatomy = value

