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

name = 'Choose best recognition'
userLevel = 2

signature = Signature(
    'labelled_graphs', ListOf( ReadDiskItem( 'Labelled Cortical folds graph',
        'Graph and data',
        requiredAttributes = { 'automatically_labelled' : 'Yes' } ) ),
    'energy_plot_files', ListOf( ReadDiskItem( 'siRelax Fold Energy',
        'siRelax Fold Energy' ) ),
    'output_graph',
        WriteDiskItem( 'Labelled Cortical folds graph', 'Graph',
            requiredAttributes = { 'automatically_labelled' : 'Yes' } ),
    'energy_plot_file', WriteDiskItem( 'siRelax Fold Energy',
        'siRelax Fold Energy' ),
    'stats_file', WriteDiskItem( 'Text file', 'Text file' ),
)


def initialization( self ):
    self.setOptional( 'stats_file' )
    self.linkParameters( 'output_graph', 'labelled_graphs' )
    self.linkParameters( 'energy_plot_files', 'labelled_graphs' )
    self.linkParameters( 'energy_plot_file', 'output_graph' )
    self.linkParameters( 'stats_file', 'output_graph' )


def execution( self, context ):
    if len( self.energy_plot_files ) != len( self.labelled_graphs ):
        raise ValueError( _t_( 'There should be one energy plot file for ' \
            'each labelled graph.' ) )
    energies = []
    for s in self.energy_plot_files:
        f = open( s.fullPath() )
        en = f.readlines()
        f.close()
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
    for x in xrange( len( self.labelled_graphs ) ):
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
            statsfile.write( self.labelled_graphs[x].fullPath() + '\t' + str( energies[x] ) + '\n' )
    mean /= len( self.labelled_graphs )
    var = var / len( self.labelled_graphs ) - mean * mean
    if self.stats_file:
        statsfile.write( '\nmin:\t' + str( m ) + '\t(' + str( emin ) + ')\n' )
        statsfile.write( 'max:\t' + str( M ) + '\n' )
        statsfile.write( 'mean:\t' + str( mean ) + '\n' )
        statsfile.write( 'stddev:\t' + str( math.sqrt( var ) ) + '\n' )
        statsfile.close()
    context.write( 'min: ', m, ' for trial ', emin, '\n' )
    context.system( 'AimsGraphConvert', '-i', self.labelled_graphs[emin], '-o',
                    self.output_graph )
    if self.energy_plot_file is not None:
        shutil.copy( self.energy_plot_files[emin].fullPath(),
            self.energy_plot_file.fullPath() )


