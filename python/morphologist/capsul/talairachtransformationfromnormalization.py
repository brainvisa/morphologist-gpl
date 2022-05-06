# -*- coding: utf-8 -*-

from soma.controller import File, undefined

import morphologist.capsul.axon.talairachtransformationfromnormalization


class TalairachTransformationFromNormalization(
    morphologist.capsul.axon.talairachtransformationfromnormalization.
        TalairachTransformationFromNormalization):
    def __init__(self, **kwargs):
        super(TalairachTransformationFromNormalization, self).__init__(**kwargs)
        self.remove_field('transform_chain_ACPC_to_Normalized')
        self.add_field('transform_chain_ACPC_to_Normalized', File)
        self.transform_chain_ACPC_to_Normalized = undefined
