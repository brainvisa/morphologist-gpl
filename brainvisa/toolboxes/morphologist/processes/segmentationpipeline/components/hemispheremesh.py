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
userLevel = 0

# Argument declaration
signature = Signature(
    'hemi_cortex', ReadDiskItem( 'CSF+GREY Mask',
        'Aims readable volume formats' ),
    'grey_white', ReadDiskItem( 'Grey White Mask',
        'Aims readable volume formats' ),
    't1mri_nobias', ReadDiskItem( 'T1 MRI Bias Corrected',
        'Aims readable volume formats' ),
    'skeleton', ReadDiskItem( 'Cortex Skeleton',
        'Aims readable volume formats' ),
    'pial_mesh', WriteDiskItem( 'Hemisphere Mesh', 'Aims mesh formats' ),
    'fix_random_seed', Boolean(),
)

# Default values
def initialization( self ):
    self.linkParameters( 'grey_white', 'hemi_cortex' )
    self.linkParameters( 't1mri_nobias', 'hemi_cortex' )
    self.linkParameters( 'skeleton', 'hemi_cortex' )
    self.linkParameters( 'pial_mesh', 'hemi_cortex' )
    self.signature['fix_random_seed'].userLevel = 3
    self.fix_random_seed = False


def execution( self, context ):
    trManager = registration.getTransformationManager()
    
    braing = context.temporary( 'NIFTI-1 Image' )
    context.system( "VipMask", "-i", self.t1mri_nobias,
                    "-m", self.grey_white, "-o", braing,
                    "-w", "t" )
    
    context.write( "Detecting spherical outer cortical surface..." )
    hemi = context.temporary( 'NIFTI-1 Image' )
    command = [ "VipHomotopic", "-i", braing,
                "-s", self.skeleton,
                "-co", self.hemi_cortex,
                "-o", hemi,
                "-m", "H", "-w", "t" ]
    if self.fix_random_seed:
        command.extend(['-srand', 10])
    context.system( *command )
    
    context.write("Reconstructing hemisphere pial mesh...")
    context.system( "VipSingleThreshold", "-i", hemi,
                    "-o", hemi, "-t", "0", "-c", "b",
                    "-m", "ne", "-w", "t" )
    
    context.system( "AimsMeshBrain", "-i", hemi.fullPath(), "-o", self.pial_mesh,
                    "--internalinterface", "--smoothIt", 50 )
    context.system( "meshCleaner", "-i", self.pial_mesh, "-o",
                    self.pial_mesh, "-maxCurv", "0.5" )
    
    trManager.copyReferential( self.hemi_cortex, self.pial_mesh )
    
    del braing
    del hemi

