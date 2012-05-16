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
import urllib, os
try:
  from soma import zipfile
except:
  import zipfile
from brainvisa.data import neuroHierarchy
from brainvisa.data.neuroHierarchy import databases
from brainvisa.configuration import neuroConfig
from soma.wip.application.api import Application
from brainvisa.configuration import databases_configuration as dbconf

name = 'SPAM models installation'
userLevel = 0


signature = Signature(
  'download_url', String(),
  'install_talairach_models', Boolean(),
  'install_global_models', Boolean(),
  'install_local_models', Boolean(),
  'install_additional_models', Boolean(),
  'install_in_compatible_database', Choice(),
  'destination_database_directory', WriteDiskItem( 'Directory', 'Directory' ),
)

def initialization( self ):
  def linkDB( self, proc ):
    print 'linkDB'
    if self.destination_database_directory is not None:
      return -1
    chc = self.signature[ 'install_in_compatible_database' ].values
    if self.install_in_compatible_database == chc[ - 1 ][1]:
      return chc[0][1]
    return self.install_in_compatible_database
  self.download_url = 'ftp://ftp.cea.fr/pub/dsv/anatomist/data'
  self.install_talairach_models = True
  self.install_global_models = True
  self.install_local_models = True
  self.install_additional_models = True
  self.instll_in_brainvisa_distribution = True
  dbs = []
  for d in databases.iterDatabases():
    if os.path.basename( d.name ).startswith( 'brainvisa-share' ) \
      and d.name.startswith( neuroConfig.mainPath ):
      dbs.insert( 0, ( 'Internal database (recommended) ' \
        + os.path.basename( d.name ), d.directory ) )
    elif d.fso.name == 'shared':
      dbs.append( ( d.name, d.directory ) )
  dbs.append( ( 'New database directory', -1 ) )
  self.signature[ 'install_in_compatible_database' ] = Choice( *dbs )
  self.setOptional( 'destination_database_directory' )
  self.install_in_compatible_database = dbs[0][1]
  self.linkParameters( 'install_in_compatible_database',
    'destination_database_directory' , linkDB )


def addSharedDatabase( context, destdir ):
  dbs = neuroConfig.DatabaseSettings( destdir )
  dbs.expert_settings.ontology = 'shared'
  #dbs.expert_settings.sqliteFileName = os.path.join( destdir,
  #  'database-' + neuroHierarchy.databaseVersion  + '.sqlite' )
  dbs.builtin = False
  dbs.name = destdir
  neuroConfig.dataPath.append( dbs )
  db = neuroHierarchy.SQLDatabase( os.path.join( destdir,
    'database-' + neuroHierarchy.databaseVersion  + '.sqlite' ),
    destdir, 'shared', settings=dbs )
  neuroHierarchy.databases.add( db )
  app = Application()
  dbc = dbconf.DatabasesConfiguration.FileSystemOntology( destdir, True )
  try:
    writeMinf( os.path.join( destdir, 'database_settings.minf' ),
              ( dbs.expert_settings, ) )
  except IOError:
    pass
  app.configuration.databases.fso.append( dbc )
  app.configuration.save( neuroConfig.userOptionFile )
  db.clear()
  db.update( context=context )


def execution( self, context ):
  files = []
  modelsversion = '4.2'
  if self.install_in_compatible_database != -1:
    destdir = self.install_in_compatible_database
  else:
    destdir = self.destination_database_directory.fullPath()
    if not os.path.exists( destdir ):
      os.makedirs( destdir )
  context.write( 'install in dir:', destdir )

  if self.install_talairach_models:
    files.append( 'descriptive_models-talairach-' + modelsversion + '.zip' )
  if self.install_global_models:
    files.append( 'descriptive_models-global-' + modelsversion + '.zip' )
  if self.install_local_models:
    files.append( 'descriptive_models-local-' + modelsversion + '.zip' )
  if self.install_additional_models:
    files.append( 'descriptive_models-additional_data-' + modelsversion \
      + '.zip' )
  pnum = len( files ) * 100 + 10
  pgs = 0
  for fname in files:
    context.write( 'downloading', fname, '...' )
    context.progress( pgs, pnum, self )
    ftp = urllib.urlopen( self.download_url + '/' + fname )
    tzf = context.temporary( 'zip file' )
    f = open( tzf.fullPath(), 'wb' )
    fsize = long( ftp.headers.get( 'content-length' ) )
    chunksize = 100000
    fread = 0
    while fread < fsize:
      pg = fread * 80 / fsize
      context.progress( pgs + pg, pnum, self )
      f.write( ftp.read( chunksize ) )
      fread += chunksize
    context.write( 'download done' )
    f.close()
    pgs += 80
    context.progress( pgs, pnum, self )
    context.write( 'installing', fname, '...' )
    f = open( tzf.fullPath(), 'rb' )
    zf = zipfile.ZipFile( f, 'r' )
    # extract zip files one by one
    # extractall() is not an option since on Mac at least it tries to
    # re-make directories even if they exist
    namelist = zf.namelist()
    fnlist = []
    for name in namelist:
      dname = os.path.join( destdir, name )
      if os.path.exists( dname ):
        if os.path.isdir( dname ):
          pass # skip existing dirs
        else: # existing file: remove it first
          os.unlink( dname )
          fnlist.append( name )
      else:
        fnlist.append( name )
    del namelist
    zf.extractall( destdir, fnlist )
    pgs += 20
  context.progress( pgs, pnum, self )
  db = None
  for d in databases.iterDatabases():
    if d.directory == destdir:
      db = d
      break
  if db is None: # new database
    mainThreadActions().call( addSharedDatabase, context, destdir )
  else:
    mainThreadActions().call( db.update, context=context )
  context.progress( 100, 100, self )

