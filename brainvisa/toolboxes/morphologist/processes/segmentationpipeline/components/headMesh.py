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
import shfjGlobals
import registration

name = 'Head Mesh'
userLevel = 0

# Argument declaration
signature = Signature(
    't1mri_nobias', ReadDiskItem( 'T1 MRI Bias Corrected',
        'Aims readable volume formats' ),
    'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
    'head_mesh', WriteDiskItem( 'Head Mesh', 'Aims mesh formats' ),
    'head_mask', WriteDiskItem( 'Head Mask',
        'Aims writable volume formats' ),
    'keep_head_mask', Boolean(),
    'remove_mask', ReadDiskItem( '3D Volume', 'Aims readable volume formats' ),
    'first_slice', Integer(),
    'threshold', Integer(),
    'closing', Float(),
)

# Default values
def initialization( self ):
    def linkMask( self, proc ):
        p = self.signature[ 'head_mask' ]
        if not self.histo_analysis:
            if self.t1mri_nobias:
                return p.findValue( self.t1mri_nobias )
            return None
        reqatt = {}
        if self.t1mri_nobias:
            format = self.t1mri_nobias.format
            if format:
                reqatt[ '_format' ] = set( [ format.name ] )
        if reqatt:
            x = p.findValue( self.histo_analysis, requiredAttributes=reqatt )
        else:
            x = p.findValue( self.histo_analysis )
        return x

    self.linkParameters( 'head_mask', ( 'histo_analysis', 't1mri_nobias' ),
        linkMask )
    self.linkParameters( 'head_mesh', 'head_mask' )
    self.linkParameters( 'histo_analysis', 't1mri_nobias' )
    self.setOptional('first_slice')
    self.setOptional('threshold')
    self.setOptional('closing')
    self.setOptional('head_mask')
    self.setOptional('histo_analysis')
    self.setOptional('remove_mask')
    self.first_slice = None
    self.threshold = None
    self.closing = None
    self.keep_head_mask = 0

def execution( self, context ):
    tm = registration.getTransformationManager()
    
    if self.head_mask is not None and self.keep_head_mask:
        mask = self.head_mask
    else:
        mask = context.temporary( 'NIFTI-1 image' )
    
    command = [ 'VipGetHead',
                '-i', self.t1mri_nobias,
                '-o', mask,
                '-w', 't', '-r', 't' ]
    if self.remove_mask is not None:
        command.extend(['-h', self.remove_mask])
    if self.histo_analysis is not None:
        command.extend(['-hn',self.histo_analysis])
    if self.first_slice is not None:
        command.extend(['-n', self.first_slice])
    if self.threshold is not None:
        command.extend(['-t', self.threshold])
    if self.closing is not None:
        command.extend([ '-c', self.closing])
    
    context.system( *command )
    context.system( 'AimsMeshBrain', '-i', mask,
                    '-o', self.head_mesh, '--smoothIt', 50,
                    '--smoothRate', 0.5, '--deciMaxClearance', 5. )
    context.system( "meshCleaner",
                    "-i", self.head_mesh,
                    "-o", self.head_mesh,
                    "-maxCurv", "0.5" )

    tm.copyReferential( self.t1mri_nobias, self.head_mesh )
    if self.keep_head_mask:
        tm.copyReferential( self.t1mri_nobias, self.head_mask )
