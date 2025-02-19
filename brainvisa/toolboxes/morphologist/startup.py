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

import os
from brainvisa.configuration import neuroConfig
from brainvisa.data import neuroHierarchy
from soma.wip.application.api import Application
import brainvisa.processes
from brainvisa.configuration.sulci_configuration import SulciConfiguration
import shutil


configuration = Application().configuration

# if FSL is present: setup a database for FSL templates
fsldir = configuration.FSL.fsldir
if not fsldir:
    fsldir = os.getenv('FSLDIR')
if not fsldir and shutil.which('fslview'):
    # probably a system-wide linux installation like on Ubuntu
    if os.path.isdir('/usr/share/fsl/data'):
        fsldir = '/usr/share/fsl'
        if not configuration.FSL.fsl_commands_prefix \
                and not shutil.which('flirt'):
            versions = [v for v in os.listdir(os.path.join(fsldir))
                        if v != 'data']
            versionsi = [v.split('.') for v in versions]
            try:
                versionsi = [int(v[0]) * 0x100 + int(v[1]) for v in versionsi]
                version = versionsi.index(max(versionsi))
                fsl_prefix = 'fsl' + versions[version] + '-'
                if shutil.which(fsl_prefix + 'flirt'):
                    configuration.FSL.fsl_commands_prefix = fsl_prefix
            except:
                print('could not read FSL versions')
if fsldir and os.path.exists(fsldir):
    fslshare = os.path.join(fsldir, 'data')
    if os.path.exists(fslshare):
        if fslshare not in [x.directory for x in neuroConfig.dataPath]:
            dbs = neuroConfig.DatabaseSettings(fslshare)
            #fsldb = os.path.join( neuroConfig.homeBrainVISADir, 'fsl' )
            # if not os.path.exists( fsldb ):
            #os.mkdir( fsldb )
            dbs.expert_settings.ontology = 'fsl'
            dbs.expert_settings.sqliteFileName = ':temporary:'
            dbs.expert_settings.uuid = 'a69ed62b-4895-4245-b42a-d211e1c6faa4'
            dbs.builtin = True
            neuroConfig.dataPath.insert(1, dbs)
            db = neuroHierarchy.SQLDatabase(
                dbs.expert_settings.sqliteFileName, fslshare, 'fsl',
                context=brainvisa.processes.defaultContext(), settings=dbs)
            neuroHierarchy.databases.add(db)
            neuroHierarchy.update_soma_workflow_translations()

            del dbs, db  # , fsldb
    del fslshare
del fsldir

# if Matlab and SPM are found: setup a database for SPM templates

spmscript = None
spmdir = None
if configuration.SPM.spm12_standalone_path:
    spmdir = configuration.SPM.spm12_standalone_path
elif configuration.SPM.spm12_path:
    spmdir = configuration.SPM.spm12_path
elif configuration.SPM.spm8_standalone_path:
    spmdir = configuration.SPM.spm8_standalone_path
elif configuration.SPM.spm8_path:
    spmdir = configuration.SPM.spm8_path
elif configuration.SPM.spm5_path:
    spmdir = configuration.SPM.spm5_path
# print('*** SPMDIR:', spmdir)
if spmdir is not None:
    spmtemplates = None
    print('SPM dir:', spmdir)
    if not os.path.isdir(os.path.join(spmdir, 'templates')) \
            and not os.path.isdir(os.path.join(spmdir, 'toolbox')):
        if os.path.isdir(os.path.join(spmdir, 'spm12_mcr', 'spm12',
                                        'toolbox', 'OldNorm')):
            spmtemplates = os.path.join(spmdir, 'spm12_mcr', 'spm12')
        elif os.path.isdir(os.path.join(spmdir, 'spm12_mcr', 'spm12', 'spm12',
                                        'toolbox', 'OldNorm')):
            # spm12-standalone-8168 is installed this way...
            spmtemplates = os.path.join(spmdir, 'spm12_mcr', 'spm12', 'spm12')
        elif os.path.isdir(os.path.join(spmdir, 'spm8_mcr', 'spm8',
                                      'templates')):
            spmtemplates = os.path.join(spmdir, 'spm8_mcr', 'spm8')
    else:
        spmtemplates = spmdir  # os.path.join( spmdir, 'templates' )
    print('spmtemplates:', spmtemplates)
    if not neuroConfig.fastStart and spmtemplates and \
            not neuroHierarchy.databases.hasDatabase(spmtemplates):
        dbs = neuroConfig.DatabaseSettings(spmtemplates)
        #spmdb = os.path.join(neuroConfig.homeBrainVISADir, 'spm')
        # if not os.path.exists(spmdb):
        # os.mkdir(spmdb)
        dbs.expert_settings.ontology = 'spm'
        dbs.expert_settings.sqliteFileName = ':temporary:'
        dbs.expert_settings.uuid = 'a91fd1bf-48cf-4759-896e-afea136c0549'
        dbs.builtin = True
        neuroConfig.dataPath.insert(1, dbs)
        db = neuroHierarchy.SQLDatabase(
            dbs.expert_settings.sqliteFileName, spmtemplates, 'spm',
            context=brainvisa.processes.defaultContext(), settings=dbs)
        neuroHierarchy.databases.add(db)
        neuroHierarchy.update_soma_workflow_translations()
        del dbs, db
    del spmtemplates, spmdir

# Sulci configuration
if not 'sulci' in configuration.signature:
    configuration.add('sulci', SulciConfiguration())
