
from brainvisa.processes import *
from brainvisa.tools.mainthreadlife import MainThreadLife

name = 'Morphologist CAPSUL iteration'

signature = Signature(
    't1mri', ListOf(ReadDiskItem('Raw T1 MRI',
                                  'aims readable volume formats')),
    'capsul_process_type', OpenChoice(
        ('Morphologist', 'morphologist.capsul.morphologist.Morphologist'),
        ('Morphologist simple',
         'morphologist.capsul.morphologist_simple.MorphologistSimple')),
    'analysis', ListOf(String()),
    'transfer_inputs', Boolean(),
    'transfer_outputs', Boolean(),
    'use_translated_shared_directory', Boolean(),
    'workflow', WriteDiskItem('Text File', 'Soma-Workflow workflow'),
    'edit_one_pipeline', Boolean(),
)


def onEditPipeline(self, process, dummy):
    if not neuroConfig.gui:
        return
    if process.edit_one_pipeline:
        mainThreadActions().push(self.openPipeline)
    else:
        self._pipeline_view = None


def openPipeline(self):
    from capsul.qt_gui.widgets import PipelineDevelopperView
    from capsul.pipeline import Pipeline
    Pipeline.hide_nodes_activation = False
    mpv = PipelineDevelopperView(
      self.get_edited_pipeline(), allow_open_controller=True,
      show_sub_pipelines=True)
    mpv.show()
    self._pipeline_view = MainThreadLife(mpv)


def change_process_type(self, process, dummy):
    if self.edit_one_pipeline:
        self.edit_one_pipeline = False
    self._edited_pipeline = None


def initialization(self):
    self.analysis = ['default_analysis']
    self.transfer_inputs = False
    self.transfer_outputs = False
    self.use_translated_shared_directory = True
    self.edit_one_pipeline = False
    self._edited_pipeline = None
    self._pipeline_view = None
    self.linkParameters(None, 'edit_one_pipeline', self.onEditPipeline)
    self.linkParameters(None, 'capsul_process_type', self.change_process_type)


def customize_process(self):
    if self.capsul_process_type \
            == 'morphologist.capsul.morphologist.Morphologist':
        self._edited_pipeline.nodes_activation.SulciRecognition = True
        self._edited_pipeline.nodes_activation.SulciRecognition_1 = True
    elif self.capsul_process_type \
            == 'morphologist.capsul.morphologist_simple.MorphologistSimple':
        self._edited_pipeline.method_ACPC = 'With SPM Normalization'


def get_initial_study_config(self):
    from soma.wip.application.api import Application as Appli2
    configuration = Appli2().configuration
    init_study_config = {
        "input_directory" : '/tmp',
        "output_directory" : '/tmp',
        "input_fom" : "morphologist-auto-1.0",
        "output_fom" : "morphologist-auto-1.0",
        "shared_fom" : "shared-brainvisa-1.0",
        "spm_directory" : configuration.SPM.spm8_standalone_path,
        "use_soma_workflow" : True,
        "use_fom" : True,
        "volumes_format" : 'NIFTI gz',
        "meshes_format" : "GIFTI",
    }
    return init_study_config


def get_edited_pipeline(self):
    if self._edited_pipeline is None:
        from capsul import info as cinfo
        cversion = (cinfo.version_major, cinfo.version_minor,
                    cinfo.version_micro)
        if cversion[0] >= 2:
            from capsul.api import get_process_instance
        else:
            from capsul.process import get_process_instance
        if cversion >= (2, 1):
            from capsul.attributes.completion_engine import CompletionEngine
        self._edited_pipeline = get_process_instance(self.capsul_process_type)
        self.customize_process()
        if cversion >= (2, 1):
            from capsul.study_config.study_config import StudyConfig
            init_study_config = self.get_initial_study_config()
            study_config = StudyConfig(
                init_config=init_study_config,
                modules=StudyConfig.default_modules
                    + ['BrainVISAConfig', 'FomConfig'])
            self._edited_pipeline.set_study_config(study_config)
            pf = CompletionEngine.get_completion_engine(self._edited_pipeline)
            self._edited_pipeline.completion_engine = pf

    return self._edited_pipeline


