
from brainvisa.processes import *
from soma.qt_gui.qtThread import MainThreadLife
from brainvisa.processing import capsul_process
from brainvisa.configuration import axon_capsul_config_link
import six

name = 'Morphologist CAPSUL iteration'

signature = Signature(
    't1mri', ListOf(ReadDiskItem('Raw T1 MRI',
                                 'aims readable volume formats')),
    'capsul_process_type', OpenChoice(
        ('Morphologist', 'morphologist.capsul.morphologist.Morphologist'),
        ('Morphologist simple',
         'morphologist.capsul.morphologist_simple.MorphologistSimple')),
    'analysis', ListOf(String()),
    'sulci_recognition_session', ListOf(String()),
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
    from capsul.qt_gui.widgets import PipelineDeveloperView
    from capsul.api import Pipeline
    Pipeline.hide_nodes_activation = False
    mpv = PipelineDeveloperView(
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
    self.sulci_recognition_session = ['default_session']
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
        self._edited_pipeline.method_ACPC = 'With SPM12 Normalization'
        self._edited_pipeline.perform_sulci_recognition = 'DeepCNN'


def get_edited_pipeline(self):
    if self._edited_pipeline is None:
        from capsul.api import Capsul
        from capsul.dataset import ProcessMetadata
        from capsul.schemas.brainvisa import declare_morpho_schemas
        import sys
        import os.path as osp

        # morphologist may be imported as a toolbox. Here we need the regular
        # module
        old_morpho = None
        if 'morphologist' in sys.modules \
                and sys.modules['morphologist'].__file__.endswith(
                    osp.join('brainvisa', 'toolboxes', 'morphologist',
                             'processes', 'morphologist.py')):
            print('change morphologist module')
            old_morpho = sys.modules['morphologist']
            del sys.modules['morphologist']
        declare_morpho_schemas('morphologist.capsul')

        capsul = getattr(defaultContext(), 'capsul', None)
        if capsul is None:
            capsul = Capsul()
            init_config = {}
        else:
            init_config = capsul.config.asdict()

        init_config.update(capsul_process.get_initial_capsul())
        capsul.config.import_dict(init_config)
        if not hasattr(capsul, 'axon_link'):
            capsul.axon_link = \
                axon_capsul_config_link.AxonCapsulConfSynchronizer(capsul)
            capsul.axon_link.sync_axon_to_capsul()
            capsul.config.builtin.on_attribute_change.add(
                capsul.axon_link.sync_capsul_to_axon)

        self._edited_pipeline = capsul.executable(
            self.capsul_process_type)
        self.capsul = capsul

        execution_context = capsul.engine().execution_context(
            self._edited_pipeline)

        ProcessMetadata(self._edited_pipeline, execution_context)
        self.customize_process()

        if old_morpho is not None:
            # restore toolbox module
            sys.modules['morphologist'] = old_morpho

    return self._edited_pipeline


def execution(self, context):
    self._pipeline_view = None  # close the GUI, if any

    from soma_workflow import client as swclient
    from capsul.execution_context import CapsulWorkflow
    from capsul.dataset import ProcessMetadata
    import numpy as np

    axon_to_capsul_formats = {}

    # dirs and formats have to be handled sorted since
    # FomConfig.check_and_update_foms(study_config) needs to be called
    # for a specific dir / format
    formats = [axon_to_capsul_formats.get(
        t1mri.format.name, t1mri.format.name) for t1mri in self.t1mri]
    aformats = np.array(formats)
    dirs = np.array([t1mri['_database'] for t1mri in self.t1mri])
    sorted_items = []
    for d in sorted(np.unique(dirs)):
        sub_items = np.where(dirs == d)[0]
        sorted_items += list(sub_items[np.argsort(aformats[sub_items])])

    old_database = self.t1mri[sorted_items[0]]['_database']

    mp = self.get_edited_pipeline()
    capsul = self.capsul
    datasets = capsul.config.builtin.dataset
    datasets.input.path = old_database
    datasets.input.metadata_schema = 'brainvisa'  # FIXME hard-coded
    datasets.output.path = old_database
    datasets.output.metadata_schema = 'brainvisa'  # FIXME hard-coded
    metadata = ProcessMetadata(mp, capsul.engine().execution_context(mp))

    # TODO FIXME: ?
    ## activate normalization methods disabling
    #if hasattr(mp, 'attach_config_activations'):
        #mp.attach_config_activations()

    # workflow config
    workflow = swclient.Workflow(name='%s CAPSUL iteration' % mp.name, jobs=[])
    workflow.root_group = []

    context.progress(0, len(self.t1mri), process=self)
    for item in range(len(self.t1mri)):
        i = sorted_items[item]
        t1mri = self.t1mri[i]
        database = t1mri['_database']
        schema_name = 'brainvisa'  # FIXME
        #metadata = ProcessMetadata(mp, capsul.engine().execution_context(mp))
        schema = getattr(metadata, schema_name)
        schema.center = t1mri['center']
        schema.subject = t1mri['subject']
        schema.acquisition = t1mri['acquisition']
        j = i
        if len(self.analysis) <= j:
            j = -1
        schema.analysis = self.analysis[j]
        if len(self.sulci_recognition_session) <= j:
            j = -1
        schema.sulci_recognition_session = self.sulci_recognition_session[j]
        # handle input format
        ext = t1mri.fullPath().rsplit('.', 1)[-1]
        if ext == 'gz':
            ext = '.'.join(t1mri.fullPath().rsplit('.', 2)[-2:])
        context.write('ext:', ext)
        schema.extension = ext
        if database != datasets.input.path \
                or database != datasets.output.path:
            datasets.input.path = database
            datasets.output.path = database
        context.write('config:', capsul.config.builtin.asdict())
        context.write('meta:', metadata.asdict())
        metadata.generate_paths(mp)
        mp.resolve_paths(metadata.execution_context)
        context.write('imported T1:', mp.imported_t1mri)

        #transfers = []
        #if self.transfer_inputs \
                #and study_config.input_directory not in transfers:
            #transfers.append(study_config.input_directory)
        #if self.transfer_outputs \
                #and study_config.output_directory not in transfers:
            #transfers.append(study_config.output_directory)

        #if len(transfers) != 0:
            #study_config.somaworkflow_computing_resources_config.localhost \
                #.transfer_paths = transfers
        #else:
            #study_config.somaworkflow_computing_resources_config.localhost \
                #.transfer_paths = []

        cwf = CapsulWorkflow(mp)
        wf = capsul_process.CapsulProcess.capsul_workflow_to_somaworkflow(
            mp.name, cwf)
        for job in wf.jobs:
            job.priority += (len(self.t1mri) - item) * 100

        workflow.jobs += wf.jobs
        workflow.dependencies += wf.dependencies
        group = swclient.Group(wf.root_group,
                               name='%s iter %i' % (mp.name, i))
        workflow.root_group.append(group)  # += wf.root_group
        workflow.groups += [group] + wf.groups
        context.progress(item+1, len(self.t1mri), process=self)

    context.write('jobs:',
                  len([j for j in workflow.jobs
                       if j.__class__.__name__ == 'Job']),
                  ' real, ', len(workflow.jobs), ' total including barriers')
    swclient.Helper.serialize(self.workflow.fullPath(), workflow)
