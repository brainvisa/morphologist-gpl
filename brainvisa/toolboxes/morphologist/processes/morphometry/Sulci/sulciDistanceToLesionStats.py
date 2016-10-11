# -*- coding: iso-8859-1 -*-

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

# Cette procedure est a ameliorer, par exemple siGraph2Label n'est peut-etre
#�plus a jour, et il faudrait utiliser label ou name...
# je m'en suis servi pour les experiences sur les invariants et la colab avec
# Pascal Cathier

from __future__ import print_function
from brainvisa.processes import *
from brainvisa.data.labelSelection import LabelSelection
import registration

name = 'Sulci Distance to Lesion Stats'
userLevel = 2

signature = Signature(
  'lgrey_white', ListOf( ReadDiskItem( 'Left Grey White Mask',
    'Aims readable volume formats' ) ),
  'rgrey_white', ListOf( ReadDiskItem( 'Right Grey White Mask',
    'Aims readable volume formats' ) ),
  'lesion_mask', ListOf( ReadDiskItem( 'Lesion Mask',
    'Aims readable volume formats' ) ),
  'distance_map', ListOf( WriteDiskItem( 'Lesion distance map',
    'Aims readable volume formats' ) ),
  'lgraph', ListOf( ReadDiskItem( 'Labelled Cortical Folds Graph',
    'Graph and data', requiredAttributes={ 'side' : 'left' } ) ),
  'rgraph', ListOf( ReadDiskItem( 'Labelled Cortical Folds Graph',
    'Graph and data', requiredAttributes={ 'side' : 'right' } ) ),
  'output_csv', WriteDiskItem( 'CSV file', 'CSV file' ),
  'nomenclature', ReadDiskItem( 'Nomenclature', 'Hierarchy' ),
  'model', ReadDiskItem( 'Model graph', 'Graph' ),
  'region_selection', LabelSelection(),
  'label_attribute', Choice( 'auto', 'label', 'name' ),
  'reuse_existing_distancemap', Boolean(),
  'lesions_sizes', WriteDiskItem( 'CSV file', 'CSV file' ),
)


def initialization( self ):
  def change_region( self, proc ):
    if self.model:
      mod = self.model.fullPath()
    else:
      mod = None
    if self.nomenclature:
      nom = self.nomenclature.fullPath()
    else:
      nom = None
    sel = self.region_selection
    if sel is None:
      sel = LabelSelection( mod, nom )
    else:
      sel.value[ 'model' ] = mod
      sel.value[ 'nomenclature' ] = nom
    return sel

  def linkModel( self, proc ):
    if len( self.lgraph ) != 0 and len( self.rgraph ) == 0:
      return self.signature[ 'model' ].findValue( self.lgraph[0] )
    elif len( self.lgraph ) == 0 and len( self.rgraph ) != 0:
      return self.signature[ 'model' ].findValue( self.rgraph[0] )
    return None

  self.nomenclature = self.signature[ 'nomenclature' ].findValue( {} )
  self.setOptional( 'model', 'nomenclature', 'region_selection',
    'distance_map', 'lgraph', 'rgraph', 'lesions_sizes', 'lgrey_white',
    'rgrey_white' )
  self.linkParameters( 'rgrey_white', 'lgrey_white' )
  self.linkParameters( 'lgraph', 'lgrey_white' )
  self.linkParameters( 'rgraph', 'lgraph' )
  self.linkParameters( 'lesion_mask', 'lgrey_white' )
  self.linkParameters( 'model', ( 'lgraph', 'rgraph' ), linkModel )
  self.linkParameters( 'region_selection', ( 'model', 'nomenclature' ),
    change_region )
  self.linkParameters( 'distance_map', 'lesion_mask' )
  self.reuse_existing_distancemap = False