def execution(self, context):
    self._pipeline_view = None # close the GUI, if any
    import time
    from soma.application import Application
    from capsul.study_config.study_config import StudyConfig
    from capsul import info as cinfo
    cversion = (cinfo.version_major, cinfo.version_minor, cinfo.version_micro)
    if cversion >= (2, 1):
        from capsul.attributes.completion_model import CompletionModel
    else:
        from capsul.process import process_with_fom
    from soma_workflow import client as swclient
    from soma.wip.application.api import Application as Appli2
    import numpy as np

    #soma_app = Application('soma.fom', '1.0')
    #soma_app.plugin_modules.append('soma.fom')
    #soma_app.initialize()
    configuration = Appli2().configuration

    if self.capsul_process_type \
            == 'morphologist.capsul.morphologist.Morphologist':
        # Morphologist uses the hand-written Capsul formats
        # formats-brainvisa-1.0
        axon_to_capsul_formats = {
            'NIFTI-1 image': "NIFTI",
            'gz compressed NIFTI-1 image': "NIFTI gz",
            'GIS image': "GIS",
            'MINC image': "MINC",
            'SPM image': "SPM",
            'GIFTI file': "GIFTI",
            'MESH mesh': "MESH",
            'PLY mesh': "PLY",
            'siRelax Fold Energy': "Energy",
        }
    else:
        # other processes use the directly translated formats
        # brainvisa-formats-3.2.0
        axon_to_capsul_formats = {}

    # dirs and formats have to be handled sorted since
    # FomConfig.check_and_update_foms(study_config) needs to be called
    # for a specific dir / format
    formats = [axon_to_capsul_formats.get(
        t1mri.format.name, t1mri.format.name) for t1mri in self.t1mri]
    aformats = np.array(formats)
    dirs = np.array([t1mri['_database'] for t1mri in self.t1mri])
    items_order = np.argsort(dirs)
    sorted_items = []
    for d in sorted(np.unique(dirs)):
        sub_items = np.where(dirs == d)[0]
        sorted_items += list(sub_items[np.argsort(aformats[sub_items])])

    old_database = self.t1mri[sorted_items[0]]['_database']
    old_format = formats[sorted_items[0]]

    init_study_config = {
        "input_directory" : old_database,
        "output_directory" : old_database,
        "input_fom" : "morphologist-auto-1.0",
        "output_fom" : "morphologist-auto-1.0",
        "shared_fom" : "shared-brainvisa-1.0",
        "spm_directory" : configuration.SPM.spm8_standalone_path,
        "use_soma_workflow" : True,
        "use_fom" : True,
        "volumes_format" : old_format,
        "meshes_format" : "GIFTI",
    }

    mp = self.get_edited_pipeline()
    if cversion >= (2, 1):
        study_config = mp.get_study_config()
        study_config.set_study_configuration(init_study_config)
        pf = mp.completion_model
    else:
        study_config = StudyConfig(
            init_config=init_study_config,
            modules=StudyConfig.default_modules
                + ['BrainVISAConfig', 'FomConfig'])
        pf = process_with_fom.ProcessWithFom(mp, study_config)

    # activate normalization methods disabling
    if hasattr(mp, 'attach_config_activations'):
        mp.attach_config_activations(study_config)

    # workflow config
    from capsul.pipeline import pipeline_workflow
    study_config.somaworkflow_computing_resource = 'localhost'
    if self.use_translated_shared_directory:
        path_translations = {
            'path_translations' : {
                study_config.shared_directory:
                    ['brainvisa', 'de25977f-abf5-9f1c-4384-2585338cd7af']}}
    else:
        path_translations = {}
    study_config.somaworkflow_computing_resources_config.localhost \
        = path_translations

    workflow = swclient.Workflow(name='%s CAPSUL iteration' % mp.name, jobs=[])
    workflow.root_group = []

    context.progress(0, len(self.t1mri), process=self)
    for item in xrange(len(self.t1mri)):
        i = sorted_items[item]
        t1mri = self.t1mri[i]
        format = formats[i]
        database = t1mri['_database']
        pf.attributes['center'] = t1mri['center']
        pf.attributes['subject'] = t1mri['subject']
        pf.attributes['acquisition'] = t1mri['acquisition']
        j = i
        if len(self.analysis) <= j:
            j = -1
        pf.attributes['analysis'] = self.analysis[j]
        # handle input format
        if database != old_database or format != old_format:
            # need to reconfigure FOMs for this new dirs/format
            study_config.input_directory = database
            study_config.output_directory = database
            study_config.volumes_format = format
            old_format = format
            old_database = database
            study_config.initialize_modules()
        format = axon_to_capsul_formats.get(t1mri.format.name,
                                            t1mri.format.name)
        if cversion >= (2, 1):
            pf.complete_parameters(mp, {'capsul_attributes': attributes})
        else:
            pf.create_completion()

        transfers = []
        if self.transfer_inputs \
                and study_config.input_directory not in transfers:
            transfers.append(study_config.input_directory)
        if self.transfer_outputs \
                    and study_config.output_directory not in transfers:
            transfers.append(study_config.output_directory)

        if len(transfers) != 0:
            study_config.somaworkflow_computing_resources_config.localhost \
                .transfer_paths = transfers
        else:
            study_config.somaworkflow_computing_resources_config.localhost \
                .transfer_paths = []

        priority = (len(self.t1mri) - item - 1) * 100
        wf = pipeline_workflow.workflow_from_pipeline(
            mp, study_config=study_config)  #, jobs_priority=priority)
        workflow.jobs += wf.jobs
        workflow.dependencies += wf.dependencies
        group = swclient.Group(wf.root_group,
                               name='%s iter %i' % (mp.name, i))
        workflow.root_group.append(group) # += wf.root_group
        workflow.groups += [group] + wf.groups
        context.progress(item+1, len(self.t1mri), process=self)

    context.write('jobs:', len(workflow.jobs))
    swclient.Helper.serialize(self.workflow.fullPath(), workflow)

