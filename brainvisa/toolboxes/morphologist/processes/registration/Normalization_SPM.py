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
from brainvisa.validation import ValidationError
from brainvisa import shelltools
import brainvisa.tools.spm_run as spm
from brainvisa.tools import spm_registration
import shutil
import os
import sys

from soma.wip.application.api import Application
import soma.subprocess

configuration = Application().configuration


def validation():
    if((not configuration.SPM.spm8_standalone_command
        or not (configuration.SPM.spm8_standalone_mcr_path or (sys.platform == "win32")))) \
            and not shutil.which(
            configuration.matlab.executable):
        raise ValidationError('SPM or matlab is not found')


name = 'Anatomy Normalization (using SPM)'
userLevel = 2

signature = Signature(
    'anatomy_data', ReadDiskItem("Raw T1 MRI", ['NIFTI-1 image', 'SPM image']),
    'anatomical_template', ReadDiskItem(
        "anatomical Template", ['NIFTI-1 image', 'MINC image', 'SPM image']),
    'job_file', WriteDiskItem("SPM2 parameters", 'Matlab file'),
    'voxel_size', Choice('[1 1 1]'),
    'cutoff_option', Integer(),
    'nbiteration', Integer(),
    'transformations_informations', WriteDiskItem(
        "SPM2 normalization matrix", 'Matlab file'),
    'normalized_anatomy_data', WriteDiskItem(
        "Raw T1 MRI", ['NIFTI-1 image', 'SPM image'], {"normalization": "SPM"})
)


capsul_param_options = {
    'anatomical_template': ['dataset="shared"'],
}


def initialization(self):
    configuration.SPM.spm5_path  # trigger the spmpathcheck process if needed
    self.linkParameters("transformations_informations", "anatomy_data")
    self.linkParameters("normalized_anatomy_data", "anatomy_data")
    self.voxel_size = "[1 1 1]"
    self.cutoff_option = "25"
    self.nbiteration = 16
    self.setOptional("anatomical_template")
    self.setOptional('job_file')
    # Link parameters
    self.linkParameters("job_file", "anatomy_data")
    self.anatomical_template = self.signature['anatomical_template'].findValue({'databasename': 'spm',
                                                                                'skull_stripped': 'no'})


def execution(self, context):
    matfileDI = context.temporary('Matlab script')
    try:
        spm.validation(configuration)
        use_spm8 = True
    except:
        context.warning('spm8 invalid!')
        use_spm8 = False
   # if configuration.SPM.spm8_standalone_command \
        # and (configuration.SPM.spm8_standalone_mcr_path or (sys.platform == "win32")):
        # SPM8 standalone variant
        # context.write( _t_( \
        #'Using SPM8 standalone version (compiled, Matlab not needed)' ) )

    if use_spm8:
        matfilePath = spm_registration.writeNormalizeMatFile(context,
                                                             configuration, self.anatomy_data.fullPath(),
                                                             self.anatomy_data.fullPath(), matfileDI.fullPath(),
                                                             self.anatomical_template.fullPath(), "''", "''", '8',
                                                             '0', "'mni'", str(self.cutoff_option), str(
                                                                 self.nbiteration),
                                                             '1', None, None, self.voxel_size, '1', '[0 0 0]', "'w'")

        #spm.runSpm8Standalone(context, configuration, matfilePath)
        spm.run(context, configuration, matfilePath)

        #mat_file = file( matfileDI.fullPath(), 'w')
        #anat_paths = []
        # for i, anat in enumerate([self.anatomy_data]):
        #anat_path = anat.fullPath()
        #anat_paths.append( anat_path )
        #j = i + 1
        # mat_file.write( \
