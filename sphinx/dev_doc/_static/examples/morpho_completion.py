#!/usr/bin/env python

from capsul.api import capsul_engine
from capsul.attributes.completion_engine import ProcessCompletionEngine
from soma.qt_gui.qt_backend import Qt
from soma.qt_gui.controller_widget import ScrollControllerWidget
import pickle

show_links_debugger = False
show_fom_gui = True
show_pipeline = False

engine = capsul_engine()
engine.load_modules(['fom', 'axon'])
with engine.settings as session:
    config = session.config('fom', 'global')
    config.input_fom = 'morphologist-auto-nonoverlap-1.0'
    config.output_fom = 'morphologist-auto-nonoverlap-1.0'
    config.input_directory = '/tmp/input_data'
    config.output_directory = '/tmp/output_data'


mp = engine.get_process_instance(
  'morphologist.capsul.morphologist.Morphologist')
# set this if you want to use custom individual files as input(s): this
# will disable completion for the input T1 parameter (before importation):
# mp.trait('t1mri').forbid_completion = True

# completion API
pc = ProcessCompletionEngine.get_completion_engine(mp)
attributes = pc.get_attribute_values()
attributes.center = 'subjects'
attributes.subject = 'irm2'
pc.complete_parameters()

if not show_fom_gui:
    # if show_fom_gui is on, the AttributedProcessWidget will connect this
    # (which is questionable)
    pc.capsul_attributes.on_trait_change(pc.attributes_changed)

if Qt.QApplication.instance() is not None:

    if show_pipeline:
        from capsul.qt_gui.widgets import PipelineDevelopperView

        mpv = PipelineDevelopperView(mp, allow_open_controller=True,
                                    show_sub_pipelines=True,
                                    enable_edition=True)
        mpv.show()

    if show_links_debugger:
        from capsul.qt_gui.widgets import links_debugger

        ldv = links_debugger.CapsulLinkDebuggerView(mp)
        #mp.t1mri = '/tmp/totor.nii'
        #ldv.update_links_view()
        ldv.show()

    if show_fom_gui:
        from capsul.qt_gui.widgets.attributed_process_widget \
            import AttributedProcessWidget
        pcv = AttributedProcessWidget(mp, enable_attr_from_filename=True,
                                      enable_load_buttons=True)
        pcv.show()

# iteration

pipeline = engine.get_iteration_pipeline('iter', 'morpho', mp, ['t1mri'])
cm = ProcessCompletionEngine.get_completion_engine(pipeline)
cm.get_attribute_values().subject = ['s1', 's2', 's3']
cm.complete_parameters()
if show_fom_gui and Qt.QApplication.instance() is not None:
    pcvi = AttributedProcessWidget(pipeline, enable_attr_from_filename=True,
                                  enable_load_buttons=True)
    pcvi.show()


#workflow
#from capsul.pipeline import pipeline_workflow
#study_config.somaworkflow_computing_resource = 'localhost'
#study_config.somaworkflow_computing_resources_config = {
    #'localhost': {
        #'transfer_paths': [study_config.input_directory],
        #'path_translations' : {
            #study_config.shared_directory:
                #['brainvisa', 'de25977f-abf5-9f1c-4384-2585338cd7af']}
    #}
#}
#wf = pipeline_workflow.workflow_from_pipeline(pipeline)
#with open('/tmp/morphoiter.workflow', 'wb') as f:
    #pickle.dump(wf, f)

