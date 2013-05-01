from brainvisa.processes import *
from brainvisa.processing.qtgui.backwardCompatibleQt import *

def validation():
  muiexe = findInPath( 'morphologist-ui.py' )
  if not muiexe:
    raise ValidationError( 'morphologist-ui.py program is not found' )

name = 'Morphologist UI 2013'
userLevel = 0

def overrideGUI( self ):
  muiexe = os.path.join( findInPath( 'morphologist-ui.py' ), 
    'morphologist-ui.py' )
  defaultContext().system( sys.executable, muiexe )
  w = QWidget( None )
  w.setAttribute( Qt.WA_DeleteOnClose )
  QTimer.singleShot( 0, w.close )
  return w

