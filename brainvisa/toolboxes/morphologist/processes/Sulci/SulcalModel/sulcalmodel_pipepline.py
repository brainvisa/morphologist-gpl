# -*- coding: utf-8 -*-
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

from __future__ import absolute_import
from brainvisa.processes import *

name = 'Sulcal Model Graph Pipeline'
userLevel = 2


package_dir = os.path.join(os.path.sep, 'neurospin', 'research', 'Fedora-4')


def createPackageSignature():
    list = ['default']
    if os.path.isdir(package_dir):
        list += os.listdir(package_dir)
    return Choice(*list)


signature = Signature(
    'model_graph', WriteDiskItem('Model Graph', 'Graph'),
    'model_version', String(),
    'data_compatibility_version', String(),
    'learningbase_data_graphs', ListOf(ReadDiskItem("Data graph", 'Graph',
                                                    requiredAttributes={'labelled': 'Yes',
                                                                        'manually_labelled': 'Yes'})),
    'testbase_data_graphs', ListOf(ReadDiskItem("Data graph", 'Graph',
                                                requiredAttributes={'labelled': 'Yes',
                                                                    'manually_labelled': 'Yes'})),
    'genbase_data_graphs', ListOf(ReadDiskItem("Data graph", 'Graph',
                                               requiredAttributes={'labelled': 'Yes',
                                                                   'manually_labelled': 'Yes'})),
    'template_node_model', ReadDiskItem(
        'Template model', 'Template model'),
    'template_rel_model', ReadDiskItem('Template model', 'Template model'),
    'learner', ReadDiskItem('Sigraph Learner', 'Sigraph Learner'),
    'session', String(),
    'Output', WriteDiskItem('CSV file', 'CSV file'),
    'parallelism_mode', Choice('local', 'grid', 'duch', 'LSF')
)


class TopNode(SerialExecutionNode):
    def __init__(*args, **kwargs):
        SerialExecutionNode.__init__(*args, **kwargs)

    def linkGraphs(self, graphs, *kwargs):
        p = self.Generation
        return p.learningbase_data_graphs + \
            p.testbase_data_graphs + \
            self.genbase_data_graphs

    def cleanSignature(self):
        def delItem(signature, item):
            if item in signature:
                del signature[item]
        items = ['parallelism_mode', 'package', 'email', 'time']
        for x in items:
            delItem(self.signature, x)
        self.changeSignature(self.signature)

    def updateSignature(self):
        self.changeSignature(self.signature)
        self.addLink(None, 'parallelism_mode', self.signature_callback)
        if self.parallelism_mode in ['grid', 'duch', 'LSF']:
            # hack : force parallelism mode to avoid removing links
            # and a lot of addLink for dynamic signature of
            # subprocesses
            self.Generation.parallelism_mode = self.parallelism_mode
            self.ModelLearning.parallelism_mode = \
                self.parallelism_mode
            self.Annealing.parallelism_mode = self.parallelism_mode
            self.addLink('Generation.package', 'package')
            self.addLink('ModelLearning.package', 'package')
            self.addLink('Annealing.package', 'package')
        if self.parallelism_mode == 'LSF':
            self.addLink('Generation.time', 'time')
            self.addLink('ModelLearning.time', 'time')
            self.addLink('Annealing.time', 'time')
            self.addLink('Generation.email', 'email')
            self.addLink('ModelLearning.email', 'email')
            self.addLink('Annealing.email', 'email')

    def signature_callback(self, parallelism_mode, **kwargs):
        self.cleanSignature()
        self.signature['parallelism_mode'] = \
            Choice('local', 'grid', 'duch', 'LSF')
        self.signature['parallelism_mode'].userLevel = 2
        if self.parallelism_mode == 'LSF':
            self.signature['time'] = String()
            self.signature['email'] = String()
        if self.parallelism_mode in ['grid', 'duch', 'LSF']:
            packslist = createPackageSignature()
            if len(packslist.values) != 1:
                self.signature['package'] = packslist
                self.signature['package'].userLevel = 2
        self.updateSignature()


def initialization(self):
    self.setOptional('model_version')
    self.setOptional('data_compatibility_version')

    eNode = TopNode(self.name, parameterized=self)

    # Childs
    eNode.addChild('ModelCreation',
                   ProcessExecutionNode('Sulcal Model Graph Creation', optional=1))
    eNode.addChild('Generation',
                   ProcessExecutionNode('Sulcal Model Graph Learning', optional=1))
    eNode.addChild('ModelLearning',
                   ProcessExecutionNode('Sulcal Model Graph Learning', optional=1))
    eNode.addChild('Annealing',
                   ProcessExecutionNode('recognition_iterator',
                                        optional=1))

    # Fix values
    eNode.Generation.learning_mode = "generateOnly"
    eNode.ModelLearning.learning_mode = "readAndTrain"

    # Top -> All
    eNode.addLink('ModelCreation.model_graph', 'model_graph')
    eNode.addLink('ModelCreation.learningbase_data_graphs',
                  'learningbase_data_graphs')
    eNode.addLink('ModelCreation.testbase_data_graphs',
                  'testbase_data_graphs')
    eNode.addLink('ModelCreation.model_version', 'model_version')
    eNode.addLink('ModelCreation.data_compatibility_version',
                  'data_compatibility_version')
    eNode.addLink('ModelCreation.template_node_model',
                  'template_node_model')
    eNode.addLink('ModelCreation.template_rel_model', 'template_rel_model')
    eNode.addLink('Generation.learner', 'learner')
    eNode.addLink('Annealing.session', 'session')
    eNode.addLink('Annealing.Output', 'Output')
    eNode.addLink('Generation.parallelism_mode', 'parallelism_mode')
    eNode.addLink('ModelLearning.parallelism_mode', 'parallelism_mode')
    eNode.addLink('Annealing.parallelism_mode', 'parallelism_mode')
    eNode.addLink('Annealing.data_graph', 'genbase_data_graphs',
                  function=eNode.linkGraphs)

    # parallelism mode
    eNode.addLink(None, 'parallelism_mode', eNode.signature_callback)

    # ModelCreation -> Generation
    eNode.addLink('Generation.model_graph', 'ModelCreation.model_graph')
    eNode.addLink('Generation.learningbase_data_graphs',
                  'ModelCreation.learningbase_data_graphs')
    eNode.addLink('Generation.testbase_data_graphs',
                  'ModelCreation.testbase_data_graphs')

    # Generation -> ModelLearning
    eNode.addLink('ModelLearning.model_graph',
                  'Generation.model_graph')
    eNode.addLink('ModelLearning.learner',
                  'Generation.learner')

    # ModelLearning -> Annealing
    eNode.addLink('Annealing.model', 'ModelLearning.model_graph')
    eNode.addLink('Annealing.data_graph',
                  'Generation.learningbase_data_graphs',
                  function=eNode.linkGraphs)
    eNode.addLink('Annealing.data_graph', 'Generation.testbase_data_graphs',
                  function=eNode.linkGraphs)
    self.setExecutionNode(eNode)
