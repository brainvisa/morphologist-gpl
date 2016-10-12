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
from brainvisa import registration

name = 'Grey White Classification 2012'
userLevel = 2

# Argument declaration
signature = Signature(
    'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
	'Aims readable volume formats' ),
    'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
    'split_mask', ReadDiskItem( 'Split Brain Mask',
	'Aims readable volume formats' ),
    'edges', ReadDiskItem( 'T1 MRI Edges',
	'Aims readable volume formats' ),
    'commissure_coordinates', ReadDiskItem( 'Commissure coordinates',
	'Commissure coordinates'),
    'Side', Choice("Both","Left","Right"),
    'left_grey_white', WriteDiskItem( 'Left Grey White Mask',
	'Aims writable volume formats' ),
    'right_grey_white', WriteDiskItem( 'Right Grey White Mask',
	'Aims writable volume formats' ),
    'fix_random_seed', Boolean(),
) 
# Default values
def initialization( self ):
    self.linkParameters( 'histo_analysis', 'mri_corrected' )
    self.linkParameters( 'left_grey_white', 'mri_corrected' )
    self.linkParameters( 'right_grey_white', 'mri_corrected' )
    self.linkParameters( 'split_mask', 'mri_corrected' )
    self.linkParameters( 'edges', 'mri_corrected' )
    self.linkParameters( 'commissure_coordinates', 'mri_corrected' )
    self.signature[ 'fix_random_seed' ].userLevel = 3
    self.Side = "Both"
    self.fix_random_seed = False
#
#

def execution( self, context ):
    tm=registration.getTransformationManager()
    
    #hemis = context.temporary( 'GIS Image' )
    #grey_white = context.temporary( 'GIS Image' )
    #context.write( "Computing hemispheres grey-white classification..." )
    #context.system( "VipDoubleThreshold", "-i",
                    #self.split_mask, "-o", hemis,
                    #"-tl", "1", "-th", "2",
                    #"-m", "be", "-c", "b", "-w", "t" )
    #context.system( "VipMerge", "-i",
                    #hemis, "-m", self.split_mask,
                    #"-o", hemis, "-c", "l",
                    #"-l", "3", "-v", "3", "-w", "t" )
    #context.system( "VipGreyWhiteClassif", "-i",
                    #self.mri_corrected, "-h",
                    #self.histo_analysis, "-mask",
                    #hemis, "-edges",
                    #self.edges, "-o",
                    #grey_white, "-l", "255",
                    #"-mode", "b", "-w",
                    #"t", "-a", "N" )
    
    #if self.Side in ('Left','Both'):
        
        #if os.path.exists(self.left_grey_white.fullName() + '.loc'):
            #context.write( "Left grey-white locked")
        #else:
            #context.system( "VipMask", "-i", grey_white,
                            #"-m", self.split_mask,
                            #"-o", self.left_grey_white,
                            #"-w", "t", "-l", "2" )
            #tm.copyReferential(self.mri_corrected, self.left_grey_white)
    
    #if self.Side in ('Right','Both'):
        
        #if os.path.exists(self.right_grey_white.fullName() + '.loc'):
            #context.write( "Right grey-white locked")
        #else:
            #context.system( "VipMask", "-i", grey_white,
                            #"-m", self.split_mask,
                            #"-o", self.right_grey_white,
                            #"-w", "t", "-l", "1" )
            #tm.copyReferential(self.mri_corrected, self.right_grey_white)
    
    #del hemis
    #del grey_white
    
    base_command = ["VipGreyWhiteClassif",
                         "-i", self.mri_corrected,
                         "-h", self.histo_analysis,
                         "-m", self.split_mask,
                         "-edges", self.edges,
                         "-P", self.commissure_coordinates,
                         "-w", "t", "-a", "N"]
    if self.fix_random_seed:
        base_command += ['-srand', '10']
    if self.Side in ('Left','Both'):
        
        if os.path.exists(self.left_grey_white.fullName() + '.loc'):
            context.write( "Left grey-white locked")
        else:
            context.write( "Computing left hemisphere grey-white classification..." )
            left_command = base_command + ["-o", self.left_grey_white,
                                           "-l", "2"]
            context.system(*left_command)

            tm.copyReferential(self.mri_corrected, self.left_grey_white)
    
    if self.Side in ('Right','Both'):
        
        if os.path.exists(self.right_grey_white.fullName() + '.loc'):
            context.write( "Right grey-white locked")
        else:
            context.write( "Computing right hemisphere grey-white classification..." )
            right_command = base_command + ["-o", self.right_grey_white,
                                           "-l", "1"]
            context.system(*right_command)
            tm.copyReferential(self.mri_corrected, self.right_grey_white)