def execution( self, context ):
  dolesionsize = False
  if self.lesions_sizes is not None:
    if not self.lesion_mask:
      raise RuntimeError( _t_( 'lesion_mask should be specified to get ' \
        'lesions_sizes' ) )
    try:
      from soma import aims
      import numpy
      dolesionsize = True
    except:
      context.warning( _t_( 'PyAims could not be loaded - lesion sizes will ' \
        'not be calculated.' ) )
  subjects = {}
  for i, s in enumerate( self.lgrey_white ):
    subject = s.get( 'subject', i )
    sdat = subjects.get( subject, subjects.get( i, None ) )
    if sdat is None:
      sdat = { 'lgrey_white' : None, 'rgrey_white' : None,
        'lesion_mask' : None, 'lgraph' : None, 'rgraph' : None,
        'distance_map' : None }
      subjects[ subject ] = sdat
    sdat[ 'lgrey_white' ] = s
  for i, s in enumerate( self.rgrey_white ):
    subject = s.get( 'subject', i )
    sdat = subjects.get( subject, subjects.get( i, None ) )
    if sdat is None:
      raise RuntimeError( 'missing lgrey_white for subject ' + subject )
    sdat[ 'rgrey_white' ] = s
  for i, s in enumerate( self.lesion_mask ):
    subject = s.get( 'subject', i )
    sdat = subjects.get( subject, subjects.get( i, None ) )
    if sdat is None:
      raise RuntimeError( 'missing l/rgrey_white for subject ' + subject )
    sdat[ 'lesion_mask' ] = s
  for i, s in enumerate( self.distance_map ):
    subject = s.get( 'subject', i )
    sdat = subjects.get( subject, subjects.get( i, None ) )
    if sdat is None:
      if not s.isReadable():
        raise RuntimeError( 'missing l/rgrey_white for subject ' + subject )
      else:
        sdat = { 'lgrey_white' : None, 'rgrey_white' : None,
          'lesion_mask' : None, 'lgraph' : None, 'rgraph' : None,
          'distance_map' : None }
        subjects[ subject ] = sdat
    sdat[ 'distance_map' ] = s
  for i, s in enumerate( self.lgraph ):
    subject = s.get( 'subject', i )
    sdat = subjects.get( subject, subjects.get( i, None ) )
    if sdat is None:
      raise RuntimeError( 'missing l/rgrey_white for subject ' + subject )
    sdat[ 'lgraph' ] = s
  for i, s in enumerate( self.rgraph ):
    subject = s.get( 'subject', i )
    sdat = subjects.get( subject, subjects.get( i, None ) )
    if sdat is None:
      raise RuntimeError( 'missing l/rgrey_white for subject ' + subject )
    sdat[ 'rgraph' ] = s
  tmpcsv = context.temporary( 'CSV file' )
  open( self.output_csv.fullPath(), 'w' )
  first = True
  ns = len( subjects )
  n = 0
  ks = subjects.keys()
  ks.sort()
  if dolesionsize:
    of = open( self.lesions_sizes.fullPath(), 'w' )
    print('subject\tlesion_size', file=of)
    del of
  for s in ks:
    sdat = subjects[ s ]
    context.progress( n, ns, process=self )
    if not sdat['lesion_mask'] and not sdat[ 'distance_map' ]:
      context.warning( 'skipping subject', s,
        'because it lacks the lesion_mask' )
    else:
      context.write( 'processing subject', n+1, '/', ns, ':', s, '...' )
      context.runProcess( 'sulciDistanceToLesionBV',
        lgrey_white=sdat['lgrey_white'],
        rgrey_white=sdat['rgrey_white'],
        lgraph=sdat['lgraph'], rgraph=sdat['rgraph'],
        lesion_mask=sdat['lesion_mask'], output_csv=tmpcsv,
        distance_map=sdat['distance_map'], nomenclature=self.nomenclature,
        model=self.model, region_selection=self.region_selection,
        label_attribute=self.label_attribute,
        reuse_existing_distancemap=self.reuse_existing_distancemap )
      of = open( self.output_csv.fullPath(), 'a' )
      f = open( tmpcsv.fullPath() )
      if first:
        first = False
      else:
        l = f.readline() # skip header line
        l[:-1] # force using iterator
      rem = f.read()
      of.write( rem )
      of.close()
      f.close()
      # lesion volume
      if dolesionsize:
        vol = aims.read( sdat[ 'lesion_mask' ].fullPath() )
        varr = numpy.array( vol, copy=False )
        nvox = len( numpy.where( varr != 0 )[0] )
        vs = vol.header()[ 'voxel_size' ]
        lvol = nvox * vs[0] * vs[1] * vs[2]
        of = open( self.lesions_sizes.fullPath(), 'a' )
        print(s, lvol, file=of)
        del of
    n += 1

  context.progress( ns, ns, process=self )

