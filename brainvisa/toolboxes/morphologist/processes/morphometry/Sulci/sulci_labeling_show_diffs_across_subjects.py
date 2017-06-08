from __future__ import print_function
from brainvisa.processes import ReadDiskItem, ListOf, Signature, String
from soma.qt_gui import qtThread
import pandas
import numpy as np

name = 'Sulci labeling show differences across subjects'
userLevel = 1

signature = Signature(
    'diff_tables', ListOf(ReadDiskItem('CSV file', 'CSV file')),
    'column', String(),
)


def initialization(self):
    self.column = 'glob.dice'


def plot(self, context, table, labels):
    from matplotlib import pyplot

    fig, ax = pyplot.subplots()
    n = table.shape[1]
    x = np.arange(table.shape[0])
    cols = ['blue', 'red', 'green', 'lime'] * int(n / 4 + 1)
    for i in range(n):
        ax.barh(x + float(i) / (n+1) , table[:, i], 1. / (n+1), color=cols[i])
    ax.set_yticks(x)
    ax.set_yticklabels(labels)
    fig.show()

    return fig


def execution(self, context):

    tables = [pandas.DataFrame.from_csv(f.fullPath())
              for f in self.diff_tables]
    tlabels = [table.label for table in tables]
    dlabels = set()
    for l in tlabels:
        dlabels.update(l)
    dlabels.remove('global')
    labels = ['global'] + sorted(dlabels)
    del dlabels
    indices = [[np.where(df.label == l)[0] for l in labels] for df in tables]
    #print('indices:', indices)
    table = np.zeros((len(labels), len(tables)),
                     dtype=tables[0][self.column].dtype)
    for i in range(len(tables)):
        t = tables[i][self.column]
        for l in range(len(labels)):
            ind = indices[i][l]
            if ind.shape != 0:
                table[l, i] = t[ind[0]]

    fig = qtThread.QtThreadCall().call(self.plot, context, table, labels)
    return fig
