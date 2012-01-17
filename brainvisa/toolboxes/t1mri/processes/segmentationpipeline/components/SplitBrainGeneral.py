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
name = 'Split Brain Mask'
userLevel = 2

signature = Signature(
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
      'Aims readable volume formats' ),
  'split_mask', WriteDiskItem( "Voronoi Diagram",
      'Aims writable volume formats' ),
  'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'brain_mask', ReadDiskItem( 'T1 Brain Mask',
      'Aims readable volume formats' ),
  'use_template', Boolean(), 
  'voronoi_template', ReadDiskItem( 'Hemispheres Template',
      'Aims readable volume formats' ),
  'commissure_coordinates', ReadDiskItem( 'Commissure coordinates',
                                          'Commissure coordinates'), 
  'use_ridges', Boolean(),
  'white_ridges', ReadDiskItem( "T1 MRI White Matter Ridges",
      'Aims readable volume formats' ),
)


def initialization( self ):
  self.setOptional('white_ridges')
  self.voronoi_template = self.signature[ 'voronoi_template' ].findValue( {} )
  self.use_template = "True"
  self.setOptional('voronoi_template')
  self.setOptional('commissure_coordinates')

  # create nodes

  eNode = SelectionExecutionNode( self.name, parameterized = self )
  eNode.addChild( 'SplitBrain05', 
                  ProcessExecutionNode( 'SplitBrain', selected = 1 ) )
  eNode.addChild( 'SplitBrain04', 
                  ProcessExecutionNode( 'AnaSplitBrainFromBrainMask',
                                        selected = 0 ) )

  # break internal links
  
  eNode.SplitBrain05.clearLinksTo( 'split_mask' )
  eNode.SplitBrain05.clearLinksTo( 'Use_ridges' )
  eNode.SplitBrain05.clearLinksTo( 'white_ridges' )
  eNode.SplitBrain05.clearLinksTo( 'histo_analysis' )
  eNode.SplitBrain05.clearLinksTo( 'brain_mask' )
  eNode.SplitBrain05.clearLinksTo( 'Use_template' )
  eNode.SplitBrain05.clearLinksTo( 'voronoi_template' )
  eNode.SplitBrain05.clearLinksTo( 'commissure_coordinates' )

  eNode.SplitBrain04.clearLinksTo( 'histo_analysis' )
  eNode.SplitBrain04.clearLinksTo( 'brain_mask' )
  eNode.SplitBrain04.clearLinksTo( 'Use_template' )
  eNode.SplitBrain04.clearLinksTo( 'brain_voronoi' )
  eNode.SplitBrain04.clearLinksTo( 'voronoi_template' )
  eNode.SplitBrain04.clearLinksTo( 'Commissure_coordinates' )

  # links for 2005 version

  eNode.addLink( 'SplitBrain05.mri_corrected', 'mri_corrected' )
  eNode.addLink( 'mri_corrected', 'SplitBrain05.mri_corrected' )
  eNode.addLink( 'SplitBrain05.split_mask', 'split_mask' )
  eNode.addLink( 'split_mask', 'SplitBrain05.split_mask' )
  eNode.addLink( 'SplitBrain05.Use_ridges', 'use_ridges' )
  eNode.addLink( 'use_ridges', 'SplitBrain05.Use_ridges' )
  eNode.addLink( 'SplitBrain05.white_ridges', 'white_ridges' )
  eNode.addLink( 'white_ridges', 'SplitBrain05.white_ridges' )
  eNode.addLink( 'SplitBrain05.histo_analysis', 'histo_analysis' )
  eNode.addLink( 'histo_analysis', 'SplitBrain05.histo_analysis' )
  eNode.addLink( 'SplitBrain05.brain_mask', 'brain_mask' )
  eNode.addLink( 'brain_mask', 'SplitBrain05.brain_mask' )
  eNode.addLink( 'SplitBrain05.Use_template', 'use_template' )
  eNode.addLink( 'use_template', 'SplitBrain05.Use_template' )
  eNode.addLink( 'SplitBrain05.voronoi_template', 'voronoi_template' )
  eNode.addLink( 'voronoi_template', 'SplitBrain05.voronoi_template' )
  eNode.addLink( 'SplitBrain05.commissure_coordinates',
                 'commissure_coordinates' )
  eNode.addLink( 'commissure_coordinates',
                 'SplitBrain05.commissure_coordinates' )

  # links for 2004 version

  eNode.addLink( 'SplitBrain04.mri_corrected', 'mri_corrected' )
  eNode.addLink( 'mri_corrected', 'SplitBrain04.mri_corrected' )
  eNode.addLink( 'SplitBrain04.histo_analysis', 'histo_analysis' )
  eNode.addLink( 'histo_analysis', 'SplitBrain04.histo_analysis' )
  eNode.addLink( 'SplitBrain04.brain_mask', 'brain_mask' )
  eNode.addLink( 'brain_mask', 'SplitBrain04.brain_mask' )
  eNode.addLink( 'SplitBrain04.Use_template', 'use_template' )
  eNode.addLink( 'use_template', 'SplitBrain04.Use_template' )
  eNode.addLink( 'SplitBrain04.voronoi_template', 'voronoi_template' )
  eNode.addLink( 'voronoi_template', 'SplitBrain04.voronoi_template' )
  eNode.addLink( 'SplitBrain04.brain_voronoi', 'split_mask' )
  eNode.addLink( 'split_mask', 'SplitBrain04.brain_voronoi' )
  eNode.addLink( 'SplitBrain04.Commissure_coordinates',
                 'commissure_coordinates' )
  eNode.addLink( 'commissure_coordinates',
                 'SplitBrain04.Commissure_coordinates' )

  # self links

  self.linkParameters( 'split_mask', 'brain_mask' )
  self.linkParameters( 'white_ridges', 'mri_corrected' )
  self.linkParameters( 'histo_analysis', 'mri_corrected' )
  self.linkParameters( 'brain_mask', 'histo_analysis' )
  self.linkParameters( 'commissure_coordinates', 'mri_corrected' )

  self.setExecutionNode( eNode )
