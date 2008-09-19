# Copyright CEA and IFR 49 (2000-2005)
#
#  This software and supporting documentation were developed by
#      CEA/DSV/SHFJ and IFR 49
#      4 place du General Leclerc
#      91401 Orsay cedex
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

name = 'Cortical Fold Graph'
userLevel = 2


signature = Signature(
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected', 'GIS Image'),
  'split_mask', ReadDiskItem( 'Voronoi Diagram', 'GIS Image'),
  'left_graph', WriteDiskItem( 'Cortical folds graph', 'Graph',
                               requiredAttributes = { 'labelled' : 'No',
                                                      'side' : 'left',
                                                      'graph_version' : '3.0'
                                                      } ),
  'right_graph', WriteDiskItem( 'Cortical folds graph', 'Graph',
                                requiredAttributes = { 'labelled' : 'No',
                                                       'side' : 'right',
                                                      'graph_version' : '3.0'
                                                       } ),
  'commissure_coordinates', ReadDiskItem( 'Commissure coordinates',
                                          'Commissure coordinates'),
  'Talairach_transform',
  ReadDiskItem( 'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
                 'Transformation matrix' ), 
 )


class switch04:
  def __init__( self, proc ):
    self.proc = proc
  def __call__( self, node ):
    if node.isSelected():
      self.proc.signature['left_graph'].requiredAttributes = \
        { 'labelled' : 'No', 'side' : 'left',
          'graph_version' : '3.0' }
      self.proc.signature['right_graph'].requiredAttributes = \
        { 'labelled' : 'No', 'side' : 'right',
          'graph_version' : '3.0' }
      self.proc.executionNode().addLink( 'CorticalFoldsGraph04.Lgraph', 'left_graph' )
      self.proc.executionNode().addLink( 'left_graph', 'CorticalFoldsGraph04.Lgraph' )
      self.proc.executionNode().addLink( 'CorticalFoldsGraph04.Rgraph', 'right_graph' )
      self.proc.executionNode().addLink( 'right_graph', 'CorticalFoldsGraph04.Rgraph' )
    else:
      self.proc.executionNode().removeLink( 'CorticalFoldsGraph04.Lgraph', 'left_graph' )
      self.proc.executionNode().removeLink( 'left_graph', 'CorticalFoldsGraph04.Lgraph' )
      self.proc.executionNode().removeLink( 'CorticalFoldsGraph04.Rgraph',
                            'right_graph' )
      self.proc.executionNode().removeLink( 'right_graph',
                            'CorticalFoldsGraph04.Rgraph' )
    self.proc._parameterHasChanged( 'mri_corrected',
                                    self.proc.mri_corrected )

class switch05:
  def __init__( self, proc ):
    self.proc = proc
  def __call__( self, node ):
    if node.isSelected():
      self.proc.signature['left_graph'].requiredAttributes = \
        { 'labelled' : 'No', 'side' : 'left',
          'graph_version' : '3.1' }
      self.proc.signature['right_graph'].requiredAttributes = \
        { 'labelled' : 'No', 'side' : 'right',
          'graph_version' : '3.1' }
      self.proc.executionNode().addLink( 'CorticalFoldsGraph05.LeftCorticalFoldsGraph05.graph', 'left_graph' )
      self.proc.executionNode().addLink( 'left_graph', 'CorticalFoldsGraph05.LeftCorticalFoldsGraph05.graph' )
      self.proc.executionNode().addLink( 'CorticalFoldsGraph05.RightCorticalFoldsGraph05.graph', 'right_graph' )
      self.proc.executionNode().addLink( 'right_graph', 'CorticalFoldsGraph05.RightCorticalFoldsGraph05.graph' )
    else:
      self.proc.executionNode().removeLink( 'CorticalFoldsGraph05.LeftCorticalFoldsGraph05.graph', 'left_graph' )
      self.proc.executionNode().removeLink( 'left_graph', 'CorticalFoldsGraph05.LeftCorticalFoldsGraph05.graph' )
      self.proc.executionNode().removeLink( 'CorticalFoldsGraph05.RightCorticalFoldsGraph05.graph', 'right_graph' )
      self.proc.executionNode().removeLink( 'right_graph', 'CorticalFoldsGraph05.RightCorticalFoldsGraph05.graph' )
    self.proc._parameterHasChanged( 'mri_corrected',
                                    self.proc.mri_corrected )

