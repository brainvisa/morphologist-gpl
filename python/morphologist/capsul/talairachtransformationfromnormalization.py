# -*- coding: utf-8 -*-
from __future__ import absolute_import

from soma.controller import File, undefined

import morphologist.capsul3.axon.talairachtransformationfromnormalization


class TalairachTransformationFromNormalization(
    morphologist.capsul3.axon.talairachtransformationfromnormalization.
        TalairachTransformationFromNormalization):
    def __init__(self, **kwargs):
        super(TalairachTransformationFromNormalization, self).__init__(**kwargs)
        self.remove_field('transform_chain_ACPC_to_Normalized')
        self.add_field('transform_chain_ACPC_to_Normalized', File)
        self.transform_chain_ACPC_to_Normalized = undefined
