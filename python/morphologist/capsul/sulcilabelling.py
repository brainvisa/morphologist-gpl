# -*- coding: utf-8 -*-
from __future__ import absolute_import

from morphologist.capsul.axon import sulcilabelling

try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

class SulciLabelling(sulcilabelling.SulciLabelling):

    def pipeline_definition(self):
        try:
            self.add_process(
                'CNN_recognition19', 'deepsulci.sulci_labeling.capsul.labeling.SulciDeepLabeling')
            self.nodes['CNN_recognition19']._weak_outputs = True
            cnn = True
        except:
            cnn = False
        # nodes section
        if cnn:
            self.add_switch('select_Sulci_Recognition', ['recognition2000', 'SPAM_recognition09', 'CNN_recognition19'], [
                            'output_graph'], output_types=[File(allowed_extensions=['.arg', '.data'])])
        else:
            self.add_switch('select_Sulci_Recognition', ['recognition2000', 'SPAM_recognition09'], [
                            'output_graph'], output_types=[File(allowed_extensions=['.arg', '.data'])])
        self.add_process(
            'recognition2000', 'morphologist.capsul.axon.sulcilabellingann.SulciLabellingANN')
        self.nodes['recognition2000']._weak_outputs = True
        self.add_process(
            'SPAM_recognition09', 'morphologist.capsul.axon.sulcilabellingspam.SulciLabellingSPAM')
        self.nodes['SPAM_recognition09']._weak_outputs = True

        # exports section
        # export input parameter
        self.export_parameter('SPAM_recognition09', 'data_graph', 'data_graph')
        # export output parameter
        self.export_parameter('select_Sulci_Recognition',
                              'output_graph', 'output_graph')
        # export input parameter
        self.export_parameter(
            'recognition2000', 'fix_random_seed', 'fix_random_seed')

        # links section
        self.add_link('fix_random_seed->SPAM_recognition09.fix_random_seed')
        self.add_link('data_graph->recognition2000.data_graph')
        if cnn:
            self.add_link('data_graph->CNN_recognition19.graph')
        self.add_link(
            'recognition2000.output_graph->select_Sulci_Recognition.recognition2000_switch_output_graph')
        self.add_link(
            'SPAM_recognition09.output_graph->select_Sulci_Recognition.SPAM_recognition09_switch_output_graph')
        if cnn:
            self.add_link(
                'CNN_recognition19.labeled_graph->select_Sulci_Recognition.CNN_recognition19_switch_output_graph')

        # initialization section
        self.nodes['select_Sulci_Recognition'].switch = 'SPAM_recognition09'
        # export orphan parameters
        if not hasattr(self, '_autoexport_nodes_parameters') \
                or self._autoexport_nodes_parameters:
            self.autoexport_nodes_parameters()

