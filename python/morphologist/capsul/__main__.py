from __future__ import print_function
from __future__ import absolute_import
import sys
import re
from soma.qt_gui import qt_backend
qt_backend.set_qt_backend(compatible_qt5=True)
from soma.qt_gui.qt_backend import QtGui
from capsul.qt_gui.widgets.activation_inspector import ActivationInspector
from capsul.pipeline import Pipeline
from capsul.qt_gui.widgets import PipelineDevelopperView
from morphologist.capsul.morphologist import Morphologist

Pipeline.hide_nodes_activation = False


app = QtGui.QApplication(sys.argv)

#import cProfile, pstats
#cProfile.run('''mp = CustomMorphologist()
#import cPickle as pickle
#print(mp)
#pickled = pickle.dumps(mp)
#for i in range(100):
  #mp = pickle.loads(pickled)
  ##mp = CustomMorphologist()
##''','/tmp/stats')
#p = pstats.Stats('/tmp/stats')
#p.sort_stats('time').print_stats(4)

mp = Morphologist()
#import pickle
#print(mp)
#pickled = pickle.dumps(mp)
#for i in range(100):
  #mp = pickle.loads(pickled)
  ##mp = CustomMorphologist()
  #print(i)
mpv = PipelineDevelopperView(mp, show_sub_pipelines=True,
                             allow_open_controller=True, enable_edition=True)
ai = ActivationInspector(mp, record_file='/tmp/activations',
                         developper_view=mpv)
ai.show()
mpv.show()
app.exec_()
