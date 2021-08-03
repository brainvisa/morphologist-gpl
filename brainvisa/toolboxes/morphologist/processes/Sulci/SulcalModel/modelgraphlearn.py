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

from __future__ import print_function
from __future__ import absolute_import
from brainvisa.processes import *
from brainvisa import shelltools
import os
import string
import stat
import sys

name = 'Sulcal Model Graph Learning'
userLevel = 2

learningbase_data_graphs_signature = ListOf(ReadDiskItem(
    "Data graph", 'Graph',
    requiredAttributes={'labelled': 'Yes',
                        'manually_labelled': 'Yes'}))
testbase_data_graphs_signature = ListOf(ReadDiskItem(
    "Data graph", 'Graph',
    requiredAttributes={'labelled': 'Yes',
                        'manually_labelled': 'Yes'}))

package_dir = os.path.join(os.path.sep, 'neurospin', 'research', 'Fedora-4')


def createPackageSignature():
    list = ['default']
    if os.path.isdir(package_dir):
        list += os.listdir(package_dir)
    return Choice(*list)


signature = Signature(
    'model_graph', ReadDiskItem('Model Graph', 'Graph'),
    'labels_translation_map',
    ReadDiskItem('Label Translation',
                 ['Label Translation', 'DEF Label translation']),
    'learner', ReadDiskItem('Sigraph Learner', 'Sigraph Learner'),
    'stopDelay', Integer(),
    'learning_mode', Choice('generateOnly', 'generateAndTrain',
                            'readAndTrain'),
    'learningbase_data_graphs', learningbase_data_graphs_signature,
    'testbase_data_graphs', testbase_data_graphs_signature,
    'cycles', Integer(),
    'cycles_tst', Integer(),
    'parallelism_mode', Choice('local',
                               ('lag (soma.workflow)', 'soma.workflow'),
                               'grid', 'LSF'))


def cleanSignature(self):
    def delItem(signature, item):
        if item in signature:
            del signature[item]
    items = ['learning_mode', 'parallelism_mode', 'time', 'email',
             'learningbase_data_graphs', 'testbase_data_graphs',
             'parallel_config_directory', 'package', 'cycles', 'cycles_tst']
    for x in items:
        delItem(self.signature, x)
    self.changeSignature(self.signature)


def parallel_config_directory_callback(self, *args, **kwargs):
    if self.model_graph is None:
        return
    if 'parallel_config_directory' in self.signature:
        self.parallel_config_directory = os.path.join(os.path.dirname(
            self.model_graph.fullPath()), 'tasks', self.learning_mode)


def updateSignature(self):
    self.changeSignature(self.signature)
    self.addLink(None, 'learning_mode', self.signature_callback)
    self.addLink(None, 'parallelism_mode', self.signature_callback)
    self.addLink(None, 'model_graph', self.parallel_config_directory_callback)
    self.addLink(None, 'learning_mode',
                 self.parallel_config_directory_callback)


def signature_callback(self, learning_mode, **kwargs):
    self.cleanSignature()
    learning_mode = self.learning_mode
    self.signature['learning_mode'] = Choice('generateOnly',
                                             'generateAndTrain', 'readAndTrain')
    if learning_mode in ['generateOnly', 'generateAndTrain']:
        self.signature['learningbase_data_graphs'] = \
            learningbase_data_graphs_signature
        self.signature['testbase_data_graphs'] = \
            testbase_data_graphs_signature
        self.signature['cycles'] = Integer()
        self.signature['cycles_tst'] = Integer()
    parmodes = ['local', 'grid', 'LSF']
    if self.soma_workflow:
        parmodes.insert(1, ('lag (soma.workflow)', 'soma.workflow'))
    self.signature['parallelism_mode'] = Choice(*parmodes)
    if self.parallelism_mode in ['grid', 'LSF', 'soma.workflow']:
        self.signature['parallel_config_directory'] = \
            WriteDiskItem('Directory', 'Directory')
        self.setOptional('parallel_config_directory')
    if self.parallelism_mode == 'LSF':
        self.signature['time'] = String()
        self.signature['email'] = String()
    if self.parallelism_mode in ['grid', 'LSF']:
        packslist = createPackageSignature()
        if len(packslist.values) != 1:
            self.signature['package'] = packslist
            self.signature['package'].userLevel = 2
    self.updateSignature()


def initialization(self):
    self.setOptional('labels_translation_map')
    self.labels_translation_map = \
        self.signature['labels_translation_map'].findValue(
            {'filename_variable': 'sulci_model_noroots'})

    self.learner = self.signature['learner'].findValue({})
    self.cycles = 2000
    self.cycles_tst = 400
    self.stopDelay = 950
    self.time = '00:30'
    self.parallel_config_directory = None

    try:
        import pwd
        names = pwd.getpwnam(os.getlogin())[4]
        self.email = '.'.join(names.split(' ')[:2]) + '@cea.fr'
    except:
        self.email = ''
    try:
        import Pyro
        import soma.workflow
        self.soma_workflow = True
    except:
        self.soma_workflow = False
    self.addLink(None, 'learning_mode', self.signature_callback)
    self.addLink(None, 'parallelism_mode', self.signature_callback)

   #   self.setOptional( 'time' )


