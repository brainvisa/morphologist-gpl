from __future__ import absolute_import
from brainvisa.processes import ReadDiskItem, WriteDiskItem, ListOf, \
    Signature, String, Choice, Boolean
from soma import aims
import numpy as np
from six.moves import zip
try:
    import pandas
except ImportError:
    pandas = None

name = 'Sulci labeling differences across subjects'
userLevel = 1


def validation():
    try:
        import pandas
    except ImportError as e:
        raise ValidationError('pandas module is not available')


signature = Signature(
    'sulci1', ListOf(ReadDiskItem(
        'Labelled cortical folds graph', 'Graph and data')),
    'sulci2', ListOf(ReadDiskItem(
        'Labelled cortical folds graph', 'Graph and data')),
    'session1_hint', String(),
    'session2_hint', String(),
    'manual1', Boolean(),
    'manual2_hint', Choice('As sulci1', 'Yes', 'No'),
    'diff_table', WriteDiskItem('CSV file', 'CSV file'),
)


def initialization(self):
    def link_sulci1(self, param):
        sulci1 = self.sulci1
        if self.session1_hint and self.sulci1 is not None:
            atts = {'sulci_recognition_session': self.session1_hint}
            if self.manual1:
                atts['manually_labelled'] = 'Yes'
                atts['automatically_labelled'] = 'No'
            else:
                atts['manually_labelled'] = 'No'
                atts['automatically_labelled'] = 'Yes'
            sulci1 = [
                self.signature['sulci1'].contentType.findValue(
                    x, requiredAttributes=atts)
                for x in self.sulci1]
        return sulci1

    def link_sulci2(self, param):
        sulci2 = None
        if self.session2_hint and self.sulci1 is not None:
            atts = {'sulci_recognition_session': self.session2_hint}
            if self.manual2_hint == 'Yes':
                atts['manually_labelled'] = 'Yes'
                atts['automatically_labelled'] = 'No'
            elif self.manual2_hint == 'No':
                atts['manually_labelled'] = 'No'
                atts['automatically_labelled'] = 'Yes'
            sulci2 = [
                self.signature['sulci2'].contentType.findValue(
                    x, requiredAttributes=atts)
                for x in self.sulci1]
        return sulci2

    self.setOptional('session1_hint', 'session2_hint')
    self.linkParameters('sulci1', ('session1_hint', 'manual1'), link_sulci1)
    self.linkParameters('sulci2', ('sulci1', 'session2_hint',
                                   'manual2_hint'), link_sulci2)


def execution(self, context):
    if len(self.sulci1) != len(self.sulci2):
        raise ValueError('sulci1 and sulci2 should be lists of the same size, '
                         'with subject correspondance between both')

    rdiff = aims.RoiDiff()
    n = 0

    dice = 0.
    stats = []
    labels = []
    s_index = {}
    glo = aims.RoiDiff.DiffStat()

    for g1, g2 in zip(self.sulci1, self.sulci2):
        context.progress(n, len(self.sulci1), process=self)
        graph1 = aims.read(g1.fullPath())
        graph2 = aims.read(g2.fullPath())
        if 'label_property' not in graph1:
            if self.manual1:
                graph1['label_property'] = 'name'
            else:
                graph1['label_property'] = 'label'
        if 'label_property' not in graph2:
            if self.manual2_hint == 'Yes' \
                    or (self.manual2_hint != 'No'
                        and graph1['label_property'] == 'name'):
                graph2['label_property'] = 'name'
            else:
                graph2['label_property'] = 'label'
        rdiff.diff(graph1, graph2)
        gs = rdiff.globalStats()
        glo.dice += gs.dice
        glo.matching_voxels += gs.matching_voxels
        glo.unmatching_voxels += gs.unmatching_voxels
        context.write(n, ':', gs.dice)
        g_labels = rdiff.roiNames()
        for name in g_labels:
            d = rdiff.statsByLabel(name)
            if name in s_index:
                s = stats[s_index[name]]
            else:
                s_index[name] = len(labels)
                labels.append(name)
                s = aims.RoiDiff.DiffStat()
                s.g2_size = 0
                s.n = 0
                stats.append(s)
            s.dice += d.dice
            s.matching_voxels += d.matching_voxels
            s.unmatching_voxels += d.unmatching_voxels
            s.g2_size += d.g2_bucket[0].size()
            s.n += 1
        del d, s, name, gs
        n += 1

    context.progress(n, len(self.sulci1), process=self)

    glo.dice /= n
    glo.n = n
    nl = len(stats)
    arr = [[], [], [], [], [], []]
    for name, s in zip(labels, stats):
        s.dice /= s.n
        arr[0].append(name)
        arr[1].append(int(s.matching_voxels))
        arr[2].append(int(s.unmatching_voxels))
        arr[3].append(int(s.g2_size))
        arr[4].append(float(s.dice))
        arr[5].append(int(s.n))

    arr[0].append('global')
    arr[1].append(int(glo.matching_voxels))
    arr[2].append(int(glo.unmatching_voxels))
    arr[3].append(int(glo.matching_voxels + glo.unmatching_voxels))
    arr[4].append(float(glo.dice))
    arr[5].append(int(glo.n))
    arr.insert(-1,
               np.asarray(arr[1]) * 2.
               / (np.asarray(arr[1]) + np.asarray(arr[2])
                  + np.asarray(arr[3])))
    context.write('average dice:', glo.dice)
    col_names = ['label', 'matching_voxels', 'unmatching_voxels', 'g2_size',
                 'avg.dice', 'glob.dice', 'n']
    df = pandas.DataFrame(dict([(n, x) for n, x in zip(col_names, arr)]),
                          columns=col_names)
    df.to_csv(self.diff_table.fullPath())
