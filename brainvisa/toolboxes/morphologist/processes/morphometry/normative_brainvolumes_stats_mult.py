
from brainvisa.processes import *
from brainvisa.morphologist.morphometry import global_sulc_morpho
import json


name = 'Normative Brain Volumes Stats, multiple datasets'
userLevel = 1

signature = Signature(
    'dataset_description', ReadDiskItem(
        'Text file', ['YAML file', 'JSON file']),
    'stats', WriteDiskItem('Normative brain volumes stats', 'JSON file'),
)


def execution(self, context):
    ds_def = global_sulc_morpho.read_datasets_def(
        self.dataset_description.fullPath())
    stats = global_sulc_morpho.build_stratified_normative_brain_vol_stats(
        ds_def)
    global_sulc_morpho.save_stats(stats, self.stats.fullPath())
