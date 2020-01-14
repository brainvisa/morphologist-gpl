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
import sys

if sys.version_info[0] >= 3:
    def next(iterator):
        return iterator.__next__()
else:
    def next(iterator):
        return iterator.next()

name = 'Sulci Recognition'
userLevel = 0

signature = Signature(
    'data_graph', ReadDiskItem('Data graph', 'Graph'),
    'output_graph',
    WriteDiskItem('Labelled Cortical folds graph', 'Graph',
                  requiredAttributes={'labelled': 'Yes',
                                      'automatically_labelled': 'Yes'}),
    'fix_random_seed', Boolean(),
)

# Default values


def initialization(self):
    # create nodes
    eNode = SelectionExecutionNode(self.name, parameterized=self)
    # detect if SPAM models are here. If not, ANN is the default method
    # otherwise use SPAMs by default
    spammodels = ReadDiskItem('Sulci Segments Model', 'Text Data Table'
                              )._findValues(selection={'sulci_segments_model_type':
                                                       'global_registered_spam'},
                                            requiredAttributes=None, write=False)
    try:
        next(spammodels)
        usespam = 1
    except StopIteration:
        usespam = 0
    eNode1 = ProcessExecutionNode('recognition', selected=1 - usespam)
    eNode1._process.name = "ANN-based"
    eNode2 = ProcessExecutionNode('spam_recognition', selected=usespam)
    eNode2._process.name = "SPAM-based"
    eNode.addChild('recognition2000', eNode1)
    eNode.addChild('SPAM_recognition09', eNode2)

    # break internal links
    eNode.recognition2000.clearLinksTo('output_graph')
    eNode.SPAM_recognition09.removeLink('output_graph', 'data_graph')

    # links for SPAM version
    eNode.addDoubleLink('SPAM_recognition09.data_graph', 'data_graph')
    eNode.addDoubleLink('SPAM_recognition09.output_graph', 'output_graph')

    # 2000 version
    eNode.addDoubleLink('recognition2000.data_graph', 'data_graph')
    eNode.addDoubleLink('recognition2000.output_graph', 'output_graph')

    # self links
    self.linkParameters('output_graph', 'data_graph')

    # for "future" pipelines
    eNode.selection_outputs = ['output_graph', 'output_graph', 'labeled_graph']
    eNode.switch_output = 'output_graph'

    self.setExecutionNode(eNode)

    self.addDoubleLink('fix_random_seed', 'recognition2000.fix_random_seed')
    self.addDoubleLink('fix_random_seed', 'SPAM_recognition09.fix_random_seed')

    self.signature['fix_random_seed'].userLevel = 3
    self.fix_random_seed = False

    # CNN models
    #eNode3 = ProcessExecutionNode('sulci_deep_labeling', selected=False)
    eNode3 = ProcessExecutionNode(
        'capsul://deepsulci.sulci_labeling.capsul.labeling', selected=False,
        skip_invalid=True)
    if eNode3.is_valid():
        eNode3._process.name = 'CNN-based'
    eNode.addChild('CNN_recognition19', eNode3)
    eNode.addDoubleLink('data_graph', 'CNN_recognition19.graph')
    eNode.addDoubleLink('output_graph', 'CNN_recognition19.labeled_graph')
    self.addDoubleLink('fix_random_seed', 'CNN_recognition19.fix_random_seed')

