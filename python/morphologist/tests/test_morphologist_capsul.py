#!/usr/bin/env python
"""
Test the morphologist capsul pipeline.

This test uses the reference database created in test_morphologist.

TODO:
  - test only mode
  - pass arguments to unittest
"""

import os
import sys
import shutil
import unittest
import tempfile
import platform
import soma_workflow.client as swclient
import soma_workflow.configuration as swconfig
from soma.path import relative_path
from soma.aims import filetools
import soma.test_utils

# CAUTION: all imports from the main brainvisa package must be done in
# functions, *after* setUpModule_axon has been called, which takes care
# of properly initializing axon for the test environment. If these modules were
# imported before setUpModule_axon is called, they would perform an incorrect
# initialization of BrainVISA.
import brainvisa.test_utils
from brainvisa.tests.test_morphologist import TestMorphologistPipeline

# debugging
import signal


def setUpModule():
    brainvisa.test_utils.setUpModule_axon()


def tearDownModule():
    brainvisa.test_utils.tearDownModule_axon()


def handle_debugger(sig, frame):
    # When the programs receives a signal SIGUSR2, import/start a debugging
    # tool.
    # Try rpdb2 first. This one allows client/server connection to a running
    # program which has no terminal attached.
    # However do NOT import rpdb2 from the global program since it installs
    # import hooks that interfere with logging config.

    # try using rpdb2/winpdp
    # don't start directly the embedded debugger because it seems to setup by
    # default some breakpoints (when starting; in fork()) and hangs.
    # so we use a signal handler (SIGUSR1) to set it up on demand:
    # use "kill -USR1 <pid>"
    # then connect via the winpdp client, with the password "neurospin".
    try:
        import rpdb2

        password = 'neurospin'
        rpdb2.start_embedded_debugger(password)

    except ImportError:

        # rpdb2/winpdp not installed
        # the problem is that pydb and pdb need an interactive terminal running
        # the current program...
        # once installed a second signal, SIGUSR1, is needed to actually run
        # the debugger.
        try:
            # try pydb
            from pydb.sighandler import SignalManager
            h = SignalManager()
            h.action('SIGUSR1 stack print stop')
        except ImportError:
            # pydb not installed

            def handle_pdb(sig, frame):
                import pdb
                pdb.Pdb().set_trace(frame)

            try:
                import signal
                signal.signal(signal.SIGUSR1, handle_pdb)
            except ImportError:
                # no debugging, then.
                pass


# Windows platform does not support the SIGUSR2 signal
if platform.system() != 'Windows':
    signal.signal(signal.SIGUSR2, handle_debugger)


class MorphologistCapsulTestLoader(soma.test_utils.SomaTestLoader):

    def __init__(self):
        super(MorphologistCapsulTestLoader, self).__init__()
        self.parser.add_argument(
            '-t', '--test-only', action='store_true',
            help='only perform comparison of results, assuming processing has '
                  'already been done and results written.')
        self.parser.add_argument('-w', '--workflow',
                                 help='write the workflow in the given file. '
                                      'Default: use a temporary one')
        self.parser.add_argument('options', nargs='*',
                                 help='passed to unittest options parser')


