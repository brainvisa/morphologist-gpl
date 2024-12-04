"""
Test morphologist pipeline. The test works by downloading data, constructing a
database and launching several pipelines. The machine specific database is
created in ref mode. In run mode, we create a new DB and compare the data to
the reference DB.

Note that we clean the run database at the begining of each run (not at the end
because we want to keep the data to inspect problems) except if we pass the
option --test-only (this is used for debugging).
The reference database is recreated at each run in ref mode. This DB is reused
in other tests.

There are a few more options for to tune the behaviour of the test.
"""
import unittest
import os
import sys
from shutil import rmtree
import time

from soma.path import relative_path
from soma.aims import filetools
from soma.aims import demotools
import soma.test_utils

# CAUTION: all imports from the main brainvisa package must be done in
# functions, *after* calling setUpModule_axon has been called, which takes care
# of properly initializing axon for the test environment. If these modules were
# imported before setUpModule_axon is called, they would perform an incorrect
# initialization of BrainVISA.
import brainvisa.test_utils


def setUpModule():
    brainvisa.test_utils.setUpModule_axon()


def tearDownModule():
    brainvisa.test_utils.tearDownModule_axon()


class MorphologistTestLoader(soma.test_utils.SomaTestLoader):

    def __init__(self):
        super(MorphologistTestLoader, self).__init__()
        self.parser.description = "Morphologist test program."
        self.parser.add_argument(
            '--no-ann', action='store_true',
            help='do not perform ANN sulci recognition test.')
        self.parser.add_argument(
            '--no-cnn', action='store_true',
            help='do not perform CNN sulci recognition test.')
        self.parser.add_argument(
            '--no-spam', action='store_true',
            help='do not perform SPAM sulci recognition test.')
        self.parser.add_argument(
            '-t', '--test-only', action='store_true',
            help='only perform comparison of results, assuming processing has '
                  'already been done and results written.')
        self.parser.add_argument(
            '--sparse', action='store_true',
            help='sparsely perform tests: segmentation is tested every time, '
                 'sulci recognition only if the date matches certain criteria '
                 '(it\'s usually too long for daily tests) '
                 'currently if the day of month is a multiple of 5.')


