# -*- coding: utf-8 -*-
try:
    from traits.api import File, Directory, Float, Int, Bool, Enum, Str, \
        List, Undefined
except ImportError:
    from enthought.traits.api import File, Directory, Float, Int, Bool, Enum, \
        Str, List, Undefined

from capsul.process import Process
from capsul.pipeline import Pipeline
from capsul.pipeline import Switch


class morphologist(Pipeline):
    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        self._autoexport_nodes_parameters = autoexport_nodes_parameters
        super(morphologist, self).__init__(False, **kwargs)
        del self._autoexport_nodes_parameters
#        if autoexport_nodes_parameters:
#            self.autoexport_nodes_parameters()


    def pipeline_definition(self):
        # nodes section
        self.add_process('PrepareSubject', 'morphologist.capsul.acpcOrNormalization.acpcOrNormalization')
        self.add_process('BiasCorrection', 'morphologist.capsul.T1BiasCorrection.T1BiasCorrection')
        self.add_process('HistoAnalysis', 'morphologist.capsul.NobiasHistoAnalysis.NobiasHistoAnalysis')
        self.add_process('BrainSegmentation', 'morphologist.capsul.BrainSegmentation.BrainSegmentation')
        self.add_process('Renorm', 'morphologist.capsul.normalization_skullstripped.normalization_skullstripped')
        self.add_process('SplitBrain', 'morphologist.capsul.SplitBrain.SplitBrain')
        self.add_process('TalairachTransformation', 'morphologist.capsul.TalairachTransformation.TalairachTransformation')
        self.add_process('HeadMesh', 'morphologist.capsul.headMesh.headMesh')
        self.add_process('GreyWhiteClassification', 'morphologist.capsul.GreyWhiteClassificationHemi.GreyWhiteClassificationHemi')
        self.add_process('GreyWhiteTopology', 'morphologist.capsul.GreyWhiteTopology.GreyWhiteTopology')
        self.add_process('GreyWhiteMesh', 'morphologist.capsul.GreyWhiteMesh.GreyWhiteMesh')
        self.add_process('SulciSkeleton', 'morphologist.capsul.sulciskeleton.sulciskeleton')
        self.add_process('PialMesh', 'morphologist.capsul.hemispheremesh.hemispheremesh')
        self.add_process('CorticalFoldsGraph', 'morphologist.capsul.corticalfoldsgraph.corticalfoldsgraph')
        self.add_process('SulciRecognition', 'morphologist.capsul.recognitionGeneral.recognitionGeneral')
        self.add_process('GreyWhiteClassification_1', 'morphologist.capsul.GreyWhiteClassificationHemi.GreyWhiteClassificationHemi')
        self.add_process('GreyWhiteTopology_1', 'morphologist.capsul.GreyWhiteTopology.GreyWhiteTopology')
        self.add_process('GreyWhiteMesh_1', 'morphologist.capsul.GreyWhiteMesh.GreyWhiteMesh')
        self.add_process('SulciSkeleton_1', 'morphologist.capsul.sulciskeleton.sulciskeleton')
        self.add_process('PialMesh_1', 'morphologist.capsul.hemispheremesh.hemispheremesh')
        self.add_process('CorticalFoldsGraph_1', 'morphologist.capsul.corticalfoldsgraph.corticalfoldsgraph')
        self.add_process('SulciRecognition_1', 'morphologist.capsul.recognitionGeneral.recognitionGeneral')

        # exports section
        # export input parameter
        self.export_parameter('PrepareSubject', 'T1mri', 't1mri')
        # export input parameter
        self.export_parameter('PrepareSubject', 'StandardACPC_Anterior_Commissure', 'anterior_commissure')
        # export input parameter
        self.export_parameter('PrepareSubject', 'StandardACPC_Posterior_Commissure', 'posterior_commissure')
        # export input parameter
        self.export_parameter('PrepareSubject', 'StandardACPC_Interhemispheric_Point', 'interhemispheric_point')
        # export input parameter
        self.export_parameter('PrepareSubject', 'StandardACPC_Left_Hemisphere_Point', 'left_hemisphere_point')
        # export output parameter
        self.export_parameter('BiasCorrection', 't1mri_nobias', 't1mri_nobias')
        # export output parameter
        self.export_parameter('HistoAnalysis', 'histo_analysis', 'histo_analysis')
        # export output parameter
        self.export_parameter('SplitBrain', 'split_brain', 'split_brain')
        # export output parameter
        self.export_parameter('CorticalFoldsGraph', 'graph', 'left_graph')
        # export output parameter
        self.export_parameter('CorticalFoldsGraph_1', 'graph', 'right_graph')
        # export output parameter
        self.export_parameter('SulciRecognition', 'output_graph', 'left_labelled_graph')
        # export output parameter
        self.export_parameter('SulciRecognition_1', 'output_graph', 'right_labelled_graph')
        # export output parameter
        self.export_parameter('Renorm', 'TalairachFromNormalization_commissure_coordinates', 'Renorm_TalairachFromNormalization_commissure_coordinates')
        # export input parameter
        self.export_parameter('CorticalFoldsGraph', 'graph_version', 'CorticalFoldsGraph_graph_version')

        # links section
        self.add_link('t1mri->BiasCorrection.t1mri')
        self.add_link('t1mri->Renorm.t1mri')
        self.add_link('SplitBrain.split_brain->CorticalFoldsGraph.split_brain')
        self.add_link('SplitBrain.split_brain->CorticalFoldsGraph_1.split_brain')
        self.add_link('PrepareSubject.commissure_coordinates->BiasCorrection.commissure_coordinates')
        self.add_link('PrepareSubject.commissure_coordinates->BrainSegmentation.commissure_coordinates')
        self.add_link('PrepareSubject.commissure_coordinates->Renorm_TalairachFromNormalization_commissure_coordinates')
        self.add_link('PrepareSubject.commissure_coordinates->SplitBrain.commissure_coordinates')
        self.add_link('PrepareSubject.commissure_coordinates->TalairachTransformation.commissure_coordinates')
        self.add_link('PrepareSubject.commissure_coordinates->GreyWhiteClassification.commissure_coordinates')
        self.add_link('PrepareSubject.commissure_coordinates->GreyWhiteClassification_1.commissure_coordinates')
        self.add_link('PrepareSubject.commissure_coordinates->CorticalFoldsGraph.commissure_coordinates')
        self.add_link('PrepareSubject.commissure_coordinates->CorticalFoldsGraph_1.commissure_coordinates')
        self.add_link('BiasCorrection.white_ridges->HistoAnalysis.white_ridges')
        self.add_link('BiasCorrection.white_ridges->BrainSegmentation.white_ridges')
        self.add_link('BiasCorrection.white_ridges->SplitBrain.white_ridges')
        self.add_link('BiasCorrection.hfiltered->HistoAnalysis.hfiltered')
        self.add_link('BiasCorrection.edges->BrainSegmentation.edges')
        self.add_link('BiasCorrection.edges->GreyWhiteClassification.edges')
        self.add_link('BiasCorrection.edges->GreyWhiteClassification_1.edges')
        self.add_link('BiasCorrection.t1mri_nobias->HistoAnalysis.t1mri_nobias')
        self.add_link('BiasCorrection.t1mri_nobias->BrainSegmentation.t1mri_nobias')
        self.add_link('BiasCorrection.t1mri_nobias->SplitBrain.t1mri_nobias')
        self.add_link('BiasCorrection.t1mri_nobias->HeadMesh.t1mri_nobias')
        self.add_link('BiasCorrection.t1mri_nobias->GreyWhiteClassification.t1mri_nobias')
        self.add_link('BiasCorrection.t1mri_nobias->GreyWhiteClassification_1.t1mri_nobias')
        self.add_link('BiasCorrection.t1mri_nobias->GreyWhiteTopology.t1mri_nobias')
        self.add_link('BiasCorrection.t1mri_nobias->GreyWhiteTopology_1.t1mri_nobias')
        self.add_link('BiasCorrection.t1mri_nobias->SulciSkeleton.t1mri_nobias')
        self.add_link('BiasCorrection.t1mri_nobias->SulciSkeleton_1.t1mri_nobias')
        self.add_link('BiasCorrection.t1mri_nobias->PialMesh.t1mri_nobias')
        self.add_link('BiasCorrection.t1mri_nobias->PialMesh_1.t1mri_nobias')
        self.add_link('BiasCorrection.variance->BrainSegmentation.variance')
        self.add_link('HistoAnalysis.histo_analysis->BrainSegmentation.histo_analysis')
        self.add_link('HistoAnalysis.histo_analysis->SplitBrain.histo_analysis')
        self.add_link('HistoAnalysis.histo_analysis->HeadMesh.histo_analysis')
        self.add_link('HistoAnalysis.histo_analysis->GreyWhiteClassification.histo_analysis')
        self.add_link('HistoAnalysis.histo_analysis->GreyWhiteClassification_1.histo_analysis')
        self.add_link('HistoAnalysis.histo_analysis->GreyWhiteTopology.histo_analysis')
        self.add_link('HistoAnalysis.histo_analysis->GreyWhiteTopology_1.histo_analysis')
        self.add_link('BrainSegmentation.brain_mask->Renorm.brain_mask')
        self.add_link('BrainSegmentation.brain_mask->SplitBrain.brain_mask')
        self.add_link('SplitBrain.split_brain->TalairachTransformation.split_mask')
        self.add_link('SplitBrain.split_brain->GreyWhiteClassification.split_brain')
        self.add_link('SplitBrain.split_brain->GreyWhiteClassification_1.split_brain')
        self.add_link('TalairachTransformation.Talairach_transform->CorticalFoldsGraph.talairach_transform')
        self.add_link('TalairachTransformation.Talairach_transform->CorticalFoldsGraph_1.talairach_transform')
        self.add_link('GreyWhiteClassification.grey_white->GreyWhiteTopology.grey_white')
        self.add_link('GreyWhiteClassification.grey_white->SulciSkeleton.grey_white')
        self.add_link('GreyWhiteClassification.grey_white->PialMesh.grey_white')
        self.add_link('GreyWhiteClassification.grey_white->CorticalFoldsGraph.grey_white')
        self.add_link('GreyWhiteTopology.hemi_cortex->GreyWhiteMesh.hemi_cortex')
        self.add_link('GreyWhiteTopology.hemi_cortex->SulciSkeleton.hemi_cortex')
        self.add_link('GreyWhiteTopology.hemi_cortex->PialMesh.hemi_cortex')
        self.add_link('GreyWhiteTopology.hemi_cortex->CorticalFoldsGraph.hemi_cortex')
        self.add_link('GreyWhiteMesh.white_mesh->CorticalFoldsGraph.white_mesh')
        self.add_link('SulciSkeleton.skeleton->PialMesh.skeleton')
        self.add_link('SulciSkeleton.skeleton->CorticalFoldsGraph.skeleton')
        self.add_link('SulciSkeleton.roots->CorticalFoldsGraph.roots')
        self.add_link('PialMesh.pial_mesh->CorticalFoldsGraph.pial_mesh')
        self.add_link('CorticalFoldsGraph_graph_version->CorticalFoldsGraph_1.graph_version')
        self.add_link('CorticalFoldsGraph.graph->SulciRecognition.data_graph')
        self.add_link('GreyWhiteClassification_1.grey_white->GreyWhiteTopology_1.grey_white')
        self.add_link('GreyWhiteClassification_1.grey_white->SulciSkeleton_1.grey_white')
        self.add_link('GreyWhiteClassification_1.grey_white->PialMesh_1.grey_white')
        self.add_link('GreyWhiteClassification_1.grey_white->CorticalFoldsGraph_1.grey_white')
        self.add_link('GreyWhiteTopology_1.hemi_cortex->GreyWhiteMesh_1.hemi_cortex')
        self.add_link('GreyWhiteTopology_1.hemi_cortex->SulciSkeleton_1.hemi_cortex')
        self.add_link('GreyWhiteTopology_1.hemi_cortex->PialMesh_1.hemi_cortex')
        self.add_link('GreyWhiteTopology_1.hemi_cortex->CorticalFoldsGraph_1.hemi_cortex')
        self.add_link('GreyWhiteMesh_1.white_mesh->CorticalFoldsGraph_1.white_mesh')
        self.add_link('SulciSkeleton_1.skeleton->PialMesh_1.skeleton')
        self.add_link('SulciSkeleton_1.skeleton->CorticalFoldsGraph_1.skeleton')
        self.add_link('SulciSkeleton_1.roots->CorticalFoldsGraph_1.roots')
        self.add_link('PialMesh_1.pial_mesh->CorticalFoldsGraph_1.pial_mesh')
        self.add_link('CorticalFoldsGraph_graph_version->CorticalFoldsGraph_1.graph_version')
        self.add_link('CorticalFoldsGraph_1.graph->SulciRecognition_1.data_graph')

        # initialization section
        self.nodes_activation.TalairachTransformation = False
        self.nodes_activation.SulciRecognition = False
        self.nodes_activation.SulciRecognition_1 = False
        # export orphan parameters
        if not hasattr(self, '_autoexport_nodes_parameters') \
                or self._autoexport_nodes_parameters:
            self.autoexport_nodes_parameters()


    def autoexport_nodes_parameters(self):
        '''export orphan and internal output parameters'''
        for node_name, node in self.nodes.iteritems():
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

