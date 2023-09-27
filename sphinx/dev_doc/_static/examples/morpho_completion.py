#!/usr/bin/env python

from capsul.api import Capsul
from soma.qt_gui.qt_backend import Qt
from capsul.schemas.brainvisa import declare_morpho_schemas
from capsul.dataset import ProcessMetadata
import time


show_links_debugger = False
show_compl_gui = True
show_pipeline = False
run_pipelines = False
workers_count = 8
output_schema = 'morphologist_bids'  # or "brainvisa'

real_morpho_module = 'morphologist.capsul'
fake_morpho_module = 'capsul.pipeline.test.fake_morphologist'
morpho_module = fake_morpho_module
#morpho_module = real_morpho_module


def get_shared_path():
    try:
        from soma import aims
        return aims.carto.Paths.resourceSearchPath()[-1]
    except Exception:
        return '!{dataset.shared.path}'


declare_morpho_schemas(morpho_module)

capsul = Capsul()
engine = capsul.engine()
config = capsul.config

config.import_dict({
    'builtin': {
        'config_modules': [
            'spm',
            'axon',
        ],
        'dataset': {
            'input': {
                'path': '/tmp/morpho-bids',
                'metadata_schema': 'bids',
            },
            'output': {
                'path': '/tmp/morpho-bv',
                'metadata_schema': output_schema,
            },
            'shared': {
                'path': get_shared_path(),
                'metadata_schema': 'brainvisa_shared',
            },
        },
        'spm': {
            'spm12_standalone': {
                'directory': '/volatile/local/spm12-standalone',
                'standalone': True,
                'version': '12',
            }
        },
        'matlab': {
            'matlab_mcr': {
                'mcr_directory': '/volatile/local/spm12-standalone/mcr/v97' # '/tmp/matlab_mcr/v97',
            }
        },
    }
})

mp = capsul.executable('%s.morphologist.Morphologist' % morpho_module)

execution_context = engine.execution_context(mp)
# get metadata from an input t1mri path in the input BIDS database
input = '/tmp/morpho-bids/rawdata/sub-aleksander/ses-m0/anat/' \
    'sub-aleksander_ses-m0_T1w.nii.gz'
# completion API
input_metadata = execution_context.dataset['input'].schema.metadata(input)

metadata = ProcessMetadata(mp, execution_context)
# set input metadata in the pipeline metadata set
metadata.bids = input_metadata
# run completion
metadata.generate_paths(mp)

if Qt.QApplication.instance() is not None:

    if show_pipeline:
        from capsul.qt_gui.widgets import PipelineDeveloperView

        mpv = PipelineDeveloperView(mp, allow_open_controller=True,
                                    show_sub_pipelines=True,
                                    enable_edition=True)
        mpv.show()

    if show_links_debugger:
        from capsul.qt_gui.widgets import links_debugger

        ldv = links_debugger.CapsulLinkDebuggerView(mp)
        #mp.t1mri = '/tmp/totor.nii.gz'
        #ldv.update_links_view()
        ldv.show()

    if show_compl_gui:
        from capsul.qt_gui.widgets.attributed_process_widget \
            import AttributedProcessWidget
        pcv = AttributedProcessWidget(mp, metadata,
                                      enable_attr_from_filename=True,
                                      enable_load_buttons=True)
        pcv.show()

# iteration
non_iterative_plugs = [f.name for f in mp.fields()
                       if metadata.parameter_dataset_name(mp, f)
                            in ('shared', None)]
pipeline = capsul.executable_iteration(
    '%s.morphologist.Morphologist' % morpho_module,
    non_iterative_plugs=non_iterative_plugs
)
execution_context = engine.execution_context(pipeline)

N = 1
paths = [
    '/tmp/morpho-bids/rawdata/sub-aleksander/ses-m0/anat/'
    'sub-aleksander_ses-m0_T1w.nii.gz',
    '/tmp/morpho-bids/rawdata/sub-aleksander/ses-m10/anat/'
    'sub-aleksander_ses-m10_T1w.nii.gz',
    '/tmp/morpho-bids/rawdata/sub-casimir/ses-m10/anat/'
    'sub-casimir_ses-m10_T1w.nii.gz',
    '/tmp/morpho-bids/rawdata/sub-calimero/ses-m10/anat/'
    'sub-calimero_ses-m10_T1w.nii.gz',
    '/tmp/morpho-bids/rawdata/sub-calimero/ses-m18/anat/'
    'sub-calimero_ses-m18_T1w.nii.gz',
] * N
iter_meta_bids = []

for path in paths:
    input_metadata = execution_context.dataset['input'].schema.metadata(path)
    iter_meta_bids.append(input_metadata)

metadata = ProcessMetadata(pipeline, execution_context)
metadata.bids = iter_meta_bids
t0 = time.time()
metadata.generate_paths(pipeline)
#pipeline.resolve_paths(execution_context)
print('completion for', len(paths), ':', time.time() - t0, 's.')

if show_compl_gui and Qt.QApplication.instance() is not None:
    pcvi = AttributedProcessWidget(pipeline, enable_attr_from_filename=True,
                                   enable_load_buttons=True)
    pcvi.show()

if run_pipelines:
    print('starting execution')
    engine.config.start_workers['count'] = workers_count
    with engine:
        execution_id = engine.start(pipeline, debug=True)
        print('running...')
        engine.wait(execution_id)
        print('execution done.')

