
import morphologist.capsul.axon.morphologistprocess
from traits.api import Undefined, File


class MorphologistSimple(
        morphologist.capsul.axon.morphologistprocess.morphologistProcess):

    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        super(MorphologistSimple, self).__init__(**kwargs)
        self.remove_trait('tal_to_normalized_transform')
        self.add_trait('tal_to_normalized_transform', File())
        self.tal_to_normalized_transform = Undefined
