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
from soma import aims
import registration

name = 'Grey White Classification 2012, one hemisphere'
userLevel = 0

# Argument declaration
signature = Signature(
    'side', Choice( "left", "right" ),
    'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
        'Aims readable volume formats' ),
    'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
    'split_mask', ReadDiskItem( 'Split Brain Mask',
        'Aims readable volume formats' ),
    'edges', ReadDiskItem( 'T1 MRI Edges',
        'Aims readable volume formats' ),
    'commissure_coordinates', ReadDiskItem( 'Commissure coordinates',
        'Commissure coordinates'),
    'grey_white', WriteDiskItem( 'Morphologist Grey White Mask',
        'Aims writable volume formats' ),
)
# Default values
def initialization( self ):
    def linkGW( self, dummy ):
        if self.mri_corrected is not None:
            return self.signature[ 'grey_white' ].findValue( self.mri_corrected, requiredAttributes={ 'side': self.side } )
    self.linkParameters( 'histo_analysis', 'mri_corrected' )
    self.linkParameters( 'grey_white', ( 'mri_corrected', 'side' ), linkGW )
    self.linkParameters( 'split_mask', 'mri_corrected' )
    self.linkParameters( 'edges', 'mri_corrected' )
    self.linkParameters( 'commissure_coordinates', 'mri_corrected' )


def execution( self, context ):
    tm=registration.getTransformationManager()

    context.write( "Computing hemisphere grey-white classification..." )
    if self.side == 'left':
        sideval = 2
    else:
        sideval = 1
    context.system( "VipGreyWhiteClassif", "-i",
                    self.mri_corrected, "-h",
                    self.histo_analysis, "-m",
                    self.split_mask, "-edges",
                    self.edges, "-P",
                    self.commissure_coordinates, "-o",
                    self.grey_white, "-l", sideval,
                    "-w", "t", "-a", "N" )
    tm.copyReferential(self.mri_corrected, self.grey_white)

