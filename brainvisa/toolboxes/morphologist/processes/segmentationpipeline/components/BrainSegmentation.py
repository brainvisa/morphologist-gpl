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

name = 'Compute Brain Mask'
userLevel = 0

# Argument declaration
signature = Signature(
    't1mri_nobias', ReadDiskItem(
        'T1 MRI Bias Corrected',
        'Aims readable volume formats'),
    'histo_analysis', ReadDiskItem(
        'Histo Analysis',
        'Histo Analysis'),
    'variance', ReadDiskItem(
        'T1 MRI Variance',
        'Aims readable volume formats'),
    'edges', ReadDiskItem(
        'T1 MRI Edges',
        'Aims readable volume formats'),
    'white_ridges', ReadDiskItem(
        'T1 MRI White Matter Ridges',
        'Aims readable volume formats'),
    'commissure_coordinates', ReadDiskItem(
        'Commissure coordinates',
        'Commissure coordinates'),
    'lesion_mask', ReadDiskItem(
        'Lesion Mask',
        'Aims readable volume formats'),
    'lesion_mask_mode', Choice(('Exclude the lesion mask', 'e'),
                               ('Include the lesion mask', 'i')),
    'variant', Choice('2010',
                      '2005 based on white ridge',
                      'Standard + (iterative erosion)',
                      'Standard + (selected erosion)',
                      'Standard + (iterative erosion) without regularisation',
                      'Robust + (iterative erosion)',
                      'Robust + (selected erosion)',
                      'Robust + (iterative erosion) without regularisation',
                      'Fast (selected erosion)'),
    'erosion_size', OpenChoice(1, 1.5, 1.8, 2, 2.5, 3, 3.5 ,4),
    'visu', Choice('No', 'Yes'),
    'layer', Choice(0, 1, 2, 3, 4, 5),
    'first_slice', Integer(),
    'last_slice', Integer(),
    'brain_mask', WriteDiskItem(
        'T1 Brain Mask',
        'Aims writable volume formats'),
    'fix_random_seed', Boolean(),
)

# Default values
def initialization( self ):
    self.linkParameters( 'histo_analysis', 't1mri_nobias' )
    self.linkParameters( 'brain_mask', 't1mri_nobias' )
    self.linkParameters( 'white_ridges', 't1mri_nobias' )
    self.linkParameters( 'variance', 't1mri_nobias' )
    self.linkParameters( 'edges', 't1mri_nobias' )
    self.linkParameters( 'commissure_coordinates', 't1mri_nobias' )
    self.setOptional('white_ridges')
    self.setOptional('lesion_mask')
    self.setOptional('commissure_coordinates')
    self.signature['fix_random_seed'].userLevel = 3
    self.erosion_size = 1.8
    self.first_slice = 0
    self.last_slice = 0
    self.variant = '2010'
    self.visu = 'No'
    self.layer = '0'
    self.lesion_mask_mode = 'e'
    self.fix_random_seed = False


def execution( self, context ):
    if os.path.exists(self.brain_mask.fullName() + '.loc'):
        context.write(self.brain_mask.fullName(), ' has been locked')
        context.write('Remove',self.brain_mask.fullName(),'.loc if you want to trigger a new segmentation')
    else:
        command = [ 'VipGetBrain', '-i', self.t1mri_nobias,
                    '-berosion', self.erosion_size,
                    '-analyse', 'r',
                    '-hname', self.histo_analysis,
                    '-bname', self.brain_mask,
                    '-First', self.first_slice,
                    '-Last', self.last_slice,
                    '-layer', self.layer ]
        if self.commissure_coordinates is not None:
            command += ['-Points', self.commissure_coordinates]
        if self.lesion_mask is not None:
            command += ['-patho', self.lesion_mask,
                        '-pmode', self.lesion_mask_mode]
        
        if self.variant == '2010':
            command += ['-m', 'V',
                        '-Variancename', self.variance,
                        '-Edgesname', self.edges,
                        '-Ridge', self.white_ridges]
        elif self.variant == '2005 based on white ridge':
            command += ['-m', '5', '-Ridge', self.white_ridges]
        elif self.variant == 'Standard + (iterative erosion)':
            command += ['-m', 'Standard']
        elif self.variant == 'Standard + (selected erosion)':
            command += ['-m', 'standard']
        elif self.variant == 'Standard + (iterative erosion) without regularisation':
            command += ['-m', 'Standard','-niter', 0]
        elif self.variant == 'Robust + (iterative erosion)':
            command += ['-m', 'Robust']
        elif self.variant == 'Robust + (selected erosion)':
            command += ['-m', 'robust']
        elif self.variant == 'Robust + (iterative erosion) without regularisation':
            command += ['-m', 'Robust','-niter', 0]
        elif self.variant == 'Fast (selected erosion)':
            command += ['-m', 'fast']
        else:
            raise RuntimeError( _t_( 'Variant <em>%s</em> not implemented' ) % self.variant )
        if self.fix_random_seed:
            command += ['-srand', '10']
        context.system( *command )
        
        tm = registration.getTransformationManager()
        tm.copyReferential(self.t1mri_nobias, self.brain_mask)
        
        result = []
        if self.visu == 'Yes':
            result.append(context.runProcess('AnatomistShowBrainMask',
                self.brain_mask, self.t1mri_nobias))
            return result

