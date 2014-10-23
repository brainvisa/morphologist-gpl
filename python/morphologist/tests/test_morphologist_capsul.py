#!/usr/bin/env python

import os
import shutil
import unittest
import tempfile
import filecmp
from soma.application import Application
from capsul.study_config.study_config import StudyConfig
from capsul.study_config.config_modules.brainvisa_config import BrainVISAConfig
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
            "volumes_format" : "NIFTI",
            "meshes_format" : "GIFTI",
        }

        soma_app = Application('soma.fom', '1.0')
        soma_app.plugin_modules.append('soma.fom')
        soma_app.initialize()
        study_config = StudyConfig(
            modules=StudyConfig.default_modules + [BrainVISAConfig, FomConfig])
        study_config.set_study_configuration(init_study_config)
        FomConfig.check_and_update_foms(study_config)
        mp = CustomMorphologist()
        #mp.nodes_activation.SulciRecognition = True
        #mp.nodes_activation.SulciRecognition_1 = True
        # until reference test is run/compared with graphs
        mp.nodes_activation.CorticalFoldsGraph = False
        mp.nodes_activation.CorticalFoldsGraph_1 = False
        mp.nodes_activation.SulciRecognition = False
        mp.nodes_activation.SulciRecognition_1 = False
        mp.select_Talairach = 'StandardACPC'
        mp.fix_random_seed = True
        ac = [114.864585876, 118.197914124, 88.7999954224]
        pc = [116.197914124, 147.53125, 91.1999969482]
        ip = [118.197914124, 99.53125, 45.6000061035]
        mp.anterior_commissure = ac
        mp.posterior_commissure = pc
        mp.interhemispheric_point = ip
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
        wf_id = controller.submit_workflow(wf)
        print 'running Morphologist...'
        swclient.Helper.wait_workflow(wf_id, controller)
        print 'finished.'
        self.workflow_status = controller.workflow_status(wf_id)
        elements_status = controller.workflow_elements_status(wf_id)
        self.failed_jobs = [element for element in elements_status[0] \
            if element[1] != swconstants.DONE \
                or element[3][0] != swconstants.FINISHED_REGULARLY]
        controller.delete_workflow(wf_id)

    def test_pipeline_results(self):
        self.assertTrue(self.workflow_status == swconstants.WORKFLOW_DONE,
            'Workflow did not finish regularly: %s' % self.workflow_status)
        self.assertTrue(len(self.failed_jobs) == 0,
            'Morphologist jobs failed')

        ref_dir = os.path.join(self.input_dir, 'test')
        test_dir = os.path.join(
            self.subject_dir, self.morpho_fom.attributes['analysis'])
        for (dirpath, dirnames, filenames) in os.walk(ref_dir):
          for f in filenames:
            if not f.endswith(".minf"):
              f_ref = os.path.join(dirpath, f)
              f_test = os.path.join(test_dir, relative_path(dirpath, ref_dir),
                                    f)
              self.assertTrue(filecmp.cmp(f_ref, f_test),
                  "The content of "+f+" in test is different from the reference results.")


def test_suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestMorphologistCapsul)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

