#!/usr/bin/env python

from capsul.api import Capsul
import json
from soma.qt_gui.qt_backend import Qt
from capsul.dataset import ProcessMetadata, BrainVISASchema
from capsul.schemas.brainvisa import (declare_morpho_schemas,
                                      morphologist_datasets)


show_links_debugger = False
show_compl_gui = True
show_pipeline = False

real_morpho_module = 'morphologist.capsul'
fake_morpho_module = 'capsul.pipeline.test.fake_morphologist'
#morpho_module = fake_morpho_module
morpho_module = real_morpho_module


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

config.builtin.add_module('spm')
config.builtin.add_module('axon')
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
                'metadata_schema': 'brainvisa',
            },
            'shared': {
                'path': get_shared_path(),
                'metadata_schema': 'brainvisa_shared',
            },
        },
        'spm': {
            'spm12_standalone': {
                'directory': '/tmp/spm12-standalone',
                'standalone': True,
                'version': '12',
            }
        },
        'matlab': {
            'matlab_mcr': {
                'mcr_directory': '/tmp/matlab_mcr/v97',
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

metadata = ProcessMetadata(mp, execution_context,
                           datasets=morphologist_datasets)
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

    if show_fom_gui:
        from capsul.qt_gui.widgets.attributed_process_widget \
            import AttributedProcessWidget
        pcv = AttributedProcessWidget(mp, enable_attr_from_filename=True,
                                      enable_load_buttons=True)
        pcv.show()

# iteration
non_iterative_plugs = [f.name for f in mp.fields()
                       if f.name in morphologist_datasets
                       and morphologist_datasets.get(f.name)
                            in ('shared', None)]
pipeline = capsul.executable_iteration(
    '%s.morphologist.Morphologist' % morpho_module,
    non_iterative_plugs=non_iterative_plugs
)
execution_context = engine.execution_context(pipeline)

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
]
iter_meta_bids = []

for path in paths:
    input_metadata = execution_context.dataset['input'].schema.metadata(path)
    iter_meta_bids.append(input_metadata)

metadata = ProcessMetadata(pipeline, execution_context,
                           datasets=morphologist_datasets, debug=False)
metadata.bids = iter_meta_bids
metadata.generate_paths(pipeline)

if show_fom_gui and Qt.QApplication.instance() is not None:
    pcvi = AttributedProcessWidget(pipeline, enable_attr_from_filename=True,
                                  enable_load_buttons=True)
    pcvi.show()


