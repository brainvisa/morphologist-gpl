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

from brainvisa.processes import *
from brainvisa.data import neuroData
name = 'Automatic recognition iterator'
userLevel = 1

package_dir = os.path.join(os.path.sep, 'neurospin', 'research', 'Fedora-4')
def createPackageSignature():
    list = ['default']
    if os.path.isdir(package_dir): list += os.listdir(package_dir)
    return Choice(*list)

signature = Signature(
	'data_graph', ListOf(ReadDiskItem('Labelled Cortical folds graph',
			'Graph', requiredAttributes = { 'labelled' :'Yes' })),
	'model', ReadDiskItem( 'Model graph', 'Graph' ),
	'session', String(),
	'Output', WriteDiskItem('CSV file', 'CSV file'),
	'parallelism_mode', Choice( 'local', 'grid', 'duch', 'LSF' ))

class TopNode(SerialExecutionNode):
	def __init__(*args, **kwargs):
		SerialExecutionNode.__init__(*args, **kwargs)

	def cleanSignature(self):
		def delItem(signature, item):
			if signature.has_key(item): del signature[item]
		items = ['parallelism_mode', 'package', 'email', 'time',
			'parallel_config_directory']
		for x in items : delItem(self.signature, x)
		self.changeSignature(self.signature)

	def updateSignature(self):
		self.changeSignature(self.signature)
		self.addLink(None, 'parallelism_mode', self.signature_callback)

	def signature_callback( self, parallelism_mode, **kwargs):
		self.cleanSignature()
		self.signature['parallelism_mode'] = \
			Choice( 'local', 'grid', 'duch', 'LSF' )
		self.signature[ 'parallelism_mode' ].userLevel = 2
		if self.parallelism_mode in ['grid', 'duch', 'LSF']:
			self.signature['parallel_config_directory'] = \
				WriteDiskItem('Directory','Directory')
			self.setOptional('parallel_config_directory')
		if self.parallelism_mode == 'LSF':
			self.signature['time'] = String()
			self.signature['email'] = String()
		if self.parallelism_mode in ['grid', 'duch', 'LSF']:
			packslist = createPackageSignature()
			if len(packslist.values) != 1:
				self.signature['package'] = packslist
				self.signature['package'].userLevel = 2
		self.updateSignature()

def parallel_config_directory_callback(self, *args, **kwargs):
	if self.model is None : return
	self.parallel_config_directory = os.path.join(os.path.dirname(
		self.model.fullPath()), 'tasks', 'annealing')



def initialization(self):
	def link_session(session, **kwargs):
		if session == None : return None
		p = kwargs['parameterized'][0]
		p2 = p._executionNode._children.values()[0]._process
		wd = WriteDiskItem( 'Labelled Cortical folds graph', 'Graph',
				requiredAttributes = { 'labelled' : 'Yes',
				'automatically_labelled' : 'Yes',
				'sulci_recognition_session' : session})
		p2.signature['output_graph'] = ListOf(wd)
		p2.changeSignature(p2.signature)
		return p2.data_graph

	def signatureListOf(process):
		params = []
		for p, v in process.signature.items() :
			if not isinstance(v, neuroData.Choice):
				params += [p, ListOf(v)]
			else:	params += [p, v]

		process.changeSignature(Signature(*params))
	p1 = getProcessInstance('recognition')
	p2 = getProcessInstance('recognition_error')
	signatureListOf(p1)
	signatureListOf(p2)
	eNode = TopNode('Recognize and test', parameterized=self)
	eNode.addChild('AutomaticRecognition',
		ProcessExecutionNode(p1, optional = 1))
	eNode.AutomaticRecognition.removeLink('output_graph', 'data_graph' )
	eNode.AutomaticRecognition.removeLink('model', 'data_graph' )
	
	eNode.addChild('RecognitionError',
		ProcessExecutionNode(p2, optional = 1))
	eNode.RecognitionError.removeLink('labeled_graph', 'base_graph')
	eNode.addLink('AutomaticRecognition.data_graph', 'data_graph')
	eNode.addLink('AutomaticRecognition.model', 'model')
	eNode.addLink('AutomaticRecognition.output_graph', 'session',
		function = link_session)
	eNode.addLink('AutomaticRecognition.output_graph', 'data_graph')
	eNode.addLink('RecognitionError.model', 'model')
	eNode.addLink('RecognitionError.base_graph',
		'AutomaticRecognition.data_graph')
	eNode.addLink('RecognitionError.labeled_graph',
		'AutomaticRecognition.output_graph')
	eNode.addLink(None, 'parallelism_mode', eNode.signature_callback)
	self.addLink(None, 'model', self.parallel_config_directory_callback)
	self.setExecutionNode(eNode)