def execution(self, context):
    if self.learning_mode in ['generateOnly', 'generateAndTrain']:
        if len(self.learningbase_data_graphs) == 0:
            raise RuntimeError('learningbase_data_graphs must not be empty')
        # if len( self.testbase_data_graphs ) == 0:
        #    raise RuntimeError( 'testbase_data_graphs must not be empty' )
    if self.parallelism_mode not in ('local', 'soma.workflow') and \
        (not hasattr(self, 'parallel_config_directory') or
            self.parallel_config_directory is None):
        raise RuntimeError('parallel_config_directory must be specified in '
                           'parallel execution mode')

    sil = context.temporary('config file')
    conf = sil.fullPath()
    if self.parallel_config_directory is not None:
        odir = self.parallel_config_directory.fullPath()
        if not os.path.isdir(odir):
            os.makedirs(odir)
            context.log("directory '%s' created" % odir)
        conf = os.path.join(odir, 'siLearn-' + self.learning_mode + '.cfg')
    elif self.parallelism_mode != 'local':
        odirdi = context.temporary('Directory')
        odir = odordi.fullPath()
    f = open(conf, 'w')
    f.write('*BEGIN TREE 1.0 siLearn\n'
            'modelFile\t' + self.model_graph.fullPath() + '\n'
            'mode\t' + self.learning_mode + '\n'
            'stopDelay\t' + str(self.stopDelay) + '\n'
            'close_learning\t1\n'
            'trainschemeFile\t' + self.learner.fullPath() + '\n')
    if self.learning_mode in ['generateOnly', 'generateAndTrain']:
        f.write('cycles\t' + str(self.cycles) + '\n'
                'cycles_tst\t' + str(self.cycles_tst) + '\n'
                'graphFiles\t')
        f.write(string.join([x.fullPath()
                             for x in self.learningbase_data_graphs]) + '\n')
        if len(self.testbase_data_graphs) != 0:
            f.write('testGraphFiles\t')
            f.write(string.join([x.fullPath()
                                 for x in self.testbase_data_graphs]) + '\n')
    if self.labels_translation_map is not None:
        f.write('labelsMapFile\t' + self.labels_translation_map.fullPath()
                + '\n')
    f.write('dimreduction\tNone\n')
    f.write('optimized_dim\tNone\n')
    f.write('predict_train\t0\n')
    f.write('selected_dim\t-1\n')
    f.write('*END\n')
    f.close()
    f = open(conf)
    context.log('siLearn config file', html=f.read())
    f.close()

    if not hasattr(self, 'package') or self.package == 'default':
        silcmd = distutils.spawn.find_executable('siLearn.py')
    else:
        silcmd = os.path.join(package_dir, self.package, 'bin', 'siLearn.py')
    try:
        os.stat(silcmd)
    except OSError:
        raise RuntimeError("'%s' does not exist!" % silcmd)

    if self.parallelism_mode == 'local':
        context.write('local learning mode')
        context.pythonSystem(silcmd, conf)
    elif self.parallelism_mode == 'grid':
        context.write('Grid (Matthieu) parallelism mode')
        sglt = distutils.spawn.find_executable('siGenerateLearningTasks.py')
        batchname = 'siLearn-' + self.learning_mode + '-grid_batch'
        batchout = os.path.join(odir, batchname)
        context.pythonSystem(sglt, '-m', self.model_graph, '-o', batchout,
                             '-p', 'grid', '-c', conf, '-b', silcmd)
        scriptname = 'siLearn-' + self.learning_mode + '-grid.sh'
        scriptout = os.path.join(odir, scriptname)
        distcmd = distutils.spawn.find_executable('grid.py')
        if distcmd is None:
            context.write("<font color=red>error</font> : can't find "
                          "grid.py program. It may be found in "
                          "'//depot/parallel-version/bin/grid.py")
            return
        fd = open(scriptout, 'w')
        print("#!/bin/bash\n", file=fd)
        print("%s %s  --host ~/neurospin-distcc-hosts --tasks %s --log %s --timeslot -" %
              (os.path.basename(sys.executable), distcmd, batchout, batchout + '.log'), file=fd)
        fd.close()
        os.chmod(scriptout, 0o0750)
    elif self.parallelism_mode == 'LSF':
        context.write('LSF (CCRT) mode')
        sglt = distutils.spawn.find_executable('siGenerateLearningTasks.py')
        out = os.path.join(odir, 'siLearn-' +
                           self.learning_mode + '-LSF_batch')
        context.pythonSystem(sglt, '-m', self.model_graph, '-o', out,
                             '-p', 'LSF', '-c', conf, '-b', silcmd,
                             '-t', self.time, '-e', self.email)
    elif self.parallelism_mode == 'soma.workflow':
        context.write('Lag (soma.workflow/Laguitton) mode')
        sglt = distutils.spawn.find_executable('siGenerateLearningTasks.py')
        out = os.path.join(odir, 'siLearn-' +
                           self.learning_mode + '-somaworkflow_batch')
        context.pythonSystem(sglt, '-m', self.model_graph, '-o', out,
                             '-p', 'somaworkflow', '-c', conf, '-b', silcmd)
    else:
        raise RuntimeError('Mode ' + self.parallelism_mode
                           + ' is not implemented yet')

    import time
    time.sleep(1)  # avoid bug in BV
