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

name = 'Cortical Fold Graph 2007-2011 (general)'
userLevel = 2


signature = Signature(
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
      'Aims readable volume formats' ),
  'split_mask', ReadDiskItem( 'Split Brain Mask',
      'Aims readable volume formats' ),
  'left_graph', WriteDiskItem( 'Cortical folds graph', 'Graph',
                               requiredAttributes = { 'labelled' : 'No',
                                                      'side' : 'left',
                                                      #'graph_version' : '3.0'
                                                      } ),
  'right_graph', WriteDiskItem( 'Cortical folds graph', 'Graph',
                                requiredAttributes = { 'labelled' : 'No',
                                                       'side' : 'right',
                                                      #'graph_version' : '3.0'
                                                       } ),
  'commissure_coordinates', ReadDiskItem( 'Commissure coordinates',
                                          'Commissure coordinates'),
  'Talairach_transform',
  ReadDiskItem( 'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
                 'Transformation matrix' ), 
 )


class switch_3_0:
  def __init__( self, proc ):
    self.proc = proc
  def __call__( self, node ):
    if node.isSelected():
      self.proc.signature['left_graph'].requiredAttributes = \
        { 'labelled' : 'No', 'side' : 'left' }
      self.proc.signature['right_graph'].requiredAttributes = \
        { 'labelled' : 'No', 'side' : 'right' }
      self.proc.executionNode().addLink( 'CorticalFoldsGraph_3_0.Lgraph',
        'left_graph' )
      self.proc.executionNode().addLink( 'left_graph',
        'CorticalFoldsGraph_3_0.Lgraph' )
      self.proc.executionNode().addLink( 'CorticalFoldsGraph_3_0.Rgraph',
        'right_graph' )
      self.proc.executionNode().addLink( 'right_graph',
        'CorticalFoldsGraph_3_0.Rgraph' )
      self.proc.executionNode().CorticalFoldsGraph_3_0._parameterHasChanged(
        'Lgraph', self.proc.executionNode().CorticalFoldsGraph_3_0.Lgraph )
      self.proc.executionNode().CorticalFoldsGraph_3_0._parameterHasChanged(
        'Rgraph', self.proc.executionNode().CorticalFoldsGraph_3_0.Rgraph )
    else:
      self.proc.executionNode().removeLink( 'CorticalFoldsGraph_3_0.Lgraph',
        'left_graph' )
      self.proc.executionNode().removeLink( 'left_graph',
        'CorticalFoldsGraph_3_0.Lgraph' )
      self.proc.executionNode().removeLink( 'CorticalFoldsGraph_3_0.Rgraph',
                            'right_graph' )
      self.proc.executionNode().removeLink( 'right_graph',
                            'CorticalFoldsGraph_3_0.Rgraph' )

class switch_3_1:
  def __init__( self, proc ):
    self.proc = proc
  def __call__( self, node ):
    if node.isSelected():
      self.proc.signature['left_graph'].requiredAttributes = \
        { 'labelled' : 'No', 'side' : 'left' }
      self.proc.signature['right_graph'].requiredAttributes = \
        { 'labelled' : 'No', 'side' : 'right' }
      self.proc.executionNode().addLink( 'left_graph',
        'CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.graph' )
      self.proc.executionNode().addLink( 'right_graph',
        'CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.graph' )
      self.proc.executionNode().addLink(
        'CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.graph', 'left_graph' )
      self.proc.executionNode().addLink(
        'CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.graph', 'right_graph' )
      self.proc.executionNode().CorticalFoldsGraph_3_1.\
        LeftCorticalFoldsGraph_3_1._parameterHasChanged( 'graph',
          self.proc.executionNode().CorticalFoldsGraph_3_1.\
            LeftCorticalFoldsGraph_3_1.graph )
      self.proc.executionNode().CorticalFoldsGraph_3_1.\
        RightCorticalFoldsGraph_3_1._parameterHasChanged( 'graph',
          self.proc.executionNode().CorticalFoldsGraph_3_1.\
            RightCorticalFoldsGraph_3_1.graph )
    else:
      self.proc.executionNode().removeLink(
        'CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.graph', 'left_graph' )
      self.proc.executionNode().removeLink( 'left_graph',
        'CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.graph' )
      self.proc.executionNode().removeLink(
        'CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.graph', 'right_graph' )
      self.proc.executionNode().removeLink( 'right_graph',
        'CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.graph' )

