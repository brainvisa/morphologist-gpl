
from .axon.fslnormalizationpipeline import FSLnormalizationPipeline
from .axon.normalization_fsl_reinit import Normalization_FSL_reinit


Normalization_FSL_reinit.requirements = {
    'fsl': 'any'
}

# cleanup in order to leave only Morphologist as a Process class in the
# module (facilitates naming)
del Normalization_FSL_reinit


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
        self.on_attribute_change.add(self.change_flip,
                                     'allow_flip_initial_MRI')

        self.nodes['converter'].field('write').allowed_extensions = ['.nii']
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

        self.node_position = {
            'ConvertFSLnormalizationToAIMS': (781., 193.),
            'NormalizeFSL': (560., 36.),
            'ReorientAnatomy': (1063., 264.),
            'converter': (387.5, 0.0),
            'inputs': (0.0, 112.),
            'outputs': (1326., 144.)}

    def change_flip(self, value):
        self.nodes_activation.ReorientAnatomy = value
