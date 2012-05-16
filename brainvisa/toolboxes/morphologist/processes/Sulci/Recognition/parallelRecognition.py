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
import shutil, math, os

name = 'Parallel recognition'
userLevel = 1

signature = Signature(
    'data_graph', ReadDiskItem( 'Data graph', 'Graph' ), 
    'model', ReadDiskItem( 'Model graph', 'Graph' ),
    'output_graph',
    WriteDiskItem( 'Labelled Cortical folds graph', 'Graph', 
                   requiredAttributes = { 'labelled' : 'Yes',
                                          'automatically_labelled' \
                                          : 'Yes'} ),
    'model_hint', Choice( ( 'Newer (2008)', 0 ), ( 'Older (2001)', 1 ) ),
    'number_of_trials', Integer(), 
    'keep_all_results', Boolean(),
    'energy_plot_file', WriteDiskItem( 'siRelax Fold Energy', 'siRelax Fold Energy' ),
    'stats_file', WriteDiskItem( 'Text file', 'Text file' ), 
    'rate', Float(),
    'stopRate', Float(),
    'niterBelowStopProp', Integer(),
    'forbid_unknown_label', Boolean(),
)


def modelValue(self, proc, procbis ):
  """
  the input graph which is linked to the model has not necessarily the same
  graph_version but this attribute is a key for Graph data, so it will be seen
  as a required attribute, so it is removed from the link information
  """
  val=None
  if proc.data_graph:
    val=proc.data_graph.attributes()
    if val.has_key( 'graph_version' ):
      del val['graph_version']
  rdi = ReadDiskItem( 'Model graph', 'Graph',
        requiredAttributes={'trained' : 'Yes'} )
  mod = list( rdi._findValues( val, None, False ) )
  db = [ x.get( 'sulci_database' ) for x in mod ]
  dind = [ i for i in range(len(db)) if db[i] is not None ]
  db = [ int(x) for x in db if x is not None ]
  newind = [ dind[db.index(x)] for x in sorted( db ) ]
  if len( mod ) == 1:
    return val
  if len( mod ) > self.model_hint:
    return mod[newind[len( mod ) - self.model_hint - 1]]
  return None


def _iterateAccept( self ):
    # Here we use a modified iteration system: instead of generating an
    # iteration on parallelRecognition, we use the results of the
    # parallelRecognition iteration (which only generates processes)
    # and build a new iteration from these results.
    try:
        params = self._iterationDialog.getLists()
        processes = self.process._iterate( **params )
        iterationProcess = brainvisa.processes.IterationProcess( self.process.name+" iteration", processes )
        procs = defaultContext().runProcess( iterationProcess )
        iteration2 = brainvisa.processes.IterationProcess( self.process.name+" iteration", procs )
        showProcess( iteration2 )
    except:
        neuroException.showException()
        self._iterationDialog.show()


def inlineGUI( self, proc, procview, externalRunButton = True ):
    # we redefine inlineGUI on this process to modify the iteration behaviour
    # (see _iterAccept above)
    gui = procview.defaultInlineGUI( None )
    # rebind the _iterateAccept method of this Process class (defined here in
    # this source) to the process view instance
    procview._iterateAccept = self.__class__._iterateAccept.__get__( procview )
    print procview._iterateAccept
    return gui


def initialization( self ):
    self.linkParameters( 'model', ( 'data_graph', 'model_hint' ),
        self.modelValue )
    self.linkParameters( 'output_graph', 'data_graph' )
    self.linkParameters( 'energy_plot_file', 'output_graph' )
    self.setOptional( 'stats_file' )
    self.linkParameters( 'stats_file', 'output_graph' )
    self.number_of_trials = 10
    self.keep_all_results = 0
    self.signature[ 'rate' ].userLevel = 2
    self.signature[ 'stopRate' ].userLevel = 2
    self.signature[ 'niterBelowStopProp' ].userLevel = 2
    self.signature[ 'forbid_unknown_label' ].userLevel = 2
    self.rate = 0.98
    self.stopRate = 0.05
    self.niterBelowStopProp = 1
    self.forbid_unknown_label = False


def execution( self, context ):
    if self.keep_all_results:
        dir = os.path.dirname( self.output_graph.fullName() )
    else:
        diritem = context.temporary( 'Directory' )
        dir = diritem.fullPath()
    res = []
    stats = []
    energies = []
    nrjfiles = []
    pn = ParallelExecutionNode( 'ParallelRecognition' )

    pproc = Process()
    pproc._id = 'MultipleANNRecognition'
    pproc.name = 'Multiple ANN Recognition'
    sign = []
    pproc.signature = Signature()

    for x in xrange( self.number_of_trials ):
        g = os.path.join( dir, '%s_res_%03d.arg' \
                          % ( os.path.basename( self.data_graph.fullName() ),
                              x ) )
        s = os.path.join( dir, '%s_stats_%03d.nrj' \
                          % ( os.path.basename( self.data_graph.fullName() ),
                              x ) )
        res.append( g )
        stats.append( s )
        context.write( str(x), ': ', g, '\n' )
        name = 'recognition_%d' % x
        pn.addChild( name, ProcessExecutionNode( 'recognition', optional=True,
            selected=True ) )
        proc = getattr( pn, name )
        proc.data_graph = self.data_graph
        proc.model = self.model
        proc.model_hint = self.model_hint
        proc.output_graph = g
        proc.energy_plot_file = s
        proc.rate = self.rate
        proc.stopRate = self.stopRate
        proc.niterBelowStopProp = self.niterBelowStopProp
        proc.forbid_unknown_label = self.forbid_unknown_label

        nrjfiles.append( s )

    eNode = SerialExecutionNode( 'ParallelRecognitionPipeline', optional=True,
        selected=True )
    eNode.addChild( 'recognition', pn )

    # find and keep the best one
    graphs = [ ReadDiskItem( 'Labelled Cortical folds graph',
        'Graph And Data' ).findValue( g ) for g in res ]
    energies = [ ReadDiskItem( 'siRelax Fold Energy',
        'siRelax Fold Energy' ).findValue( s ) for s in stats ]

    choose = ProcessExecutionNode( 'chooseBestRecognition', optional=True,
        selected=True )
    eNode.addChild( 'chooseBestRecognition', choose )
    proc = getattr( eNode, 'chooseBestRecognition' )
    proc.labelled_graphs = graphs
    proc.energy_plot_files = energies
    proc.output_graph = self.output_graph
    proc.energy_plot_file = self.energy_plot_file
    proc.stats_file = self.stats_file

    pproc.setExecutionNode( eNode )

    if hasattr( context, 'inlineGUI' ):
        pv = mainThreadActions().call( ProcessView, pproc )
    return pproc
