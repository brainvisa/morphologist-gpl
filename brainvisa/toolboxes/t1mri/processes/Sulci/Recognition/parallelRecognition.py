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
    for x in xrange( self.number_of_trials ):
        s = nrjfiles[x]
        f = open( s )
        en = f.readlines()
        f.close()
        #context.write( en )
        #context.write( '\n' )
        #context.write( 'len(en):', len(en), '\n' )
        en = en[ len(en)-1 ].split()[2]
        energies.append( float( en ) )
        context.write( 'energy:', en, '\n' )
    context.write( '\nfinal energies:\n' )
    context.write( energies )
    emin = 0
    M = 0
    mean = 0
    var = 0
    if self.stats_file:
        statsfile = open( self.stats_file.fullPath(), 'w' )
    for x in xrange( self.number_of_trials ):
        mean += energies[x]
        var += energies[x] * energies[x]
        if x == 0:
            m = energies[x]
            M = energies[x]
        elif energies[x] < m:
            emin = x
            m = energies[x]
        if M < energies[x]:
            M = energies[x]
        if self.stats_file:
            statsfile.write( res[x] + '\t' + str( energies[x] ) + '\n' )
    mean /= self.number_of_trials
    var = var / self.number_of_trials - mean * mean
    if self.stats_file:
        statsfile.write( '\nmin:\t' + str( m ) + '\t(' + str( emin ) + ')\n' )
        statsfile.write( 'max:\t' + str( M ) + '\n' )
        statsfile.write( 'mean:\t' + str( mean ) + '\n' )
        statsfile.write( 'stddev:\t' + str( math.sqrt( var ) ) + '\n' )
        statsfile.close()
    context.write( 'min: ', m, ' for trial ', emin, '\n' )
    context.system( 'AimsGraphConvert', '-i', res[emin], '-o',
                    self.output_graph )
    if self.energy_plot_file is not None:
        shutil.copy( stats[emin], self.energy_plot_file.fullPath() )