#################################### Task ######################################
class Task(object):
	def __init__(self, cmd):
		self.cmd = cmd

	def tostring(self):
		return self.cmd

class TaskList(Task):
	def __init__(self):
		self.cmd = []

	def append(self, cmd):
		self.cmd += [cmd]

	def tostring(self):
		return ' && '.join(self.cmd)


################################ Task Manager ##################################
class TaskManager(object):
	def __init__(self, process, context): pass
	def addInfo(self, parent, ind, processes): pass
	def update(self, processes, selected): pass
	def finalize(self): self.stream.close()


class ParallelTaskManager(TaskManager):
	def __init__(self, process, context):
		TaskManager.__init__(self, process, context)
		
	def addInfo(self, parent, ind, processes):
		self.tasks = TaskList()
		for p in processes:
			p.parent['manage_tasks'] = True
			p.parent['self'] = parent
			p.parent['ind'] = ind
			p.parent['tasks'] = self.tasks
			p.parent['package_dir'] = package_dir


class LsfParallelTaskManager(ParallelTaskManager):
	def __init__(self, process, context):
		context.write('LSF parallelism mode')
		ParallelTaskManager.__init__(self, process, context)
		raise RuntimeError('LSF mode : not implemented yet')


class GridParallelTaskManager(ParallelTaskManager):
	def __init__(self, process, context):
		context.write('Grid (Matthieu) parallelism mode')
		ParallelTaskManager.__init__(self, process, context)
		self.dir = process.parallel_config_directory.fullPath()
		if not os.path.isdir(self.dir): os.makedirs(self.dir)	
		self.name = os.path.join(self.dir, 'siRelax-grid_batch')
		self.stream = open(self.name, 'w')
		self.csvstream = open(process.Output.fullPath(), 'w')
		self.csvstream.write("Subject\tRates\n")
		self.csvstream.close()

	def update(self, processes, selected):
		p1 = processes[0]
		cmd = p1.parent['tasks'].tostring()
		cmd = 'bash -c "%s"' % cmd
		log = p1.parent['file'] + ".log"
		cmd = 'cd %s && nice %s > %s\n'  % (self.dir, cmd, log)
		self.stream.write(cmd)

	def finalize(self):
		ParallelTaskManager.finalize(self)
		distcmd = distutils.spawn.find_executable(\
			'grid.py')
		scriptname = os.path.join(self.dir, 'siRelax-grid.sh')
		stream = open(scriptname, 'w')
		stream.write('#!/bin/bash\n\n')
		stream.write("python2 %s  --host ~/neurospin-distcc-hosts --tasks %s --log %s --timeslot -" % (distcmd, self.name, self.name + '.log'))
		stream.close()
		os.chmod(scriptname, 0o750)


