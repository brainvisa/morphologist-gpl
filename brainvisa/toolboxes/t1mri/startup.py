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

# if FSL is present: setup a database for FSL templates
fsldir = os.getenv( 'FSLDIR' )
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

spm = 'spm5.m'
spmscript = None
for p in neuroConfig.matlabPath:
  if os.path.exists( os.path.join( p, spm ) ):
    spmscript = os.path.join( p, spm )
    break
if not spmscript:
  for p in neuroConfig.matlabPath:
    if os.path.exists( os.path.join( p, 'spm.m' ) ):
      spmscript = os.path.join( p, 'spm.m' )
      break
if not spmscript:
  mexe = distutils.spawn.find_executable( neuroConfig.matlabExecutable )
  #if not mexe:
    #print 'matlab executable not found'
  if mexe:
    #print mexe
    mexe2 = None
    mre = re.compile( '^\s*MATLAB\s*=\s*(.*)$' )
    for l in open( mexe ).xreadlines():
      x = mre.match( l )
      if x:
        mexe2 = x.group(1)
        if os.path.exists(mexe2):
          break
        else:
          mexe2=None
    if mexe2 is None:
      mexe2 = mexe
    mexe2 = os.path.realpath( mexe2 )
    #print mexe2
    del mexe, mre
    mdir = os.path.dirname( mexe2 )
    if os.path.basename( mdir ) == 'bin':
      mdir = os.path.dirname( mdir )
    #print 'matlab dir:', mdir
    del mexe2
    mtoolbox = os.path.join( mdir, 'toolbox', 'local' )
    #print mtoolbox
    spmscript = os.path.join( mtoolbox, spm )
    #print spmscript
    if not os.path.exists( spmscript ):
      spmscript = os.path.join( mtoolbox, 'spm.m' )
      if not os.path.exists( spmscript ):
        #print 'spm script not found'
        spmscript=None
    del mtoolbox, mdir
    if spmscript:
      spmscript = os.path.realpath( spmscript )
      #print 'spm script:', spmscript
      pre = re.compile( '^\s*.*path\s*\(\s*\'([^\']*)\'' )
      spmdir = None
      for l in open( spmscript ).xreadlines():
        x = pre.match( l )
        if x:
          #print l, x.groups()
          spmdir = x.group(1)
      del pre
      if spmdir is None:
        spmdir = os.path.dirname( spmscript )
      #print 'SPM dir:', spmdir
if spmscript:
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
  del dbs, db, spmtemplates

del spmscript
del spm
