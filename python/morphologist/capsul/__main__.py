from __future__ import absolute_import
import sys
import re
from soma.qt_gui import qt_backend
qt_backend.set_qt_backend('PyQt4')
from PyQt4 import QtGui
from capsul.apps_qt.base.pipeline_widgets import PipelineDevelopperView
from morphologist.process.customized.morphologist import CustomMorphologist



import os, re
from PyQt4 import QtGui
from PyQt4.uic import loadUi
from capsul.pipeline.pipeline_nodes import PipelineNode

class ActivationsInspector(QtGui.QWidget):
    def __init__(self, pipeline, file, parent=None):
        super(ActivationsInspector, self).__init__(parent)
        ui = os.path.join(os.path.dirname(__file__),'activations_inspector.ui')
        loadUi(ui,self)
        self.pipeline = pipeline
        self.file = file
        self.pipeline._debug_activations = self.file
        self.pipeline.update_nodes_and_plugs_activation()
        self.update()
        self.events.currentRowChanged.connect(self.update_pipeline_activation)
        self.btnUpdate.clicked.connect(self.update)
        self.next.clicked.connect(self.find_next)
        self.previous.clicked.connect(self.find_previous)
        
    def update(self):
        f = open(self.file)
        pipeline_name = f.readline().strip()
        if pipeline_name != self.pipeline.id:
            raise ValueError('"%s" recorded activations for pipeline "%s" but not for "%s"' % (self.file, pipeline_name, self.pipeline.id))
        self.activations = []
        current_activations = {}
        self.events.clear()
        parser=re.compile(r'(\d+)([+-=])([^:]*)(:([a-zA-Z_0-9]+))?')
        for i in f.readlines():
            iteration, activation, node, x, plug = parser.match(i.strip()).groups()
            if activation == '+':
                current_activations['%s:%s' % (node,plug or '')] = True
            else:
                del current_activations['%s:%s' % (node,plug or '')]
            self.activations.append(current_activations.copy())
            self.events.addItem('%s %s:%s' % (activation, node, plug or ''))
        self.events.setCurrentRow(self.events.count()-1)
    
    def update_pipeline_activation(self,index):
        activations = self.activations[self.events.currentRow()]
        for node in self.pipeline.all_nodes():
            node_name = node.full_name
            for plug_name, plug in node.plugs.iteritems():
                plug.activated = activations.get('%s:%s' % (node_name, plug_name), False)
            node.activated = activations.get('%s:' % node_name, False)
        
        # Refresh views relying on plugs and nodes selection
        for node in self.pipeline.all_nodes():
            if isinstance(node, PipelineNode):
                node.process.selection_changed = True

    def find_next(self):
        pattern = re.compile(self.pattern.text())
        i = self.events.currentRow() + 1
        while i < self.events.count():
            if pattern.search(self.events.item(i).text()):
                self.events.setCurrentRow(i)
                break
            i += 1
        
    def find_previous(self):
        pattern = re.compile(self.pattern.text())
        i = self.events.currentRow() - 1
        while i > 0:
            if pattern.search(self.events.item(i).text()):
                self.events.setCurrentRow(i)
                break
            i -= 1
        
        
def plug_clicked(plug_name):
    ai.pattern.setText(plug_name)

app = QtGui.QApplication(sys.argv)
mp = CustomMorphologist()
mpv = PipelineDevelopperView(mp, show_sub_pipelines=True, allow_open_controller=True)
mpv.plug_clicked.connect(plug_clicked)
ai = ActivationsInspector(mp,'/tmp/activations')
ai.show()
mpv.show()
app.exec_()