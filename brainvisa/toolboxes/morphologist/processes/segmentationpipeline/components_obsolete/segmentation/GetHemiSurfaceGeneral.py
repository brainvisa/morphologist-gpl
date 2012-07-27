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

import shfjGlobals

from brainvisa.processes import *
name ='Get Hemi Surface'
userLevel = 2

signature = Signature(
  'Side', Choice("Both","Left","Right"),
  'mri_corrected', ReadDiskItem( "T1 MRI Bias Corrected",
      shfjGlobals.vipVolumeFormats ),
  'split_mask', ReadDiskItem( 'Split Brain Mask',
      shfjGlobals.vipVolumeFormats ),
  'left_hemi_cortex', ReadDiskItem( 'Left CSF+GREY Mask',
      'Aims writable volume formats' ),
  'right_hemi_cortex', ReadDiskItem( 'Right CSF+GREY Mask',
      'Aims writable volume formats' ),
  'left_hemi_mesh', WriteDiskItem( 'Left Hemisphere Mesh',
      'Aims mesh formats' ),
  'right_hemi_mesh', WriteDiskItem( 'Right Hemisphere Mesh',
      'Aims mesh formats' ),
)

def initialization( self ):
    
  # create nodes

  eNode = SelectionExecutionNode( self.name, parameterized = self )
  eNode.addChild( 'GetSphericalHemiSurface',
                  ProcessExecutionNode( 'GetSphericalHemiSurface', selected = 1 ) )
  eNode.addChild( 'GetOpenedHemiSurface',
                  ProcessExecutionNode( 'AnaGetOpenedHemiSurface', selected = 0 ) )

  # break internal links
  eNode.GetSphericalHemiSurface.clearLinksTo('split_mask')
  eNode.GetSphericalHemiSurface.clearLinksTo('left_hemi_cortex')
  eNode.GetSphericalHemiSurface.clearLinksTo('right_hemi_cortex')
  eNode.GetSphericalHemiSurface.clearLinksTo('left_hemi_mesh')
  eNode.GetSphericalHemiSurface.clearLinksTo('right_hemi_mesh')
  
  eNode.GetOpenedHemiSurface.clearLinksTo('split_mask')
  eNode.GetOpenedHemiSurface.clearLinksTo('left_hemi_cortex')
  eNode.GetOpenedHemiSurface.clearLinksTo('right_hemi_cortex')
  eNode.GetOpenedHemiSurface.clearLinksTo('left_hemi_mesh')
  eNode.GetOpenedHemiSurface.clearLinksTo('right_hemi_mesh')
  
  # links
  eNode.addLink('GetSphericalHemiSurface.mri_corrected', 'mri_corrected')
  eNode.addLink('mri_corrected', 'GetSphericalHemiSurface.mri_corrected')
  eNode.addLink('GetSphericalHemiSurface.split_mask', 'split_mask')
  eNode.addLink('split_mask', 'GetSphericalHemiSurface.split_mask')
  eNode.addLink('GetSphericalHemiSurface.left_hemi_cortex', 'left_hemi_cortex')
  eNode.addLink('left_hemi_cortex', 'GetSphericalHemiSurface.left_hemi_cortex')
  eNode.addLink('GetSphericalHemiSurface.right_hemi_cortex', 'right_hemi_cortex')
  eNode.addLink('right_hemi_cortex', 'GetSphericalHemiSurface.right_hemi_cortex')
  eNode.addLink('GetSphericalHemiSurface.left_hemi_mesh', 'left_hemi_mesh')
  eNode.addLink('left_hemi_mesh', 'GetSphericalHemiSurface.left_hemi_mesh')
  eNode.addLink('GetSphericalHemiSurface.right_hemi_mesh', 'right_hemi_mesh')
  eNode.addLink('right_hemi_mesh', 'GetSphericalHemiSurface.right_hemi_mesh')
  
  eNode.addLink('GetOpenedHemiSurface.mri_corrected', 'mri_corrected')
  eNode.addLink('mri_corrected', 'GetOpenedHemiSurface.mri_corrected')
  eNode.addLink('GetOpenedHemiSurface.split_mask', 'split_mask')
  eNode.addLink('split_mask', 'GetOpenedHemiSurface.split_mask')
  eNode.addLink('GetOpenedHemiSurface.left_hemi_cortex', 'left_hemi_cortex')
  eNode.addLink('left_hemi_cortex', 'GetOpenedHemiSurface.left_hemi_cortex')
  eNode.addLink('GetOpenedHemiSurface.right_hemi_cortex', 'right_hemi_cortex')
  eNode.addLink('right_hemi_cortex', 'GetOpenedHemiSurface.right_hemi_cortex')
  eNode.addLink('GetOpenedHemiSurface.left_hemi_mesh', 'left_hemi_mesh')
  eNode.addLink('left_hemi_mesh', 'GetOpenedHemiSurface.left_hemi_mesh')
  eNode.addLink('GetOpenedHemiSurface.right_hemi_mesh', 'right_hemi_mesh')
  eNode.addLink('right_hemi_mesh', 'GetOpenedHemiSurface.right_hemi_mesh')
  
  # self links
  self.linkParameters( 'split_mask', 'mri_corrected' )
  self.linkParameters( 'left_hemi_cortex', 'mri_corrected' )
  self.linkParameters( 'right_hemi_cortex', 'mri_corrected' )
  self.linkParameters( 'left_hemi_mesh', 'mri_corrected' )
  self.linkParameters( 'right_hemi_mesh', 'mri_corrected' )
  
  self.setExecutionNode( eNode )