def initialization( self ):
  self.setOptional( 'commissure_coordinates' )

  # create nodes

  eNode = SelectionExecutionNode( self.name, parameterized = self )

  eNode1 = ParallelExecutionNode( 'CorticalFoldsGraph_3_1', selected=0 )
  eNode1.addChild( 'LeftCorticalFoldsGraph_3_1',
                   ProcessExecutionNode( 'CorticalFoldsGraphPipeline', optional = 1 ) )
  eNode1.addChild( 'RightCorticalFoldsGraph_3_1',
                   ProcessExecutionNode( 'CorticalFoldsGraphPipeline', optional = 1 ) )
  eNode.addChild( 'CorticalFoldsGraph_3_1', eNode1 )

  eNode.addChild( 'CorticalFoldsGraph_3_0',
                  ProcessExecutionNode( 'AnaComputeCorticalFoldArg',
                  selected=1 ) )

  eNode.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.signature[ \
      'side' ].userLevel = 3
  eNode.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.side = 'Left'
  eNode.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.signature[ \
      'side' ].userLevel = 3
  eNode.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.side = 'Right'

  # break internal links

  eNode.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.removeLink( \
      'split_mask', 'mri_corrected' )
  eNode.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.removeLink( \
      'commissure_coordinates', 'mri_corrected' )
  eNode.CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.removeLink( \
      'Talairach_transform', 'split_mask' )

  eNode.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.removeLink( \
      'split_mask', 'mri_corrected' )
  eNode.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.removeLink( \
      'commissure_coordinates', 'mri_corrected' )
  eNode.CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.removeLink( \
      'Talairach_transform', 'split_mask' )

  eNode.CorticalFoldsGraph_3_0.clearLinksTo( 'split_mask' )
  eNode.CorticalFoldsGraph_3_0.clearLinksTo( 'Commissure_coordinates' )

  # links for 3.1 version

  eNode.addLink( 'CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.mri_corrected',
                 'mri_corrected' )
  eNode.addLink( \
      'mri_corrected',
      'CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.mri_corrected' )

  eNode.addLink( 'CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.split_mask',
                 'split_mask' )
  eNode.addLink( 'split_mask',
                 'CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.split_mask' )

  eNode.addLink( \
      'CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.commissure_coordinates',
      'commissure_coordinates' )
  eNode.addLink( \
      'commissure_coordinates',
      'CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.commissure_coordinates' )

  eNode.addLink( \
      'CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.Talairach_transform',
      'Talairach_transform' )
  eNode.addLink( \
      'Talairach_transform',
      'CorticalFoldsGraph_3_1.LeftCorticalFoldsGraph_3_1.Talairach_transform' )


  eNode.addLink( \
      'CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.mri_corrected',
      'mri_corrected' )
  eNode.addLink( \
      'mri_corrected',
      'CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.mri_corrected' )

  eNode.addLink( 'CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.split_mask',
                 'split_mask' )
  eNode.addLink( 'split_mask',
                 'CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.split_mask' )


  eNode.addLink( \
      'CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.commissure_coordinates',
      'commissure_coordinates' )
  eNode.addLink( \
      'commissure_coordinates',
      'CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.commissure_coordinates' )

  eNode.addLink( \
      'CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.Talairach_transform',
      'Talairach_transform' )
  eNode.addLink( \
      'Talairach_transform',
      'CorticalFoldsGraph_3_1.RightCorticalFoldsGraph_3_1.Talairach_transform' )


  eNode.addLink( 'CorticalFoldsGraph_3_0.mri_corrected', 'mri_corrected' )
  eNode.addLink( 'mri_corrected', 'CorticalFoldsGraph_3_0.mri_corrected' )

  eNode.addLink( 'CorticalFoldsGraph_3_0.split_mask', 'split_mask' )
  eNode.addLink( 'split_mask', 'CorticalFoldsGraph_3_0.split_mask' )

  eNode.addLink( 'CorticalFoldsGraph_3_0.Lgraph', 'left_graph' )
  eNode.addLink( 'left_graph', 'CorticalFoldsGraph_3_0.Lgraph' )

  eNode.addLink( 'CorticalFoldsGraph_3_0.Rgraph', 'right_graph' )
  eNode.addLink( 'right_graph', 'CorticalFoldsGraph_3_0.Rgraph' )

  eNode.addLink( 'CorticalFoldsGraph_3_0.Commissure_coordinates',
                 'commissure_coordinates' )
  eNode.addLink( 'commissure_coordinates',
                 'CorticalFoldsGraph_3_0.Commissure_coordinates' )
                 
  # self links
  self.linkParameters( 'split_mask', 'mri_corrected' )
  self.linkParameters( 'commissure_coordinates', 'mri_corrected' )
  self.linkParameters( 'Talairach_transform', 'split_mask' )
  
  self.setExecutionNode( eNode )

  x = switch_3_1( self )
  eNode.CorticalFoldsGraph_3_1._selectionChange.add( x )
  x = switch_3_0( self )
  eNode.CorticalFoldsGraph_3_0._selectionChange.add( x )

