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

from neuroProcesses import *
from soma import aims
import registration

name = 'Grey White Surface 2012'
userLevel = 0

# Argument declaration
signature = Signature(
    'Side', Choice("Both","Left","Right"),
    'left_grey_white', ReadDiskItem( 'Left Grey White Mask',
        'Aims writable volume formats' ),
    'right_grey_white', ReadDiskItem( 'Right Grey White Mask',
        'Aims writable volume formats' ),
    'left_hemi_cortex', WriteDiskItem( 'Left CSF+GREY Mask',
        'Aims writable volume formats' ),
    'right_hemi_cortex', WriteDiskItem( 'Right CSF+GREY Mask',
        'Aims writable volume formats' ),
    'left_white_mesh', WriteDiskItem( 'Left Hemisphere White Mesh',
                                        'Aims mesh formats' ),
    'right_white_mesh', WriteDiskItem( 'Right Hemisphere White Mesh',
                                        'Aims mesh formats' ),
) 
# Default values
def initialization( self ):
    self.linkParameters( 'right_grey_white', 'left_grey_white' )
    self.linkParameters( 'left_hemi_cortex', 'left_grey_white' )
    self.linkParameters( 'right_hemi_cortex', 'right_grey_white' )
    self.linkParameters( 'left_white_mesh', 'left_grey_white' )
    self.linkParameters( 'right_white_mesh', 'right_grey_white' )
    self.Side = "Both"
#
#

def execution( self, context ):
    tm=registration.getTransformationManager()
    if self.Side in ('Left','Both'):
        
        if os.path.exists(self.left_hemi_cortex.fullName() + '.loc'):
            context.write( "Left cortex locked")
        else:
            context.write( "Detecting left spherical cortex interface..." )
            context.system( "VipHomotopic", "-i",
                            self.left_grey_white, "-o",
                            self.left_hemi_cortex,
                            "-m", "C", "-w", "t" )
            tm.copyReferential(self.left_grey_white, self.left_hemi_cortex)
    
        if os.path.exists(self.left_white_mesh.fullName() + '.loc'):
            context.write( "Left Hemisphere White Mesh Locked")
        else:
            context.write("Reconstructing left hemisphere white surface...")
            white = context.temporary( 'GIS Image' )
            white_mesh = context.temporary( 'MESH mesh' )
            context.system( "VipSingleThreshold", "-i", self.left_hemi_cortex,
                    "-o", white, "-t", "0", "-c", "b", "-m",
                    "ne", "-w", "t" )
            context.system( "AimsMesh", "-i", white, "-o",
                    white_mesh )
            
            white_mesh_ext_name = white_mesh.fullPath()[:-5] + '_255_1.mesh'
            white_mesh_ext = aims.read(white_mesh_ext_name)
            poly = white_mesh_ext.polygon()
            poly.assign( [ aims.AimsVector_U32_3( [ x[2], x[1], x[0] ] ) for x in poly ] )
            normal = white_mesh_ext.normal()
            normal.assign( [ -x for x in normal ] )
            aims.write( white_mesh_ext, self.left_white_mesh.fullPath() )
            
            context.write( "Smoothing mesh..." )
            for i in range(3):
                context.runProcess( 'meshSmooth', mesh=self.left_white_mesh,
                                    iterations=10,rate=0.2 )
            
            tm.copyReferential(self.left_grey_white, self.left_white_mesh)
            
            del white
            del white_mesh
        
    if self.Side in ('Right','Both'):
        
        if os.path.exists(self.right_hemi_cortex.fullName() + '.loc'):
            context.write( "Right cortex locked")
        else:
            context.write( "Detecting right spherical cortex interface..." )
            context.system( "VipHomotopic", "-i",
                            self.right_grey_white, "-o",
                            self.right_hemi_cortex,
                            "-m", "C", "-w", "t" )
            tm.copyReferential(self.right_grey_white, self.right_hemi_cortex)
        
        if os.path.exists(self.right_white_mesh.fullName() + '.loc'):
            context.write( "Right Hemisphere White Mesh Locked")
        else:
            context.write("Reconstructing right hemisphere white surface...")
            white = context.temporary( 'GIS Image' )
            white_mesh = context.temporary( 'MESH mesh' )
            context.system( "VipSingleThreshold", "-i", self.right_hemi_cortex,
                    "-o", white, "-t", "0", "-c", "b", "-m",
                    "ne", "-w", "t" )
            context.system( "AimsMesh", "-i", white, "-o",
                    white_mesh )
            
            white_mesh_ext_name = white_mesh.fullPath()[:-5] + '_255_1.mesh'
            white_mesh_ext = aims.read(white_mesh_ext_name)
            poly = white_mesh_ext.polygon()
            poly.assign( [ aims.AimsVector_U32_3( [ x[2], x[1], x[0] ] ) for x in poly ] )
            normal = white_mesh_ext.normal()
            normal.assign( [ -x for x in normal ] )
            aims.write( white_mesh_ext, self.right_white_mesh.fullPath() )
            
            context.write( "Smoothing mesh..." )
            for i in range(3):
                context.runProcess( 'meshSmooth', mesh=self.right_white_mesh,
                                    iterations=10,rate=0.2 )
            
            tm.copyReferential(self.right_grey_white, self.right_white_mesh)
            
            del white
            del white_mesh
    
