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

name = 'Skull-stripped brain normalization'
userLevel = 2

signature = Signature(
    't1mri', ReadDiskItem( "Raw T1 MRI", "Aims readable volume formats" ),
    'brain_mask', ReadDiskItem( "Brain Mask", "Aims readable volume formats" ),
    'template', ReadDiskItem( "anatomical Template", ['NIFTI-1 image', 'MINC image', 'SPM image'], requiredAttributes={'skull_stripped':'yes'} ),
    'skull_stripped', WriteDiskItem( '3D Volume',
      'Aims writable volume formats' ),
    'transformation', WriteDiskItem( \
      'Transform Raw T1 MRI to Talairach-MNI template-SPM',
      'Transformation matrix' ),
)

def initialization( self ):
    self.linkParameters("transformation", "t1mri" )
    self.skull_stripped = defaultContext().temporary( 'NIFTI-1 image' )
    normalized = defaultContext().temporary( 'NIFTI-1 image' )
    self.template = self.signature['template' ].findValue( \
        { '_database' : os.path.normpath( os.path.join( mainPath,
            '..', 'share', 'brainvisa-share-%s.%s' \
                % tuple(versionString().split('.')[:2] ) ) ),
          'Size': '2 mm' } )

    eNode = SerialExecutionNode( self.name, parameterized=self )
    eNode.addChild( 'SkullStripping',
      ProcessExecutionNode( 'skullstripping', selected=1 ) )
    eNode.addChild( 'Normalization',
      ProcessExecutionNode( 'normalizationPipeline', selected=1 ) )
    eNode.Normalization.removeLink( 'transformation', 't1mri' )
    eNode.addDoubleLink( 'SkullStripping.t1mri', 't1mri' )
    eNode.addDoubleLink( 'SkullStripping.brain_mask', 'brain_mask' )
    eNode.addDoubleLink( 'SkullStripping.skull_stripped', 'skull_stripped' )
    eNode.addDoubleLink( 'Normalization.t1mri', 'skull_stripped' )
    eNode.addDoubleLink( 'Normalization.transformation', 'transformation' )
    try:
        fsl = getProcess( 'FSLnormalizationPipeline' )
    except:
        fsl = None
    try:
        spm = getProcess( 'SPMnormalizationPipeline' )
    except:
        spm = None
    try:
        bal = getProcess( 'BaladinNormalizationPipeline' )
    except:
        bal = None

    self.setExecutionNode( eNode )

    if fsl:
        eNode.addDoubleLink( 'Normalization.NormalizeFSL.template',
            'template' )
        eNode.Normalization.NormalizeFSL.NormalizeFSL.removeLink( \
            'normalized_anatomy_data', 'anatomy_data' )
        normalizedc = defaultContext().temporary( \
            'gz compressed NIFTI-1 image' )
        eNode.Normalization.NormalizeFSL.NormalizeFSL.normalized_anatomy_data \
            = normalizedc
    if spm:
        eNode.addDoubleLink( 'Normalization.NormalizeSPM.template',
            'template' )
        eNode.Normalization.NormalizeSPM.NormalizeSPM.removeLink( \
            'normalized_anatomy_data', 'anatomy_data' )
        eNode.Normalization.NormalizeSPM.NormalizeSPM.normalized_anatomy_data \
            = normalized
    if bal:
        eNode.addDoubleLink( 'Normalization.NormalizeBaladin.template',
            'template' )
        eNode.Normalization.NormalizeBaladin.NormalizeBaladin.removeLink( \
            'normalized_anatomy_data', 'anatomy_data' )
        eNode.Normalization.NormalizeBaladin.NormalizeBaladin.normalized_anatomy_data = normalized