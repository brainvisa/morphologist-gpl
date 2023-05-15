# -*- coding: utf-8 -*-
from soma.controller import File, Directory, undefined, Any, \
    Literal, field
from pydantic import conlist
from capsul.api import Process
from capsul.api import Pipeline
from capsul.api import Switch


class BrainOrientation(Pipeline):
    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        self._autoexport_nodes_parameters = autoexport_nodes_parameters
        super(BrainOrientation, self).__init__(False, **kwargs)
        del self._autoexport_nodes_parameters
#        if autoexport_nodes_parameters:
#            self.autoexport_nodes_parameters()

    def pipeline_definition(self):
        # nodes section
        self.add_process(
            'StandardACPC', 'morphologist.capsul.axon.acpcorientation.AcpcOrientation')
        self.nodes['StandardACPC']._weak_outputs = True
        self.add_process(
            'Normalization', 'morphologist.capsul.axon.normalization.Normalization')
        self.nodes['Normalization']._weak_outputs = True
        self.add_process('TalairachFromNormalization',
                         'morphologist.capsul.talairachtransformationfromnormalization.TalairachTransformationFromNormalization')
        self.nodes['TalairachFromNormalization']._weak_outputs = True

        # switches section
        self.add_switch('select_AC_PC_Or_Normalization', ['StandardACPC', 'Normalization'], ['commissure_coordinates', 'reoriented_t1mri', 'talairach_transformation'], output_types=[field(type_=File, write=True, optional=True, allowed_extensions=['.APC']), field(type_=File, write=True, allowed_extensions=[
                        '.nii.gz', '.bmp', '.dcm', '', '.i', '.v', '.fdf', '.gif', '.ima', '.dim', '.jpg', '.mnc', '.nii', '.pbm', '.pgm', '.png', '.ppm', '.img', '.hdr', '.tiff', '.tif', '.vimg', '.vinfo', '.vhdr', '.xbm', '.xpm', '.mnc.gz']), field(type_=File, write=True, allowed_extensions=['.trm'])])

        # exports section
        # export input parameter
        self.export_parameter('StandardACPC', 'T1mri', 'T1mri')
        # export output parameter
        self.export_parameter('select_AC_PC_Or_Normalization',
                              'commissure_coordinates', 'commissure_coordinates')
        # export input parameter
        self.export_parameter(
            'StandardACPC', 'allow_flip_initial_MRI', 'allow_flip_initial_MRI')
        # export output parameter
        self.export_parameter('select_AC_PC_Or_Normalization',
                              'reoriented_t1mri', 'reoriented_t1mri')
        # export output parameter
        self.export_parameter('select_AC_PC_Or_Normalization',
                              'talairach_transformation', 'talairach_transformation')
        self.do_not_export.add(
            ('select_AC_PC_Or_Normalization', 'StandardACPC_switch_talairach_transformation'))
        self.do_not_export.update(
            [('Normalization', 'output_commissures_coordinates')])

        # links section
        self.add_link('T1mri->Normalization.t1mri')
        self.add_link(
            'allow_flip_initial_MRI->Normalization.allow_flip_initial_MRI')
        self.add_link(
            'Normalization.transformation->TalairachFromNormalization.normalization_transformation')
        self.add_link(
            'Normalization.reoriented_t1mri->TalairachFromNormalization.t1mri')

        # initialization section
        if 'Normalization' in self.nodes:
            self.dispatch_value(
                self, 'select_AC_PC_Or_Normalization', 'Normalization')
        # export orphan parameters
        if not hasattr(self, '_autoexport_nodes_parameters') \
                or self._autoexport_nodes_parameters:
            self.autoexport_nodes_parameters()

    def autoexport_nodes_parameters(self):
        '''export orphan and internal output parameters'''
        for node_name, node in self.nodes.items():
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
