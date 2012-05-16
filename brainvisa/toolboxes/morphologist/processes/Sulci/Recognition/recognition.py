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
name = 'Sulci Recognition with ANN'
userLevel = 0
import registration


signature = Signature(
    'data_graph', ReadDiskItem( 'Data graph', 'Graph' ),
    'model', ReadDiskItem( 'Model graph', 'Graph',
        requiredAttributes={'trained' : 'Yes'} ),
    'output_graph',
    WriteDiskItem( 'Labelled Cortical folds graph', 'Graph',
                   requiredAttributes = { 'labelled' : 'Yes',
                                          'automatically_labelled' \
                                          : 'Yes'} ),
    'model_hint', Choice( ( 'Newer (2008)', 0 ), ( 'Older (2001)', 1 ) ),
    'energy_plot_file', WriteDiskItem( 'siRelax Fold Energy',
                                       'siRelax Fold Energy' ),
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

def initialization( self ):
    self.linkParameters( 'model', ( 'data_graph', 'model_hint' ),
        self.modelValue )
    self.linkParameters( 'output_graph', 'data_graph' )
    self.linkParameters( 'energy_plot_file', 'output_graph' )
    for p in ['rate', 'stopRate', 'niterBelowStopProp',
        'forbid_unknown_label' ]:
        self.signature[p].userLevel = 2
    self.rate = 0.98
    self.stopRate = 0.05
    self.niterBelowStopProp = 1
    self.parent = {}
    self.parent['manage_tasks'] = False
    self.forbid_unknown_label = False

def getConfigFile(self, context, graphname):
    def exist(file):
        try : os.stat(file)
        except OSError : return False
        else: return True
    dir = self.parent['self'].parallel_config_directory.fullPath()
    cfgfile = os.path.join(dir, 'siRelax-' + graphname)
    if not exist(cfgfile + '.cfg'): return cfgfile + '.cfg'
    n = 0
    while exist(cfgfile + '-' + str(n) + '.cfg'): n += 1
    return cfgfile + '-' + str(n) + '.cfg'

def cmd_duch(self, batchfile, cfgfile):
    import os
    log = os.path.join(dir, batchfile + '.log')
    cmd = '"cd ' + dir + " && nice siRelax " + cfgfile + " > " + log + '"\n'
    return cmd


def execution( self, context ):
    context.write( "Automatic recognition" )
    graphname = self.data_graph.get('subject')
    if not self.parent['manage_tasks']:
        progname = 'siRelax'
        cfgfile = context.temporary( 'Config file' ).fullPath()
    else:
        package = self.parent['self'].package
        if package == 'default':
            progname = distutils.spawn.find_executable('siRelax')
        else:
            progname = os.path.join(self.parent['package_dir'], package,
                                    'bin', 'siRelax')
        cfgfile = self.getConfigFile(context, graphname)
    context.write( 'config : ', cfgfile)
    try:
        stream = open(cfgfile, 'w' )
    except IOError, (errno, strerror):
        error(strerror, maker.output)
    else:
        stream.write( '*BEGIN TREE 1.0 siRelax\n' )
        stream.write( 'modelFile ' + self.model.fullPath() + '\n' )
        stream.write( 'graphFile ' + self.data_graph.fullPath() + '\n' )
        stream.write( 'output ' + self.output_graph.fullPath() + '\n' )
        stream.write( 'plotfile ' + self.energy_plot_file.fullPath() \
                          + '\n' )
        stream.write( 'rate ' + str( self.rate ) + '\n' )
        stream.write( 'stopRate ' + str( self.stopRate ) + '\n' )
        stream.write( 'niterBelowStopProp ' + str( self.niterBelowStopProp ) \
                      + '\n' )
        stream.write( 'extensionMode CONNECT_VOID CONNECT\n' )
        stream.write( '*END\n' )
        stream.close()
        f = open(cfgfile)
        context.log( 'siRelax input file', html=f.read() )
        f.close()
    if self.parent['manage_tasks']:
        self.parent['tasks'].append(progname + ' ' + cfgfile)
        self.parent['file'] = cfgfile
    else:
        context.system(progname, cfgfile)
        if self.forbid_unknown_label:
            context.write( _t_( 'second pass to remove unknown labels...' ) )
            stream = open(cfgfile, 'w' )
            stream.write( '*BEGIN TREE 1.0 siRelax\n' )
            stream.write( 'modelFile ' + self.model.fullPath() + '\n' )
            stream.write( 'graphFile ' + self.output_graph.fullPath() + '\n' )
            stream.write( 'output ' + self.output_graph.fullPath() + '\n' )
            stream.write( 'plotfile ' + self.energy_plot_file.fullPath() \
                              + '\n' )
            stream.write( 'rate ' + str( self.rate ) + '\n' )
            stream.write( 'stopRate ' + str( self.stopRate ) + '\n' )
            stream.write( 'niterBelowStopProp ' + str( self.niterBelowStopProp ) \
                          + '\n' )
            stream.write( 'mode icm\n' )
            stream.write( 'forbidVoidLabel 1\n' )
            stream.write( 'initLabelsType NONE\n' )
            stream.write( '*END\n' )
            stream.close()
            f = open(cfgfile)
            context.log( 'siRelax input file for 2nd pass removing ' \
                '"unknown" label', html=f.read() )
            f.close()
            context.system(progname, cfgfile)

        trManager = registration.getTransformationManager()
        trManager.copyReferential( self.data_graph, self.output_graph )
