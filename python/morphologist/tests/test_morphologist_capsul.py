#!/usr/bin/env python

import os
import shutil
import unittest
import tempfile
import filecmp
from soma.application import Application
from capsul.study_config.study_config import StudyConfig
from capsul.study_config.config_modules.fom_config import FomConfig
from morphologist.process.customized.morphologist import CustomMorphologist
from capsul.process import process_with_fom
import soma.config as soma_config
from capsul.pipeline import pipeline_workflow
from soma import aims
from soma import uuid
import soma_workflow.client as swclient
import soma_workflow.constants as swconstants
from soma.path import relative_path


class TestMorphologistCapsul(unittest.TestCase):

    def import_data(self):
        subject = self.morpho_fom.attributes['subject']
        self.subject_dir = os.path.join(
            self.db_dir, self.morpho_fom.attributes['center'],
            subject, 't1mri', 'default_acquisition')
        self.input_dir = (os.path.join(
            self.db_dir, 'test', 'sujet01', 't1mri', 'default_acquisition'))
        if self.subject_dir != self.input_dir:
            if os.path.exists(self.subject_dir):
                shutil.rmtree(self.subject_dir)
            os.makedirs(os.path.join(self.subject_dir, 'registration'))
            vol = aims.read(os.path.join(self.input_dir, 'sujet01.nii'))
            ref_uid = uuid.Uuid()
            vol.header()['referential'] = str(ref_uuid)
            aims.write(vol, os.path.join(self.subject_dir, '%s.nii' % subject ))
            open(os.path.join(self.subject_dir,
                'registration/RawT1-%s_default_acquisition.referential' \
                    % subject )
            ).write('attributes = {\'uuid\': %s}\n' % repr(ref_uuid))

    def setUp(self):
        tempdir = tempfile.gettempdir()
        self.tests_dir = os.path.join(tempdir, "tmp_tests_brainvisa")
        self.db_dir = os.path.join(
            self.tests_dir, "db_morphologist-%s" % soma_config.full_version)

        init_study_config = {
            "input_directory" : self.db_dir,
            "output_directory" : self.db_dir,
            "input_fom" : "morphologist-auto-1.0",
            "output_fom" : "morphologist-auto-1.0",
            "shared_fom" : "shared-brainvisa-1.0",
            "spm_directory" : "/i2bm/local/spm8-standalone",
            "use_soma_workflow" : True,
            "use_fom" : True,
        }

        soma_app = Application('soma.fom', '1.0')
        soma_app.plugin_modules.append('soma.fom')
        soma_app.initialize()
        study_config = StudyConfig(
            modules=StudyConfig.default_modules + [FomConfig])
        study_config.set_study_configuration(init_study_config)
        FomConfig.check_and_update_foms(study_config)
        mp = CustomMorphologist()
        mp.nodes_activation.SulciRecognition = True
        mp.nodes_activation.SulciRecognition_1 = True
        mp.fix_random_seed = True
        pf = process_with_fom.ProcessWithFom(mp, study_config)
        pf.attributes['center'] = 'test'
        pf.attributes['subject'] = 'sujet01'
        pf.attributes['analysis'] = 'capsul'
        pf.create_completion()

        # workflow
        study_config.somaworkflow_computing_resource = 'localhost'
        study_config.somaworkflow_computing_resources_config['localhost'] = {
            'transfer_paths': [],
            'path_translations' : {}}
        wf = pipeline_workflow.workflow_from_pipeline(
            mp, study_config=study_config)

        self.morpho_fom = pf
        self.morpho = mp
        self.study_config = study_config

        self.import_data()

        controller = swclient.WorkflowController()
        print 'submit WF...'
        wf_id = controller.submit_workflow(wf)
        print 'running...'
        swclient.Helper.wait_workflow(wf_id, controller)
        print 'finished.'
        self.workflow_status = controller.workflow_status(wf_id)
        print 'status:', self.workflow_status
        controller.delete_workflow(wf_id)

    def test_pipeline_results(self):
        self.assertTrue(self.workflow_status == swconstants.WORKFLOW_DONE,
            'Workflow did not finish regularly: %s' % self.workflow_status)

        ref_dir = os.path.join(self.input_dir, 'test')
        test_dir = os.path.join(
            self.subject_dir, self.morpho_fom.attributes['analysis'])
        for (dirpath, dirnames, filenames) in os.walk(ref_dir):
          for f in filenames:
            if not f.endswith(".minf"):
              f_ref = os.path.join(dirpath, f)
              f_test = os.path.join(test_dir, relative_path(dirpath, ref_dir), f)
              self.assertTrue(filecmp.cmp(f_ref, f_test),
                  "The content of "+f+" in test is different from the reference results.")


def test_suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestMorphologistCapsul)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

