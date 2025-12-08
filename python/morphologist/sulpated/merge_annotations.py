#!/usr/bin/env python

from . import sulpated_data
import argparse
import sys
import os
import os.path as osp
import json
import numpy as np


def merge_annotations(sources, dest):
    print('merge:', sources)
    print('into:', dest)

    data = {}
    if not osp.exists(dest):
        os.makedirs(dest)
    out_dat = None

    first = True
    patterns = []
    region = None
    for source in sources:
        dat = sulpated_data.SulcalPatternsData(source, None)
        dat.update()
        data[source] = dat
        if first:
            # must init in a single thread, non concurrently
            dat.update_thread.join()
            first = False
            opatdefr = {}
            opatdef = {dat.region: opatdefr}
            opatdefr.update(dat.pattern_def[dat.region])
            for s in range(len(sources)):
                opatdef[dat.region].update({
                    f'{chr(65 + s)}_{k}': v
                    for k, v in dat.pattern_def[dat.region].items()})

            ofpatdef = {
                'database_definition': {
                    'database_filter': dat.db_filter,
                    'output_database_filter': dat.out_db_filter,
                    'region': dat.region,
                    'ro_database': dat.ro_database,
                    'sulci_database': dat.sulci_database,  # FIXME
                    'force_sulci_locks_state': False,
                },
                'patterns_definition': opatdef,
            }
            with open(osp.join(dest, 'patterns_def.json'), 'w') as f:
                json.dump(ofpatdef, f)

            out_dat = sulpated_data.SulcalPatternsData(dest, None)
            #out_dat.update()
            #out_dat.update_thread.join()

            out_dat.pattern_def = opatdef
            out_dat.region = dat.region
            out_dat.db_def = dat.db_def
            out_dat.db_filter = dat.db_filter
            out_dat.ro_database = dat.ro_database
            out_dat.sulci_database = dat.sulci_database  # FIXME
            out_dat.out_database = dest
            out_dat.out_db_filter = dat.out_db_filter
            out_dat.subjects = dat.subjects
            out_dat.version_file = osp.join(dest, 'data_versions.json')
            patterns = list(dat.pattern_def[dat.region].keys())

    for si, (source, dat) in enumerate(data.items()):
        dat.update_thread.join()
        # pat_def = dat.pattern_def[dat.region]
        #opd = out_dat.pattern_def[dat.region]
        #opd.update({f'{chr(65 + si)}_{k}': v for k, v in pat_def.items()})
        for sub, pitem in dat.patterns.items():
            for side, pattern in pitem.items():
                if side not in out_dat.patterns.setdefault(sub, {}):
                    pat = out_dat._new_pattern(sub, side, pattern.sulci_di)
                    out_dat.patterns[sub][side] = pat
                # print('before', sub, side, ':', out_dat.patterns[sub][side].patterns)
                for label, p in pattern.patterns.items():
                    # print('set state', sub, side, f'{chr(65 + si)}_{label}', p)
                    out_dat.set_pattern_state(
                        sub, side, f'{chr(65 + si)}_{label}', p)
                    # force implying <label>+ on -> <label> on
                    if label.endswith('+') and p.get('enabled'):
                        out_dat.set_pattern_state(
                            sub, side, f'{chr(65 + si)}_{label[:-1]}', p)
                # print('after:', out_dat.patterns[sub][side].patterns)
    print('patterns read')

    avg_agreement = {}
    npts = {}

    for sub, pitem in out_dat.patterns.items():
        for side, pattern in pitem.items():
            votes = {}
            for label, p in pattern.patterns.items():
                if label in patterns:
                    continue
                slabel = label[2:]
                # TODO we may use confidence factors to weight votes
                # w = p.get('confidence', 100.)
                v = int(p.get('enabled', 0))
                # if v == 0:
                #     w = 100 - w
                votes.setdefault(slabel, []).append(v)
            for label, values in votes.items():
                value = sum(values) / len(sources)
                print(sub, side, label, ':', value, values)
                p = pattern.patterns.get(label, {})
                bval = bool(round(value))
                value = value * 100
                p['enabled'] = bval
                if not bval:
                    value = 100. - value
                ag = avg_agreement.get(label, 0.)
                ag += value / 100.  # rescale agreement to [0.,1.]
                avg_agreement[label] = ag
                n = npts.get(label, 0)
                npts[label] = n + 1
                p['confidence'] = value
                values = values + [0] * (len(sources) - len(values))
                sigma = np.std(values)
                p['annotation'] = f'sigma: {sigma}'
                out_dat.set_pattern_state(sub, side, label, p)

    for label, n in npts.items():
        ntot = len(out_dat.subjects) * 2
        avg_a = (avg_agreement[label] + ntot - n) / ntot
        print('label:', label, 'npts:', n, ', tot:', ntot,
              ', agreement:', avg_a, avg_agreement[label])

    out_dat.save_all()



def main(argv):
    parser = argparse.ArgumentParser(
      'Merge annotations from several Sulpated sessions into a new session.')

    parser.add_argument('input', nargs='+', help='input session directories')
    parser.add_argument('-o', '--output', required=True,
                        help='output session directory')
    #parser.add_argument('-m', '--mode',
                        #help='merge mode (concat or maj) [default: concat]',
                        #default='concat')

    options = parser.parse_args()
    print(options)

    merge_annotations(options.input, options.output)


if __name__ == '__main__':
    main(sys.argv)
