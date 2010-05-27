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

name = 'Import Brain Mask'
roles = ('importer',)
userLevel = 0

def validation():
  try:
    from soma import aims
  except:
    raise ValidationError( 'aims module not available' )
  try:
    import numpy
  except:
    raise ValidationError( 'numpy module not available' )

signature=Signature(
  'input', ReadDiskItem( 'Raw T1 MRI', 'Aims readable volume formats' ),
  'output', WriteDiskItem( 'T1 Brain Mask', 'Aims writable volume formats', exactType=1),
  'copy_referential_of', ReadDiskItem( 'Raw T1 MRI',
    'Aims readable volume formats' ),
  'background_value', OpenChoice( 'minimum value' ),
  #'input_spm_orientation', Choice( 'Not applicable' ),
)

def initialization( self ):
  self.linkParameters( 'copy_referential_of', 'output' )
  self.signature[ 'output' ].browseUserLevel = 3
  self.signature[ 'input' ].databaseUserLevel = 2

def execution( self, context ):
  # WARNING: runs in BrainVisa memory space...
  from soma import aims
  import numpy
  vol = aims.read( self.input.fullPath() )
  if self.background_value == 'minimum value':
    bg = numpy.array( vol, copy=False ).min()
    context.write( 'background:', bg )
  else:
    bg = int( self.background_value )
  if vol.header()[ 'data_type' ] != 'S16':
    vol2 = aims.Volume_S16( vol.getSizeX(), vol.getSizeY(), vol.getSizeZ() )
    vol2.header().update( vol.header() )
    arr2 = numpy.array( vol2, copy=False )
  else:
    vol2 = vol
    arr2 = numpy.array( vol, copy=False )
  arr = numpy.array( vol, copy=False )
  # set all values except background to 255
  arr2[ arr != bg ] = 255
  # set background to zero
  arr2[ arr == bg ] = 0
  aims.write( vol2, self.output.fullPath() )
  if self.copy_referential_of:
    tm=registration.getTransformationManager()
    tm.copyReferential( self.copy_referential_of, self.output )

