# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

import morpho.TalairachTransformationFromNormalization


class TalairachTransformationFromNormalization(
        morpho.TalairachTransformationFromNormalization.TalairachTransformationFromNormalization):
    def __init__(self, **kwargs):
        super(TalairachTransformationFromNormalization, self).__init__()
        self.remove_trait('transform_chain_ACPC_to_Normalized')
        self.add_trait('transform_chain_ACPC_to_Normalized', File())
        self.transform_chain_ACPC_to_Normalized = Undefined