#"""matlabbatch{%d}.spm.spatial.normalise.estwrite.subj.source = {'%s,1'};
# matlabbatch{%d}.spm.spatial.normalise.estwrite.subj.wtsrc = '';
# matlabbatch{%d}.spm.spatial.normalise.estwrite.subj.resample = {'%s'};
# matlabbatch{%d}.spm.spatial.normalise.estwrite.eoptions.template = {'%s,1'};
# matlabbatch{%d}.spm.spatial.normalise.estwrite.eoptions.weight = '';
# matlabbatch{%d}.spm.spatial.normalise.estwrite.eoptions.smosrc = 8;
# matlabbatch{%d}.spm.spatial.normalise.estwrite.eoptions.smoref = 0;
# matlabbatch{%d}.spm.spatial.normalise.estwrite.eoptions.regtype = 'mni';
# matlabbatch{%d}.spm.spatial.normalise.estwrite.eoptions.cutoff = %d;
# matlabbatch{%d}.spm.spatial.normalise.estwrite.eoptions.nits = %d;
# matlabbatch{%d}.spm.spatial.normalise.estwrite.eoptions.reg = 1;
# matlabbatch{%d}.spm.spatial.normalise.estwrite.roptions.vox = %s;
# matlabbatch{%d}.spm.spatial.normalise.estwrite.roptions.interp = 1;
# matlabbatch{%d}.spm.spatial.normalise.estwrite.roptions.wrap = [0 0 0];
# matlabbatch{%d}.spm.spatial.normalise.estwrite.roptions.prefix = 'w';
#""" \
        #% ( j, anat_path, j, j, anat_path,
        #j, self.anatomical_template.fullPath(), j, j, j, j,
        #j, self.cutoff_option, j, self.nbiteration, j,
        # j, self.voxel_size, j, j, j ) )
        # mat_file.close()

        #mexe = configuration.SPM.spm8_standalone_command
        #pd = os.getcwd()
        #os.chdir( os.path.dirname(matfileDI.fullPath() ))
        # cmd = [ mexe, configuration.SPM.spm8_standalone_mcr_path, 'run',
        # matfileDI.fullPath() ]
        #context.write( 'running SPM command:', cmd )
        #context.system( *cmd )
        #os.chdir( pd )

    else:
        # Matlab-based SPM5-style variant
        mat_file = open(matfileDI.fullPath(), 'w')
        if os.path.isdir(configuration.SPM.spm8_path):
            context.write(_t_('Using SPM8 with Matlab (experimental)'))
        else:
            context.write(_t_('Using SPM5 with Matlab'))
        if configuration.SPM.spm5_path:
            mat_file.write("addpath( '" + configuration.SPM.spm5_path
                           + "')\n")
        mat_file.write("if exist('spm8')==2\n  spm8;\n")
        mat_file.write("elseif exist('spm5')==2\n  spm5;\n")
        mat_file.write("elseif exist('spm')==2\n  spm;\n")
        mat_file.write("else disp('error : spm cannot be loaded');end\n")
        mat_file.write(
            'jobs{1}.spatial{1}.normalise{1}.estwrite.roptions.vox = %s\n' % self.voxel_size)
        mat_file.write(
            'jobs{1}.spatial{1}.normalise{1}.estwrite.eoptions.template = ...\n')
        if self.anatomical_template != None:
            mat_file.write("{'%s'}\n" % self.anatomical_template.fullPath())
        else:
            mat_file.write(
                "cellstr(fullfile(spm('Dir'),'templates','T1.nii'))\n")
        mat_file.write(
            'jobs{1}.spatial{1}.normalise{1}.estwrite.eoptions.cutoff = %d\n' % self.cutoff_option)
        mat_file.write(
            'jobs{1}.spatial{1}.normalise{1}.estwrite.eoptions.nits = %i\n' % self.nbiteration)
        for i, anat in enumerate([self.anatomy_data]):
            anat_paths = [path for path in anat.fullPaths() if path[-4:] == '.img' or path[-4:]
                          == '.ima' or path[-4:] == '.nii' or path.endswith('.nii.gz')]
            mat_file.write("anat_ref = { '%s'\n" % anat_paths[0])
            for path in anat_paths[1:-1]:
                mat_file.write("'%s'\n" % path)
            if len(anat_paths) != 1:
                mat_file.write("'%s'}\n" % anat_paths[-1])
            else:
                mat_file.write('}\n')
            j = i + 1
            mat_file.write(
                'jobs{1}.spatial{1}.normalise{1}.estwrite.subj(%i).source = anat_ref\n' % j)
            mat_file.write(
                'jobs{1}.spatial{1}.normalise{1}.estwrite.subj(%i).resample = anat_ref\n' % j)
        if self.job_file is None:
            job_file = context.temporary('Matlab file')
        else:
            job_file = self.job_file
        mat_file.write("save('%s','jobs')\n" % job_file.fullPath())
        mat_file.write("load ('%s')\n" % job_file.fullPath())
        mat_file.write("spm_jobman('run',jobs)\n")
        mat_file.write("exit\n")
        mat_file.close()

        mexe = shutil.which(configuration.matlab.executable)
        pd = os.getcwd()
        # context.write(matfileDI.fullPath())
        os.chdir(os.path.dirname(matfileDI.fullPath()))
        cmd = [mexe] + configuration.matlab.options.split() + \
            ['-r', os.path.basename(matfileDI.fullName())]
        context.write('running matlab command:', cmd)
        context.system(*cmd)
        os.chdir(pd)

    # place output at correct location
    outfile = self.anatomy_data.fullPath()[
        :self.anatomy_data.fullPath().rfind('.')] + '_sn.mat'
    if self.transformations_informations.fullPath() != outfile:
        shelltools.mv(outfile,
                      self.transformations_informations.fullPath())

    # Rename the normalized volume written by spm in a form that fits
    # bv hierarchy
    for f in self.anatomy_data.fullPaths():
        anatdir = os.path.dirname(f)
        anatname, ext = os.path.splitext(os.path.basename(f))
        wanat = os.path.join(anatdir, "w"+anatname+ext)
        if os.path.exists(wanat):
            shelltools.mv(wanat,
                          self.normalized_anatomy_data.fullName()+ext)
    #tm = registration.getTransformationManager()
    #tm.copyReferential( self.anatomical_template, self.normalized_anatomy_data )
