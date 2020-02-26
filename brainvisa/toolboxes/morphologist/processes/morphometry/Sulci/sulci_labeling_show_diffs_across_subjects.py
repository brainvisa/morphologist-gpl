from __future__ import print_function
from __future__ import absolute_import
from brainvisa.processes import ReadDiskItem, WriteDiskItem, ListOf, \
    Signature, String
from soma.qt_gui import qtThread
import numpy as np
import os
from six.moves import range
try:
    import pandas
except ImportError:
    pandas = None

name = 'Sulci labeling show differences across subjects'
userLevel = 1


def validation():
    try:
        import pandas
    except ImportError as e:
        raise ValidationError('pandas module is not available')
    try:
        import matplotlib
    except ImportError as e:
        raise ValidationError('matplotlib module is not available')


signature = Signature(
    'diff_tables', ListOf(ReadDiskItem('CSV file', 'CSV file')),
    'column', String(),
    'save_plot', WriteDiskItem('SVG figure', 'SVG file'),
)


def initialization(self):
    self.column = 'glob.dice'
    self.setOptional('save_plot')


def plot(self, context, table, labels, legend=None, out_filename=None):
    from matplotlib import pyplot

    fig, ax = pyplot.subplots()
    fig.subplots_adjust(bottom=0.03, top=0.99, right=0.99)
    nitem = table.shape[0]
    n = table.shape[1]
    x = np.arange(nitem)
    cols = ['blue', 'red', 'green', 'gold', 'darkchid', 'orange', 'darkcyan']
    for i in range(n):
        ax.barh(x + float(i) / (n+1), table[:, i], 1. / (n+1),
                color=cols[i % len(cols)])
    ax.set_yticks(x)
    sz = 10
    if nitem >= 30:
        sz = 8
        if nitem >= 60:
            sz = 6
    ax.set_yticklabels(labels, size=sz)
    ax.set_ylim(0, nitem)
    ax.grid(True, axis='x')
    if legend:
        ax.legend(legend)
    fig.show()

    if out_filename is not None:
        fig.savefig(out_filename.fullPath())

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

    if len(self.diff_tables) >= 2:
        legend = [os.path.basename(f.fullName()) for f in self.diff_tables]
    else:
        legend = None
    fig = qtThread.QtThreadCall().call(self.plot, context, table, labels,
                                       legend, self.save_plot)
    return fig
