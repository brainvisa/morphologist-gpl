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
import registration
import shfjGlobals

name = 'Talairach Transformation From Normalization'
userLevel = 2

def validation():
  try:
    import soma.aims
  except:
    raise ValidationError( 'soma.aims module not present' )

signature = Signature(
  'normalization_transformation', ReadDiskItem( 'Transform Raw T1 MRI to ' \
      'Talairach-MNI template-SPM', 'Transformation matrix' ),
  'Talairach_transform',
    WriteDiskItem( 'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
                   'Transformation matrix' ),
  'Commissure_coordinates', WriteDiskItem( 'Commissure coordinates',
                                           'Commissure coordinates'),
  't1mri', ReadDiskItem( 'Raw T1 MRI', 'Aims Readable Volume Formats' ),
  'source_referential', ReadDiskItem( 'Referential', 'Referential' ),
  'normalized_referential', ReadDiskItem( 'Referential', 'Referential' ),
)


def initialization( self ):
  def linkRef( proc, param ):
    if proc.normalization_transformation:
      s = proc.normalization_transformation.get( 'source_referential', None )
      if s:
        trManager = registration.getTransformationManager()
        res = trManager.referential( s )
        if res:
          return res
    if proc.t1mri:
      import sys
      return ReadDiskItem( 'Referential of Raw T1 MRI', \
			'Referential' ).findValue(self.t1mri )
    return None
  def linkNormRef( proc, param ):
    trManager = registration.getTransformationManager()
    if proc.normalization_transformation:
      s = proc.normalization_transformation.get( 'destination_referential',
        None )
      if s:
        return trManager.referential( s )
    return trManager.referential( registration.talairachMNIReferentialId )
  self.linkParameters( 'Talairach_transform',
    'normalization_transformation' )
  self.linkParameters( 'Commissure_coordinates', 'Talairach_transform' )
  self.setOptional( 'Commissure_coordinates' )
  self.linkParameters( 't1mri', 'Commissure_coordinates' )
  self.setOptional( 't1mri' )
  self.linkParameters( 'source_referential', [ 'normalization_transformation',
    't1mri' ], linkRef )
  self.linkParameters( 'normalized_referential',
    'normalization_transformation', linkNormRef )

def execution( self, context ):
  from soma import aims
  t1toMni = aims.read( self.normalization_transformation.fullPath() )
  trManager = registration.getTransformationManager()
  _mniToACPCpaths = trManager.findPaths( \
    registration.talairachACPCReferentialId,
    self.normalized_referential.uuid() )
  for x in _mniToACPCpaths:
    _mniToACPC = x
    break
  else:
    raise RuntimeError( 'No transformation found between AC/PC and the ' \
      'normalized' )
  mniToACPC = aims.Motion()
  for mf in _mniToACPC:
    m = aims.read( mf.fullPath() )
    mniToACPC *= m
  mniToACPC = mniToACPC.inverse()
  t1toACPC = mniToACPC * t1toMni
  aims.write( t1toACPC, self.Talairach_transform.fullPath() )
  acpcReferential = trManager.referential(
    registration.talairachACPCReferentialId )
  if acpcReferential is None:
    context.warning( _t_( 'Talairach-AC/PC-Anatomist not found - maybe an ' \
      'installation problem ?' ) )
  else:
    trManager.setNewTransformationInfo(
      self.Talairach_transform,
      source_referential = self.source_referential,
      destination_referential = acpcReferential )
  if self.Commissure_coordinates:
    if not self.t1mri:
      context.warning( 't1mri parameter is not set. Cannot write ' \
        'Commissure_coordinates output' )
      return
    va = shfjGlobals.aimsVolumeAttributes( self.t1mri )
    vs = va.get( 'voxel_size', [ 1., 1., 1. ] )
    trinv = t1toACPC.inverse()
    acmm = trinv.transform( [ 0, 0, 0 ] )
    pcmm = trinv.transform( [ 0, 30, 0 ] )
    ipmm = trinv.transform( [ 0, 40, -60 ] )
    ac = [ int( round( x / y ) ) for x,y in zip( acmm, vs ) ]
    pc = [ int( round( x / y ) ) for x,y in zip( pcmm, vs ) ]
    ip = [ int( round( x / y ) ) for x,y in zip( ipmm, vs ) ]
    context.write( 'AC:', ac, ', mm:', list( acmm ) )
    context.write( 'PC:', pc, ', mm:', list( pcmm ) )
    context.write( 'IP:', ip, ', mm:', list( ipmm ) )
    apc = open( self.Commissure_coordinates.fullPath(), 'w' )
    print >> apc, 'AC:', ' '.join( [ str(x) for x in ac ] )
    print >> apc, 'PC:', ' '.join( [ str(x) for x in pc ] )
    print >> apc, 'IH:', ' '.join( [ str(x) for x in ip ] )
    print >> apc, 'The previous coordinates, used by the system, are ' \
      'defined in voxels'
    print >> apc, 'They stem from the following coordinates in millimeters:'
    print >> apc, 'ACmm:', ' '.join( [ str(x) for x in acmm ] )
    print >> apc, 'PCmm:', ' '.join( [ str(x) for x in pcmm ] )
    print >> apc, 'IHmm:', ' '.join( [ str(x) for x in ipmm ] )
    apc.close()

