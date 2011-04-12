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

import os, re
import neuroConfig
import neuroHierarchy
import distutils.spawn
from soma.wip.application.api import Application
import neuroProcesses
import subprocess
import glob

configuration = Application().configuration

# if FSL is present: setup a database for FSL templates
fsldir = os.getenv( 'FSLDIR' )
if not fsldir and distutils.spawn.find_executable( 'fslview' ):
  # probably a system-wide linux installation like on Ubuntu
  if os.path.isdir( '/usr/share/fsl/data' ):
    fsldir = '/usr/share/fsl'
    if not configuration.FSL.fsl_commands_prefix \
      and not distutils.spawn.find_executable( 'flirt' ):
        versions = [ v for v in os.listdir( os.path.join( fsldir ) ) \
          if v != 'data' ]
        versionsi = [ v.split( '.' ) for v in versions ]
        try:
          versionsi = [ int( v[0] ) * 0x100 + int( v[1] ) for v in versionsi ]
          version = versionsi.index( max( versionsi ) )
          fsl_prefix = 'fsl' + versions[ version ] + '-'
          if distutils.spawn.find_executable( fsl_prefix + 'flirt' ):
            configuration.FSL.fsl_commands_prefix = fsl_prefix
        except:
          print 'could not read FSL versions'
if fsldir and os.path.exists( fsldir ):
  fslshare = os.path.join( fsldir, 'data' )
  if os.path.exists( fslshare ):
    if fslshare not in [ x.directory for x in neuroConfig.dataPath ]:
      dbs = neuroConfig.DatabaseSettings( fslshare )
      fsldb = os.path.join( neuroConfig.homeBrainVISADir, 'fsl' )
      if not os.path.exists( fsldb ):
        os.mkdir( fsldb )
      dbs.expert_settings.ontology = 'fsl'
      dbs.expert_settings.sqliteFileName = ":memory:"#os.path.join( fsldb, 'fsl.sqlite' )
      dbs.builtin = True
      neuroConfig.dataPath.insert( 1, dbs )
      db = neuroHierarchy.SQLDatabase( dbs.expert_settings.sqliteFileName,
        fslshare, 'fsl' )
      db.uuid = getattr( dbs.expert_settings, 'uuid', 'a69ed62b-4895-4245-b42a-d211e1c6faa4' )
      neuroHierarchy.databases.add( db )
      db.clear()
      db.update( context=defaultContext() )
      del dbs, db, fsldb
  del fslshare
del fsldir

# if Matlab and SPM are found: setup a database for SPM templates

spmscript = None
spmdir = None

if configuration.SPM.spm5_path == '' and configuration.SPM.check_spm_path:
  mexe = distutils.spawn.find_executable( \
    configuration.matlab.executable )
  c = neuroProcesses.defaultContext()
  mscfile = c.temporary( 'Matlab Script' )
  spmf = c.temporary( 'Text File' )
  mscfn = mscfile.fullPath()
  mscript = '''a = which( 'spm5' );
if ~isempty( a )
  spm5;
end
spmpath = which( 'spm' );
f = fopen( ''' + "'" + spmf.fullPath() + "'" + ''', 'w' );
fprintf( f, '%s\\n', spmpath );
exit;
'''
  open( mscfn, 'w' ).write( mscript )
  print mscfn
  pd = os.getcwd()
  os.chdir( os.path.dirname( mscfn ) )
  cmd = [ mexe ] + configuration.matlab.options.split() \
    + [ '-r', os.path.basename( mscfile.fullName() ) ]
  # print 'running matlab command:', cmd
  try:
    subprocess.check_call( cmd )
    spmscript = open( spmf.fullPath() ).read().strip()
    spmpath = os.path.dirname( spmscript )
    configuration.SPM.spm5_path = spmpath
    configuration.save( neuroConfig.userOptionFile )
    del spmscript
  except Exception, e:
    print 'could not run Matlab script:', e
  os.chdir( pd )
  del mexe, mscfn, mscript, spmf, mscfile, c, cmd, pd

if configuration.SPM.spm5_path:
  spmdir = configuration.SPM.spm5_path
  # print 'SPM dir:', spmdir
  spmtemplates = os.path.join( spmdir, 'templates' )
  #print 'spmtemplates:', spmtemplates
  dbs = neuroConfig.DatabaseSettings( spmtemplates )
  spmdb = os.path.join( neuroConfig.homeBrainVISADir, 'spm' )
  if not os.path.exists( spmdb ):
    os.mkdir( spmdb )
  dbs.expert_settings.ontology = 'spm'
  dbs.expert_settings.sqliteFileName = ":memory:"
  dbs.builtin = True
  neuroConfig.dataPath.insert( 1, dbs )
  db = neuroHierarchy.SQLDatabase( dbs.expert_settings.sqliteFileName,
    spmtemplates, 'spm' )
  db.uuid = getattr( dbs.expert_settings, 'uuid', 'a91fd1bf-48cf-4759-896e-afea136c0549')
  neuroHierarchy.databases.add( db )
  db.clear()
  db.update( context=defaultContext() )
  del dbs, db, spmtemplates, spmdir

