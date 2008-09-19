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

import shfjGlobals     

name = 'Ana Brain Mask from T1 MRI'
userLevel = 0

signature = Signature(
  'T1mri', ReadDiskItem( "Raw T1 MRI", shfjGlobals.vipVolumeFormats ),   
  'Contrast',Choice('High grey/white contrast','Low grey/white contrast'),
  'Bias_type',Choice('Standard bias field','High bias in Z direction'),
  'mri_corrected', WriteDiskItem( 'T1 MRI Bias Corrected', 'GIS image' ),
  'histo_analysis', WriteDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'brain_mask', WriteDiskItem( 'T1 Brain Mask', 'GIS Image' ),
  'Commissure_coordinates', ReadDiskItem( 'Commissure coordinates','Commissure coordinates'),
  'lesion_mask', ReadDiskItem( '3D Volume', shfjGlobals.vipVolumeFormats),
  )


def initialization( self ):
  self.setOptional('lesion_mask')
  self.Contrast = 'High grey/white contrast'
  self.Bias_type = 'Standard bias field'
  self.linkParameters( 'Commissure_coordinates', 'T1mri' )
  self.setOptional('Commissure_coordinates')
  self.linkParameters( 'mri_corrected', 'T1mri' )
  self.linkParameters( 'histo_analysis', 'T1mri' )
  self.linkParameters( 'brain_mask', 'T1mri' )


def execution( self, context ):
  if self.Contrast == 'Low grey/white contrast':
    field_rigidity=20
    sampling=16
    ngrid=2
  else:
    field_rigidity=10
    sampling=16
    ngrid=2
  if self.Bias_type == 'High bias in Z direction':
    Zcorrection=0.5
  else:
    Zcorrection=1
  context.runProcess( 'VipBiasCorrection', mri=self.T1mri, mri_corrected=self.mri_corrected,field_rigidity=field_rigidity,zdir_multiply_regul=Zcorrection,ngrid=ngrid)
  if os.path.exists(self.histo_analysis.fullName() + '.han.loc'):
    context.write(self.histo_analysis.fullName(),'.han has been locked')
    context.write('Remove',self.histo_analysis.fullName(),'.han.loc if you want to trigger a new correction')
  else:
    context.runProcess('VipHistoAnalysis', self.mri_corrected, self.histo_analysis,0)
  context.runProcess('VipGetBrain', mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
