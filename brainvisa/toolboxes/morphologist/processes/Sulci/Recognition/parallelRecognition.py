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

from neuroProcesses import *
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
                                          : 'Yes' } ),
    'number_of_trials', Integer(), 
    'keep_all_results', Boolean(),
    'energy_plot_file', WriteDiskItem( 'siRelax Fold Energy', 'siRelax Fold Energy' ),
    'stats_file', WriteDiskItem( 'Text file', 'Text file' ), 
    'rate', Float(),
    'stopRate', Float(),
    'niterBelowStopProp', Integer(),
)

def initialization( self ):
    self.setOptional( 'stats_file' )
    self.linkParameters( 'model', 'data_graph' )
    self.linkParameters( 'output_graph', 'data_graph' )
    self.linkParameters( 'energy_plot_file', 'output_graph' )
    self.linkParameters( 'stats_file', 'output_graph' )
    self.number_of_trials = 10
    self.keep_all_results = 0
    self.signature[ 'rate' ].userLevel = 2
    self.signature[ 'stopRate' ].userLevel = 2
    self.signature[ 'niterBelowStopProp' ].userLevel = 2
    self.rate = 0.98
    self.stopRate = 0.05
    self.niterBelowStopProp = 1

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
    if self.keep_all_results:
      pn = ParallelExecutionNode( 'ParallelRecognition' )
    else:
      pn = SerialExecutionNode( 'ParallelRecognition' )
      context.write( 'executing in serial mode when keep_all_results is False' )
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
        pn.addChild( name, ProcessExecutionNode( 'recognition' ) )
        proc = getattr( pn, name )
        proc.data_graph = self.data_graph
        proc.model = self.model
        proc.output_graph = g
        proc.energy_plot_file = s
        proc.rate = self.rate
        proc.stopRate = self.stopRate
        proc.niterBelowStopProp = self.niterBelowStopProp

        nrjfiles.append( s )
    context.write( 'running ParallelRecognition nodes' )
    pn.run( context )
    context.write( 'ParallelRecognition nodes done' )

    # find and keep the best one
    graphs = [ ReadDiskItem( 'Labelled Cortical folds graph',
        'Graph And Data' ).findValue( g ) for g in res ]
    energies = [ ReadDiskItem( 'siRelax Fold Energy',
        'siRelax Fold Energy' ).findValue( s ) for s in stats ]
    context.runProcess( 'chooseBestRecognition', labelled_graphs=graphs,
        energy_plot_files=energies, output_graph=self.output_graph,
        energy_plot_file=self.energy_plot_file, stats_file=self.stats_file )

