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

name = 'Brain Mask Segmentation'
userLevel = 2

signature = Signature(
  'mri_corrected', ReadDiskItem( "T1 MRI Bias Corrected",
      'aims readable Volume Formats' ),
  'brain_mask', WriteDiskItem( 'T1 Brain Mask',
      'aims Writable Volume Formats' ),
  'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'Commissure_coordinates', ReadDiskItem( 'Commissure coordinates',
      'Commissure coordinates'),
  'lesion_mask', ReadDiskItem( 'Lesion Mask', 'aims readable Volume Formats' ),
  'white_ridges', ReadDiskItem( "T1 MRI White Matter Ridges",
      'aims Writable Volume Formats' ),
)

def initialization( self ):
  def linkMask( self, proc ):
    p = self.signature[ 'brain_mask' ]
    if not self.histo_analysis:
      if self.mri_corrected:
        return p.findValue( self.mri_corrected )
      return None
    reqatt = {}
    if self.mri_corrected:
      format = self.mri_corrected.format
      if format:
        reqatt[ '_format' ] = set( [ format.name ] )
    if reqatt:
      x = p.findValue( self.histo_analysis, requiredAttributes=reqatt )
    else:
      x = p.findValue( self.histo_analysis )
    return x

  self.setOptional('white_ridges')
  self.setOptional('lesion_mask')
  self.setOptional('Commissure_coordinates')

  # create nodes

  eNode = SelectionExecutionNode( self.name, parameterized = self )
  eNode.addChild( 'BrainSegmentation05',
                  ProcessExecutionNode( 'BrainSegmentation', selected = 0 ) )
  eNode.addChild( 'BrainSegmentation04',
                  ProcessExecutionNode( 'VipGetBrain', selected = 1 ) )

  # break internal links

  eNode.BrainSegmentation05.clearLinksTo( 'brain_mask' )
  eNode.BrainSegmentation05.clearLinksTo( 'white_ridges' )
  eNode.BrainSegmentation05.clearLinksTo( 'commissure_coordinates' )
  eNode.BrainSegmentation05.clearLinksTo( 'histo_analysis' )
  # eNode.BrainSegmentation05.clearLinksTo( 'lesion_mask' )

  eNode.BrainSegmentation04.clearLinksTo( 'histo_analysis' )
  eNode.BrainSegmentation04.clearLinksTo( 'Commissure_coordinates' )
  eNode.BrainSegmentation04.clearLinksTo( 'brain_mask' )
  # eNode.BrainSegmentation04.clearLinksTo( 'lesion_mask' )

  # links for 2005 version

  eNode.addLink( 'BrainSegmentation05.t1mri_nobias', 'mri_corrected' )
  eNode.addLink( 'mri_corrected', 'BrainSegmentation05.t1mri_nobias' )
  eNode.addLink( 'BrainSegmentation05.brain_mask', 'brain_mask' )
  eNode.addLink( 'brain_mask', 'BrainSegmentation05.brain_mask' )
  eNode.addLink( 'BrainSegmentation05.commissure_coordinates',
                 'Commissure_coordinates' )
  eNode.addLink( 'Commissure_coordinates',
                 'BrainSegmentation05.commissure_coordinates' )
  eNode.addLink( 'BrainSegmentation05.histo_analysis', 'histo_analysis' )
  eNode.addLink( 'histo_analysis', 'BrainSegmentation05.histo_analysis' )
  eNode.addLink( 'BrainSegmentation05.lesion_mask', 'lesion_mask' )
  eNode.addLink( 'lesion_mask', 'BrainSegmentation05.lesion_mask' )
  eNode.addLink( 'BrainSegmentation05.white_ridges', 'white_ridges' )
  eNode.addLink( 'white_ridges', 'BrainSegmentation05.white_ridges' )

  # links for 2004 version

  eNode.addLink( 'BrainSegmentation04.mri_corrected', 'mri_corrected' )
  eNode.addLink( 'mri_corrected', 'BrainSegmentation04.mri_corrected' )
  eNode.addLink( 'BrainSegmentation04.brain_mask', 'brain_mask' )
  eNode.addLink( 'brain_mask', 'BrainSegmentation04.brain_mask' )
  eNode.addLink( 'BrainSegmentation04.Commissure_coordinates',
                 'Commissure_coordinates' )
  eNode.addLink( 'Commissure_coordinates',
                 'BrainSegmentation04.Commissure_coordinates' )
  eNode.addLink( 'BrainSegmentation04.histo_analysis', 'histo_analysis' )
  eNode.addLink( 'histo_analysis', 'BrainSegmentation04.histo_analysis' )
  eNode.addLink( 'BrainSegmentation04.lesion_mask', 'lesion_mask' )
  eNode.addLink( 'lesion_mask', 'BrainSegmentation04.lesion_mask' )

  # self links

  self.linkParameters( 'brain_mask', ( 'histo_analysis', 'mri_corrected' ),
    linkMask )
  self.linkParameters( 'histo_analysis', 'mri_corrected' )
  self.linkParameters( 'Commissure_coordinates', 'mri_corrected' )
  self.linkParameters( 'white_ridges', 'mri_corrected' )

  self.setExecutionNode( eNode )

