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

name = 'Grey white Interface'
userLevel = 2

signature = Signature(
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
      'Aims readable volume formats' ),
  'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'split_mask', ReadDiskItem( "Voronoi Diagram",
      'Aims readable volume formats' ),
  'LGW_interface', WriteDiskItem( 'Left Grey White Mask',
      'Aims writable volume formats' ),
  'RGW_interface', WriteDiskItem( 'Right Grey White Mask',
      'Aims writable volume formats' ),
  'left_white_mesh', WriteDiskItem( 'Left Hemisphere White Mesh',
                                    'Aims mesh formats' ),
  'right_white_mesh', WriteDiskItem( 'Right Hemisphere White Mesh',
                                     'Aims mesh formats' ),
  'use_ridges', Boolean(),
  'white_ridges', ReadDiskItem( "T1 MRI White Matter Ridges",
      'Aims readable volume formats' ),
 ) 

def initialization( self ):
  self.use_ridges = "True"
  self.setOptional('white_ridges')

  # create nodes

  eNode = SelectionExecutionNode( self.name, parameterized = self )
  eNode.addChild( 'GreyWhiteInterface05', 
                  ProcessExecutionNode( 'ComputeGreyWhiteInterface',
                                        selected = 0 ) )
  eNode1 = SerialExecutionNode( 'GreyWhiteInterface04', selected = 1 )
  eNode1.addChild( 'GreyWhiteInterface',
                   ProcessExecutionNode( 'AnaComputeHemiGreyWhiteClassif',
                                         optional = 1 ) )
  eNode1.addChild( 'GreyWhiteMesh',
                   ProcessExecutionNode( 'AnaGetSphericalCorticalSurface',
                                         optional = 1 ) )
  eNode.addChild( 'GreyWhiteInterface04', eNode1 )

  # break internal links
  
  eNode.GreyWhiteInterface05.clearLinksTo( 'histo_analysis' )
  eNode.GreyWhiteInterface05.clearLinksTo( 'split_mask' )
  eNode.GreyWhiteInterface05.clearLinksTo( 'white_ridges' )
  eNode.GreyWhiteInterface05.clearLinksTo( 'LGW_interface' )
  eNode.GreyWhiteInterface05.clearLinksTo( 'RGW_interface' )
  eNode.GreyWhiteInterface05.clearLinksTo( 'left_white_mesh' )
  eNode.GreyWhiteInterface05.clearLinksTo( 'right_white_mesh' )

  eNode.GreyWhiteInterface04.GreyWhiteInterface.clearLinksTo( \
      'histo_analysis' )
  eNode.GreyWhiteInterface04.GreyWhiteInterface.clearLinksTo( \
      'brain_voronoi' )
  eNode.GreyWhiteInterface04.GreyWhiteInterface.clearLinksTo( \
      'left_grey_white' )
  eNode.GreyWhiteInterface04.GreyWhiteInterface.clearLinksTo( \
      'right_grey_white' )
  eNode.GreyWhiteInterface04.GreyWhiteMesh.clearLinksTo( 'histo_analysis' )
  eNode.GreyWhiteInterface04.GreyWhiteMesh.clearLinksTo( 'brain_voronoi' )
  eNode.GreyWhiteInterface04.GreyWhiteMesh.clearLinksTo( 'left_white_mesh' )
  eNode.GreyWhiteInterface04.GreyWhiteMesh.clearLinksTo( 'right_white_mesh' )

  # links for 2005 version

  eNode.addLink( 'GreyWhiteInterface05.mri_corrected', 'mri_corrected' )
  eNode.addLink( 'mri_corrected', 'GreyWhiteInterface05.mri_corrected' )
  eNode.addLink( 'GreyWhiteInterface05.histo_analysis', 'histo_analysis' )
  eNode.addLink( 'histo_analysis', 'GreyWhiteInterface05.histo_analysis' )
  eNode.addLink( 'GreyWhiteInterface05.split_mask', 'split_mask' )
  eNode.addLink( 'split_mask', 'GreyWhiteInterface05.split_mask' )
  eNode.addLink( 'GreyWhiteInterface05.LGW_interface', 'LGW_interface' )
  eNode.addLink( 'LGW_interface', 'GreyWhiteInterface05.LGW_interface' )
  eNode.addLink( 'GreyWhiteInterface05.RGW_interface', 'RGW_interface' )
  eNode.addLink( 'RGW_interface', 'GreyWhiteInterface05.RGW_interface' )
  eNode.addLink( 'GreyWhiteInterface05.left_white_mesh', 'left_white_mesh' )
  eNode.addLink( 'left_white_mesh', 'GreyWhiteInterface05.left_white_mesh' )
  eNode.addLink( 'GreyWhiteInterface05.right_white_mesh', 'right_white_mesh' )
  eNode.addLink( 'right_white_mesh', 'GreyWhiteInterface05.right_white_mesh' )
  eNode.addLink( 'GreyWhiteInterface05.Use_ridges', 'use_ridges' )
  eNode.addLink( 'use_ridges', 'GreyWhiteInterface05.Use_ridges' )
  eNode.addLink( 'GreyWhiteInterface05.white_ridges', 'white_ridges' )
  eNode.addLink( 'white_ridges', 'GreyWhiteInterface05.white_ridges' )

  # links for 2004 version

  eNode.addLink( 'GreyWhiteInterface04.GreyWhiteInterface.mri_corrected',
                 'mri_corrected' )
  eNode.addLink( 'mri_corrected',
                 'GreyWhiteInterface04.GreyWhiteInterface.mri_corrected' )
  eNode.addLink( 'GreyWhiteInterface04.GreyWhiteInterface.histo_analysis',
                 'histo_analysis' )
  eNode.addLink( 'histo_analysis',
                 'GreyWhiteInterface04.GreyWhiteInterface.histo_analysis' )
  eNode.addLink( 'GreyWhiteInterface04.GreyWhiteInterface.brain_voronoi',
                 'split_mask' )
  eNode.addLink( 'split_mask',
                 'GreyWhiteInterface04.GreyWhiteInterface.brain_voronoi' )
  eNode.addLink( 'GreyWhiteInterface04.GreyWhiteInterface.left_grey_white',
                 'LGW_interface' )
  eNode.addLink( 'LGW_interface',
                 'GreyWhiteInterface04.GreyWhiteInterface.left_grey_white' )
  eNode.addLink( 'GreyWhiteInterface04.GreyWhiteInterface.right_grey_white',
                 'RGW_interface' )
  eNode.addLink( 'RGW_interface',
                 'GreyWhiteInterface04.GreyWhiteInterface.right_grey_white' )

  eNode.addLink( 'GreyWhiteInterface04.GreyWhiteMesh.mri_corrected',
                 'mri_corrected' )
  eNode.addLink( 'mri_corrected',
                 'GreyWhiteInterface04.GreyWhiteMesh.mri_corrected' )
  eNode.addLink( 'GreyWhiteInterface04.GreyWhiteMesh.histo_analysis',
                 'histo_analysis' )
  eNode.addLink( 'histo_analysis',
                 'GreyWhiteInterface04.GreyWhiteMesh.histo_analysis' )
  eNode.addLink( 'GreyWhiteInterface04.GreyWhiteMesh.brain_voronoi',
                 'split_mask' )
  eNode.addLink( 'split_mask',
                 'GreyWhiteInterface04.GreyWhiteMesh.brain_voronoi' )
  eNode.addLink( 'GreyWhiteInterface04.GreyWhiteMesh.left_white_mesh',
                 'left_white_mesh' )
  eNode.addLink( 'left_white_mesh',
                 'GreyWhiteInterface04.GreyWhiteMesh.left_white_mesh' )
  eNode.addLink( 'GreyWhiteInterface04.GreyWhiteMesh.right_white_mesh',
                 'right_white_mesh' )
  eNode.addLink( 'right_white_mesh',
                 'GreyWhiteInterface04.GreyWhiteMesh.right_white_mesh' )

  # self links

  eNode.addLink( 'histo_analysis', 'mri_corrected' )
  eNode.addLink( 'split_mask', 'histo_analysis' )
  eNode.addLink( 'white_ridges', 'mri_corrected' )
  eNode.addLink( 'LGW_interface', 'split_mask' )
  eNode.addLink( 'RGW_interface', 'LGW_interface' )
  eNode.addLink( 'left_white_mesh', 'LGW_interface' )
  eNode.addLink( 'right_white_mesh', 'RGW_interface' )

  self.setExecutionNode( eNode )

