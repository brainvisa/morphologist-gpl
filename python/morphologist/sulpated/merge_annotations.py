#!/usr/bin/env python

from . import sulpated_data
import argparse
import sys
import os
import os.path as osp
import json


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
                print('before', sub, side, ':', out_dat.patterns[sub][side].patterns)
                for label, p in pattern.patterns.items():
                    print('set state', sub, side, f'{chr(65 + si)}_{label}', p)
                    out_dat.set_pattern_state(
                        sub, side, f'{chr(65 + si)}_{label}', p)
                print('after:', out_dat.patterns[sub][side].patterns)
    print('patterns read')

    for sub, pitem in out_dat.patterns.items():
        for side, pattern in pitem.items():
            votes = {}
            for label, p in pattern.patterns.items():
                if label in patterns:
                    continue
                slabel = label[2:]
                # TODO we may use confidence factors to weight votes
                votes.setdefault(slabel, []).append(int(p.get('enabled', 0)))
            for label, values in votes.items():
                value = bool(round(sum(values) / len(values)))
                p = pattern.patterns.get(label, {})
                p['enabled'] = value
                out_dat.set_pattern_state(sub, side, label, p)

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
