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
import registration
from brainvisa import anatomist

name = 'Prepare Subject for Anatomical Pipeline'
userLevel = 0

signature = Signature(
  'T1mri', ReadDiskItem( "Raw T1 MRI", shfjGlobals.vipVolumeFormats ),  
  'Commissure_coordinates', WriteDiskItem( 'Commissure coordinates','Commissure coordinates'),
  'Normalised',Choice('No','MNI from SPM','MNI from Mritotal', 'Marseille from SPM'),
  'Anterior_Commissure', Point3D(), 
  'Posterior_Commissure', Point3D(), 
  'Interhemispheric_Point', Point3D(),
  'Left_Hemisphere_Point', Point3D(),
  'allow_flip_initial_MRI', Boolean(), 
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
  def linknorm( values, process ):
    if values.T1mri and values.T1mri.get( 'normalized' ) == 'yes':
      return 'MNI from SPM'
    return 'No'

  self.linkParameters( 'Commissure_coordinates', 'T1mri' )
  self.Normalised = 'No'
  self.setOptional( 'Anterior_Commissure' )
  self.setOptional( 'Posterior_Commissure' )
  self.setOptional( 'Interhemispheric_Point' )
  self.signature[ 'Anterior_Commissure' ].add3DLink( self, 'T1mri' )
  self.signature[ 'Posterior_Commissure' ].add3DLink( self, 'T1mri' )
  self.signature[ 'Interhemispheric_Point' ].add3DLink( self, 'T1mri' )
  self.signature[ 'Left_Hemisphere_Point' ].add3DLink( self, 'T1mri' )
  self.linkParameters( 'Anterior_Commissure',
                       'Commissure_coordinates', APCReader( 'AC' ) )
  self.linkParameters( 'Posterior_Commissure',
                       'Commissure_coordinates', APCReader( 'PC' ) )
  self.linkParameters( 'Interhemispheric_Point',
                       'Commissure_coordinates', APCReader( 'IH' ) )
  self.setOptional( 'Left_Hemisphere_Point' )
  self.allow_flip_initial_MRI = 0
  self.linkParameters( 'Normalised', 'T1mri', linknorm )

def execution( self, context ):
  ac = []
  pc = []
  ip = []
  lh = []
  acmm = self.Anterior_Commissure
  pcmm = self.Posterior_Commissure
  ipmm = self.Interhemispheric_Point
  if self.Normalised == 'No':
    atts = shfjGlobals.aimsVolumeAttributes( self.T1mri )
    vs = atts[ 'voxel_size' ]
    context.write( 'voxel size: ', vs )
    ac = self.Anterior_Commissure
    pc = self.Posterior_Commissure
    ip = self.Interhemispheric_Point
    lh = self.Left_Hemisphere_Point
    if not ac or len( ac ) != 3 or not pc or len( pc ) != 3 or not ip or \
      len(ip ) != 3:
      raise RuntimeError( _t_( 'In non-normalized mode, the 3 points AC, PC '
        'and IP are mandatory (in mm)' ) )

    # determine image orientation
    v1 = ( pc[0] - ac[0], pc[1] - ac[1], pc[2] - ac[2] )
    v2 = ( ip[0] - ac[0], ip[1] - ac[1], ip[2] - ac[2] )
    n = [ v1[1] * v2[2] - v1[2] * v2[1],
          v1[2] * v2[2] - v1[0] * v2[2],
          v1[0] * v2[1] - v1[1] * v2[0] ]
    dn = 1. / math.sqrt( n[0] * n[0] + n[1] * n[1] + n[2] * n[2] )
    n[0] *= dn
    n[1] *= dn
    n[2] *= dn
    # context.write( 'AC:', ac )
    # context.write( 'PC:', pc )
    # context.write( 'IP:', ip )
    # context.write( 'LH:', lh )
    # context.write( 'AC-IP vector:', v2 )
    v2 = [ n[1] * v1[2] - n[2] * v1[1],
           n[2] * v1[2] - n[0] * v1[2],
           n[0] * v1[1] - n[1] * v1[0] ]
    # context.write( 'AC-PC vector:', v1 )
    # context.write( 'corrected AC-IP vector:', v2 )
    context.write( 'IH plane normal:', n )

    flip = [ 1, 0, 0,  0, 1, 0,  0, 0, 1, 0, 0, 0 ]

    m = max( map( abs, n ) )
    a = max( map( abs, v1 ) )
    if m == abs( n[0] ) and a == abs( v1[1] ):
      context.write( _t_( 'image is axial' ) )
      if ac[1] > pc[1]:
        context.write( _t_( 'front/rear are inverted' ) )
        flip[4] = -1
      else: context.write( _t_( 'front is on the expected side' ) )
      if ac[2] < ip[2]:
        context.write( _t_( 'image is upside down' ) )
        flip[8] = -1
      else: context.write( 'upside on the top. OK' )
      if lh is not None and len( lh ) == 3 and lh != ( 0, 0, 0 ) \
             and lh[0] < ac[0]:
        context.write( 'image is in neurological mode' )
        flip[0] = -1
    elif m == abs( n[0] ) and a == abs( v1[2] ):
      context.write( _t_( 'image is coronal' ) )
      flip[4] = 0
      flip[5] = 1
      flip[7] = 1
      flip[8] = 0
      if ac[2] > pc[2]:
        context.write( _t_( 'z axis should be flipped' ) )
        flip[5] = -1
      if ip[1] > ac[1]:
        context.write( _t_( 'y axis should be flipped' ) )
        flip[7] = -1
      if lh is not None and len( lh ) == 3 and lh != ( 0, 0, 0 ) \
             and lh[0] < ac[0]:
        context.write( _t_( 'x axis should be flipped' ) )
        flip[0] = -1
    elif m == abs( n[2] ) and a == abs( v1[0] ):
      context.write( _t_( 'image is sagittal' ) )
      flip[0] = 0
      flip[2] = -1
      flip[3] = 1
      flip[4] = 0
      flip[7] = 1
      flip[8] = 0
      if ac[0] > pc[0]:
        context.write( _t_( 'x axis should be flipped' ) )
        flip[3] = -1
      if ip[1] > ac[1]:
        context.write( _t_( 'y axis should be flipped' ) )
        flip[7] = -1
      if lh is not None and len( lh ) == 3 and lh != ( 0, 0, 0 ) \
             and lh[2] > ac[2]:
        context.write( _t_( 'z axis should be flipped' ) )
        flip[2] = 1
    else:
      context.write( _t_( 'Unusual orientation, not taken into account ' \
                          'today' ) )

    id = max( map( lambda x,y: abs( x - y ),
                   flip[:9], ( 1, 0, 0,  0, 1, 0,  0, 0, 1 ) ) )
    if id > 1e-5 and not self.allow_flip_initial_MRI:
      context.write( '<b>Image needs to be flipped</b>, but you did not ' \
                     'allow it, so it won\'t change. Expect problems in ' \
                     'hemispheres separation, and sulci recognition will ' \
                     'not work anyway.' )
    if id > 1e-5 and self.allow_flip_initial_MRI:
      def matrixMult( m, p ):
        return [ m[0] * p[0] + m[1] * p[1] + m[2] * p[2] + m[9],
                 m[3] * p[0] + m[4] * p[1] + m[5] * p[2] + m[10],
                 m[6] * p[0] + m[7] * p[1] + m[8] * p[2] + m[11] ]

      vs2 = map( abs, matrixMult( flip, vs ) )
      dims = atts[ 'volume_dimension' ][:3]
      dims2 = ( dims[0] * vs[0], dims[1] * vs[1], dims[2] * vs[2] )
      dims3 = matrixMult( flip, dims2 )
      dims4 = map( lambda x,y: int( round( abs( x ) / y ) ), dims3, vs2 )

      flip[9] = -min( 0, dims3[0] )
      flip[10] = -min( 0, dims3[1] )
      flip[11] = -min( 0, dims3[2] )

      context.write( '<b><font color="#c00000">WARNING:</font> Flipping and ' \
                     're-writing source image</b>' )
      context.write( 'voxel size orig :', vs )
      context.write( 'voxel size final:', vs2 )
      context.write( 'dims orig :', dims )
      context.write( 'dims final:', dims4 )
      context.write( 'transformation:', flip )

      mfile = context.temporary( 'Transformation matrix' )
      mf = open( mfile.fullPath(), 'w' )
      mf.write( string.join( map( str, flip[9:12] ) ) + '\n' )
      mf.write( string.join( map( str, flip[:3] ) ) + '\n' )
      mf.write( string.join( map( str, flip[3:6] ) ) + '\n' )
      mf.write( string.join( map( str, flip[6:9] ) ) + '\n' )
      mf.close()
      context.log( 'Transformation',
                   html = 'transformation: R = ' + str( flip[:9] ) \
                   + ', T = ' + str( flip[9:] ) )

      context.system( 'AimsResample', '-i', self.T1mri.fullPath(),
                      '-o', self.T1mri.fullPath(), '-m', mfile.fullPath(),
                      '--sx', vs2[0], '--sy', vs2[1], '--sz', vs2[2],
                      '--dx', dims4[0], '--dy', dims4[1], '--dz', dims4[2] )

      acmm = matrixMult( flip, ac )
      pcmm = matrixMult( flip, pc )
      ipmm = matrixMult( flip, ip )
      context.write( 'new AC:', acmm )
      context.write( 'new PC:', pcmm )
      context.write( 'new IP:', ipmm )
      vs = vs2
      # reload image in Anatomist
      a = anatomist.Anatomist( create=False ) # test if anatomist is started
      if a:
        object=a.getObject(self.T1mri.fullPath())
        if object is not None:
          a.reloadObjects([object])

    ac = [ int( acmm[0] / vs[0] +0.5 ), int( acmm[1] / vs[1] +0.5),
           int( acmm[2] / vs[2] +0.5) ]
    pc = [ int( pcmm[0] / vs[0] +0.5 ), int( pcmm[1] / vs[1] +0.5),
           int( pcmm[2] / vs[2] +0.5) ]
    ip = [ int( ipmm[0] / vs[0] +0.5 ), int( ipmm[1] / vs[1] +0.5),
           int( ipmm[2] / vs[2] +0.5) ]

  # normalized case
  else:
    atts = shfjGlobals.aimsVolumeAttributes( self.T1mri )
    refs = atts.get( 'referentials' )
    trans = atts.get( 'transformations' )
    vs = atts[ 'voxel_size' ]
    autonorm = False
    if refs and trans:
      for i in range( len( refs ) ):
        if refs[i] == 'Talairach-MNI template-SPM':
          break
      if i >= len( refs ):
        i = 0
      tr = trans[0]
      try:
        import soma.aims as aims
        a2t = aims.Motion( tr )
        t2a = a2t.inverse()
        acmm = t2a.transform( [ 0, 0, 0 ] )
        ac = [ int( acmm[0] / vs[0] ), int( acmm[1] / vs[1] ),
               int( acmm[2] / vs[2] ) ]
        pcmm = t2a.transform( [ 0, -28, 0 ] )
        pc = [ int( pcmm[0] / vs[0] ), int( pcmm[1] / vs[1] ),
               int( pcmm[2] / vs[2] ) ]
        ipmm = t2a.transform( [ 0, -20, 60 ] )
        ip = [ int( ipmm[0] / vs[0] ), int( ipmm[1] / vs[1] ),
               int( ipmm[2] / vs[2] ) ]
        autonorm = True
      except Exception, e:
        context.warning( e )

    if not autonorm:
      if self.Normalised == 'MNI from SPM' :
        ac = [ 77, 73, 88 ]
        pc = [ 77, 100, 83 ]
        ip = [ 76, 60, 35 ]
        acmm = ac
        pcmm = pc
        ipmm = ip
        #self.T1mri.setMinf( 'referential',
                            #registration.talairachMNIReferentialId )
        #try:
          #self.T1mri.saveMinf()
        #except:
          #context.warning( 'could not set SPM/MNI normalized '
                          #'referential to', self.T1mri.fullName() )
      elif self.Normalised == 'MNI from Mritotal' :
        ac = [ 91, 88, 113 ]
        pc = [ 91, 115, 109 ]
        ip = [ 90, 109, 53 ]
        acmm = ac
        pcmm = pc
        ipmm = ip
      elif self.Normalised == 'Marseille from SPM' :
        ac = [ 91, 93, 108 ]
        pc = [ 91, 118, 106 ]
        ip = [ 91, 98, 68 ]
        acmm = ac
        pcmm = pc
        ipmm = ip

  f = open( self.Commissure_coordinates.fullPath(), 'w' )
  f.write( "AC: " + string.join( map( lambda x:str(x), ac ) ) + '\n' )
  f.write( "PC: " + string.join( map( lambda x:str(x), pc ) ) + '\n' )
  f.write( "IH: " + string.join( map( lambda x:str(x), ip ) ) + '\n' )
  f.write( "The previous coordinates, used by the system, are defined in " \
           "voxels\n" )
  f.write( "They stem from the following coordinates in millimeters:\n" )
  if self.Normalised == 'No':
    f.write( "ACmm: " + string.join( map( str, acmm ) ) + '\n' )
    f.write( "PCmm: " + string.join( map( str, pcmm ) ) + '\n' )
    f.write( "IHmm: " + string.join( map( str, ipmm ) ) + '\n' )
  else:
    f.write( "ACmm: " + string.join( map( str, ac ) ) + '\n' )
    f.write( "PCmm: " + string.join( map( str, pc ) ) + '\n' )
    f.write( "IHmm: " + string.join( map( str, ip ) ) + '\n' )
  f.close()

  # manage referential
  tm = registration.getTransformationManager()
  ref = tm.referential( self.T1mri )
  if ref is None:
    tm.createNewReferentialFor( self.T1mri )

