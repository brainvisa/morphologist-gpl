from __future__ import absolute_import
import sys
import re
from soma.qt_gui import qt_backend
qt_backend.set_qt_backend('PyQt4')
from soma.qt_gui.qt_backend import QtGui
from capsul.qt_gui.activation_inspector import ActivationInspector
from capsul.apps_qt.base.pipeline_widgets import PipelineDevelopperView
from morphologist.process.customized.morphologist import CustomMorphologist


app = QtGui.QApplication(sys.argv)
mp = CustomMorphologist()
mpv = PipelineDevelopperView(mp, show_sub_pipelines=True, allow_open_controller=True)
ai = ActivationInspector(mp,'/tmp/activations', mpv)
ai.show()
mpv.show()
app.exec_()