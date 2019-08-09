# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Any, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Any, Undefined

from capsul.api import Process
import six
from capsul.api import Pipeline
from capsul.api import Switch


class SulciLabelling(Pipeline):
    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        self._autoexport_nodes_parameters = autoexport_nodes_parameters
        super(SulciLabelling, self).__init__(False, **kwargs)
        del self._autoexport_nodes_parameters
#        if autoexport_nodes_parameters:
#            self.autoexport_nodes_parameters()

    def pipeline_definition(self):
        # nodes section
        self.add_switch('select_Sulci_Recognition', ['recognition2000', 'SPAM_recognition09', 'CNN_recognition19'], [
                        'output_graph'], output_types=[File(allowed_extensions=['.arg', '.data'])])
        self.add_process(
            'recognition2000', 'morphologist.capsul.axon.sulcilabellingann.SulciLabellingANN')
        self.nodes['recognition2000']._weak_outputs = True
        self.add_process(
            'SPAM_recognition09', 'morphologist.capsul.axon.sulcilabellingspam.SulciLabellingSPAM')
        self.nodes['SPAM_recognition09']._weak_outputs = True
        self.add_process(
            'CNN_recognition19', 'deepsulci.sulci_labeling.capsul.labeling.SulciDeepLabeling')
        self.nodes['CNN_recognition19']._weak_outputs = True

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
        self.add_link('data_graph->CNN_recognition19.graph')
        self.add_link(
            'recognition2000.output_graph->select_Sulci_Recognition.recognition2000_switch_output_graph')
        self.add_link(
            'SPAM_recognition09.output_graph->select_Sulci_Recognition.SPAM_recognition09_switch_output_graph')
        self.add_link(
            'CNN_recognition19.labeled_graph->select_Sulci_Recognition.CNN_recognition19_switch_output_graph')

        # initialization section
        self.nodes['select_Sulci_Recognition'].switch = 'SPAM_recognition09'
        # export orphan parameters
        if not hasattr(self, '_autoexport_nodes_parameters') \
                or self._autoexport_nodes_parameters:
            self.autoexport_nodes_parameters()

    def autoexport_nodes_parameters(self):
        '''export orphan and internal output parameters'''
        for node_name, node in six.iteritems(self.nodes):
            if node_name == '':
                continue  # skip main node
            if hasattr(node, '_weak_outputs'):
                weak_outputs = node._weak_outputs
            else:
                weak_outputs = False
            for parameter_name, plug in node.plugs.items():
                if parameter_name in ('nodes_activation', 'selection_changed'):
                    continue
                if (node_name, parameter_name) not in self.do_not_export:
                    if not plug.output and plug.links_from:
                        continue
                    weak_link = False
                    if plug.output:
                        if plug.links_to:  # or plug.links_from:
                            # some links exist
                            if [True for x in plug.links_to
                                    if x[0] == '' or isinstance(x[2], Switch)] \
                                    or \
                                    [True for x in plug.links_from
                                     if x[0] == '' or isinstance(x[2], Switch)]:
                                # a link to the main pipeline or to a switch
                                # already exists
                                continue
                            # links exist but not to the pipeline: export
                            # weak_link = True
                    if weak_outputs and plug.output:
                        weak_link = True
                    self.export_parameter(node_name, parameter_name,
                                          '_'.join(
                                              (node_name, parameter_name)),
                                          weak_link=weak_link, is_optional=True)
