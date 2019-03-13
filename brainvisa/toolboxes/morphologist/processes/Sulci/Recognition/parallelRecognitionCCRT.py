#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
#
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.

from brainvisa.processes import *
import shutil
import os
import six

name = 'Parallel recognition CCRT'
userLevel = 1

signature = Signature(
    'data_graph', ReadDiskItem('Data graph', 'Graph'),
    'model', ReadDiskItem('Model graph', 'Graph'),
    'output_graph',
    WriteDiskItem('Labelled Cortical folds graph', 'Graph',
                  requiredAttributes={'labelled': 'Yes',
                                      'automatically_labelled': 'Yes'}),
    'number_of_trials', Integer(),
    'energy_plot_file', WriteDiskItem(
        'siRelax Fold Energy', 'siRelax Fold Energy'),
    'rate', Float(),
    'stopRate', Float(),
    'niterBelowStopProp', Integer(),
    'model_repl_path', String(),
    'data_repl_path', String(),
)


def initialization(self):
    self.linkParameters('model', 'data_graph')
    self.linkParameters('output_graph', 'data_graph')
    self.linkParameters('energy_plot_file', 'output_graph')
    self.number_of_trials = 10
    self.signature['rate'].userLevel = 2
    self.signature['stopRate'].userLevel = 2
    self.signature['niterBelowStopProp'].userLevel = 2
    self.rate = 0.98
    self.stopRate = 0.05
    self.niterBelowStopProp = 1


def execution(self, context):
    dir = os.path.dirname(self.output_graph.fullName())
    for x in six.moves.xrange(self.number_of_trials):
        g = os.path.join(dir, '%s_res_%03d.arg'
                         % (os.path.basename(self.data_graph.fullName()),
                              x))
        s = os.path.join(dir, '%s_stats_%03d.nrj'
                         % (os.path.basename(self.data_graph.fullName()),
                              x))
        config = os.path.join(dir, '%s_res_%03d.sirelax'
                              % (os.path.basename(self.data_graph.fullName()),
                                 x))
        context.write(str(x), ': ', g, '\n')
        try:
            stream = open(config, 'w')
        except IOError as e:
            error(e.strerror, maker.output)
        else:
            mpath = self.model.fullPath()
            dpath = self.data_graph.fullPath()
            ograph = self.output_graph.fullPath()
            eplot = self.energy_plot_file.fullPath()
            mdone = 0
            ddone = 0
            gdone = 0
            pdone = 0
            for p in dataPath:
                if not mdone and mpath.startswith(p[0]):
                    mpath = os.path.join(
                        self.model_repl_path, mpath[len(p[0])+1:])
                    mdone = 1
                if not ddone and dpath.startswith(p[0]):
                    dpath = os.path.join(
                        self.data_repl_path, dpath[len(p[0])+1:])
                    ddone = 1
                if not gdone and ograph.startswith(p[0]):
                    ograph = os.path.join(
                        self.data_repl_path, ograph[len(p[0])+1:])
                    gdone = 1
                if not pdone and eplot.startswith(p[0]):
                    eplot = os.path.join(
                        self.data_repl_path, eplot[len(p[0])+1:])
                    pdone = 1
                if mdone and ddone and gdone and pdone:
                    break
            stream.write('*BEGIN TREE 1.0 siRelax\n')
            stream.write('modelFile ' + mpath + '\n')
            stream.write('graphFile ' + dpath + '\n')
            stream.write('output ' + ograph + '\n')
            stream.write('plotfile ' + eplot + '\n')
            stream.write('rate ' + str(self.rate) + '\n')
            stream.write('stopRate ' + str(self.stopRate) + '\n')
            stream.write('niterBelowStopProp ' + str(self.niterBelowStopProp)
                         + '\n')
            stream.write('*END\n')
            stream.close()
            f = open(config)
            context.log('siRelax input file', f.read())
            f.close()
