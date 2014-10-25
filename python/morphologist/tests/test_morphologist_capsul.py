#!/usr/bin/env python

import os
import shutil
import unittest
import tempfile
import filecmp
from morphologist.process.customized.morphologist import CustomMorphologist
import soma.config as soma_config
import soma_workflow.client as swclient
import soma_workflow.constants as swconstants
from soma.path import relative_path
import brainvisa.axon
from brainvisa.processes import defaultContext
from brainvisa.data.writediskitem import WriteDiskItem
from brainvisa.configuration import neuroConfig
from brainvisa.data import neuroHierarchy


class TestMorphologistCapsul(unittest.TestCase):

    def create_test_database(self):
        database_settings = neuroConfig.DatabaseSettings(
            self.db_dir)
        database = neuroHierarchy.SQLDatabase(
            os.path.join(self.db_dir, "database.sqlite"),
            self.db_dir,
            'brainvisa-3.2.0',
            context=defaultContext(),
            settings=database_settings)
        neuroHierarchy.databases.add(database)
        neuroConfig.dataPath.append(database_settings)
        database.clear(context=defaultContext())
        database.update(context=defaultContext())
        self.input_dir = (os.path.join(
            self.db_dir, 'test', 'sujet01', 't1mri', 'default_acquisition'))
        return database

    def setUp(self):
        print '* initialize brainVisa'
        brainvisa.axon.initializeProcesses()
        tempdir = tempfile.gettempdir()
        self.tests_dir = os.path.join(tempdir, "tmp_tests_brainvisa")
        self.db_dir = os.path.join(
            self.tests_dir, "db_morphologist-%s" % soma_config.full_version)
        print '* create database'
        self.database = self.create_test_database()
        self.db_name = self.database.name

        print '* create process'
        process = brainvisa.processes.getProcessInstance("morphologist_capsul")
        mp = CustomMorphologist()
        process._edited_pipeline = mp
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

        t1mri = [process.signature['t1mri'].contentType.findValue(
            {   "_database" : self.db_name,
                "_format" : "NIFTI-1 image",
                "center" : "test", "subject" : "sujet01"})]
        analysis = ['capsul']
        self.analysis = analysis

        context = defaultContext()
        workflow_di = context.temporary('Soma-Workflow workflow')
        process.workflow = workflow_di

        analysis_dir = os.path.join(self.db_dir, 'test', 'sujet01', 't1mri',
                                'default_acquisition', 'capsul')
        self.analysis_dir = analysis_dir
        if os.path.exists(analysis_dir):
            shutil.rmtree(analysis_dir)
        print "* Run Morphologist_Capsul to get test results"
        defaultContext().runProcess(process, t1mri=t1mri,
            analysis=analysis, use_translated_shared_directory=False,
            workflow=workflow_di)
        print 'workflow:', workflow_di.fullPath()
        wf = swclient.Helper.unserialize(workflow_di.fullPath())

        controller = swclient.WorkflowController()
        wf_id = controller.submit_workflow(wf)
        print '* running Morphologist...'
        swclient.Helper.wait_workflow(wf_id, controller)
        print '* finished.'
        self.workflow_status = controller.workflow_status(wf_id)
        elements_status = controller.workflow_elements_status(wf_id)
        self.failed_jobs = [element for element in elements_status[0] \
            if element[1] != swconstants.DONE \
                or element[3][0] != swconstants.FINISHED_REGULARLY]
        controller.delete_workflow(wf_id)

    def test_pipeline_results(self):
        self.assertTrue(self.workflow_status == swconstants.WORKFLOW_DONE,
            'Workflow did not finish regularly: %s' % self.workflow_status)
        print '** workflow status OK'
        self.assertTrue(len(self.failed_jobs) == 0,
            'Morphologist jobs failed')
        print '** No failed jobs.'

        ref_dir = os.path.join(self.input_dir, 'test')
        #test_dir = os.path.join(
            #self.subject_dir, self.morpho_fom.attributes['analysis'])
        test_dir = self.analysis_dir
        for (dirpath, dirnames, filenames) in os.walk(ref_dir):
          for f in filenames:
            if not f.endswith(".minf"):
              f_ref = os.path.join(dirpath, f)
              f_test = os.path.join(test_dir, relative_path(dirpath, ref_dir),
                                    f)
              self.assertTrue(filecmp.cmp(f_ref, f_test),
                  "The content of "+f+" in test is different from the reference results.")
              print 'file', f_test, 'OK.'
        print '** all OK.'

    def tearDown(self):
        brainvisa.axon.cleanup()


def test_suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestMorphologistCapsul)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

