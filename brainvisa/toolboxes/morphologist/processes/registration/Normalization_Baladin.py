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
from brainvisa.configuration import neuroConfig
import brainvisa.tools.aimsGlobals as shfjGlobals
from brainvisa import registration
import os

def validation():
    import distutils.spawn
    if not distutils.spawn.find_executable('baladin'):
        raise ValidationError(_t_("'baladin' commandline " + \
                    "could not be found in PATH"))

name = 'Anatomy Normalization (using Baladin)'
userLevel = 2

# Baladin does not accept all image format -> conversion to .ima
signature = Signature(
    'anatomy_data', ReadDiskItem( "Raw T1 MRI", ['GIS Image']),
    'anatomical_template', ReadDiskItem( "anatomical Template", ['GIS Image'] ),
    'transformation_matrix', WriteDiskItem("baladin Transformation",
                            'Text file'),
    'normalized_anatomy_data', WriteDiskItem( "Raw T1 MRI",
        [ 'GIS image', 'NIFTI-1 image', 'gz compressed NIFTI-1 image' ],
        requiredAttributes={    'normalized' : 'yes',
                    'normalization' : 'baladin'}
    ),
)

def initialization( self ):
    self.linkParameters("transformation_matrix", "anatomy_data")
    self.linkParameters("normalized_anatomy_data", "anatomy_data")
    self.anatomical_template = self.signature[ 'anatomical_template' ].findValue({'database' : neuroConfig.dataPath[0], 'Size' : '1 mm', 'skull_stripped' : 'no'})

def execution( self, context ):
    anat = self.anatomy_data.fullPath()
    template = self.anatomical_template.fullPath()
    transformation = self.transformation_matrix.fullPath()
    normanat = self.normalized_anatomy_data.fullPath()

    if self.normalized_anatomy_data.format != 'GIS Image':
        normanat2 = context.temporary('GIS Image')
    else:    normanat2 = normanat

    anat_dim = anat.rstrip('ima') + 'dim'
    template_dim = template.rstrip('ima') + 'dim'

    # Baladin registration with some tuned values to work on a template.
    context.system( 'baladin', '-ref', template_dim, '-flo', anat_dim,
        '-res', normanat2, '-result-real-matrix', transformation,
        '-result-matrix', '/dev/null', '-transformation', 'affine',
        '-pyramid-levels' ,'4', '-pyramid-finest-level', '1',
        '-max-iterations', '10', '-command-line', '/dev/null')

    if self.normalized_anatomy_data.format != 'GIS Image':
        context.system( 'AimsFileConvert', '-i', normanat2,
                        '-o', normanat)

    tm = registration.getTransformationManager()
    tm.copyReferential(self.anatomical_template,
            self.normalized_anatomy_data)
