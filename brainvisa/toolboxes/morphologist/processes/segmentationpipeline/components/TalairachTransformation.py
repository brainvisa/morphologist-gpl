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
name = 'Talairach Transformation'
userLevel = 2

signature = Signature(
  'split_mask', ReadDiskItem( "Voronoi Diagram",
      'Aims readable volume formats' ),
  'Commissure_coordinates', ReadDiskItem( 'Commissure coordinates',
                                          'Commissure coordinates'), 
  'Talairach_transform',
  WriteDiskItem( 'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
                 'Transformation matrix' ), 
)


def initialization( self ):
  self.linkParameters( 'Commissure_coordinates', 'split_mask' )
  self.linkParameters( 'Talairach_transform', 'split_mask' )

def execution( self, context ):
  tmp = context.temporary( 'GIS image' )
  context.system( 'AimsThreshold', '-i', self.split_mask, '-o', tmp,
                  '-m', 'be', '-t', '1', '-u', '2', '-b' )
  context.system( 'VipTalairachTransform', '-i',
                  self.Commissure_coordinates, '-o', 
                  self.Talairach_transform, '-m', tmp )
  trManager = registration.getTransformationManager()
  acpcReferential = trManager.referential( 
    registration.talairachACPCReferentialId )
  if acpcReferential is None:
    context.warning( _t_( 'Talairach-AC/PC-Anatomist not found - maybe an installation problem ?' ) )
  else:
    trManager.setNewTransformationInfo(
      self.Talairach_transform,
      source_referential = self.split_mask,
      destination_referential = acpcReferential )