def initialization( self ):
  self.setOptional( 'commissure_coordinates' )

  # create nodes

  eNode = SelectionExecutionNode( self.name, parameterized = self )

  eNode1 = ParallelExecutionNode( 'CorticalFoldsGraph05', selected=0 )
  eNode1.addChild( 'LeftCorticalFoldsGraph05',
                   ProcessExecutionNode( 'CorticalFoldsGraph', optional = 1 ) )
  eNode1.addChild( 'RightCorticalFoldsGraph05',
                   ProcessExecutionNode( 'CorticalFoldsGraph', optional = 1 ) )
  eNode.addChild( 'CorticalFoldsGraph05', eNode1 )

  eNode.addChild( 'CorticalFoldsGraph04',
                  ProcessExecutionNode( 'AnaComputeCorticalFoldArg',
                  selected=1 ) )

  eNode.CorticalFoldsGraph05.LeftCorticalFoldsGraph05.signature[ \
      'side' ].userLevel = 3
  eNode.CorticalFoldsGraph05.RightCorticalFoldsGraph05.side = 'Left'
  eNode.CorticalFoldsGraph05.RightCorticalFoldsGraph05.signature[ \
      'side' ].userLevel = 3
  eNode.CorticalFoldsGraph05.RightCorticalFoldsGraph05.side = 'Right'

  # break internal links

  eNode.CorticalFoldsGraph05.LeftCorticalFoldsGraph05.clearLinksTo( \
      'split_mask' )
  eNode.removeLink( 'CorticalFoldsGraph05.LeftCorticalFoldsGraph05.graph',
    'CorticalFoldsGraph05.LeftCorticalFoldsGraph05.hemi_cortex' )
  eNode.CorticalFoldsGraph05.LeftCorticalFoldsGraph05.clearLinksTo( \
      'commissure_coordinates' )
  eNode.CorticalFoldsGraph05.LeftCorticalFoldsGraph05.clearLinksTo( \
      'Talairach_transform' )

  eNode.CorticalFoldsGraph05.RightCorticalFoldsGraph05.clearLinksTo( \
      'split_mask' )
  eNode.removeLink( 'CorticalFoldsGraph05.RightCorticalFoldsGraph05.graph',
    'CorticalFoldsGraph05.RightCorticalFoldsGraph05.hemi_cortex' )
  eNode.CorticalFoldsGraph05.RightCorticalFoldsGraph05.clearLinksTo( \
      'commissure_coordinates' )
  eNode.CorticalFoldsGraph05.RightCorticalFoldsGraph05.clearLinksTo( \
      'Talairach_transform' )

  eNode.CorticalFoldsGraph04.clearLinksTo( 'brain_voronoi' )
  eNode.CorticalFoldsGraph04.clearLinksTo( 'Lgraph' )
  eNode.CorticalFoldsGraph04.clearLinksTo( 'Rgraph' )
  eNode.CorticalFoldsGraph04.clearLinksTo( 'Commissure_coordinates' )

  # links for 2005 version

  eNode.addLink( 'CorticalFoldsGraph05.LeftCorticalFoldsGraph05.mri_corrected',
                 'mri_corrected' )
  eNode.addLink( \
      'mri_corrected',
      'CorticalFoldsGraph05.LeftCorticalFoldsGraph05.mri_corrected' )

  eNode.addLink( 'CorticalFoldsGraph05.LeftCorticalFoldsGraph05.split_mask',
                 'split_mask' )
  eNode.addLink( 'split_mask',
                 'CorticalFoldsGraph05.LeftCorticalFoldsGraph05.split_mask' )

  eNode.addLink( \
      'CorticalFoldsGraph05.LeftCorticalFoldsGraph05.commissure_coordinates',
      'commissure_coordinates' )
  eNode.addLink( \
      'commissure_coordinates',
      'CorticalFoldsGraph05.LeftCorticalFoldsGraph05.commissure_coordinates' )

  eNode.addLink( \
      'CorticalFoldsGraph05.LeftCorticalFoldsGraph05.Talairach_transform',
      'Talairach_transform' )
  eNode.addLink( \
      'Talairach_transform',
      'CorticalFoldsGraph05.LeftCorticalFoldsGraph05.Talairach_transform' )


  eNode.addLink( \
      'CorticalFoldsGraph05.RightCorticalFoldsGraph05.mri_corrected',
      'mri_corrected' )
  eNode.addLink( \
      'mri_corrected',
      'CorticalFoldsGraph05.RightCorticalFoldsGraph05.mri_corrected' )

  eNode.addLink( 'CorticalFoldsGraph05.RightCorticalFoldsGraph05.split_mask',
                 'split_mask' )
  eNode.addLink( 'split_mask',
                 'CorticalFoldsGraph05.RightCorticalFoldsGraph05.split_mask' )

  eNode.addLink( 'CorticalFoldsGraph05.LeftCorticalFoldsGraph05.graph', 'left_graph' )
  eNode.addLink( 'left_graph', 'CorticalFoldsGraph05.LeftCorticalFoldsGraph05.graph' )
  eNode.addLink( 'CorticalFoldsGraph05.RightCorticalFoldsGraph05.graph', 'right_graph' )
  eNode.addLink( 'right_graph', 'CorticalFoldsGraph05.RightCorticalFoldsGraph05.graph' )


  eNode.addLink( \
      'CorticalFoldsGraph05.RightCorticalFoldsGraph05.commissure_coordinates',
      'commissure_coordinates' )
  eNode.addLink( \
      'commissure_coordinates',
      'CorticalFoldsGraph05.RightCorticalFoldsGraph05.commissure_coordinates' )

  eNode.addLink( \
      'CorticalFoldsGraph05.RightCorticalFoldsGraph05.Talairach_transform',
      'Talairach_transform' )
  eNode.addLink( \
      'Talairach_transform',
      'CorticalFoldsGraph05.RightCorticalFoldsGraph05.Talairach_transform' )


  eNode.addLink( 'CorticalFoldsGraph04.mri_corrected', 'mri_corrected' )
  eNode.addLink( 'mri_corrected', 'CorticalFoldsGraph04.mri_corrected' )

  eNode.addLink( 'CorticalFoldsGraph04.brain_voronoi', 'split_mask' )
  eNode.addLink( 'split_mask', 'CorticalFoldsGraph04.brain_voronoi' )

  eNode.addLink( 'CorticalFoldsGraph04.Lgraph', 'left_graph' )
  eNode.addLink( 'left_graph', 'CorticalFoldsGraph04.Lgraph' )

  eNode.addLink( 'CorticalFoldsGraph04.Rgraph', 'right_graph' )
  eNode.addLink( 'right_graph', 'CorticalFoldsGraph04.Rgraph' )

  eNode.addLink( 'CorticalFoldsGraph04.Commissure_coordinates',
                 'commissure_coordinates' )
  eNode.addLink( 'commissure_coordinates',
                 'CorticalFoldsGraph04.Commissure_coordinates' )
                 
  # self links

  eNode.addLink( 'split_mask', 'mri_corrected' )
  eNode.addLink( 'left_graph', 'mri_corrected' )
  eNode.addLink( 'right_graph', 'mri_corrected' )
  eNode.addLink( 'commissure_coordinates', 'mri_corrected' )
  eNode.addLink( 'Talairach_transform', 'mri_corrected' )

  self.setExecutionNode( eNode )

  x = switch05( self )
  eNode.CorticalFoldsGraph05._selectionChange.add( x )
  x = switch04( self )
  eNode.CorticalFoldsGraph04._selectionChange.add( x )