#
# We want to use the reference data of TestMorphologistPipeline. To do so, we
# override the private_ref_data_dir method to get private reference data
#
# In ref mode we just check that ref database exists.
#
class TestMorphologistCapsul(soma.test_utils.SomaTestCase):
    private_dir = "test_morphologist_capsul"

    @classmethod
    def private_ref_data_dir(cls):
        # We can't call TestMorphologistPipeline.private_ref_data_dir() because
        # private_ref_data_dir is not loaded through the overloaded laoders so
        # base_ref_data_dir and co. are not set.
        path = os.path.join(cls.base_ref_data_dir,
                            TestMorphologistPipeline.private_dir)
        return path

    def __init__(self, testName):
        super(TestMorphologistCapsul, self).__init__(testName)
        # Set some internal variables from CLI arguments (the functions were
        # coded with those variables)
        self.test_workflow_file = self.workflow

    def setUp(self):
        from brainvisa.processes import defaultContext
        print("* Check SPAM models installation")
        # warning: models install needs write permissions to the shared
        # database. If not, and if models are not already here, this will
        # make the test fail. But it is more or less what we want.
        defaultContext().runProcess("check_spam_models", auto_install=True)

        ref_data_dir = self.private_ref_data_dir()
        self.ref_database_dir = os.path.join(
            ref_data_dir, 'db_morphologist'
        )
        # Call setUp_ref_mode or setUp_run_mode depending on the current mode.
        super(TestMorphologistCapsul, self).setUp()

    def setUp_run_mode(self):
        # Location of the ref database
        self.setUp_ref_mode()
        # Location of run database
        run_data_dir = self.private_run_data_dir()
        self.run_database_dir = os.path.join(
            run_data_dir, 'db_morphologist'
        )
        # Remove the run database
        if os.path.exists(self.run_database_dir) and not self.test_only:
            shutil.rmtree(self.run_database_dir)
        # Create the run database. If test_only, return a read-only database.
        self.run_database = TestMorphologistPipeline.create_database(
            self.run_database_dir, self.test_only)
        if self.test_only:
            return
        # Import data
        TestMorphologistPipeline.download_data(run_data_dir)
        TestMorphologistPipeline.import_data(run_data_dir,
                                             self.run_database.name)
        self.input_dir = (os.path.join(
            self.run_database_dir, 'test', 'sujet01', 't1mri',
            'default_acquisition'))

    def compare_files(self, ref_file, test_file):
        # tolerate up to 5 differing labels because of internal randomness
        return filetools.cmp(ref_file, test_file, graph_max_label_diff=5)

    def test_pipeline_results(self):
        from brainvisa.processes import defaultContext
        from brainvisa.data.writediskitem import WriteDiskItem
        if self.test_mode == soma.test_utils.ref_mode:
            # In ref mode we just check that ref database exists (this could be
            # done in setUp_ref_mode too)
            self.assert_(
                os.path.isdir(self.ref_database_dir),
                msg="Reference results do not exist in %s. Please run the "
                    "Morphologist test in ref mode first"
                    % self.ref_database_dir
            )
            return

        # In run mode we create and launch the process
        print('* create process')
        process = brainvisa.processes.getProcessInstance("morphologist_capsul")
        mp = process.get_edited_pipeline()
        mp.nodes_activation.SulciRecognition = True
        mp.nodes_activation.SulciRecognition_1 = True
        mp.select_Talairach = 'StandardACPC'
        mp.perform_skull_stripped_renormalization = 'initial'
        mp.fix_random_seed = True
        ac = [114.864585876, 118.197914124, 88.7999954224]
        pc = [116.197914124, 147.53125, 91.1999969482]
        ip = [118.197914124, 99.53125, 45.6000061035]
        mp.anterior_commissure = ac
        mp.posterior_commissure = pc
        mp.interhemispheric_point = ip
        mp.select_sulci_recognition = 'SPAM_recognition09'

        t1mri = [process.signature['t1mri'].contentType.findValue(
            {"_database": self.run_database.name,
             "_format": "NIFTI-1 image",
             "center": "test",
             "subject": "sujet01"
             }
        )]
        analysis = ['capsul']
        self.analysis = analysis

        context = defaultContext()
        if not self.test_workflow_file:
            workflow_di = context.temporary('Soma-Workflow workflow')
        else:
            workflow_di = WriteDiskItem(
                'Text file',
                'Soma-Workflow workflow').findValue(self.test_workflow_file)
        process.workflow = workflow_di

        analysis_dir = os.path.join(self.run_database_dir, 'test', 'sujet01',
                                    't1mri', 'default_acquisition', 'capsul')
        self.analysis_dir = analysis_dir
        if os.path.exists(analysis_dir):
            shutil.rmtree(analysis_dir)
        print("* Run Morphologist_Capsul to get test results")
        defaultContext().runProcess(
            process,
            t1mri=t1mri,
            analysis=analysis,
            use_translated_shared_directory=False,
            workflow=workflow_di
        )
        print('workflow:', workflow_di.fullPath())
        wf = swclient.Helper.unserialize(workflow_di.fullPath())

        # use a temporary sqlite database in soma-workflow to avoid concurrent
        # access problems
        config = swconfig.Configuration.load_from_file()
        tmpdb = tempfile.mkstemp('.db', prefix='swf_')
        os.close(tmpdb[0])
        os.unlink(tmpdb[1])
        config._database_file = tmpdb[1]
        controller = swclient.WorkflowController(config=config)
        try:
            wf_id = controller.submit_workflow(wf)
            print('* running Morphologist...')
            swclient.Helper.wait_workflow(wf_id, controller)
            print('* finished.')

            ok = controller.log_failed_workflow(wf_id)
            controller.delete_workflow(wf_id)

            self.assertTrue(ok,
                            'Failure during Morphologist workflow execution')

            # run CNN if available
            if 'CNN_recognition19' \
                    in mp.trait('select_sulci_recognition').get_validate()[1]:
                mp.select_sulci_recognition = 'CNN_recognition19'
                for step in mp.pipeline_steps.user_traits().keys():
                    if step not in ('sulci_labelling', 'sulcal_morphometry'):
                        setattr(mp.pipeline_steps, step, False)
                    else:
                        setattr(mp.pipeline_steps, step, True)
                # from capsul.attributes.completion_engine \
                    # import ProcessCompletionEngine
                # pce = ProcessCompletionEngine.get_completion_engine(mp)
                # atts = pce.get_attribute_values()
                # atts.sulci_recognition_session = 'cnn'
                # pce.complete_parameters()
                print("* Run Morphologist_Capsul CNN sulci recognition")
                defaultContext().runProcess(
                    process, t1mri=t1mri,
                    analysis=analysis,
                    sulci_recognition_session='cnn',
                    use_translated_shared_directory=False,
                    workflow=workflow_di
                )
                print('workflow:', workflow_di.fullPath())
                wf = swclient.Helper.unserialize(workflow_di.fullPath())

                wf_id = controller.submit_workflow(wf)
                print('* running CNN...')
                swclient.Helper.wait_workflow(wf_id, controller)
                print('* finished.')

                ok = controller.log_failed_workflow(wf_id)
                controller.delete_workflow(wf_id)

                self.assertTrue(ok, 'Failure during CNN workflow execution')

            print('** No failed jobs.')

        finally:
            # remove the temporary database
            del controller
            del config
            os.unlink(tmpdb[1])

        skipped_dirs = [
            "_global_TO_local",
            # skip .data directories for graphs because their contents order is
            # not always the same
            ".data",
            # skip ANN recognition results (not run in this test)
            "ann_auto"]
        skipped_files = [
            # the PDF contains the creation date and thus cannot be the same
            'morphologist_report.pdf',
            # the SPAM transform may have slight differences, but if labels
            # are OK, then this one is not important.
            'Lsujet01_default_session_auto_T1_TO_SPAM.trm',
            'Rsujet01_default_session_auto_T1_TO_SPAM.trm',
            'Lsujet01_default_session_auto_Tal_TO_SPAM.trm',
            'Rsujet01_default_session_auto_Tal_TO_SPAM.trm',
            'sujet01_default_session_auto_sulcal_morphometry.csv',
        ]
        ref_dir = os.path.join(self.ref_database_dir, 'test', 'sujet01',
                               't1mri', 'default_acquisition',
                               'default_analysis')

        # check that the ref data actually exist
        ref_data = (
            'nobias_sujet01.nii',
            'folds/3.1/default_session_auto/Lsujet01_default_session_auto.arg',
            'folds/3.1/default_session_auto/Rsujet01_default_session_auto.arg',
            'folds/3.1/cnn_auto/Lsujet01_cnn_auto.arg',
            'folds/3.1/cnn_auto/Rsujet01_cnn_auto.arg',
        )
        for ref_item in ref_data:
            self.assertTrue(os.path.exists(os.path.join(ref_dir, ref_item)),
                            msg='Reference data missing.')

        test_dir = self.analysis_dir
        for (dirpath, dirnames, filenames) in os.walk(ref_dir):
            if len([1 for ext in skipped_dirs if dirpath.endswith(ext)]) != 0:
                continue
            for f in filenames:
                if f in skipped_files:
                    continue
                f_ref = os.path.join(dirpath, f)
                f_test = os.path.join(test_dir,
                                      relative_path(dirpath, ref_dir), f)
                self.assertTrue(
                    self.compare_files(f_ref, f_test),
                    "The content of " + f_test + " in test is different from "
                    "the reference results " + f_ref + "."
                )
                # print('file', f_test, 'OK.')
        print('** all OK.')


# def test_suite():
#    return unittest.TestLoader().loadTestsFromTestCase(TestMorphologistCapsul)
#
# try:
#    if __name__ == '__main__':
#        parser = ArgumentParser("test Morphologist CAPSUL version")
#        parser.add_argument('-w', '--workflow',
#                            help='write the workflow in the given file. '
#                            'Default: use a temporary one')
#        parser.add_argument('options', nargs='*',
#                            help='passed to unittest options parser')
#        args = parser.parse_args()
#        if args.workflow:
#            test_workflow_file = args.workflow
#
#        unittest.main(defaultTest='test_suite',
#                      argv=[sys.argv[0]]+args.options)
# finally:
#    shutil.rmtree(homedir)
#    del homedir


def test(argv):
    """
    Function to execute unitest
    """
    loader = MorphologistCapsulTestLoader()
    suite = loader.loadTestsFromTestCase(TestMorphologistCapsul, argv)
    runtime = unittest.TextTestRunner(verbosity=2).run(suite)
    return runtime.wasSuccessful()


if __name__ == "__main__":
    print(sys.argv)
    ret = test(sys.argv[1:])
    print("RETURNCODE: ", ret)
    if ret:
        sys.exit(0)
    else:
        sys.exit(1)
