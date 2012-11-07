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
import registration
name = '4 - Split Brain Mask'
userLevel = 2

signature = Signature(
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
      'Aims readable volume formats' ),
  'mode', Choice("Voronoi", "Watershed (2011)"),
  'variant', Choice("regularized","GW Barycentre","WM Standard Deviation"),
  'split_mask', WriteDiskItem( 'Split Brain Mask',
      'Aims writable volume formats' ),
  'bary_factor', Choice("0.9","0.8","0.7","0.6","0.5","0.4","0.3","0.2","0.1"),
  'mult_factor', Choice("0.5","1","1.5","2","2.5","3","3.5","4"),
  'initial_erosion', Float(),
  'cc_min_size', Integer(),
  'visu', Choice("No","Yes"),
  'Use_ridges', Boolean(),
  'white_ridges', ReadDiskItem( 'T1 MRI White Matter Ridges',
      'Aims readable volume formats' ),
  'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'brain_mask', ReadDiskItem( 'T1 Brain Mask',
      'Aims readable volume formats' ),
  'Use_template', Boolean(), 
  'split_template', ReadDiskItem( 'Hemispheres Template',
      'Aims readable volume formats' ),
  'commissure_coordinates', ReadDiskItem( 'Commissure coordinates',
                                          'Commissure coordinates'),
  'fix_random_seed', Boolean(),
)


def initialization( self ):
  self.linkParameters( 'histo_analysis', 'mri_corrected' )
  self.linkParameters( 'brain_mask', 'mri_corrected' )
  self.linkParameters( 'split_mask', 'mri_corrected' )
  self.linkParameters( 'commissure_coordinates', 'mri_corrected' )
  self.linkParameters( 'white_ridges', 'mri_corrected' )
  self.signature[ 'fix_random_seed' ].userLevel = 3
  self.Use_ridges = "True"
  self.setOptional('white_ridges')
  self.visu = "No"
  self.mode = "Watershed (2011)"
  self.variant = "GW Barycentre"
  self.split_template = self.signature[ 'split_template' ].findValue( {} )
  self.Use_template = "True"
  self.setOptional('split_template')
  self.setOptional('commissure_coordinates')
  self.bary_factor = "0.6"
  self.setOptional('bary_factor')
  self.initial_erosion = 2
  self.cc_min_size = 500
  self.setOptional('mult_factor')
  self.mult_factor = "2"
  self.fix_random_seed = False

def execution( self, context ):
    if os.path.exists(self.split_mask.fullName() + '.loc'):
      context.write(self.split_mask.fullName(), ' has been locked')
      context.write('Remove',self.split_mask.fullName(),'.loc if you want to trigger a new segmentation')
    else:
      option_list = []
      if self.commissure_coordinates is not None:
        option_list += ['-Points', self.commissure_coordinates.fullPath()]
      if self.variant=="regularized":
        option_list += ['-walgo','r']
      if self.variant=="GW Barycentre":
        option_list += ['-Bary', self.bary_factor,'-walgo','b']
      elif self.variant=="WM Standard Deviation":
        option_list += ['-Coef', self.mult_factor,'-walgo','c']
      if self.Use_template:
        option_list += ['-template', self.split_template.fullPath(),'-TemplateUse', 'y']
      else:
        option_list += ['-TemplateUse', 'n']
      if self.Use_ridges:
        option_list += ['-Ridge', self.white_ridges.fullPath()]
      if self.fix_random_seed:
        option_list += ['-srand', '10']
      call_list = ['VipSplitBrain',
                     '-input',  self.mri_corrected.fullPath(),
                     '-brain', self.brain_mask.fullPath(),
                     '-analyse', 'r', '-hname', self.histo_analysis.fullPath(),
                     '-output', self.split_mask.fullPath(),
                     '-mode', self.mode,
                     '-erosion', self.initial_erosion,
                     '-ccsize', self.cc_min_size]
      result = []
      apply( context.system, call_list+option_list )
      
      # manage referentials
      tm = registration.getTransformationManager()
      tm.copyReferential(self.mri_corrected, self.split_mask)
      
      return result
