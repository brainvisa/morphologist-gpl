# -*- coding: utf-8 -*-
# This software and supporting documentation are distributed by
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
import registration

name = 'Hemisphere Pial Mesh'
userLevel = 2

# Argument declaration
signature = Signature(
    'hemi_cortex', ReadDiskItem( 'CSF+GREY Mask',
        'Aims writable volume formats' ),
    'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
        'Aims readable volume formats' ),
    'split_mask', ReadDiskItem( 'Split Brain Mask',
        'Aims readable volume formats' ),
    'hemi_mesh', WriteDiskItem( 'Hemisphere Mesh', 'Aims mesh formats' ),
    'side', Choice( 'left', 'right' ),
)

# Default values
def initialization( self ):
    def linkSide( self, proc ):
        if self.hemi_cortex is not None:
            side = self.hemi_cortex.get( 'side' )
            if side is not None:
                return side
        return self.side
    self.linkParameters( 'split_mask', 'mri_corrected' )
    self.linkParameters( 'mri_corrected', 'hemi_cortex' )
    self.linkParameters( 'hemi_mesh', 'hemi_cortex' )
    self.linkParameters( 'side', 'hemi_cortex', linkSide )
    self.signature[ 'side' ].userLevel = 3


def execution( self, context ):
    trManager = registration.getTransformationManager()

    if self.side == 'left':
        sideval = 2
    else:
        sideval = 1
    context.write( "Masking Bias corrected image with hemisphere mask...")
    braing = context.temporary( 'GIS Image' )
    context.system( "VipMask", "-i", self.mri_corrected, "-m", self.split_mask, "-o", braing, "-w", "t", "-l", sideval )

    context.write("Computing skeleton...")
    skeleton = context.temporary( 'GIS Image' )
    roots = context.temporary( 'GIS Image' )
    context.system( "VipSkeleton", "-i", self.hemi_cortex, "-so", skeleton, "-vo", roots, "-g", braing, "-w", "t" )

    context.write("Reconstructing hemisphere surface...")
    hemi = context.temporary( 'GIS Image' )
    context.system( "VipHomotopic", "-i", braing, "-s", skeleton, "-co", self.hemi_cortex, "-o", hemi, "-m", "H", "-w", "t" )

    context.system( "VipSingleThreshold", "-i", hemi, "-o", hemi, "-t", "0", "-c", "b", "-m", "ne", "-w", "t" )

    context.system( "AimsMeshBrain", "-i", hemi.fullPath(), "-o", self.hemi_mesh, '--internalinterface' )
    context.system( "meshCleaner", "-i", self.hemi_mesh, "-o", self.hemi_mesh, "-maxCurv", "0.5" )

    trManager.copyReferential( self.mri_corrected, self.hemi_mesh )
