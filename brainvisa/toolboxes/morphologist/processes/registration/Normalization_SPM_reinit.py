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
from brainvisa.validation import ValidationError
from brainvisa import shelltools
#from numpy import *
import commands
import distutils.spawn
import os
#import registration

from soma.wip.application.api import Application
import subprocess

configuration = Application().configuration


def validation():
    if( ( not configuration.SPM.spm8_standalone_command \
          or not (configuration.SPM.spm8_standalone_mcr_path or (sys.platform == "win32")) ) ) \
        and not distutils.spawn.find_executable( \
          configuration.matlab.executable ):
        raise ValidationError( 'SPM or matlab is not found' )

name = 'Anatomy Normalization (using SPM) with Re-initialization'
userLevel = 0

signature = Signature(
    'anatomy_data', ReadDiskItem( "Raw T1 MRI", ['NIFTI-1 image', 'SPM image' ]),
    'anatomical_template', ReadDiskItem( "anatomical Template", ['NIFTI-1 image', 'MINC image', 'SPM image'] ),
    'job_file', WriteDiskItem("SPM2 parameters", 'Matlab file'),
    'voxel_size', Choice('[1 1 1]'),
    'cutoff_option', Integer(),
    'nbiteration', Integer(),
    'transformations_informations', WriteDiskItem("SPM2 normalization matrix", 'Matlab file'),
    'normalized_anatomy_data', WriteDiskItem("Raw T1 MRI", ['NIFTI-1 image', 'SPM image' ], {"normalization" : "SPM"}),
    'allow_retry_initialization', Boolean(),
    'init_translation_origin', Choice( ( 'Center of the image', 0 ), ( 'Gravity center', 1 ) ),
)

def initialization( self ):
    configuration.SPM.spm5_path # trigger the spmpathcheck process if needed
    self.linkParameters("transformations_informations", "anatomy_data" )
    self.linkParameters("normalized_anatomy_data", "anatomy_data" )
    self.voxel_size = "[1 1 1]"
    self.cutoff_option = "25"
    self.nbiteration = 16
    self.setOptional("anatomical_template")
    self.setOptional( 'job_file' )
    # Link parameters
    def get_dir(self, process):
        if self.anatomy_data and self.anatomy_data != []:
            path = os.path.dirname(self.anatomy_data.fullPath())
            return os.path.join(path,'job_anat_normalization.mat')
    self.linkParameters("job_file", "anatomy_data", get_dir)
    self.anatomical_template = self.signature[ 'anatomical_template' ].findValue( { 'databasename' : 'spm',
            'skull_stripped' : 'no' } )
    self.allow_retry_initialization = False


def execution( self, context ):
    context.write( _t_( 'Trying 1st pass of normalization...' ) )
    if os.path.exists( self.transformations_informations.fullPath() ):
        os.unlink( self.transformations_informations.fullPath() )
    failed = False
    normproc = { 'anatomy_data' : [self.anatomy_data],
        'anatomical_template' : self.anatomical_template,
        'job_file' : self.job_file,
        'voxel_size' : self.voxel_size,
        'cutoff_option' : self.cutoff_option,
        'nbiteration' : self.nbiteration,
        'transformations_informations' : [self.transformations_informations],
        'normalized_anatomy_data' : [self.normalized_anatomy_data],
    }
    try:
        context.runProcess( 'Normalization_SPM', **normproc )
        if not os.path.exists( self.transformations_informations.fullPath() ):
            failed = True
    except:
        failed = True
        if not self.allow_retry_initialization:
            raise
    if failed:
        context.write( _t_( '1st pass failed, changing internal transformation initialization' ) )
        if not self.allow_retry_initialization:
            raise RuntimeError( 'Normalization failed' )
        context.runProcess( 'resetInternalImageTransformation',
            input_image=self.anatomy_data, output_image=self.anatomy_data,
            origin=self.init_translation_origin )
        context.write( _t_( 'Retrying normalization after changing initialization...' ) )
        context.runProcess( 'Normalization_SPM', **normproc )
