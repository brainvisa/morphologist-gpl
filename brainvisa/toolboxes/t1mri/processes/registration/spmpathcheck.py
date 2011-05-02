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
  self.perform_check = configuration.SPM.check_spm_path

def inlineGUI( self, values, pview, parent, externalRunButton=False ):
  from PyQt4 import QtGui
  import neuroProcessesGUI
  vb = QtGui.QWidget()
  lay = QtGui.QVBoxLayout( vb )
  lay.addWidget( neuroProcessesGUI.ProcessView.defaultInlineGUI( pview, vb,
    externalRunButton, None ) )
  lay.addWidget( QtGui.QLabel( \
    _t_( 'The SPM5 path has not been setup in the configuration.\nCurrently, processes using SPM might not work,\nand the SPM database (normalization templates...) cannot be used.\nThis process can try to detect it and set it in the configuration.\nYou should re-open any process depending on SPM afterwards.\n\nIf this process fails for any reason, you can set the path manually in the Preferences.' ),
    vb ) )
  return vb

def execution( self, context ):
  configuration = Application().configuration

  if self.perform_check == False:
    configuration.SPM.check_spm_path = False

  if not configuration.SPM.check_spm_path:
    return None # don't check, do nothing.

  if configuration.SPM.spm5_path is not None \
    and configuration.SPM.spm5_path != "":
      context.write( 'SPM path is already set.' )
      return

  spmscript = None

  mexe = distutils.spawn.find_executable( \
    configuration.matlab.executable )
  mscfile = context.temporary( 'Matlab Script' )
  spmf = context.temporary( 'Text File' )
  mscfn = mscfile.fullPath()
  mscript = '''try
  a = which( 'spm5' );
  if ~isempty( a )
    try
      spm5;
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
  spmscript = open( spmf.fullPath() ).read().strip()
  spmpath = os.path.dirname( spmscript )
  configuration.SPM.spm5_path = spmpath
  context.write( 'found SPM path:', spmpath )
  configuration.save( neuroConfig.userOptionFile )
  context.write( 'options saved' )
  del spmscript
  os.chdir( pd )
  del mexe, mscfn, mscript, spmf, mscfile, c, cmd, pd

  if configuration.SPM.spm5_path:
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
    db.uuid = getattr( dbs.expert_settings, 'uuid', 'a91fd1bf-48cf-4759-896e-afea136c0549')
    neuroHierarchy.databases.add( db )
    db.clear()
    db.update( context=defaultContext() )

