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
import shfjGlobals, math
from brainvisa import anatomist

name = 'View in hippocampic referential'
userLevel = 0

signature = Signature(
  'T1mri', ReadDiskItem( "Raw T1 MRI", shfjGlobals.vipVolumeFormats ),  
  'Transformation_to_hippocamic_ref', WriteDiskItem( 'Transformation matrix', 'Transformation matrix' ),
  'Commissure_coordinates', WriteDiskItem( 'Commissure coordinates','Commissure coordinates'),
  'Normalised',Choice('No','SHFJ from SPM','MNI from Mritotal', 'Marseille from SPM'),
  'Anterior_Commissure', Point3D(), 
  'Posterior_Commissure', Point3D(), 
  'Interhemispheric_Point', Point3D(),
  'Left_Hemisphere_Point', Point3D(),
  'allow_flip_initial_MRI', Boolean(),
  'Rotation_angle', Float(),
  'Rotation_axis', Choice('x','y','z'),
  )

def validation():
  anatomist.validation()

class APCReader:
  def __init__( self, key ):
    self._key = key + 'mm:'
    
  def __call__( self, values, process ):
    acp = None
    if values.Commissure_coordinates is not None:
      acp = values.Commissure_coordinates
    #elif values.T1mri:
    #  acp = ReadDiskItem( 'Commissure coordinates','Commissure coordinates')\
    #    .findValue( values.T1mri )
    if acp is not None and acp.isReadable():
      f = open( acp.fullPath() )
      for l in f.readlines():
        if l[ :len(self._key) ] == self._key:
          return map( float, string.split( l[ len(self._key)+1: ] ) )

def initialization( self ):
  self.linkParameters( 'Commissure_coordinates', 'T1mri' )
  self.linkParameters( 'Transformation_to_hippocamic_ref', 'T1mri' )
  self.Normalised = 'No'
  self.setOptional( 'Anterior_Commissure' )
  self.setOptional( 'Posterior_Commissure' )
  self.setOptional( 'Interhemispheric_Point' )
  self.linkParameters( 'Anterior_Commissure',
                       'T1mri', APCReader( 'AC' ) )
  self.linkParameters( 'Posterior_Commissure',
                       'T1mri', APCReader( 'PC' ) )
  self.linkParameters( 'Interhemispheric_Point',
                       'T1mri', APCReader( 'IH' ) )
  self.linkParameters( 'Left_Hemisphere_Point',
                       'T1mri' ) #, APCReader( 'LH' ) )
  self.setOptional( 'Left_Hemisphere_Point' )
  self.allow_flip_initial_MRI = 0
  self.Rotation_angle = 30.
  self.Rotation_axis = 'x'
  
def execution( self, context ):
  context.runProcess( 'PrepareSubject',
                      T1mri=self.T1mri,
                      Commissure_coordinates=self.Commissure_coordinates,
                      Normalised=self.Normalised,
                      Anterior_Commissure=self.Anterior_Commissure,
                      Posterior_Commissure=self.Posterior_Commissure,
                      Interhemispheric_Point = self.Interhemispheric_Point,
                      Left_Hemisphere_Point=self.Left_Hemisphere_Point,
                      allow_flip_initial_MRI=self.allow_flip_initial_MRI)
  
  
  if self.Commissure_coordinates is not None and self.Commissure_coordinates.isReadable():
    f = open( self.Commissure_coordinates.fullPath() )
    for l in f.readlines():
      if l[ :len('ACmm') ] == 'ACmm':
        self.acmm = map( float, string.split( l[ len('ACmm')+1: ] ) )
      if l[ :len('PCmm') ] == 'PCmm':
        self.pcmm = map( float, string.split( l[ len('PCmm')+1: ] ) )
      if l[ :len('IHmm') ] == 'IHmm':
        self.ihmm = map( float, string.split( l[ len('ACmm')+1: ] ) )
    
  context.system( '/volatile/devel/aimsalgo-main-linux-debug/bin/AimsHippocampicReferential', '--ac', self.acmm[0], self.acmm[1], self.acmm[2], 
                  '--pc', self.pcmm[0], self.pcmm[1], self.pcmm[2], 
                  '--ih', self.ihmm[0], self.ihmm[1], self.ihmm[2], 
                  '-o', self.Transformation_to_hippocamic_ref.fullPath(), 
		  '--angle', self.Rotation_angle, '--axis', self.Rotation_axis )
  
  selfdestroy = []
  a = anatomist.Anatomist()
  
  img = a.loadObject( self.T1mri )
  selfdestroy.append(img)
  
  rw = img.referential
  ri = a.createReferential()
  tiw = a.loadTransformation(self.Transformation_to_hippocamic_ref.fullPath(), ri, rw )
  selfdestroy.append(tiw)
  
  win = a.createWindow( '3D' )
  win.assignReferential( rw )
  win.addObjects( [img] )
  selfdestroy.append(win)

  return selfdestroy





