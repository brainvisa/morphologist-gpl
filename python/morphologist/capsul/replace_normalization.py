
from capsul.api import Process
import os
import os.path as osp
from soma import aims
import traits.api as traits
import queue
from soma import mpfork


class ReplaceNormalization(Process):
    excluded_exts = ('#', '%', '.minf', '.txt', '.pdf', '.csv', '.tsv', '.trm',
                     '.referential', '.json', '.dat', '.nrj', '.APC',
                     '.mat', '.han', '.his', '.npy')
    excluded_prefixes = ('.', '~', 'normalized_')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_trait(
            'transformation',
            traits.File(
                allowed_extensions=['.trm'],
                desc='Affine transformation file'))
        self.add_trait('target_referential',
                       traits.Enum('Talairach-ACPC', 'ICBM'))
        self.add_trait('acquisition_dir', traits.Directory())
        self.add_trait(
            'talairach_transform',
            traits.File(output=True, optional=True,
                        allowed_extensions=['.trm']))
        self.add_trait(
            'icbm_transform',
            traits.File(output=True, optional=True,
                        allowed_extensions=['.trm']))
        self.add_trait('threads', traits.Int())
        self.dry_run = False  # debug
        self.verbose = False  # debug
        self.threads = 0

    def _run_process(self):
        print('ReplaceNormalization')
        trans = aims.read(self.transformation)
        if self.target_referential == 'Talairach-ACPC':
            self.tal_trans = trans
            self.icbm_trans = (aims.StandardReferentials.talairachToICBM()
                               * trans)
        else:
            self.icbm_trans = trans
            self.tal_trans = (
                aims.StandardReferentials.talairachToICBM().inverse() * trans)

        if (not self.dry_run
                and self.talairach_transform not in
                (traits.Undefined, None, '')):
            if self.verbose:
                print('write', self.talairach_transform)
            aims.write(self.tal_trans, self.talairach_transform)
        if (not self.dry_run
                and self.icbm_transform not in (traits.Undefined, None, '')):
            if self.verbose:
                print('write', self.icbm_transform)
            aims.write(self.icbm_trans, self.icbm_transform)

        todo = []

        finder = aims.Finder()
        for dirname, dirs, files in os.walk(self.acquisition_dir):
            for fname in files:
                fullp = osp.join(dirname, fname)
                if self.filter_out(fullp):
                    continue
                try:
                    finder.check(fullp)
                except OSError:
                    continue
                print('recognized', fullp)
                todo.append(fullp)
                # self.fix_transform(fullp)

        q = queue.Queue()
        res = [None] * len(todo)
        workers = mpfork.allocate_workers(
            q, self.threads, max_workers=len(res), thread_only=True)
        for i, fullp in enumerate(todo):
            job = (i, self.fix_transform, (fullp, ), {}, res)
            q.put(job)

        # add as many empty jobs as the workers number to end them
        for i in range(len(workers)):
            q.put(None)

        # wait for every job to complete
        q.join()

        # terminate all workers
        for w in workers:
            w.join()

        # print('result:', res)

    def filter_out(self, fullp):
        for ext in self.excluded_exts:
            if fullp.endswith(ext):
                return True
        for prefix in self.excluded_prefixes:
            if fullp.startswith(prefix):
                return True
        return False

    def fix_transform(self, fullp):
        data = aims.read(fullp)
        if isinstance(data, aims.Graph):
            aims.GraphManip.storeTalairach(data, self.tal_trans)
        else:
            hdr = data.header()
            refs = list(hdr.get('referentials', []))
            trans = [list(x) for x in hdr.get('transformations', [])]
            index = -1
            for ref in (aims.StandardReferentials.mniTemplateReferentialID(),
                        aims.StandardReferentials.mniTemplateReferential()):
                if ref in refs:
                    index = refs.index(ref)
                    break
            if index < 0:
                refs.append(
                    aims.StandardReferentials.mniTemplateReferentialID())
                trans.append([])
            trans[index] = self.icbm_trans.toVector()

            index = -1
            for ref in (aims.StandardReferentials.acPcReferentialID(),
                        aims.StandardReferentials.acPcReferential()):
                if ref in refs:
                    index = refs.index(ref)
                    break
            if index >= 0:
                trans[index] = self.tal_trans.toVector()

            hdr['referentials'] = refs
            hdr['transformations'] = trans
            del trans, refs, hdr
        if self.dry_run or self.verbose:
            print('write', fullp)
        if not self.dry_run:
            aims.write(data, fullp)
        del data
