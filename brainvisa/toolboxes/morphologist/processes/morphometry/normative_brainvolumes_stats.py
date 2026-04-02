
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
    covariables = None
    covar_csv = None
    if self.covariables_csv is not None:
        covar_csv = self.covariables_csv.fullPath()
        covariables = json.loads(self.covariables)
    hdr, morph, avg, std, sums, quantiles = \
        global_sulc_morpho.build_normative_brain_vol_stats(
            [d.fullPath() for d in self.brain_volumes_files],
            covar_csv=covar_csv, covariables=covariables)
    # subj_row = hdr.index('subject')  # normally 0
    stat_dict = {
        # 'subjects': [row[subj_row] for row in morph],
        'columns': [c for c in hdr if c != 'subject'],
        'averages': list(avg.astype(float)),
        'std': list(std.astype(float)),
        'quantiles': [list(x) for x in quantiles],
        'N': [int(x) for x in sums],
    }
    with open(self.stats.fullPath(), 'w') as f:
        json.dump(stat_dict, f)


