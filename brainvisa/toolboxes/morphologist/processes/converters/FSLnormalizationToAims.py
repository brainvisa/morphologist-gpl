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
import sys

if sys.version_info[0] >= 3:
  basestring = str

name = 'FSL Normalization to AIMS converter'
userLevel=0

def validation():
  try:
    from soma import aims
  except:
    raise ValidationError( 'aims module not here' )

signature = Signature(
  'read', ReadDiskItem( 'FSL Transformation', 'Matlab file',
                        enableConversion = 0 ),
  'source_volume', ReadDiskItem( '4D Volume',
                                 'aims readable Volume Formats' ),
  'write', WriteDiskItem( 'Transform Raw T1 MRI to Talairach-MNI template-SPM', 'Transformation matrix' ),
  'registered_volume', ReadDiskItem( '4D Volume',
    'aims readable Volume Formats',
    requiredAttributes={ 'normalized' : 'yes' } ),
  'standard_template', Choice( ( 'FSL 182x218x218, 1x1x1 mm', 0 ),
    ( 'FSL 91x109x91, 2x2x2 mm', 1 ),
    ( 'SPM 158x..., 1x1x1 mm', 2 ), ),
  'set_transformation_in_source_volume', Boolean(),
  # 'removeSource', Boolean(),
)

def initialization( self ):
  def linkStdTemplate( self, proc ):
    if self.registered_volume is None:
      x = Choice( \
        ( 'FSL 182x218x218, 1x1x1 mm', 0 ),
        ( 'FSL 91x109x91, 2x2x2 mm', 1 ),
        ( 'SPM 157x189x136, 1x1x1 mm', 2 ), )
      self.signature[ 'standard_template' ] = x
      res = 'FSL 182x218x218, 1x1x1 mm'
    else:
      x = Choice( ( 'taken from registered_volume', 0 ) )
      self.signature[ 'standard_template' ] = x
      res = 'taken from registered_volume'
    self.changeSignature( self.signature )
    return res
  def linkSetTransfo( self, proc ):
    if self.source_volume is not None and self.source_volume.isWriteable():
      return True
    else:
      return False
  self.linkParameters( 'source_volume', 'read' )
  self.linkParameters( 'write', 'source_volume' )
  self.linkParameters( 'registered_volume', 'read' )
  self.setOptional( 'registered_volume' )
  self.linkParameters( 'standard_template', 'registered_volume',
    linkStdTemplate )
  self.linkParameters( 'set_transformation_in_source_volume', 'source_volume',
    linkSetTransfo )
  #self.removeSource = 0

def execution( self, context ):
  from soma import aims
  from soma.aims import fslTransformation
  if self.registered_volume is None:
    if self.standard_template == 1:
      tmplimg = { 'voxel_size' : [ 2, 2, 2 ],
        'volume_dimension' : [ 91, 109, 91 ] }
    elif self.standard_template == 2:
      tmplimg = { 'voxel_size' : [ 1, 1, 1 ],
      'volume_dimension' : [ 157, 189, 136 ] }
    else:
      tmplimg = { 'voxel_size' : [ 1, 1, 1 ],
        'volume_dimension' : [ 182, 218, 182 ] }
  else:
    tmplimg = self.registered_volume.fullPath()
  # get aims -> aims matrix from read to template
  trm = fslTransformation.fslMatToTrm( self.read.fullPath(),
    self.source_volume.fullPath(), tmplimg )

  tm = registration.getTransformationManager()

  # now go to the MNI template coords (or another standard ref)
  # 1. first try o get direct transformation info in the template image header
  aimsToMni = None
  outref = None
  if isinstance( tmplimg, basestring ):
    tmplimg = neuroDiskItems.aimsFileInfo( self.registered_volume.fullPath() )
    refs = tmplimg.get( 'referentials' )
    trans = tmplimg.get( 'transformations' )
    if refs and trans:
      for ref, t in zip(refs, trans):
        if ref == str( registration.talairachMNIReferentialId ) \
          or ref == 'Talairach-MNI template-SPM':
          aimsToMni = aims.Motion( t )
          outref = registration.talairachMNIReferentialId
          break
        elif ref == str( registration.talairachACPCReferentialId ) \
          or ref == 'Talairach-AC/PC-Anatomist':
          aimsToMni = aims.Motion( t )
          outref = registration.talairachACPCReferentialId
          break

  # 2. otherwise, get a had-hoc [pre]calculation
  if aimsToMni is None:
    rp = list( tm.findPaths( \
      'f3848046-b581-cae4-ecb9-d80ada0278d5',
      registration.talairachMNIReferentialId ) )
    if len( rp ) != 1 or len( rp[0] ) != 1:
      raise RuntimeError( 'Could not find standard transformation for MNI ' \
        'template' )
      return
    spmAimsToMni = aims.read( rp[0][0].fullPath() )
    # now correct for the template size
    vs = tmplimg.get( 'voxel_size' )
    dim = tmplimg.get( 'volume_dimension' )
    d = [ (float(x)*y-z)/2. for x,y,z in zip( dim[:3], vs[:3], [157,189,136] ) ]
    trl = aims.Motion()
    trl.translation()[0] = d[0]
    trl.translation()[1] = d[1]
    trl.translation()[2] = d[2]
    aimsToMni = trl * spmAimsToMni
    outref = registration.talairachMNIReferentialId

  trm = aimsToMni * trm
  aims.write( trm, self.write.fullPath() )
  tm.setNewTransformationInfo( self.write,
    tm.referential( self.source_volume ), outref )

  if self.set_transformation_in_source_volume:
    if self.source_volume.isWriteable():
      context.write( 'source is writeable: setting its header information' )
      self.source_volume.readAndUpdateMinf()
      refs = self.source_volume.get( 'referentials' )
      trans = self.source_volume.get( 'transformations' )
      if outref == registration.talairachMNIReferentialId:
        stroutref = 'Talairach-MNI template-SPM'
      elif outref == registration.talairachACPCReferentialId:
        stroutref = 'Talairach-AC/PC-Anatomist'
      else:
        raise RuntimeError( 'output referential is unknown: ' + str(outref) )
      vectrm = list( trm.toVector() )
      if refs and trans:
        hasit = False
        i = 0
        for ref, t in zip(refs, trans):
          if ref in ( str(outref), stroutref ):
            if t != vectrm:
              context.warning( 'overriding existing normalization information!' )
              context.write( 'older one: ' + str( t ) )
              context.write( 'new one  : ' + str( vectrm ) )
            trans[i] = vectrm
            hasit = True
            break
          i += 1
        if not hasit:
          refs.append( stroutref )
          trans.append( vectrm )
      else: # no existing refs/trans
        refs = [ stroutref ]
        trans = [ vectrm ]
      self.source_volume.setMinf( 'referentials', refs )
      self.source_volume.setMinf( 'transformations', trans )
      self.source_volume.saveMinf()
      # forece re-writing image with full native header
      context.system( 'AimsFileConvert', '-i', self.source_volume, '-o',
        self.source_volume )
    else: # not writeable
      context.warning( 'source_volume is not writeable: transformation information will not be set into its header.' )
  # if self.removeSource: TODO

