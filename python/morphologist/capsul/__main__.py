from __future__ import absolute_import
import sys
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
        self.events.activated.connect(self.update_pipeline_activation)
        self.btnUpdate.clicked.connect(self.update)
        
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
            self.events.addItem('%s %s:%s' % (activation, node, plug))
     
    def update_pipeline_activation(self,index):
        activations = self.activations[index.row()]
        for node in self.pipeline.all_nodes():
            node_name = node.full_name
            for plug_name, plug in node.plugs.iteritems():
                plug.activated = activations.get('%s:%s' % (node_name, plug_name), False)
            node.activated = activations.get('%s:' % node_name, False)
        
        # Refresh views relying on plugs and nodes selection
        for node in self.pipeline.all_nodes():
            if isinstance(node, PipelineNode):
                node.process.selection_changed = True

        
        
        
        
app = QtGui.QApplication(sys.argv)
mp = CustomMorphologist()
mpv = PipelineDevelopperView(mp, show_sub_pipelines=True, allow_open_controller=True)
ai = ActivationsInspector(mp,'/tmp/activations')
ai.show()
mpv.show()
app.exec_()