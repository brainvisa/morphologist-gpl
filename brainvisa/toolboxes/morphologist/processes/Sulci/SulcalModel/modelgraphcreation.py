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
from brainvisa import shelltools
import os, string

name = 'Sulcal Model Graph Creation'
userLevel = 2


signature = Signature(
    'model_graph', WriteDiskItem( 'Model Graph', 'Graph' ),
    'learningbase_data_graphs',
    ListOf( ReadDiskItem( "Data graph", 'Graph',
      requiredAttributes = { 'labelled' : 'Yes', 'manually_labelled': 'Yes' }
      ) ),
    'testbase_data_graphs',
    ListOf( ReadDiskItem( "Data graph", 'Graph',
      requiredAttributes = { 'labelled' : 'Yes', 'manually_labelled': 'Yes' }
      ) ),
    'labels_translation_map',
    ReadDiskItem( 'Label Translation',
                  [ 'Label Translation', 'DEF Label translation' ] ),
    'template_node_model', ReadDiskItem( 'Template model', 'Template model' ), 
    'template_rel_model', ReadDiskItem( 'Template model', 'Template model' ), 
    'template_domain_model', ReadDiskItem( 'Template model domain', 
                                           'Template model domain' ), 
    # 'stat_model_type', Choice( 'from template', 'MLP', 'SVM classifier',
    #                            'SVM regression' ),
    'fallback_rel_model', ReadDiskItem( 'Template model', 'Template model' ),
    #'node_descriptor', OpenChoice( 'from template', 'fold_descriptor2',
    #                               'fold_descriptor3',
    #                               'fold_descriptor4' ), 
    #'rel_descriptor', OpenChoice( 'from template', 'inter_fold_descriptor2',
    #                              'inter_fold_descriptor4' ),
    'model_version', String(), 
    'data_compatibility_version', String(), 
    )

def initialization( self ):
    self.labels_translation_map = \
      self.signature[ 'labels_translation_map' ].findValue(
        { 'filename_variable' : 'sulci_model_noroots' } )
    self.template_node_model = \
      self.signature[ 'template_node_model' ].findValue(
        { 'filename_variable' : 'vertex_descr2_27_mlp' } )
      #  { 'model_type' : 'vertex', 'inputs' : 27 } )
    self.template_rel_model = \
      self.signature[ 'template_rel_model' ].findValue(
        { 'filename_variable' : 'edge_descr2_23_mlp' } )
      #  { 'model_type' : 'edge', 'inputs' : 23 } )
    self.template_domain_model = \
      self.signature[ 'template_domain_model' ].findValue(
        { 'filename_variable' : 'inertialbox' } )
      #  { 'domain_type' : 'inertial_box' } )
    self.stat_model_type = 'from template'
    self.fallback_rel_model = \
      self.signature[ 'fallback_rel_model' ].findValue(
        { 'model_element_type' : 'fake_relation' } )
    self.setOptional( 'model_version' )
    self.setOptional( 'data_compatibility_version' )

def execution( self, context ):
    if len( self.learningbase_data_graphs ) == 0:
        raise RuntimeError( 'learningbase_data_graphs must not be empty' )
    #if self.stat_model_type == 'MLP' and len( self.testbase_data_graphs ) == 0:
    #    raise RuntimeError( 'testbase_data_graphs must not be empty' )
    moddir = os.path.dirname( self.model_graph.fullPath() )
    # ---
    context.write( _t_( 'clearing any pre-existing model data...' ) )
    dataname = self.model_graph.fullPaths()[1]
    if not os.path.isdir(moddir): os.makedirs(moddir)
    if os.path.exists( self.model_graph.fullPath() ):
      shelltools.rm( self.model_graph.fullPath() )
    if os.path.exists( dataname ):
      shelltools.rm( dataname )

    context.write( _t_( 'making model nodes...' ) )
    args = [ self.model_graph, self.labels_translation_map,
             self.template_node_model, self.template_domain_model, '-',
             self.fallback_rel_model ]
    if self.model_version:
        args += [ '--mversion', self.model_version ]
    if self.data_compatibility_version:
        args += [ '--dversion', self.data_compatibility_version ]
    context.system( 'siMakeModel', *args )

    context.write( _t_( 'making domains...' ) )
    domlrn = context.temporary( 'config file' )
    f = open( domlrn.fullPath(), 'w' )
    f.write( '*BEGIN TREE 1.0 domain_learner\n*END\n' )
    f.close()
    sidom = context.temporary( 'config file' )
    f = open( sidom.fullPath(), 'w' )
    f.write( '*BEGIN TREE domTrain\n'
             'modelFile\t' + self.model_graph.fullPath() + '\n'
             'trainschemeFile\t' + domlrn.fullPath() + '\n'
             'graphFiles\t' )
    base = [ x.fullPath() for x in self.learningbase_data_graphs \
             + self.testbase_data_graphs ]
    f.write( string.join( base ) + '\n' )
    f.write( 'clear\t1\n'
             '*END\n' )
    f.close()
    f = open( sidom.fullPath() )
    context.log( 'siDomTrain input file', html=f.read() )
    f.close()
    f = open( domlrn.fullPath() )
    context.log( 'siDomTrain learner input file', html=f.read() )
    f.close()
    context.system( 'siDomTrain', sidom )

    context.write( _t_( 'creating relations...' ) )
    mkedg = context.temporary( 'config file' )
    f = open( mkedg.fullPath(), 'w' )
    f.write( '*BEGIN TREE 1.0 siMkModelEdges\n' 
             'model\t' + self.model_graph.fullPath() + '\n' 
             'labels\t' + self.labels_translation_map.fullPath() + '\n' 
             'adap\t' + self.template_rel_model.fullPath() + '\n' 
             'graphs\t' + string.join( base ) + '\n' 
             'frequency_min\t0.15\n' 
             'remove_brain\t1\n' 
             'set_weights\t1\n' 
             '*END\n' )
    f.close()
    f = open( mkedg.fullPath() )
    context.log( 'siMkModelEdges input file', html=f.read() )
    f.close()
    context.system( 'siMkModelEdges', mkedg )

    context.write( 'learning stats...' )
    stlrn = context.temporary( 'config file' )
    f = open( stlrn.fullPath(), 'w' )
    f.write( '*BEGIN TREE 1.0 const_learner\n' 
             '*BEGIN TREE stats_learner\n' 
             '*END\n' 
             '*END\n' )
    stats = context.temporary( 'config file' )
    f = open( stats.fullPath(), 'w' )
    f.write( '*BEGIN TREE 1.0 siLearn\n' 
             'modelFile\t' + self.model_graph.fullPath() + '\n' 
             'trainschemeFile\t' + stlrn.fullPath() + '\n' 
             'graphFiles\t' + string.join( base ) + '\n' 
             'mode\ttrainStats\n' 
             'stats\t1\n' 
             'cycles\t1\n'
             'label_attribute\tname\n'
             '*END\n' )
    f.close()
    f = open( stats.fullPath() )
    context.log( 'siLearn stats input file', html=f.read() )
    f.close()
    f = open( stlrn.fullPath() )
    context.log( 'stats learner', html=f.read() )
    f.close()
    context.system( 'siLearn.py', stats )

