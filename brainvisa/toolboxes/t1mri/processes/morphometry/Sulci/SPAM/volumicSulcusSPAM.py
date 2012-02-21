# -*- coding: iso-8859-1 -*-

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

import shfjGlobals     
from brainvisa import shelltools

from neuroProcesses import *
name = 'Volumic Sulcus SPAM'
userLevel = 1

signature = Signature(
    'graphs', ListOf( ReadDiskItem( 'Cortical folds graph', 'Graph' ) ),
    'mri', ReadDiskItem( '3D Volume', 'Aims readable volume formats' ),
    'SPAM', WriteDiskItem( '3D Volume', 'Aims writable volume formats' ),
    'smoothing', Choice('Yes','No'),
    'smoothing_parameter', Float(),
    'bucket',Choice( 'custom', 'Sulci', 'Simple Surfaces','Bottoms',
                     'Junctions with brain hull' ),
    'custom_buckets', String(),
    'label_translation',ReadDiskItem('Label Translation','Label Translation' ),
    'int_to_label_translation', WriteDiskItem( 'log file', 'log file' ),
    'label_attributes', Choice( 'custom', '(label, name)', 'label', 'name' ), 
    'custom_label_attributes', String(),
    'node_edge_types', Choice( 'All', 'custom',
                               'Nodes (fold, cluster, roi, nucleus)',
                               'Relations (junction, cortical, etc.)'), 
    'custom_node_edge_types', String(),
    'label_values', String(), 
)

def initialization( self ):
     self.bucket = 'Sulci'
     self.smoothing = 'Yes'
     self.label_attributes = '(label, name)'
     self.setOptional( 'label_translation' )
     self.setOptional( 'int_to_label_translation' )
     self.setOptional( 'custom_buckets' )
     self.setOptional( 'custom_node_edge_types' )
     self.setOptional( 'custom_label_attributes' )
     self.setOptional( 'label_values' )
     self.smoothing_parameter = 0.25

def execution( self, context ):
     
     NbGraph =  len( self.graphs )
     inc = 1
     context.write('WARNING : This process works with normalized data having the SAME SPATIAL RESOLUTION')
     context.write('')
     context.write('Number of graphes: ', NbGraph)
     if NbGraph == 0:
        raise Exception( _t_( 'argument <em>graph</em> should not be ' \
                              'empty' ) )
   
     temp = context.temporary( 'GIS Image' )
     ok = 0
     
     for graph in self.graphs:

          context.write( 'Subject : ', graph.get('subject'), '(', inc, '/', NbGraph, ')' )
  
          cmd = [ 'siGraph2Label', '-g', graph.fullPath() ]

          if self.mri is not None:
               cmd += [ '-tv', self.mri.fullPath() ]

          if self.label_translation is not None:
               cmd += [ '-tr', self.label_translation.fullPath() ]

          if self.label_attributes == 'custom':
               if self.custom_label_attributes:
                    la = string.split( self.custom_label_attributes )
               else:
                    la = ()
          elif self.label_attributes == '(label, name)':
               la = ()
          else:
               la = ( self.label_attributes, )
          for i in la:
               cmd += [ '-a', i ]

          if self.int_to_label_translation is not None:
               cmd += [ '-ot', self.int_to_label_translation.fullPath() ]

          a = ()
          if self.node_edge_types == 'custom':
               if self.custom_node_edge_types:
                    a = string.split( self.custom_node_edge_types )
          elif self.node_edge_types == 'Nodes (fold, cluster, roi, nucleus)':
               a = ( 'fold', 'cluster', 'roi', 'nucleus' )
          elif self.node_edge_types == 'Relations (junction, cortical, etc.)':
               a = ( 'junction', 'cortical', 'hull_junction', 'plidepassage',
                'scalebloblink', 'blob_saddle_link', 'roi_junction', )
          for i in a:
               cmd += [ '-s', i ]

          if self.label_values:
               a = string.split( self.label_values )
               for i in a:
                    cmd += [ '-l', i ]
         
          if self.bucket == 'custom':
               if not self.custom_buckets:
                    raise Exception( '<em>custom_buckets</em> must be non-empty '
                                'in custom bucket mode' )
               cmd += ['-o', self.temp ]
               a = string.split( self.custom_buckets )
               for i in a:
                    cmd += [ '-b', i ]
               context.system( *cmd )
          else:
               if self.bucket in ('Sulci',):
                    cmd += [ '-o', temp, '-b', 'aims_ss', '-b', 'aims_bottom', '-b', 'aims_other' ]
                    context.system( *cmd )
               if self.bucket in ('Bottoms',):
                    cmd += [ '-o', temp, '-b', 'aims_bottom' ]
                    context.system( *cmd )
               if self.bucket in ('Junctions with brain hull',):
                    cmd += [ '-o', temp, '-b',
                             'aims_junction', '-s', 'hull_junction' ]
                    context.system( *cmd )
               if self.bucket in ('Simple Surfaces',):
                    cmd += [ '-o',temp, '-b', 'aims_ss' ]
                    context.system( *cmd )
          context.system('AimsThreshold', '-i',temp,'-m', 'gt', '-t', '0', '-b','-o', temp  )

          if ok == 0:
               context.system('AimsReplaceLevel', '-o', self.SPAM.fullPath(),'-g', '32767', '-n', '1', '-i', temp )
               ok = 1
          else:
               context.system('AimsReplaceLevel', '-i',temp,'-g','32767', '-n','1', '-o', temp )
               context.system('AimsLinearComb', '-i',temp,'-j', self.SPAM.fullPath(), '-o',self.SPAM.fullPath() )

          inc = inc + 1

     context.system('AimsLinearComb', '-i',self.SPAM.fullPath(),'-b', NbGraph, '-a', '100', '-o',self.SPAM.fullPath() )
     if self.smoothing == 'Yes' :
          context.system('AimsFileConvert', '-i',self.SPAM.fullPath(),'-o',self.SPAM.fullPath(), '-t', 'FLOAT' )
          context.system('AimsImageSmoothing', '-i',self.SPAM.fullPath(),'-o',self.SPAM.fullPath(), '-t', self.smoothing_parameter, '-s', '0' )
   
