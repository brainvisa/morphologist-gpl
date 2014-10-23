#!/usr/bin/env python

import os
import unittest
import tempfile
import time
import cPickle
from soma.application import Application
from capsul.study_config.study_config import StudyConfig
from capsul.study_config.config_modules.brainvisa_config import BrainVISAConfig
from capsul.study_config.config_modules.fom_config import FomConfig
from morphologist.process.customized.morphologist import CustomMorphologist
from capsul.process import process_with_fom
import soma.config as soma_config
from capsul.pipeline import pipeline_workflow


class TestMorphologistCapsulPerf(unittest.TestCase):

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
            "volumes_format" : "NIFTI gz",
            "meshes_format" : "GIFTI",
        }

        soma_app = Application('soma.fom', '1.0')
        soma_app.plugin_modules.append('soma.fom')
        soma_app.initialize()
        study_config = StudyConfig(
            modules=StudyConfig.default_modules + [BrainVISAConfig, FomConfig])
        study_config.set_study_configuration(init_study_config)
        FomConfig.check_and_update_foms(study_config)
        self.study_config = study_config

    def test_morpho_perf(self):
        t0 = time.clock()
        mp = CustomMorphologist()
        mp.nodes_activation.SulciRecognition = True
        mp.nodes_activation.SulciRecognition_1 = True
        t1 = time.clock()
        dur = t1 - t0
        print 'time to instantiate one Morphologist pipeline: %f' % (t1 - t0)
        self.morpho = mp
        t0 = time.clock()
        morpho_list1 = [CustomMorphologist() for i in xrange(10)]
        t1 = time.clock()
        print 'time to instantiate 10 Morphologist pipelines: %f' % (t1 - t0)
        nmorpho = 200
        t0 = time.clock()
        mpick = cPickle.dumps(mp)
        self.morpho_list = [cPickle.loads(mpick) for i in xrange(nmorpho)]
        t1 = time.clock()
        print 'time to duplicate %d Morphologist pipelines: %f' \
            % (nmorpho, t1 - t0)
        #dur += t1 - t0

        t0 = time.clock()
        pf = process_with_fom.ProcessWithFom(self.morpho, self.study_config)
        t1 = time.clock()
        print 'time to instantiate ProcessWithFom for Morphologist: %f' \
            % (t1 - t0)
        dur += t1 - t0
        pf.attributes['center'] = 'test'
        pf.attributes['analysis'] = 'capsul'
        self.morpho_fom = pf
        t0 = time.clock()
        self.morpho_fom_list \
            = [process_with_fom.ProcessWithFom(mp, self.study_config)
                for mp in self.morpho_list]
        t1 = time.clock()
        print 'time to instantiate %d process_with_fom: %f' \
            % (len(self.morpho_fom_list), t1 - t0)
        t0 = time.clock()
        self.morpho_fom.study_config = None
        mfompick = cPickle.dumps(self.morpho_fom)
        self.morpho_fom.study_config = self.study_config
        self.morpho_fom_list \
            = [cPickle.loads(mfompick) for mp in self.morpho_list]
        for pf in self.morpho_fom_list:
            pf.study_config = self.study_config
        t1 = time.clock()
        print 'time to duplicate %d process_with_fom: %f' \
            % (len(self.morpho_fom_list), t1 - t0)
        dur += t1 - t0

        self.morpho_fom.attributes['subject'] = 'sujet01'
        t0 = time.clock()
        self.morpho_fom.create_completion()
        t1 = time.clock()
        print 'time to complete Morphologist parameters: %f' % (t1 - t0)
        subjects = ['subject%03d' % i \
                    for i in xrange(len(self.morpho_fom_list))]
        t0 = time.clock()
        for pf, subject in zip(self.morpho_fom_list, subjects):
            pf.attributes['center'] = 'test'
            pf.attributes['analysis'] = 'capsul'
            pf.attributes['subject'] = subject
            pf.create_completion()
        t1 = time.clock()
        print 'time to complete %d Morphologist completions: %f' \
            % (len(self.morpho_fom_list), t1 - t0)
        dur += t1 - t0

        pf = self.morpho_fom_list[12]
        expected_fname = os.path.join(
            self.study_config.output_directory,
            pf.attributes['center'], pf.attributes['subject'],
            't1mri/default_acquisition', pf.attributes['analysis'],
            'folds/3.1/default_session_auto/L%s_default_session_auto_T1_TO_SPAM.trm' % pf.attributes['subject'])
        self.assertTrue(
            pf.process.SulciRecognition_SPAM_recognition09_global_recognition_output_t1_to_global_transformation \
                == expected_fname,
            'Wrong completion, expected: %s, got: %s' % (expected_fname,
                pf.process.SulciRecognition_SPAM_recognition09_global_recognition_output_t1_to_global_transformation))

        # workflow
        self.study_config.somaworkflow_computing_resource = 'localhost'
        self.study_config.somaworkflow_computing_resources_config['localhost'] \
            = {
                'transfer_paths': [],
                'path_translations' : {}}

        t0 = time.clock()
        wf = pipeline_workflow.workflow_from_pipeline(
            self.morpho, study_config=self.study_config)
        t1 = time.clock()
        print 'time to build a Morphologist workflow: %f' % (t1 - t0)
        t0 = time.clock()
        wf_list = [pipeline_workflow.workflow_from_pipeline(
            mp, study_config=self.study_config) for mp in self.morpho_list]
        t1 = time.clock()
        print 'time to build %d Morphologist workflows: %f' \
            % (len(wf_list), t1 - t0)
        dur += t1 - t0
        print 'time to build the complete %d workflows from the beginning ' \
            'using duplication: %f' % (len(wf_list), dur)



def test_suite():
    return unittest.TestLoader().loadTestsFromTestCase(
        TestMorphologistCapsulPerf)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

