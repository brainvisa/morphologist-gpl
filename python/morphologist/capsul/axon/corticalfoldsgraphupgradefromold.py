# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
try:
    from pydantic.v1 import conlist
except ImportError:
    from pydantic import conlist
from capsul.api import Process
from capsul.api import Pipeline
from capsul.api import Switch


class CorticalFoldsGraphUpgradeFromOld(Pipeline):
    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        self._autoexport_nodes_parameters = autoexport_nodes_parameters
        super(CorticalFoldsGraphUpgradeFromOld, self).__init__(False, **kwargs)
        del self._autoexport_nodes_parameters
#        if autoexport_nodes_parameters:
#            self.autoexport_nodes_parameters()


    def pipeline_definition(self):
        # nodes section
        self.add_process('FoldGraphUpgradeStructure', 'morphologist.capsul.axon.foldgraphupgradestructure.foldgraphupgradestructure')
        self.add_process('SulciVoronoi', 'morphologist.capsul.axon.sulcivoronoi.sulcivoronoi')
        self.add_process('CorticalFoldsGraphThickness', 'morphologist.capsul.axon.corticalfoldsgraphthickness.CorticalFoldsGraphThickness')

        # exports section
        # export input parameter
        self.export_parameter('FoldGraphUpgradeStructure', 'old_graph', 'old_graph')
        # export input parameter
        self.export_parameter('FoldGraphUpgradeStructure', 'skeleton', 'skeleton')
        # export input parameter
        self.export_parameter('FoldGraphUpgradeStructure', 'graph_version', 'graph_version')
        # export output parameter
        self.export_parameter('FoldGraphUpgradeStructure', 'graph', 'graph')
        # export input parameter
        self.export_parameter('FoldGraphUpgradeStructure', 'commissure_coordinates', 'commissure_coordinates')
        # export input parameter
        self.export_parameter('FoldGraphUpgradeStructure', 'Talairach_transform', 'Talairach_transform')
        # export input parameter
        self.export_parameter('SulciVoronoi', 'hemi_cortex', 'SulciVoronoi_hemi_cortex')

        # links section
        self.add_link('FoldGraphUpgradeStructure.graph->SulciVoronoi.graph')
        self.add_link('FoldGraphUpgradeStructure.graph->CorticalFoldsGraphThickness.graph')
        self.add_link('CorticalFoldsGraphThickness.output_graph->graph')
        self.add_link('SulciVoronoi_hemi_cortex->CorticalFoldsGraphThickness.hemi_cortex')
        self.add_link('SulciVoronoi.sulci_voronoi->CorticalFoldsGraphThickness.sulci_voronoi')
        self.add_link('SulciVoronoi_hemi_cortex->CorticalFoldsGraphThickness.hemi_cortex')

        # initialization section
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

