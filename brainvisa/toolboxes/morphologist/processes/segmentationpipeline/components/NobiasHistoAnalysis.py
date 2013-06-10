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

name = 'Histogram analysis'
userLevel = 0

signature = Signature(
    't1mri_nobias', ReadDiskItem( 'T1 MRI Bias Corrected',
        'Aims readable volume formats' ),
    'use_hfiltered', Boolean(),
    'hfiltered', ReadDiskItem( 'T1 MRI Filtered For Histo',
        'Aims readable volume formats' ),
    'use_wridges', Boolean(),
    'white_ridges', ReadDiskItem( 'T1 MRI White Matter Ridges',
        'Aims readable volume formats' ),
    'undersampling', Choice('2', '4', '8', '16', '32', 'auto', 'iteration' ),
    'histo_analysis', WriteDiskItem( 'Histo Analysis', 'Histo Analysis' ),
    'histo', WriteDiskItem( 'Histogram', 'Histogram' ),
    'fix_random_seed', Boolean(),
)

def initialization( self ):
    self.signature[ 'fix_random_seed' ].userLevel = 3
    self.linkParameters( 'histo_analysis', 't1mri_nobias' )
    self.linkParameters( 'histo', 't1mri_nobias' )
    self.linkParameters( 'hfiltered', 't1mri_nobias' )
    self.linkParameters( 'white_ridges', 't1mri_nobias' )
    self.setOptional( 'hfiltered' )
    self.setOptional( 'white_ridges' )
    self.use_hfiltered =  True
    self.use_wridges = True
    self.undersampling = 'iteration'
    self.fix_random_seed = False


def execution( self, context ):
    if os.path.exists(self.histo_analysis.fullName() + '.han.loc'):
        context.write(self.histo_analysis.fullName(), '.han has been locked')
        context.write('Remove',self.histo_analysis.fullName(),'.han.loc if you want to trigger automated analysis')
    else:
        command = [ 'VipHistoAnalysis',
                    '-i', self.t1mri_nobias,
                    '-o', self.histo_analysis,
                    '-Save', 'y' ]
    if self.use_hfiltered and self.hfiltered is not None:
        command += ['-Mask', self.hfiltered]
    if self.use_wridges and self.white_ridges is not None:
        command += ['-Ridge', self.white_ridges]
    if self.undersampling == 'iteration':
        command += ['-mode', 'i']
    else:
        command += ['-mode', 'a', '-u', self.undersampling]
    if self.fix_random_seed:
        command += ['-srand', '10']
    context.system( *command )

