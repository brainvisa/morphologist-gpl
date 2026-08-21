
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
        self.add_trait('t1mri', traits.File(optional=True))
        self.add_trait('commissure_coordinates',
                       traits.File(output=True, optional=True))
        self.add_trait('threads', traits.Int())
        self.dry_run = False  # debug
        self.verbose = False  # debug
        self.threads = 0

    def _run_process(self):
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
        self.update_commissures()

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

    def update_commissures(self):
        if (self.t1mri in (traits.Undefined, None, '')
                or self.commissure_coordinates
                in (traits.Undefined, None, '')):
            return

        if self.dry_run or self.verbose:
            print('write', self.commissure_coordinates)

        f = aims.Finder()
        f.check(self.t1mri)
        va = f.header()
        vs = va.get('voxel_size', [1., 1., 1.])
        trinv = self.tal_trans.inverse()
        acmm = trinv.transform([0., 0., 0.])
        pcmm = trinv.transform([0., 30., 0.])
        ipmm = trinv.transform([0., 40., -60.])
        ac = [int(round(x / y)) for x, y in zip(acmm, vs)]
        pc = [int(round(x / y)) for x, y in zip(pcmm, vs)]
        ip = [int(round(x / y)) for x, y in zip(ipmm, vs)]
        print('AC:', ac, ', mm:', list(acmm))
        print('PC:', pc, ', mm:', list(pcmm))
        print('IP:', ip, ', mm:', list(ipmm))
        if not self.dry_run:
            with open(self.commissure_coordinates, 'w') as apc:
                print('AC:', ' '.join([str(x) for x in ac]), file=apc)
                print('PC:', ' '.join([str(x) for x in pc]), file=apc)
                print('IH:', ' '.join([str(x) for x in ip]), file=apc)
                print('The previous coordinates, used by the system, are '
                      'defined in voxels', file=apc)
                print('They stem from the following coordinates in '
                      'millimeters:', file=apc)
                print('ACmm:', ' '.join([str(x) for x in acmm]), file=apc)
                print('PCmm:', ' '.join([str(x) for x in pcmm]), file=apc)
                print('IHmm:', ' '.join([str(x) for x in ipmm]), file=apc)
