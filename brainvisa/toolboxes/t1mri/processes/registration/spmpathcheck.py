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
import neuroConfig, neuroHierarchy

def validation():
  configuration = Application().configuration
  if not distutils.spawn.find_executable( \
    configuration.matlab.executable ):
    raise ValidationError( 'matlab is not found' )

name = 'SPM path check'
userLevel = 2

signature = Signature(
  'perform_check', Choice( ( 'check it', True ),
    ( 'don\'t ask again', False ) ),
)


def initialization( self ):
  configuration = Application().configuration
  configuration.SPM._spmpath_checked = True # avoid opening this several times
  self.perform_check = configuration.SPM.check_spm_path

def inlineGUI( self, values, pview, parent, externalRunButton=False ):
  from PyQt4 import QtGui
  import neuroProcessesGUI
  vb = QtGui.QWidget()
  lay = QtGui.QVBoxLayout( vb )
  lay.addWidget( neuroProcessesGUI.ProcessView.defaultInlineGUI( pview, vb,
    externalRunButton, None ) )
  lay.addWidget( QtGui.QLabel( \
    _t_( 'The SPM paths have not been setup in the configuration.\nCurrently, processes using SPM might not work,\nand the SPM database (normalization templates...) cannot be used.\nThis process can try to detect it and set it in the configuration.\nYou should re-open any process depending on SPM afterwards.\n\nIf this process fails for any reason, you can set the path manually in the Preferences.' ),
    vb ) )
  return vb

def checkSPMCommand( context, cmd ):
  configuration = Application().configuration
  spmscript = None
  mexe = distutils.spawn.find_executable( \
    configuration.matlab.executable )
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
  # print 'running matlab command:', cmd
  context.system( *cmd )
  os.chdir( pd )
  spmscript = open( spmf.fullPath() ).read().strip()
  spmpath = os.path.dirname( spmscript )
  return spmpath


def execution( self, context ):
  configuration = Application().configuration

  if self.perform_check == False:
    configuration.SPM.check_spm_path = False

  if not configuration.SPM.check_spm_path:
    return None # don't check, do nothing.

  if ( configuration.SPM.spm5_path is not None \
    and configuration.SPM.spm5_path != "" ) \
    or ( configuration.SPM.spm8_path is not None \
    and configuration.SPM.spm8_path != "" ):
      context.write( 'SPM path is already set.' )
      return

  spm8path = self.checkSPMCommand( context, 'spm8' )
  if spm8path:
    configuration.SPM.spm8_path = spm8path
    context.write( 'found SPM8 path:', spm8path )

  spm5path = self.checkSPMCommand( context, 'spm5' )
  if spm5path:
    configuration.SPM.spm5_path = spm5path
    context.write( 'found SPM5 path:', spm5path )
  spmpath = None
  if spm8path or spm5path:
    configuration.save( neuroConfig.userOptionFile )
    context.write( 'options saved' )
    if spm8path:
      spmpath = spm8path
    else:
      spmpath = spm5path

  if spmpath:
    context.write( 'setting up SPM templates database' )
    spmtemplates = os.path.join( spmpath, 'templates' )
    dbs = neuroConfig.DatabaseSettings( spmtemplates )
    spmdb = os.path.join( neuroConfig.homeBrainVISADir, 'spm' )
    if not os.path.exists( spmdb ):
      os.mkdir( spmdb )
    dbs.expert_settings.ontology = 'spm'
    dbs.expert_settings.sqliteFileName = ":memory:"
    dbs.builtin = True
    neuroConfig.dataPath.insert( 1, dbs )
    db = neuroHierarchy.SQLDatabase( dbs.expert_settings.sqliteFileName, spmtemplates, 'spm' )
    db.uuid = dbs.expert_settings.uuid
    neuroHierarchy.databases.add( db )
    db.clear()
    db.update( context=defaultContext() )
    neuroHierarchy.update_soma_workflow_translations()
