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
from soma.wip.application.api import Application
from brainvisa.configuration import neuroConfig
from brainvisa.data import neuroHierarchy
import distutils.spawn
import sys


name = 'SPM path check'
userLevel = 2

signature = Signature(
)


def initialization( self ):
  pass

def inlineGUI( self, values, pview, parent, externalRunButton=False ):
  from PyQt4 import QtGui
  from brainvisa.processing.qtgui import neuroProcessesGUI
  vb = QtGui.QWidget()
  lay = QtGui.QVBoxLayout( vb )
  lay.addWidget( neuroProcessesGUI.ProcessView.defaultInlineGUI( pview, vb,
    externalRunButton, None ) )
  lay.addWidget( QtGui.QLabel( \
    _t_( 'The SPM paths have not been setup in the configuration.\nCurrently, processes using SPM might not work,\nand the SPM database (normalization templates...) cannot be used.\nThis process can try to detect it and set it in the configuration.\nYou should re-open any process depending on SPM afterwards.' ),
    vb ) )
  return vb

def checkSPMCommand( context, cmd ):
  configuration = Application().configuration
  spmscript = None
  mexe = distutils.spawn.find_executable( \
    configuration.matlab.executable )
  if mexe == None:
    context.write('The Matlab executable was not found.')
    return
  mscfile = context.temporary( 'Matlab Script' )
  spmf = context.temporary( 'Text File' )
  mscfn = mscfile.fullPath()
  mscript = '''try
  a = which( \'''' + cmd + '''\' );
  if ~isempty( a )
    try
      ''' + cmd + ''';
    catch me
    end
  end
  spmpath = which( 'spm' );
  f = fopen( ''' + "'" + spmf.fullPath() + "'" + ''', 'w' );
  fprintf( f, '%s\\n', spmpath );
catch me
end
exit;
'''
  open( mscfn, 'w' ).write( mscript )
  pd = os.getcwd()
  os.chdir( os.path.dirname( mscfn ) )
  cmd = [ mexe ] + configuration.matlab.options.split() \
    + [ '-r', os.path.basename( mscfile.fullName() ) ]
  context.write('Attempt to run the matlab command: ' + repr(cmd))
  #print 'running matlab command: ', cmd
  try:
    context.system( *cmd )
  except Exception, e:
    return None
  os.chdir( pd )
  spmscript = open( spmf.fullPath() ).read().strip()
  spmpath = os.path.dirname( spmscript )
  return spmpath


def execution( self, context ):
  configuration = Application().configuration

  old_spm8_standalone_path=configuration.SPM.spm8_standalone_path
  old_spm8path=configuration.SPM.spm8_path
  old_spm5path=configuration.SPM.spm5_path
  
  spm8_standalone_mcr_path = None
  spm8_standalone_command = None
  spm8_standalone_path = None
  context.write('\nLooking for spm8 standalone...')
  if sys.platform == "win32":
    spm8exe="spm8_w32.exe"
  else:
    spm8exe="run_spm8.sh"
  
  spm8_standalone_command = distutils.spawn.find_executable(spm8exe)
  if spm8_standalone_command is not None:
    spm8_standalone_command = os.path.realpath( spm8_standalone_command ) # to follow symlinks if needed
    spm8_standalone = os.path.dirname(spm8_standalone_command)
    # Search for the matlab compiler runtime path
    if sys.platform != "win32": # no need of mcr on windows
      spm8_standalone_mcr_path = os.path.join(spm8_standalone, 'mcr', 'v713')
      if not os.path.exists(spm8_standalone_mcr_path):
        if sys.patform == "darwin":
          spm8_standalone_mcr_path = "/Applications/MATLAB/MATLAB_Compiler_Runtime/v713/"
        else:
          spm8_standalone_mcr_path = "/usr/local/MATLAB/MATLAB_Compiler_Runtime/v713/"
        if not os.path.exists(spm8_standalone_mcr_path):
          spm8_standalone_mcr_path = None
    
    spm8_standalone_path = os.path.join(spm8_standalone, 'spm8_mcr', 'spm8')
    if not os.path.exists(spm8_standalone_path):
      spm8_standalone_path=None
  if (spm8_standalone_command and (spm8_standalone_mcr_path or (sys.platform == "win32")) and spm8_standalone_path):
    configuration.SPM.spm8_standalone_command = spm8_standalone_command
    configuration.SPM.spm8_standalone_mcr_path = spm8_standalone_mcr_path
    configuration.SPM.spm8_standalone_path = spm8_standalone_path
    context.write('=> spm8 standalone was found: ', spm8_standalone_command)
  else:
    configuration.SPM.spm8_standalone_command = ""
    configuration.SPM.spm8_standalone_mcr_path = ""
    configuration.SPM.spm8_standalone_path = ""
    context.write('=> spm8 standalone was not found.')

  context.write('\nLooking for spm8 with Matlab...')
  spm8path = self.checkSPMCommand( context, 'spm8' )
  if spm8path:
    configuration.SPM.spm8_path = spm8path
    context.write('=> spm8 was found: ', spm8path)
  else:
    configuration.SPM.spm8_path = ""
    context.write('=> spm8 was not found.')

  context.write('\nLooking for spm5 ...')
  spm5path = self.checkSPMCommand( context, 'spm5' )
  if spm5path:
    configuration.SPM.spm5_path = spm5path
    context.write('=> spm5 was found: ', spm5path)
  else:
    configuration.SPM.spm5_path = spm5path
    context.write('=> spm5 was not found.')

  spmpath = None
  if spm8_standalone_command or spm8path or spm5path:
    configuration.save( neuroConfig.userOptionFile )
    context.write( '\noptions saved' )
    if spm8_standalone_command:
      context.write('=> spm8 standalone is configured.')
      spmpath = spm8_standalone_path
    elif spm8path:
      context.write('=> spm8 is now configured.')
      spmpath = spm8path
    else:
      context.write('=> spm5 is now configured.')
      spmpath = spm5path
  else:
    context.write("=> spm could not be found automatically, however "
                  "the path can be set manually in the menu " "BrainVISA/Preferences/SPM.")

  if spmpath:
    context.write( '\nSetting up SPM templates database' )
    spmtemplates = spmpath #os.path.join( spmpath, 'templates' )
    
    # remove previous spm databases if any
    for old_spmpath in [old_spm8_standalone_path, old_spm5path, old_spm8path]:
      if old_spmpath:
        old_spmtemplates = old_spmpath #os.path.join( old_spmpath, 'templates' )
        if neuroHierarchy.databases.hasDatabase( old_spmtemplates ):
          neuroHierarchy.databases.remove( old_spmtemplates )
          for settings in neuroConfig.dataPath:
            if settings.directory == old_spmtemplates:
              neuroConfig.dataPath.remove(settings)
              

    dbs = neuroConfig.DatabaseSettings( spmtemplates )
    dbs.expert_settings.ontology = 'spm'
    dbs.expert_settings.sqliteFileName = ':temporary:'
    dbs.expert_settings.uuid = 'a91fd1bf-48cf-4759-896e-afea136c0549'
    dbs.builtin = True
    neuroConfig.dataPath.insert( 1, dbs )
    db = neuroHierarchy.SQLDatabase( dbs.expert_settings.sqliteFileName, spmtemplates, 'spm', settings=dbs )
    neuroHierarchy.databases.add( db )
    db.clear()
    db.update( context=defaultContext() )
    neuroHierarchy.update_soma_workflow_translations()
