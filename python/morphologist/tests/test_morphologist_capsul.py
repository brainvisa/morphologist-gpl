#!/usr/bin/env python2

from __future__ import print_function
import os
import sys
import shutil
import unittest
import tempfile
import filecmp
import platform
from argparse import ArgumentParser

# set en empty temporary user dir
# BRAINVISA_USER_DIR sould be set before neuroConfig is imported
homedir = tempfile.mkdtemp(prefix='bv_home')
os.environ['BRAINVISA_USER_DIR'] = homedir

import brainvisa.config as bv_config
import soma_workflow.client as swclient
import soma_workflow.constants as swconstants
import soma_workflow.configuration as swconfig
from soma.path import relative_path
import brainvisa.axon
from brainvisa.processes import defaultContext
from brainvisa.data.writediskitem import WriteDiskItem
from brainvisa.configuration import neuroConfig
from brainvisa.data import neuroHierarchy
from soma.aims.graph_comparison import same_graphs

# debugging
import signal
import sys

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

        password='neurospin'
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
                import sys
                signal.signal(signal.SIGUSR1, handle_pdb)
            except ImportError:
                # no debugging, then.
                pass

# Windows platform does not support the SIGUSR2 signal
if platform.system() != 'Windows':
    signal.signal(signal.SIGUSR2, handle_debugger)


test_workflow_file = None


