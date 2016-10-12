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

name = 'Ana Split Brain from Brain Mask'
userLevel = 2

signature = Signature(
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
      'Aims readable volume formats' ),
  'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'brain_mask', ReadDiskItem( 'T1 Brain Mask',
      'Aims readable volume formats' ),
  'Use_template', Boolean(), 
  'split_template', ReadDiskItem( 'Hemispheres Template',
      'Aims readable volume formats' ),
  'split_mask', WriteDiskItem( 'Split Brain Mask',
      'Aims writable volume formats' ),
   'Commissure_coordinates', ReadDiskItem( 'Commissure coordinates',
       'Commissure coordinates'),
)


def initialization( self ):
  self.linkParameters( 'histo_analysis', 'mri_corrected' )
  self.linkParameters( 'brain_mask', 'mri_corrected' )
  self.linkParameters( 'split_mask', 'mri_corrected' )
  self.linkParameters( 'Commissure_coordinates', 'mri_corrected' )
  self.split_template = self.signature[ 'split_template' ].findValue( {} )
  self.Use_template = 1
  self.setOptional('split_template')
  self.setOptional('Commissure_coordinates')

def execution( self, context ):
    context.runProcess( 'VipSplitBrain',
                        mri_corrected = self.mri_corrected,
                        histo_analysis = self.histo_analysis,
                        brain_mask = self.brain_mask,
                        split_mask = self.split_mask,
                        split_template = self.split_template,
                        Use_template = self.Use_template,
                        Commissure_coordinates = self.Commissure_coordinates )
    # manage referentials
    tm = registration.getTransformationManager()
    tm.copyReferential(self.mri_corrected, self.split_mask)
