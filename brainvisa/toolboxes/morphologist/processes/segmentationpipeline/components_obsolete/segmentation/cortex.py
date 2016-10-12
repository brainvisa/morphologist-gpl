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
from brainvisa import registration

name = 'Compute Cortex image'
userLevel = 2

# Argument declaration
signature = Signature(
  'Side', Choice("Both","Left","Right"),
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
      'Aims readable volume formats' ),
  'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'split_mask', ReadDiskItem( 'Split Brain Mask',
      'Aims readable volume formats' ),
  'use_ridges', Boolean(),
  'white_ridges', ReadDiskItem( "T1 MRI White Matter Ridges",
      'Aims readable volume formats' ),
  'left_hemi_cortex', WriteDiskItem( 'Left CSF+GREY Mask',
      'Aims writable volume formats' ),
  'right_hemi_cortex', WriteDiskItem( 'Right CSF+GREY Mask',
      'Aims writable volume formats' ),
  'pressure', Choice("0","25","50","75","100","125","150"),
 )
# Default values
def initialization( self ):
  self.linkParameters( 'histo_analysis', 'mri_corrected' )
  self.linkParameters( 'left_hemi_cortex', 'mri_corrected' )
  self.linkParameters( 'right_hemi_cortex', 'mri_corrected' )
  self.linkParameters( 'split_mask', 'mri_corrected' )
  self.linkParameters( 'white_ridges', 'mri_corrected' )
  self.use_ridges = "True"
  self.setOptional('white_ridges')
  self.Side = "Both"
  self.pressure = "0"
#

def execution( self, context ):
  context.write( "Masking Bias corrected image with hemisphere masks...")
  Lbraing = context.temporary( 'GIS Image' )
  context.system( 'VipMask', '-i', self.mri_corrected, "-m",
                  self.split_mask, "-o", Lbraing, "-w",
                  "t", "-l", "2" )
  Rbraing = context.temporary( 'GIS Image' )
  context.system( "VipMask", "-i", self.mri_corrected, "-m",
                  self.split_mask, "-o", Rbraing,
                  "-w", "t", "-l", "1" )
  tm=registration.getTransformationManager()
  if self.Side in ('Left','Both'):

      if os.path.exists(self.left_hemi_cortex.fullName() + '.loc'):
        context.write( "Left cortex locked" )
      else:
        context.write( "Detecting left cortex interface..." )
        if self.use_ridges:
          context.system( "VipHomotopicSnake", "-i", Lbraing, "-h",
                        self.histo_analysis, "-o",
                        self.left_hemi_cortex, "-R",  self.white_ridges,
                        "-w", "t", "-p", self.pressure )
        else:
          context.system( "VipHomotopicSnake", "-i", Lbraing, "-h",
                        self.histo_analysis, "-o",
                        self.left_hemi_cortex, "-w", "t", "-p", self.pressure )
        tm.copyReferential(self.mri_corrected, self.left_hemi_cortex)

  if self.Side in ('Right','Both'):

      if os.path.exists(self.right_hemi_cortex.fullName() + '.loc'):
        context.write( "Right cortex locked" )
      else:
        context.write( "Detecting right cortex interface..." )
        if self.use_ridges:
          context.system( "VipHomotopicSnake", "-i", Rbraing, "-h",
                        self.histo_analysis, "-o",
                        self.right_hemi_cortex, "-R",  self.white_ridges,
                        "-w", "t", "-p", self.pressure )
        else:
          context.system( "VipHomotopicSnake", "-i", Rbraing, "-h",
                        self.histo_analysis, "-o",
                        self.right_hemi_cortex, "-w", "t",
                        "-p", self.pressure )
        tm.copyReferential(self.mri_corrected, self.right_hemi_cortex)

