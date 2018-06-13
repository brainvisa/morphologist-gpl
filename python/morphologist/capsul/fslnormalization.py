
from __future__ import absolute_import
from morphologist.capsul.axon.fslnormalizationpipeline \
    import FSLnormalizationPipeline
from traits.api import Undefined, Bool, File, Set
import six


class FSLNormalization(FSLnormalizationPipeline):

    def pipeline_definition(self):
        super(FSLNormalization, self).pipeline_definition()

        # add converter as 1st step
        self.remove_link('t1mri->NormalizeFSL.anatomy_data')
        self.add_process(
            'converter',
            'morphologist.capsul.axon.aimsconverter.AimsConverter')
        self.add_link('t1mri->converter.read')
        self.add_link('converter.write->NormalizeFSL.anatomy_data')

        self.nodes_activation.ReorientAnatomy = True
        self.on_trait_change(self.change_flip, 'allow_flip_initial_MRI')

        self.nodes['converter'].process.trait('write').allowed_extensions \
            = ['.nii']
        self.nodes['converter'].process.trait('write').optional = False
        self.nodes['converter'].process.trait('removeSource').optional = True
        self.nodes['converter'].process.trait('ascii').optional = True
        self.nodes['converter'].process.trait('rescaleDynamic').optional = True
        self.nodes['converter'].process.trait(
            'useInputTypeLimits').optional = True
        self.nodes['converter'].plugs['removeSource'].optional = True
        self.nodes['converter'].plugs['ascii'].optional = True
        self.nodes['converter'].plugs['rescaleDynamic'].optional = True
        self.nodes['converter'].plugs['useInputTypeLimits'].optional = True

        self.node_position = {
            'ConvertFSLnormalizationToAIMS': (781., 193.),
            'NormalizeFSL': (560., 36.),
            'ReorientAnatomy': (1063., 264.),
            'converter': (387.5, 0.0),
            'inputs': (0.0, 112.),
            'outputs': (1326., 144.)}

    def change_flip(self, value):
        self.nodes_activation.ReorientAnatomy = value
