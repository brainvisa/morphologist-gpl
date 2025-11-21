
import filelock
import pandas as pd
import os
import os.path as osp
import json


def update_qc_table(statuses, qc_file, prune=False):
    # print('update_qc_table:', statuses)
    # import sys
    # sys.stdout.flush()
    lock_path = f'{qc_file}.tmplock'
    lock = filelock.SoftFileLock(lock_path)
    try:
        with lock:
            if osp.exists(qc_file):
                qc_table = pd.read_csv(qc_file, delimiter='\t')
                if 'morpho_qc' not in qc_table.columns:
                    qc_table.insert(len(qc_table.columns), 'morpho_qc')
                if 'bids' not in qc_table.columns:
                    qc_table.insert(len(qc_table.columns) - 1, 'bids',
                                    ['run-0'] * qc_table.shape[0])
            else:
                qc_table = pd.DataFrame(columns=['participant_id', 'bids',
                                                 'morpho_qc'])
            added_rows = []
            if isinstance(statuses, dict):
                statuses = [statuses]
            for sub_stat in statuses:
                sub = sub_stat['subject']
                if not sub.startswith('sub-'):
                    # apparently BIDS tables include the "sub-" prefix
                    sub = f'sub-{sub}'
                bids = sub_stat.get('bids_attributes', 'run-0')
                status = sub_stat.get('status', 'Undefined')
                done = False
                # print('sub:', sub, ', bids:', bids)
                if not prune:
                    sel = qc_table[(qc_table.participant_id == sub)
                                   & (qc_table.bids == bids)]
                    if sel.shape[0] != 0:
                        qc_table.loc[sel.index, 'morpho_qc'] = status
                        done = True
                if not done:
                    # print('add row')
                    added_rows.append([sub, bids, status])
            # print('added_rows:', added_rows)
            # sys.stdout.flush()
            if prune:
                qc_table = pd.DataFrame(added_rows,
                                        columns=qc_table.columns)
            elif added_rows:
                rows = pd.DataFrame(added_rows,
                                    columns=qc_table.columns)
                qc_table = pd.concat((qc_table, rows))

            qc_table.to_csv(qc_file, sep='\t', index=False)
    finally:
        try:
            os.unlink(lock_path)
        except FileNotFoundError:
            pass


def _read_indiv_qc_file(qc_file, subject_def):
    with open(qc_file) as f:
        stats = json.load(f)
    return {'subject': subject_def.get('subject'),
            'bids_attributes': subject_def.get('bids'),
            'status': stats.get('status')}


def qc_table_from_indiv(indiv_qc_files, subjects_def, qc_file,
                        prune=False, threads=0):
    from soma import mpfork
    import queue

    print('qc_table_from_indiv', indiv_qc_files)
    njobs = len(indiv_qc_files)
    q = queue.Queue()
    qc_stats = [None] * njobs
    workers = mpfork.allocate_workers(q, threads, max_workers=njobs,
                                      thread_only=True)
    for i, (indiv_qc_file, subject_def) in enumerate(zip(indiv_qc_files,
                                                         subjects_def)):
        job = (i, _read_indiv_qc_file, (indiv_qc_file, subject_def), {},
               qc_stats)
        q.put(job)

    for i in range(len(workers)):
        q.put(None)

    print('running jobs...')
    q.join()
    for w in workers:
        w.join()

    print('jobs done.')
    print('qc_stats:', qc_stats)
    import sys
    sys.stdout.flush()
    update_qc_table(qc_stats, qc_file, prune=prune)
