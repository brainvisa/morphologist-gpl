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
from brainvisa import anatomist
from brainvisa import registration
from soma import aims
import numpy
from brainvisa.data.neuroHierarchy import databases

name = 'Anatomist Show Symmetrized data'
#roles = ('viewer',)
userLevel = 2

def validation():
    anatomist.validation()

signature = Signature(
 'data_type', Choice( 'Any Type' ),
 'items', ListOf( ReadDiskItem( 'Any Type', getAllFormats() ) ),
)


def dataTypeChanged(self, dataType):
  if dataType:
    formats=list(databases.getTypesFormats(dataType))
    if not formats:
      formats=getAllFormats()
    self.signature['items'] = ListOf( ReadDiskItem( dataType, formats ) )
    self.signatureChangeNotifier.notify(self)


def initialization( self ):
  possibleTypes = [ t.name for t in getAllDiskItemTypes() ]
  self.signature[ 'data_type' ].setChoices(*sorted(possibleTypes))
  self.data_type='Any Type'
  self.addLink( 'items', 'data_type' , self.dataTypeChanged )


def execution( self, context ):
  a = anatomist.Anatomist()
  alive = []
  objs = []
  reftable = {}
  tm = registration.getTransformationManager()
  acpc = tm.referential( registration.talairachACPCReferentialId )
  mni = tm.referential( registration.talairachMNIReferentialId )
  for data in self.items:
    ad = a.loadObject( data, forceReload=True )
    alive.append( ad )
    ref = tm.referential( data )
    if ref is None:
      context.write( 'Warning: no referential on data %s, assuming ACPC ref.' \
        % data.fullPath() )
      ref = acpc
    oref = reftable.get( ref )
    if oref:
      ad.assignReferential( oref )
      continue
    pr = aims.AffineTransformation3d()
    pth = tm.findPaths( ref.uuid(), acpc.uuid() )
    dest = a.centralRef
    for pt in pth:
      break
    else:
      pth = tm.findPaths( ref.uuid(), mni.uuid() )
      for pt in pth:
        dest = a.mniTemplateRef
        break
      else:
        context.write( 'no path.' )
        pt = []
    for p in pt:
      pr2 = aims.read( p.fullPath() )
      pr = pr2 * pr
    if dest == a.mniTemplateRef:
      pth = tm.findPaths( acpc.uuid(), mni.uuid() )
      for pt in pth:
        break
      for p in pt:
        pr2 = aims.read( p.fullPath() )
        pr = pr2.inverse() * pr
      dest = a.centralRef
    inv = aims.Motion( [ -1, 0, 0, 0,  0, 1, 0, 0,  0, 0, 1, 0,  0, 0, 0, 1 ] )
    pr = inv * pr
    trans = list( pr.translation() ) + list( numpy.array( \
      pr.rotation().volume(), copy=False ).ravel() )
    trans = [ float( x ) for x in trans ]
    oref = a.createReferential()
    newid = a.newId()
    a.execute( 'LoadTransformation', origin=oref, destination=dest,
      matrix=trans, res_pointer=newid )
    ad.setMaterial( front_face="counterclockwise" )
    reftable[ ref ] = oref
    ad.assignReferential( oref )
  if len( alive ) != 0:
    w = a.createWindow( '3D' )
    w.addObjects( alive )
    alive.append( w )
  return alive