class DuchParallelTaskManager(ParallelTaskManager):
	def __init__(self, process, context):
		context.write('Duch parallelism mode')
		ParallelTaskManager.__init__(self, process, context)
		self.dir = process.parallel_config_directory.fullPath()
		if not os.path.isdir(self.dir): os.makedirs(self.dir)	
		self.name = os.path.join(self.dir, 'siRelax-duch_batch')
		self.stream = open(self.name, 'w')
		self.csvstream = open(process.Output.fullPath(), 'w')
		self.csvstream.write("Subject\tRates\n")
		self.csvstream.close()

	def update(self, processes, selected):
		p1 = processes[0]
		cmd = p1.parent['tasks'].tostring()
		cmd = 'bash -c \\"%s\\"' % cmd
		log = p1.parent['file'] + ".log"
		cmd = '"cd %s && nice %s > %s"\n'  % (self.dir, cmd, log)
		self.stream.write(cmd)

	def finalize(self):
		ParallelTaskManager.finalize(self)
		distcmd = distutils.spawn.find_executable(\
			'distributed_computing.py')
		scriptname = os.path.join(self.dir, 'siRelax-duch.sh')
		stream = open(scriptname, 'w')
		stream.write('#!/bin/bash\n\n')
		stream.write("python2 %s -l 1 -v ~/hosts '%s' '%s'" % \
			(distcmd, self.name, self.name + '.log'))
		stream.close()
		os.chmod(scriptname, 0o750)
	
	
class LocalParallelTaskManager(ParallelTaskManager):
	def __init__(self, process, context):
		self.stream = open(process.Output.fullPath(), 'w')
		self.stream.write("Subject\tRates\n")
		self.context = context
		self.rates = {}

	def addInfo(self, parent, ind, processes):
		for p in processes:
			p.parent['manage_tasks'] = False

	def update(self, processes, selected):
		p = processes[1]
		if selected[p.name]:
			subject = p.labeled_graph.get('subject')
			rate = float(p.parent['error_rate'])
			self.rates[subject] = rate
			self.stream.write("%s\t%f\n" % (subject, rate))
			self.stream.flush()

	def finalize(self):
		ParallelTaskManager.finalize(self)
		self.context.write("\n-------------------------\n")
		self.context.write("rates = ")
		self.context.write(self.rates)

def taskManagerFactory(self, context):
	if self.parallelism_mode == 'grid':
		return GridParallelTaskManager(self, context)
	elif self.parallelism_mode == 'duch':
		return DuchParallelTaskManager(self, context)
	elif self.parallelism_mode == 'LSF':
		return LsfParallelTaskManager(self, context)
	elif self.parallelism_mode == 'local':
		return LocalParallelTaskManager(self, context)

		
################################# Processes ####################################
def change_signature_test(self, process):
	if self.parallelism_mode in ['grid', 'duch', 'LSF']:
		del process.signature['labeled_graph']
		process.signature['labeled_graph'] = \
			WriteDiskItem('Data graph', 'Graph')
	else:
		del process.signature['labeled_graph']
		process.signature['labeled_graph'] = \
			ReadDiskItem('Data graph', 'Graph')
	process.changeSignature(process.signature)


def createProcesses(self, context):
	subprocess = {}
	selected = {}
	process_name_list = []
	for i, node in enumerate(self._executionNode._children.values()):
		name = node._process.name
		process_name_list.append(name)
		signature = node._process.signature
		params = {}
		size = 0
		for n in node._process.signature.keys():
			s = len(getattr(node._process, n, None))
			if size < s: size = s
		for n in node._process.signature.keys():
			params[n] = getattr(node._process, n, None)	
			if len(params[n]) == 1:
				params[n] = params[n] * size
		p_origin = getProcessInstance(name)
		processes = p_origin._iterate(**params)
		
		if name == 'Recognition Error':
			for p in processes:
				self.change_signature_test(p)	
		subprocess[name] , selected[name] = processes, node._selected
	processes = zip(*[subprocess[n] for n in process_name_list])
	return processes, selected


def execution(self, context):
	context.write('create processes...')
	processes, selected = self.createProcesses(context)
	n = len(processes)
	for name, select in selected.items():
		if not select:
			context.write('<font color=orange>' +
				'Skip unselected node: ' + name + '</font>')
	context.write('%d iterations : ' % n)
	taskManager = self.taskManagerFactory(context)

	# run processes :
	for i, (p1, p2) in enumerate(processes):
		context.write("%d / %d" % (i + 1, n))
		taskManager.addInfo(self, i, [p1, p2])
		if selected[p1.name]: context.runProcess(p1)
		if selected[p2.name]: context.runProcess(p2)
		taskManager.update([p1, p2], selected)
	taskManager.finalize()