# Some methods could be transformed to class method
class TestMorphologistPipeline(soma.test_utils.SomaTestCase):
    private_dir = "test_morphologist_pipeline"

    def __init__(self, testName):
        super(TestMorphologistPipeline, self).__init__(testName)

        # Set some internal variables from CLI arguments (the functions were
        # coded with those variables)
        self.do_spam = not self.no_spam
        self.do_ann = not self.no_ann
        self.do_cnn = not self.no_cnn
        self.day_filter = self.sparse

    def setUp(self):
        # Create the pipelines (we need them to query the databases)
        self.pipeline = self.create_spam_pipeline()
        self.ann_pipeline = self.create_ann_pipeline()
        self.cnn_pipeline = self.create_cnn_pipeline()
        # Call setUp_ref_mode or setUp_run_mode depending on the current mode.
        super(TestMorphologistPipeline, self).setUp()

    @staticmethod
    def create_spam_pipeline():
        import brainvisa.processes
        pipeline = brainvisa.processes.getProcessInstance("morphologist")
        nodes = pipeline.executionNode()
        pipeline.perform_normalization = False
        nodes.child('TalairachTransformation').setSelected(True)
        # nodes.child('HeadMesh').setSelected(0)
        nodes.HemispheresProcessing.LeftHemisphere.CorticalFoldsGraph.setSelected(
            1)
        nodes.HemispheresProcessing.RightHemisphere.CorticalFoldsGraph.setSelected(
            1)
        nodes.child('BiasCorrection').fix_random_seed = True
        nodes.child('HistoAnalysis').fix_random_seed = True
        nodes.child('BrainSegmentation').fix_random_seed = True
        nodes.child('SplitBrain').fix_random_seed = True
        nodes.HemispheresProcessing.LeftHemisphere.GreyWhiteClassification.fix_random_seed = True
        nodes.HemispheresProcessing.RightHemisphere.GreyWhiteClassification.fix_random_seed = True
        nodes.HemispheresProcessing.LeftHemisphere.GreyWhiteTopology.fix_random_seed = True
        nodes.HemispheresProcessing.RightHemisphere.GreyWhiteTopology.fix_random_seed = True
        nodes.HemispheresProcessing.LeftHemisphere.SulciSkeleton.fix_random_seed = True
        nodes.HemispheresProcessing.RightHemisphere.SulciSkeleton.fix_random_seed = True
        nodes.HemispheresProcessing.LeftHemisphere.PialMesh.fix_random_seed = True
        nodes.HemispheresProcessing.RightHemisphere.PialMesh.fix_random_seed = True
        pipeline.perform_sulci_recognition = True
        nodes.HemispheresProcessing.LeftHemisphere.SulciRecognition.fix_random_seed = True
        nodes.HemispheresProcessing.RightHemisphere.SulciRecognition.fix_random_seed = True
        nodes.HemispheresProcessing.LeftHemisphere.SulciRecognition.SPAM_recognition09.setSelected(
            1)
        nodes.HemispheresProcessing.RightHemisphere.SulciRecognition.SPAM_recognition09.setSelected(
            1)

        return pipeline

    @staticmethod
    def create_ann_pipeline():
        pipeline = TestMorphologistPipeline.create_spam_pipeline()
        nodes = pipeline.executionNode()
        nodes.PrepareSubject.setSelected(0)
        nodes.BiasCorrection.setSelected(0)
        nodes.HistoAnalysis.setSelected(0)
        nodes.BrainSegmentation.setSelected(0)
        # nodes.Renorm.setSelected(0)
        nodes.SplitBrain.setSelected(0)
        nodes.TalairachTransformation.setSelected(0)
        nodes.HeadMesh.setSelected(0)
        nodes.HemispheresProcessing.LeftHemisphere.GreyWhiteClassification.setSelected(
            0)
        nodes.HemispheresProcessing.LeftHemisphere.GreyWhiteTopology.setSelected(
            0)
        nodes.HemispheresProcessing.LeftHemisphere.GreyWhiteMesh.setSelected(0)
        nodes.HemispheresProcessing.LeftHemisphere.SulciSkeleton.setSelected(0)
        nodes.HemispheresProcessing.LeftHemisphere.PialMesh.setSelected(0)
        nodes.HemispheresProcessing.LeftHemisphere.CorticalFoldsGraph.setSelected(
            0)
        nodes.HemispheresProcessing.LeftHemisphere.SulciRecognition.recognition2000.setSelected(
            1)
        nodes.HemispheresProcessing.RightHemisphere.GreyWhiteClassification.setSelected(
            0)
        nodes.HemispheresProcessing.RightHemisphere.GreyWhiteTopology.setSelected(
            0)
        nodes.HemispheresProcessing.RightHemisphere.GreyWhiteMesh.setSelected(
            0)
        nodes.HemispheresProcessing.RightHemisphere.SulciSkeleton.setSelected(
            0)
        nodes.HemispheresProcessing.RightHemisphere.PialMesh.setSelected(0)
        nodes.HemispheresProcessing.RightHemisphere.CorticalFoldsGraph.setSelected(
            0)
        nodes.HemispheresProcessing.RightHemisphere.SulciRecognition.recognition2000.setSelected(
            1)

        return pipeline

    @staticmethod
    def create_cnn_pipeline():
        pipeline = TestMorphologistPipeline.create_spam_pipeline()
        nodes = pipeline.executionNode()
        if 'Sulci recognition with Deep CNN' not in \
                [p.name() for p in
                 nodes.HemispheresProcessing.LeftHemisphere.SulciRecognition \
                    .executionNode().children()]:
            # CNN not available
            return None
        nodes.PrepareSubject.setSelected(0)
        nodes.BiasCorrection.setSelected(0)
        nodes.HistoAnalysis.setSelected(0)
        nodes.BrainSegmentation.setSelected(0)
        # nodes.Renorm.setSelected(0)
        nodes.SplitBrain.setSelected(0)
        nodes.TalairachTransformation.setSelected(0)
        nodes.HeadMesh.setSelected(0)
        nodes.HemispheresProcessing.LeftHemisphere.GreyWhiteClassification.setSelected(
            0)
        nodes.HemispheresProcessing.LeftHemisphere.GreyWhiteTopology.setSelected(
            0)
        nodes.HemispheresProcessing.LeftHemisphere.GreyWhiteMesh.setSelected(0)
        nodes.HemispheresProcessing.LeftHemisphere.SulciSkeleton.setSelected(0)
        nodes.HemispheresProcessing.LeftHemisphere.PialMesh.setSelected(0)
        nodes.HemispheresProcessing.LeftHemisphere.CorticalFoldsGraph.setSelected(
            0)
        nodes.HemispheresProcessing.LeftHemisphere.SulciRecognition.CNN_recognition19.setSelected(
            1)
        nodes.HemispheresProcessing.RightHemisphere.GreyWhiteClassification.setSelected(
            0)
        nodes.HemispheresProcessing.RightHemisphere.GreyWhiteTopology.setSelected(
            0)
        nodes.HemispheresProcessing.RightHemisphere.GreyWhiteMesh.setSelected(
            0)
        nodes.HemispheresProcessing.RightHemisphere.SulciSkeleton.setSelected(
            0)
        nodes.HemispheresProcessing.RightHemisphere.PialMesh.setSelected(0)
        nodes.HemispheresProcessing.RightHemisphere.CorticalFoldsGraph.setSelected(
            0)
        nodes.HemispheresProcessing.RightHemisphere.SulciRecognition.CNN_recognition19.setSelected(
            1)

        return pipeline

    @staticmethod
    def download_data(dir_):
        demotools.install_demo_data("demo_data.zip", install_dir=dir_)

    @staticmethod
    def create_database(database_directory, allow_ro=False):
        from brainvisa.configuration import neuroConfig
        from brainvisa.data import neuroHierarchy
        from brainvisa.processes import defaultContext
        if not os.path.exists(database_directory):
            print("* Create test database")
            os.makedirs(database_directory)
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
        # update new database
        try:
            database.clear(context=defaultContext())
            database.update(context=defaultContext())
        except Exception:
            if not allow_ro:
                raise
        return database

    @staticmethod
    def import_data(dir_, db_name):
        from brainvisa.data.writediskitem import WriteDiskItem
        from brainvisa.processes import defaultContext
        input = os.path.join(dir_, "data_unprocessed",
                             "sujet01", "anatomy", "sujet01.ima")
        wd = WriteDiskItem("Raw T1 MRI", "NIFTI-1 image")
        output = wd.findValue({"_database": db_name,
                               "center": "test", "subject": "sujet01"})
        if not output.isReadable():
            print("* Import test data")
            defaultContext().runProcess('ImportT1MRI', input, output)
        return output

    def do_sulci_today(self):
        if self.day_filter and time.localtime(time.time()).tm_mday % 5 != 0:
            return False
        return True

    def get_data(self, database):
        from brainvisa.data.writediskitem import WriteDiskItem
        wd = WriteDiskItem("Raw T1 MRI", "NIFTI-1 image")
        t1 = wd.findValue({"_database": database.name,
                           "center": "test", "subject": "sujet01"})
        nbwd = self.pipeline.signature["t1mri_nobias"]
        t1_nobias = nbwd.findValue({"_database": database.name,
                                    "_format": "NIFTI-1 image",
                                    "center": "test",
                                    "subject": "sujet01"})
        glwd = self.pipeline.signature["left_labelled_graph"]
        grwd = self.pipeline.signature["right_labelled_graph"]
        if self.do_ann:
            left_ann_graph = glwd.findValue(
                t1_nobias,
                requiredAttributes={"sulci_recognition_session": "ann",
                                    "graph_version": "3.1",
                                    "manually_labelled": "No",
                                    "side": "left"})
            right_ann_graph = grwd.findValue(
                t1_nobias,
                requiredAttributes={"sulci_recognition_session": "ann",
                                    "graph_version": "3.1",
                                    "manually_labelled": "No",
                                    "side": "right"})
        else:
            left_ann_graph = None
            right_ann_graph = None

        if self.do_cnn:
            left_cnn_graph = glwd.findValue(
                t1_nobias,
                requiredAttributes={"sulci_recognition_session": "cnn",
                                    "graph_version": "3.1",
                                    "manually_labelled": "No",
                                    "side": "left"})
            right_cnn_graph = grwd.findValue(
                t1_nobias,
                requiredAttributes={"sulci_recognition_session": "cnn",
                                    "graph_version": "3.1",
                                    "manually_labelled": "No",
                                    "side": "right"})
        else:
            left_cnn_graph = None
            right_cnn_graph = None

        return (t1, t1_nobias, left_ann_graph, right_ann_graph, left_cnn_graph,
                right_cnn_graph)

    def run_pipelines(self, database, skip_ann=False, skip_cnn=False):
        from brainvisa.processes import defaultContext
        # Constants
        ac = [114.864585876, 118.197914124, 88.7999954224]
        pc = [116.197914124, 147.53125, 91.1999969482]
        ip = [118.197914124, 99.53125, 45.6000061035]
        # Get data
        t1, t1_nobias, left_ann_graph, right_ann_graph, left_cnn_graph, \
            right_cnn_graph = self.get_data(database)
        # Run pipelines
        print("* Check SPAM models installation")
        # warning: models install needs write permissions to the shared
        # database. If not, and if models are not already here, this will
        # make the test fail. But it is more or less what we want.
        defaultContext().runProcess("check_spam_models", auto_install=True)
        print("* Run Morphologist")
        defaultContext().runProcess(
            self.pipeline, t1mri=t1, t1mri_nobias=t1_nobias,
            anterior_commissure=ac, posterior_commissure=pc,
            interhemispheric_point=ip)
        if not skip_ann:
            print("* Run ANN recognition")
            defaultContext().runProcess(
                self.ann_pipeline, t1mri=t1, t1mri_nobias=t1_nobias,
                anterior_commissure=ac, posterior_commissure=pc,
                interhemispheric_point=ip, left_labelled_graph=left_ann_graph,
                right_labelled_graph=right_ann_graph)
        if not skip_cnn and self.cnn_pipeline:
            print("* Run CNN recognition")
            defaultContext().runProcess(
                self.cnn_pipeline, t1mri=t1, t1mri_nobias=t1_nobias,
                anterior_commissure=ac, posterior_commissure=pc,
                interhemispheric_point=ip, left_labelled_graph=left_cnn_graph,
                right_labelled_graph=right_cnn_graph)
        elif not skip_cnn:
            print('-- CNN recognition is disabled due to missing '
                  'dependencies --')

    def setUp_ref_mode(self):
        # ref mode ignores options test_only, no_ann and no_spam
        ref_data_dir = self.private_ref_data_dir()
        ref_database_dir = os.path.join(
            ref_data_dir, 'db_morphologist'
        )
        # Remove the old database
        if os.path.exists(ref_database_dir):
            rmtree(ref_database_dir)
        # Create the ref database
        TestMorphologistPipeline.download_data(ref_data_dir)
        self.ref_database = TestMorphologistPipeline.create_database(
            ref_database_dir
        )
        TestMorphologistPipeline.import_data(ref_data_dir,
                                             self.ref_database.name)

        # Run the pipelines (conditionnaly).
        if not self.do_spam:
            self.pipeline.perform_sulci_recognition = False
            print('(not doing SPAM sulci recognition tests)')
        if not self.do_ann:
            print('(not doing ANN sulci recognition tests)')
            skip_ann = True
        else:
            skip_ann = False
        if not self.do_cnn:
            print('(not doing CNN sulci recognition tests)')
        skip_cnn = not self.do_cnn

        # Run the pipelines (always use ANN)
        self.run_pipelines(self.ref_database, skip_ann, skip_cnn)

    def setUp_run_mode(self):
        # Get the ref database
        ref_data_dir = self.private_ref_data_dir()
        ref_database_dir = os.path.join(
            ref_data_dir, 'db_morphologist'
        )
        self.ref_database = TestMorphologistPipeline.create_database(
            ref_database_dir, allow_ro=True
        )
        # Location of run database
        run_data_dir = self.private_run_data_dir()
        run_database_dir = os.path.join(
            run_data_dir, 'db_morphologist'
        )
        # Remove the run database
        if os.path.exists(run_database_dir) and not self.test_only:
            rmtree(run_database_dir)
        # Create the run database. If test_only, return a read-only database.
        self.run_database = TestMorphologistPipeline.create_database(
            run_database_dir,
            self.test_only
        )
        if self.test_only:
            return
        # Import data
        TestMorphologistPipeline.download_data(run_data_dir)
        TestMorphologistPipeline.import_data(run_data_dir,
                                             self.run_database.name)
        # Run the pipelines (conditionnaly).
        if not self.do_spam or not self.do_sulci_today():
            self.pipeline.perform_sulci_recognition = False
            print('(not doing SPAM sulci recognition tests today)')
        if not self.do_ann or not self.do_sulci_today():
            print('(not doing ANN sulci recognition tests today)')
            skip_ann = True
        else:
            skip_ann = False
        if not self.do_cnn:
            print('(not doing CNN sulci recognition tests)')
        skip_cnn = not self.do_cnn
        self.run_pipelines(self.run_database, skip_ann, skip_cnn)

    def compare_files(self, ref_file, test_file):
        # tolerate up to 5 differing labels because of internal randomness
        return filetools.cmp(ref_file, test_file, graph_max_label_diff=5)

    def test_pipeline_results(self):
        if self.test_mode == soma.test_utils.ref_mode:
            self.assert_(True)
            return
        skipped_dirs = [
            "_global_TO_local",
            # skip .data directories for graphs because their contents order is
            # not always the same
            ".data"]
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
        if not self.do_ann or not self.do_sulci_today():
            skipped_dirs.append('ann_auto')
        if not self.do_spam or not self.do_sulci_today():
            skipped_dirs.append('default_session_auto')
        # Get data
        ref_data = self.get_data(self.ref_database)
        ref_t1_nobias = ref_data[1]

        _, run_t1_nobias, _, _, _, _ = self.get_data(self.run_database)
        ref_dir = os.path.dirname(ref_t1_nobias.fullPath())

        # check that the ref data actually exist
        for ref_item in ref_data:
            if ref_item:
                self.assertTrue(os.path.exists(ref_item.fullPath()),
                                msg='Reference data missing: %s'
                                % ref_item.fullPath())

        test_dir = os.path.dirname(run_t1_nobias.fullPath())
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
                    "the reference results " + f_ref + ".")

    def tearDown(self):
        super(TestMorphologistPipeline, self).tearDown()


def test(argv):
    """
    Function to execute unitest
    """
    loader = MorphologistTestLoader()
    suite = loader.loadTestsFromTestCase(TestMorphologistPipeline, argv)
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
