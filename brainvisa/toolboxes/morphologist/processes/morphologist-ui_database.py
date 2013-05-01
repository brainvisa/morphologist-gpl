from brainvisa.processes import *
from brainvisa.processing.qtgui.backwardCompatibleQt import *

def validation():
  muiexe = findInPath( 'morphologist-ui.py' )
  if not muiexe:
    raise ValidationError( 'morphologist-ui.py program is not found' )

name = 'Morphologist UI 2013, run on database'
userLevel = 0

signature = Signature(
  'database', Choice(),
)


def initialization(self):
  databases=[(dbs.directory, neuroHierarchy.databases.database(dbs.directory)) for dbs in neuroConfig.dataPath if dbs.expert_settings.ontology=='brainvisa-3.1.0' ]
  self.signature['database'].setChoices(*databases)
  if databases:
    self.database=databases[0][1]
  else:
    self.database=None


def runinthread( self ):
  muiexe = os.path.join( findInPath( 'morphologist-ui.py' ), 
    'morphologist-ui.py' )
  print self.database.directory
  print type( self.database )
  defaultContext().system( sys.executable, muiexe, 
    '-i', self.database.directory )


def execution( self, context ):
  thread = threading.Thread( target = self.runinthread )
  thread.start()

