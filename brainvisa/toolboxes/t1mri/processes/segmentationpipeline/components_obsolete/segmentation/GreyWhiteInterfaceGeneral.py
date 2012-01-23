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
  'left_hemi_cortex', WriteDiskItem( 'Left CSF+GREY Mask',
      'Aims writable volume formats' ),
  'right_hemi_cortex', WriteDiskItem( 'Right CSF+GREY Mask',
      'Aims writable volume formats' ),
  'left_white_mesh', WriteDiskItem( 'Left Hemisphere White Mesh',
                                    'Aims mesh formats' ),
  'right_white_mesh', WriteDiskItem( 'Right Hemisphere White Mesh',
                                     'Aims mesh formats' ),
  'left_white_mesh_fine', WriteDiskItem( 'Left Fine Hemisphere White Mesh',
                                    'Aims mesh formats' ),
  'right_white_mesh_fine', WriteDiskItem( 'Right Fine Hemisphere White Mesh',
                                     'Aims mesh formats' ),
  'use_ridges', Boolean(),
  'white_ridges', ReadDiskItem( "T1 MRI White Matter Ridges",
      'Aims readable volume formats' ),
 ) 

def initialization( self ):
  self.use_ridges = "True"
  self.setOptional('white_ridges')

  # create nodes

  eNode = SerialExecutionNode( self.name, parameterized = self )
  eNode.addChild( 'GreyWhiteInterface',
    ProcessExecutionNode( 'AnaComputeHemiGreyWhiteClassif', optional = 1,
    selected=1 ) )
  eNode.addChild( 'cortex_image',
    ProcessExecutionNode( 'cortex', optional = 1, selected=1 ) )

  eNode1 = SelectionExecutionNode( 'Grey/White Mesh', optional=1, selected=1 )
  eNode1.addChild( 'GreyWhiteInterface05', 
                   ProcessExecutionNode( 'ComputeGreyWhiteInterface',
                                         selected = 1 ) )
  eNode1.addChild( 'GreyWhiteMesh',
                   ProcessExecutionNode( 'AnaGetSphericalCorticalSurface',
                                         selected = 0 ) )
  eNode.addChild( 'GreyWhiteMesh', eNode1 )

  # break internal links

  eNode.cortex_image.clearLinksTo( 'histo_analysis' )
  eNode.cortex_image.clearLinksTo( 'split_mask' )
  eNode.cortex_image.clearLinksTo( 'white_ridges' )
  eNode.cortex_image.clearLinksTo( 'left_hemi_cortex' )
  eNode.cortex_image.clearLinksTo( 'right_hemi_cortex' )
  eNode.GreyWhiteMesh.GreyWhiteInterface05.clearLinksTo( 'left_white_mesh' )
  eNode.GreyWhiteMesh.GreyWhiteInterface05.clearLinksTo( 'right_white_mesh' )
  eNode.GreyWhiteMesh.GreyWhiteInterface05.clearLinksTo( 'left_white_mesh_fine' )
  eNode.GreyWhiteMesh.GreyWhiteInterface05.clearLinksTo( 'right_white_mesh_fine' )
  
  eNode.GreyWhiteInterface.clearLinksTo( 'histo_analysis' )
  eNode.GreyWhiteInterface.clearLinksTo( 'brain_voronoi' )
  eNode.GreyWhiteInterface.clearLinksTo( 'left_grey_white' )
  eNode.GreyWhiteInterface.clearLinksTo( 'right_grey_white' )
  eNode.GreyWhiteMesh.GreyWhiteMesh.clearLinksTo( 'histo_analysis' )
  eNode.GreyWhiteMesh.GreyWhiteMesh.clearLinksTo( 'brain_voronoi' )
  eNode.GreyWhiteMesh.GreyWhiteMesh.clearLinksTo( 'left_white_mesh' )
  eNode.GreyWhiteMesh.GreyWhiteMesh.clearLinksTo( 'right_white_mesh' )
  eNode.GreyWhiteMesh.GreyWhiteMesh.clearLinksTo( 'left_white_mesh_fine' )
  eNode.GreyWhiteMesh.GreyWhiteMesh.clearLinksTo( 'right_white_mesh_fine' )

  ## links

  eNode.addLink( 'GreyWhiteInterface.mri_corrected', 'mri_corrected' )
  eNode.addLink( 'mri_corrected', 'GreyWhiteInterface.mri_corrected' )
  eNode.addLink( 'GreyWhiteInterface.histo_analysis', 'histo_analysis' )
  eNode.addLink( 'histo_analysis', 'GreyWhiteInterface.histo_analysis' )
  eNode.addLink( 'GreyWhiteInterface.brain_voronoi', 'split_mask' )
  eNode.addLink( 'split_mask', 'GreyWhiteInterface.brain_voronoi' )
  eNode.addLink( 'GreyWhiteInterface.left_grey_white', 'LGW_interface' )
  eNode.addLink( 'LGW_interface', 'GreyWhiteInterface.left_grey_white' )
  eNode.addLink( 'GreyWhiteInterface.right_grey_white', 'RGW_interface' )
  eNode.addLink( 'RGW_interface', 'GreyWhiteInterface.right_grey_white' )

  eNode.addLink( 'cortex_image.mri_corrected', 'mri_corrected' )
  eNode.addLink( 'mri_corrected', 'cortex_image.mri_corrected' )
  eNode.addLink( 'cortex_image.histo_analysis', 'histo_analysis' )
  eNode.addLink( 'histo_analysis', 'cortex_image.histo_analysis' )
  eNode.addLink( 'cortex_image.split_mask', 'split_mask' )
  eNode.addLink( 'split_mask', 'cortex_image.split_mask' )
  eNode.addLink( 'cortex_image.use_ridges', 'use_ridges' )
  eNode.addLink( 'use_ridges', 'cortex_image.use_ridges' )
  eNode.addLink( 'cortex_image.white_ridges', 'white_ridges' )
  eNode.addLink( 'white_ridges', 'cortex_image.white_ridges' )
  eNode.addLink( 'cortex_image.left_hemi_cortex', 'left_hemi_cortex' )
  eNode.addLink( 'left_hemi_cortex', 'cortex_image.left_hemi_cortex' )
  eNode.addLink( 'cortex_image.right_hemi_cortex', 'right_hemi_cortex' )
  eNode.addLink( 'right_hemi_cortex', 'cortex_image.right_hemi_cortex' )

  ## links for 2005 version

  eNode.addLink( 'GreyWhiteMesh.GreyWhiteInterface05.left_hemi_cortex',
    'left_hemi_cortex' )
  eNode.addLink( 'left_hemi_cortex',
    'GreyWhiteMesh.GreyWhiteInterface05.left_hemi_cortex' )
  eNode.addLink( 'GreyWhiteMesh.GreyWhiteInterface05.right_hemi_cortex',
    'right_hemi_cortex' )
  eNode.addLink( 'right_hemi_cortex',
    'GreyWhiteMesh.GreyWhiteInterface05.right_hemi_cortex' )
  eNode.addLink( 'GreyWhiteMesh.GreyWhiteInterface05.left_white_mesh',
    'left_white_mesh' )
  eNode.addLink( 'left_white_mesh',
    'GreyWhiteMesh.GreyWhiteInterface05.left_white_mesh' )
  eNode.addLink( 'GreyWhiteMesh.GreyWhiteInterface05.right_white_mesh',
    'right_white_mesh' )
  eNode.addLink( 'right_white_mesh',
    'GreyWhiteMesh.GreyWhiteInterface05.right_white_mesh' )
  eNode.addLink( 'GreyWhiteMesh.GreyWhiteInterface05.left_white_mesh_fine',
    'left_white_mesh_fine' )
  eNode.addLink( 'left_white_mesh_fine',
    'GreyWhiteMesh.GreyWhiteInterface05.left_white_mesh_fine' )
  eNode.addLink( 'GreyWhiteMesh.GreyWhiteInterface05.right_white_mesh_fine',
    'right_white_mesh_fine' )
  eNode.addLink( 'right_white_mesh_fine',
    'GreyWhiteMesh.GreyWhiteInterface05.right_white_mesh_fine' )

  ## links for 2004 version

  eNode.addLink( 'GreyWhiteMesh.GreyWhiteMesh.mri_corrected',
                 'mri_corrected' )
  eNode.addLink( 'mri_corrected',
                 'GreyWhiteMesh.GreyWhiteMesh.mri_corrected' )
  eNode.addLink( 'GreyWhiteMesh.GreyWhiteMesh.histo_analysis',
                 'histo_analysis' )
  eNode.addLink( 'histo_analysis',
                 'GreyWhiteMesh.GreyWhiteMesh.histo_analysis' )
  eNode.addLink( 'GreyWhiteMesh.GreyWhiteMesh.brain_voronoi',
                 'split_mask' )
  eNode.addLink( 'split_mask',
                 'GreyWhiteMesh.GreyWhiteMesh.brain_voronoi' )
  eNode.addLink( 'GreyWhiteMesh.GreyWhiteMesh.left_white_mesh',
                 'left_white_mesh' )
  eNode.addLink( 'left_white_mesh',
                 'GreyWhiteMesh.GreyWhiteMesh.left_white_mesh' )
  eNode.addLink( 'GreyWhiteMesh.GreyWhiteMesh.right_white_mesh',
                 'right_white_mesh' )
  eNode.addLink( 'right_white_mesh',
                 'GreyWhiteMesh.GreyWhiteMesh.right_white_mesh' )
  eNode.addLink( 'GreyWhiteMesh.GreyWhiteMesh.left_white_mesh_fine',
                 'left_white_mesh_fine' )
  eNode.addLink( 'left_white_mesh_fine',
                 'GreyWhiteMesh.GreyWhiteMesh.left_white_mesh_fine' )
  eNode.addLink( 'GreyWhiteMesh.GreyWhiteMesh.right_white_mesh_fine',
                 'right_white_mesh_fine' )
  eNode.addLink( 'right_white_mesh_fine',
                 'GreyWhiteMesh.GreyWhiteMesh.right_white_mesh_fine' )
                 
  ## self links

  self.linkParameters( 'histo_analysis', 'mri_corrected' )
  self.linkParameters( 'split_mask', 'histo_analysis' )
  self.linkParameters( 'white_ridges', 'mri_corrected' )
  self.linkParameters( 'LGW_interface', 'split_mask' )
  self.linkParameters( 'RGW_interface', 'LGW_interface' )
  self.linkParameters( 'left_hemi_cortex', 'LGW_interface' )
  self.linkParameters( 'right_hemi_cortex', 'RGW_interface' )
  self.linkParameters( 'left_white_mesh', 'left_hemi_cortex' )
  self.linkParameters( 'right_white_mesh', 'right_hemi_cortex' )
  self.linkParameters( 'left_white_mesh_fine', 'left_hemi_cortex' )
  self.linkParameters( 'right_white_mesh_fine', 'right_hemi_cortex' )

  self.setExecutionNode( eNode )

