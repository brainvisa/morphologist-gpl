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
from brainvisa import registration

name = 'Hemisphere Grey White Classification'
userLevel = 0

# Argument declaration
signature = Signature(
    'side', Choice('left', 'right'),
    't1mri_nobias', ReadDiskItem(
        'T1 MRI Bias Corrected',
        'Aims readable volume formats'),
    'histo_analysis', ReadDiskItem(
        'Histo Analysis',
        'Histo Analysis'),
    'split_brain', ReadDiskItem(
        'Split Brain Mask',
        'Aims readable volume formats'),
    'edges', ReadDiskItem(
        'T1 MRI Edges',
        'Aims readable volume formats'),
    'commissure_coordinates', ReadDiskItem(
        'Commissure coordinates',
        'Commissure coordinates'),
    'lesion_mask', ReadDiskItem(
        'Lesion Mask',
        'Aims readable volume formats'),
    'lesion_mask_mode', Choice(('Exclude the lesion mask', 'e'),
                               ('Include the lesion mask as WM', 'w'),
                               ('Include the lesion mask as GM', 'g')),
    'grey_white', WriteDiskItem(
        'Morphologist Grey White Mask',
        'Aims writable volume formats'),
    'fix_random_seed', Boolean(),
)

# Default values
def initialization( self ):
    def linkGW( self, dummy ):
        if self.t1mri_nobias is not None:
            return self.signature[ 'grey_white' ].findValue( self.t1mri_nobias, requiredAttributes={'side': self.side})
    self.linkParameters('histo_analysis', 't1mri_nobias')
    self.linkParameters('grey_white',
                        ('t1mri_nobias', 'side'),
                        linkGW)
    self.linkParameters('split_brain', 't1mri_nobias')
    self.linkParameters('edges', 't1mri_nobias')
    self.linkParameters('commissure_coordinates', 't1mri_nobias')
    self.signature[ 'fix_random_seed' ].userLevel = 3
    self.fix_random_seed = False
    self.setOptional('lesion_mask')
    self.lesion_mask_mode = 'e'
    


def execution( self, context ):
    if os.path.exists(self.grey_white.fullName() + '.loc'):
        context.write(self.grey_white.fullName(), 'has been locked')
        context.write('Remove', self.grey_white.fullName(), '.loc if you want to trigger a new classification')
    else:
        context.write( 'Computing ' + self.side + ' hemisphere grey-white classification...' )
        if self.side == 'left':
            sideval = 2
        else:
            sideval = 1
        command = [ 'VipGreyWhiteClassif', '-i',
                    self.t1mri_nobias, '-h',
                    self.histo_analysis, '-m',
                    self.split_brain, '-edges',
                    self.edges, '-P',
                    self.commissure_coordinates, '-o',
                    self.grey_white, '-l', sideval,
                    '-w', 't', '-a', 'N' ]
        if self.lesion_mask is not None:
            command += ['-patho', self.lesion_mask,
                        '-pmode', self.lesion_mask_mode]
        if self.fix_random_seed:
            command += ['-srand', '10']
        context.system( *command )
        
        tm = registration.getTransformationManager()
        tm.copyReferential(self.t1mri_nobias, self.grey_white)

