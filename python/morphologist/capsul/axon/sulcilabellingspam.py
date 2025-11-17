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


class SulciLabellingSPAM(Pipeline):
    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        self._autoexport_nodes_parameters = autoexport_nodes_parameters
        super(SulciLabellingSPAM, self).__init__(False, **kwargs)
        del self._autoexport_nodes_parameters
#        if autoexport_nodes_parameters:
#            self.autoexport_nodes_parameters()


    def pipeline_definition(self):
        # nodes section
        self.add_process('global_recognition', 'morphologist.capsul.axon.sulcilabellingspamglobal.SulciLabellingSPAMGlobal')
        self.add_process('local_recognition', 'morphologist.capsul.axon.sulcilabellingspamlocal.SulciLabellingSPAMLocal')
        self.nodes['local_recognition']._weak_outputs = True
        self.add_process('markovian_recognition', 'morphologist.capsul.axon.sulcilabellingspammarkov.SulciLabellingSPAMMarkov')
        self.nodes['markovian_recognition']._weak_outputs = True

        # switches section
        self.add_switch('local_or_markovian', ['local_recognition', 'markovian_recognition'], ['output_graph'], output_types=[File(allowed_extensions=['.arg', '.data'])])

        # exports section
        # export input parameter
        self.export_parameter('global_recognition', 'data_graph', 'data_graph')
        # export output parameter
        self.export_parameter('local_or_markovian', 'output_graph', 'output_graph')
        # export input parameter
        self.export_parameter('markovian_recognition', 'fix_random_seed', 'fix_random_seed')
        # export input parameter
        self.export_parameter('global_recognition', 'labels_translation_map', 'global_recognition_labels_translation_map')
        # export input parameter
        self.export_parameter('global_recognition', 'labels_priors', 'global_recognition_labels_priors')
        # export input parameter
        self.export_parameter('global_recognition', 'initial_transformation', 'global_recognition_initial_transformation')

        # links section
        self.add_link('global_recognition.output_graph->output_graph')
        self.add_link('global_recognition.output_graph->local_recognition.data_graph')
        self.add_link('global_recognition.output_graph->markovian_recognition.data_graph')
        self.add_link('global_recognition_labels_translation_map->local_recognition.labels_translation_map')
        self.add_link('global_recognition_labels_translation_map->markovian_recognition.labels_translation_map')
        self.add_link('global_recognition_labels_priors->local_recognition.labels_priors')
        self.add_link('global_recognition_labels_priors->markovian_recognition.labels_priors')
        self.add_link('global_recognition_initial_transformation->local_recognition.initial_transformation')
        self.add_link('global_recognition_initial_transformation->markovian_recognition.initial_transformation')
        self.add_link('global_recognition.output_transformation->local_recognition.global_transformation')
        self.add_link('global_recognition.output_transformation->markovian_recognition.global_transformation')
        self.add_link('global_recognition_labels_translation_map->local_recognition.labels_translation_map')
        self.add_link('global_recognition_labels_priors->local_recognition.labels_priors')
        self.add_link('global_recognition_initial_transformation->local_recognition.initial_transformation')
        self.add_link('markovian_recognition.output_graph->local_or_markovian.markovian_recognition_switch_output_graph')
        self.add_link('local_recognition.output_graph->local_or_markovian.local_recognition_switch_output_graph')

        # initialization section
        if 'local_recognition' in self.nodes:
            self.local_or_markovian = 'local_recognition'
        # export orphan parameters
        if not hasattr(self, '_autoexport_nodes_parameters') \
                or self._autoexport_nodes_parameters:
            self.autoexport_nodes_parameters()


    def autoexport_nodes_parameters(self):
        '''export orphan and internal output parameters'''
        for node_name, node in self.nodes.items():
            if node_name == '':
                continue # skip main node
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
                        if plug.links_to: # or plug.links_from:
                            # some links exist
                            if [True for x in plug.links_to \
                                    if x[0]=='' or isinstance(x[2], Switch)] \
                                    or \
                                    [True for x in plug.links_from \
                                    if x[0]=='' or isinstance(x[2], Switch)]:
                                # a link to the main pipeline or to a switch
                                # already exists
                                continue
                            # links exist but not to the pipeline: export
                            # weak_link = True
                    if weak_outputs and plug.output:
                        weak_link = True
                    self.export_parameter(node_name, parameter_name,
                        '_'.join((node_name, parameter_name)),
                        weak_link=weak_link, is_optional=True)

