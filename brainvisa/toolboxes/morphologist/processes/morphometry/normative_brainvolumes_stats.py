
from brainvisa.processes import *
from brainvisa.morphologist.morphometry import global_sulc_morpho
import json


name = 'Normative Brain Volumes Stats'
userLevel = 1

signature = Signature(
    'brain_volumes_files', ListOf(ReadDiskItem(
        'Brain volumetry measurements', 'CSV file')),
    'covariables_csv', ReadDiskItem('CSV file', ['CSV file', 'TSV file']),
    'stats', WriteDiskItem('Normative brain volumes stats', 'JSON file'),
    'covariables', String(),
)


def initialization(self):
    self.covariables = '["age", "sex"]'


def execution(self, context):
    ds = {
        'dataset': {
            'variables': {
            },
            'brain_morphometry': {
                'local': [f.fullPath() for f in self.brain_volumes_files],
            },
        },
    }
    covariables = json.loads(self.covariables)
    if isinstance(covariables, list):
        varskey = ', '.join(self.covariables)
        vardict = {}
        ds['dataset']['variables'][varskey] = {'local': vardict}
        for var in self.covariables:
            vardict[var] = self.covariables_csv.fullPath()
    else:
        for var, cvar in covariables.items():
            vardict = {}
            ds['dataset']['variables'][var] = {'local': vardict}
            vardict[cvar] = self.covariables_csv.fullPath()

    ds_def = global_sulc_morpho.read_datasets_def(ds)
    stats = global_sulc_morpho.build_stratified_normative_brain_vol_stats(
        ds_def)
    global_sulc_morpho.save_stats(stats, self.stats.fullPath())