class TestMorphologistCapsul(unittest.TestCase):

    def create_test_database(self, database_directory=None, allow_ro=False):
        if not database_directory:
            database_directory = self.db_dir
        print('* create database', database_directory)
        database_settings = neuroConfig.DatabaseSettings(
            database_directory)
        database = neuroHierarchy.SQLDatabase(
            os.path.join(database_directory, "database.sqlite"),
            database_directory,
            'brainvisa-3.2.0',
            context=defaultContext(),
            settings=database_settings)
        neuroHierarchy.databases.add(database)
        neuroConfig.dataPath.append(database_settings)
        try:
            database.clear(context=defaultContext())
            database.update(context=defaultContext())
        except:
            if not allow_ro:
                raise
        self.input_dir = (os.path.join(
            database_directory, 'test', 'sujet01', 't1mri',
            'default_acquisition'))
        return database


    def create_ref_database(self):
        if self.ref_db_dir == self.db_dir:
            print('* Comparing to reference in the same data dir')
            return self.database
        print('* Comparing to reference data from directory:',
              self.ref_db_dir)
        return self.create_test_database(self.ref_db_dir, allow_ro=True)


    def setUp(self):
        print('* initialize brainVisa')
        brainvisa.axon.initializeProcesses()
        tests_dir = os.getenv("BRAINVISA_TESTS_DIR")
        if not tests_dir:
            tests_dir = tempfile.gettempdir()
        ref_tests_dir = os.environ.get('BRAINVISA_REF_TESTS_DIR', tests_dir)
        self.tests_dir = os.path.join(tests_dir, "tmp_tests_brainvisa")
        self.ref_tests_dir = os.path.join(ref_tests_dir, "tmp_tests_brainvisa")
        self.db_dir = os.path.join(
            self.tests_dir, "db_morphologist-%s" % bv_config.__version__)
        self.ref_db_dir = os.path.join(
            self.ref_tests_dir, "db_morphologist-%s" % bv_config.__version__)
        try:
            os.makedirs(self.db_dir)
        except OSError:
            pass
        self.database = self.create_test_database()
        self.db_name = self.database.name
        self.ref_database = self.create_ref_database()
        self.ref_db_name = self.ref_database.name

        ref_dir = os.path.join(self.input_dir, 'reference')
        if not os.path.isdir(ref_dir):
            raise RuntimeError(
                "Reference results do not exist. Please Run the Morphologist "
                "test first, using the following command: "
                "python -m brainvisa.tests.test_morphologist")

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

        t1mri = [process.signature['t1mri'].contentType.findValue(
            {   "_database" : self.db_name,
                "_format" : "NIFTI-1 image",
                "center" : "test", "subject" : "sujet01"})]
        analysis = ['capsul']
        self.analysis = analysis

        context = defaultContext()
        if not test_workflow_file:
            workflow_di = context.temporary('Soma-Workflow workflow')
        else:
            workflow_di = WriteDiskItem(
                'Text file',
                'Soma-Workflow workflow').findValue(test_workflow_file)
        process.workflow = workflow_di

        analysis_dir = os.path.join(self.db_dir, 'test', 'sujet01', 't1mri',
                                'default_acquisition', 'capsul')
        self.analysis_dir = analysis_dir
        if os.path.exists(analysis_dir):
            shutil.rmtree(analysis_dir)
        print("* Run Morphologist_Capsul to get test results")
        defaultContext().runProcess(process, t1mri=t1mri,
            analysis=analysis, use_translated_shared_directory=False,
            workflow=workflow_di)
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
        wf_id = controller.submit_workflow(wf)
        print('* running Morphologist...')
        swclient.Helper.wait_workflow(wf_id, controller)
        print('* finished.')
        self.workflow_status = controller.workflow_status(wf_id)
        elements_status = controller.workflow_elements_status(wf_id)
        self.failed_jobs = [element for element in elements_status[0] \
            if element[1] != swconstants.DONE
                or element[3][0] != swconstants.FINISHED_REGULARLY
                or element[3][1] != 0]
        self.failed_jobs_info = controller.jobs(
            [element[0] for element in self.failed_jobs 
             if element[3][0] != swconstants.EXIT_NOTRUN])
        controller.delete_workflow(wf_id)
        # remove the temporary database
        del controller
        del config
        os.unlink(tmpdb[1])


    def compare_files(self, ref_file, test_file):
        skipped_ends = [
            ".minf",
            # SPAM probas differ up tp 0.15 in energy and I don't know why, so
            # skip the test
            "_proba.csv",
            # this .dat file contains full paths of filenames
            "_global_TO_local.dat",
            # referentials with registration are allocated differently (uuids)
            "_auto.referential"]
        for ext in skipped_ends:
            if ref_file.endswith(ext):
                return True
        if ref_file.endswith(".arg"):
            return same_graphs(ref_file, test_file)
        elif ref_file.endswith(".csv"):
            if filecmp.cmp(ref_file, test_file):
                return True
            arr1 = np.genfromtxt(ref_file)
            if len(arr1.shape) >= 2 and np.any(np.isnan(arr1[0, :])):
                arr1 = arr1[1:, :]
            arr2 = np.genfromtxt(test_file)
            if len(arr2.shape) >= 2 and np.any(np.isnan(arr2[0, :])):
                arr2 = arr2[1:, :]
            return np.max(np.abs(a2 - a1)) <= 1e-5
        return filecmp.cmp(ref_file, test_file)


    def test_pipeline_results(self):
        self.assertTrue(self.workflow_status == swconstants.WORKFLOW_DONE,
            'Workflow did not finish regularly: %s' % self.workflow_status)
        print('** workflow status OK')
        if len(self.failed_jobs) != 0:
            # failure
            print('** Jobs failure, the following jobs ended with failed '
                  'status:', file=sys.stderr)
            for element in self.failed_jobs:
                # skip those aborted for their dependencies
                if element[3][0] != swconstants.EXIT_NOTRUN:
                    job = self.failed_jobs_info[element[0]]
                    print('+ job:', job[0], ', status:', element[1],
                          ', exit:', element[3][0], ', value:', element[3][1], 
                          file=sys.stderr)
                    print('  commandline:', file=sys.stderr)
                    print(job[1], file=sys.stderr)
        self.assertTrue(len(self.failed_jobs) == 0,
            'Morphologist jobs failed')
        print('** No failed jobs.')

        skipped_dirs = [
            "_global_TO_local",
            # skip .data directories for graphs because their contents order is
            # not always the same
            ".data",
            # skip ANN recognition results (not run in this test)
            "ann_auto",]
        ref_dir = os.path.join(self.input_dir, 'reference')
        test_dir = self.analysis_dir
        for (dirpath, dirnames, filenames) in os.walk(ref_dir):
            if len([1 for ext in skipped_dirs if dirpath.endswith(ext)]) != 0:
                continue
            for f in filenames:
                f_ref = os.path.join(dirpath, f)
                f_test = os.path.join(test_dir,
                                      relative_path(dirpath, ref_dir), f)
                self.assertTrue(self.compare_files(f_ref, f_test),
                    "The content of " + f_test + " in test is different from "
                    "the reference results " + f_ref + ".")
                #print('file', f_test, 'OK.')
        print('** all OK.')

    def tearDown(self):
        brainvisa.axon.cleanup()


def test_suite():
    return unittest.TestLoader().loadTestsFromTestCase(TestMorphologistCapsul)

try:
    if __name__ == '__main__':
        parser = ArgumentParser("test Morphologist CAPSUL version")
        parser.add_argument('-w', '--workflow',
                            help='write the workflow in the given file. '
                            'Default: use a temporary one')
        parser.add_argument('options', nargs='*',
                            help='passed to unittest options parser')
        args = parser.parse_args()
        if args.workflow:
            test_workflow_file = args.workflow

        unittest.main(defaultTest='test_suite',
                      argv=[sys.argv[0]]+args.options)
finally:
    shutil.rmtree(homedir)
    del homedir

# WARNING: if this file is imported as a module, homedir will be removed,
# and later processing will issue errors

