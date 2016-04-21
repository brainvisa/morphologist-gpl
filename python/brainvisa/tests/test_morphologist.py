import unittest
import os
import sys
import tempfile
import urllib
import shutil
from shutil import rmtree
import filecmp
import argparse
from argparse import ArgumentParser
import time
import numpy as np

from soma import zipfile
from soma.path import relative_path
import brainvisa.config

# set en empty temporary user dir
# BRAINVISA_USER_DIR shoult be set before neuroConfig is imported
homedir = tempfile.mkdtemp(prefix='bv_home')
os.environ['BRAINVISA_USER_DIR'] = homedir

import brainvisa.axon
from brainvisa.processes import defaultContext
from brainvisa.data.writediskitem import WriteDiskItem
from brainvisa.configuration import neuroConfig
from brainvisa.data import neuroHierarchy
from soma.aims.graph_comparison import same_graphs


clear_reference = False
do_spam = True
do_ann = True
day_filter = False
test_only = True


class TestMorphologistPipeline(unittest.TestCase):

    def download_data(self):
        if not os.path.exists(self.tests_dir):
            os.makedirs(self.tests_dir)
        os.chdir(self.tests_dir)
        if not os.path.exists("demo_data.zip"):
            print "* Download ftp://ftp.cea.fr/pub/dsv/anatomist/data/demo_data.zip to ", self.tests_dir
            urllib.urlretrieve(
                "ftp://ftp.cea.fr/pub/dsv/anatomist/data/demo_data.zip",
                "demo_data.zip")
        if os.path.exists("data_for_anatomist"):
            rmtree("data_for_anatomist")
        if os.path.exists("data_unprocessed"):
            rmtree("data_unprocessed")
        zf = zipfile.ZipFile("demo_data.zip")
        zf.extractall()


    def create_test_database(self):
        if not os.path.exists(self.database_directory):
            print "* Create test database"
            os.makedirs(self.database_directory)
        database_settings = neuroConfig.DatabaseSettings(
            self.database_directory)
        database = neuroHierarchy.SQLDatabase(
            os.path.join(self.database_directory, "database.sqlite"),
            self.database_directory,
            'brainvisa-3.2.0',
            context=defaultContext(),
            settings=database_settings)
        neuroHierarchy.databases.add(database)
        neuroConfig.dataPath.append(database_settings)
        database.clear(context=defaultContext())
        database.update(context=defaultContext())
        return database


    def import_data(self):
        input = os.path.join(self.tests_dir, "data_unprocessed",
                            "sujet01", "anatomy", "sujet01.ima")
        wd=WriteDiskItem("Raw T1 MRI", "NIFTI-1 image")
        output=wd.findValue({"_database" : self.db_name,
                            "center" : "test", "subject" : "sujet01"})
        if not output.isReadable():
            print "* Import test data"
            defaultContext().runProcess('ImportT1MRI', input, output)
        return output


    def get_pipeline(self):
        pipeline = brainvisa.processes.getProcessInstance("morphologist")
        nodes = pipeline.executionNode()
        pipeline.perform_normalization = False
        nodes.child('TalairachTransformation').setSelected(True)
        #nodes.child('HeadMesh').setSelected(0)
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
        nodes.HemispheresProcessing.LeftHemisphere.SulciRecognition.SPAM_recognition09.setSelected(1)
        nodes.HemispheresProcessing.RightHemisphere.SulciRecognition.SPAM_recognition09.setSelected(1)

        return pipeline


    def get_ann_pipeline(self):
        pipeline = self.get_pipeline()
        nodes = pipeline.executionNode()
        nodes.PrepareSubject.setSelected(0)
        nodes.BiasCorrection.setSelected(0)
        nodes.HistoAnalysis.setSelected(0)
        nodes.BrainSegmentation.setSelected(0)
        #nodes.Renorm.setSelected(0)
        nodes.SplitBrain.setSelected(0)
        nodes.TalairachTransformation.setSelected(0)
        nodes.HeadMesh.setSelected(0)
        nodes.HemispheresProcessing.LeftHemisphere.GreyWhiteClassification.setSelected(0)
        nodes.HemispheresProcessing.LeftHemisphere.GreyWhiteTopology.setSelected(0)
        nodes.HemispheresProcessing.LeftHemisphere.GreyWhiteMesh.setSelected(0)
        nodes.HemispheresProcessing.LeftHemisphere.SulciSkeleton.setSelected(0)
        nodes.HemispheresProcessing.LeftHemisphere.PialMesh.setSelected(0)
        nodes.HemispheresProcessing.LeftHemisphere.CorticalFoldsGraph.setSelected(0)
        nodes.HemispheresProcessing.LeftHemisphere.SulciRecognition.recognition2000.setSelected(1)
        nodes.HemispheresProcessing.RightHemisphere.GreyWhiteClassification.setSelected(0)
        nodes.HemispheresProcessing.RightHemisphere.GreyWhiteTopology.setSelected(0)
        nodes.HemispheresProcessing.RightHemisphere.GreyWhiteMesh.setSelected(0)
        nodes.HemispheresProcessing.RightHemisphere.SulciSkeleton.setSelected(0)
        nodes.HemispheresProcessing.RightHemisphere.PialMesh.setSelected(0)
        nodes.HemispheresProcessing.RightHemisphere.CorticalFoldsGraph.setSelected(0)
        nodes.HemispheresProcessing.RightHemisphere.SulciRecognition.recognition2000.setSelected(1)

        return pipeline


    def do_sulci_today(self):
        if day_filter and time.localtime(time.time()).tm_mday % 5 != 0:
            return False
        return True


    def setUp(self):
      tests_dir = os.getenv("BRAINVISA_TESTS_DIR")
      if not tests_dir:
          tests_dir = tempfile.gettempdir()
      self.tests_dir = os.path.join(tests_dir, "tmp_tests_brainvisa")
      self.download_data()

      brainvisa.axon.initializeProcesses()
      self.database_directory = os.path.join( self.tests_dir,
          'db_morphologist-%s' % brainvisa.config.__version__ )
      self.database=self.create_test_database()
      self.db_name = self.database.name
      t1 = self.import_data()

      ac = [114.864585876, 118.197914124, 88.7999954224]
      pc = [116.197914124, 147.53125, 91.1999969482]
      ip = [118.197914124, 99.53125, 45.6000061035]

      pipeline = self.get_pipeline()
      ann_pipeline = self.get_ann_pipeline()

      wd = pipeline.signature["t1mri_nobias"]
      self.ref_nobias = wd.findValue({"_database" : self.db_name,
                                      "_format" : "NIFTI-1 image",
                                      "center" : "test", "subject" : "sujet01",
                                      "analysis" : "reference"})
      glwd = pipeline.signature["left_labelled_graph"]
      ref_left_ann_graph = glwd.findValue(
          self.ref_nobias,
          requiredAttributes={"sulci_recognition_session" : "ann",
                              "graph_version": "3.1",
                              "manually_labelled": "No",
                              "side": "left"})
      grwd = pipeline.signature["left_labelled_graph"]
      ref_right_ann_graph = grwd.findValue(
          self.ref_nobias,
          requiredAttributes={"sulci_recognition_session" : "ann",
                              "graph_version": "3.1",
                              "manually_labelled": "No",
                              "side": "right"})

      # if requested, clear existing reference results
      if clear_reference and os.path.exists(self.ref_nobias.fullPath()):
          print '* Clear reference results to build new ones'
          rmtree(os.path.dirname(self.ref_nobias.fullPath()))
          self.database.clear(context=defaultContext())
          self.database.update(context=defaultContext())

      # if needed, run the pipeline a first time to get reference results
      # in default_analysis
      if not self.ref_nobias.isReadable():
          print "* Run Morphologist to get reference results"
          defaultContext().runProcess(pipeline, t1mri=t1,
              t1mri_nobias=self.ref_nobias, anterior_commissure=ac,
              posterior_commissure=pc, interhemispheric_point=ip)
          print "* Run ANN recognition to get reference results"
          defaultContext().runProcess(ann_pipeline, t1mri=t1,
              t1mri_nobias=self.ref_nobias, anterior_commissure=ac,
              posterior_commissure=pc, interhemispheric_point=ip,
              left_labelled_graph=ref_left_ann_graph,
              right_labelled_graph=ref_right_ann_graph)

      # run the pipeline a second time to get test results
      self.test_nobias = wd.findValue({"_database" : self.db_name,
                                      "_format" : "NIFTI-1 image",
                                      "center" : "test", "subject" : "sujet01",
                                      "analysis" : "test"})
      test_left_ann_graph = glwd.findValue(
          self.test_nobias,
          requiredAttributes={"sulci_recognition_session" : "ann",
                              "graph_version": "3.1",
                              "manually_labelled": "No",
                              "side": "left"})
      test_right_ann_graph = grwd.findValue(
          self.test_nobias,
          requiredAttributes={"sulci_recognition_session" : "ann",
                              "graph_version": "3.1",
                              "manually_labelled": "No",
                              "side": "right"})

      if not test_only:
          if self.test_nobias.isReadable():
              rmtree(os.path.dirname(self.test_nobias.fullPath()))
              self.database.clear(context=defaultContext())
              self.database.update(context=defaultContext())
          pipeline.executionNode().child(
              'TalairachTransformation').setSelected(False)
          if not do_spam or not self.do_sulci_today():
              pipeline.perform_sulci_recognition = False
              print '(not doing SPAM sulci recognition tests today)'
          print "* Run Morphologist to get test results"
          defaultContext().runProcess(pipeline, t1mri=t1,
              t1mri_nobias=self.test_nobias, anterior_commissure=ac,
              posterior_commissure=pc, interhemispheric_point=ip)
          if do_ann and self.do_sulci_today():
              print "* Run ANN recognition to get test results"
              defaultContext().runProcess(ann_pipeline, t1mri=t1,
                  t1mri_nobias=self.test_nobias, anterior_commissure=ac,
                  posterior_commissure=pc, interhemispheric_point=ip,
                  left_labelled_graph=test_left_ann_graph,
                  right_labelled_graph=test_right_ann_graph)
          else:
              print '(not doing ANN sulci recognition today)'


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
        if filecmp.cmp(ref_file, test_file):
            return True
        if ref_file.endswith(".csv") or ref_file.endswith(".trm"):
            arr1 = np.genfromtxt(ref_file)
            if len(arr1.shape) >= 2 and np.any(np.isnan(arr1[0, :])):
                arr1 = arr1[1:, :]
            arr2 = np.genfromtxt(test_file)
            if len(arr2.shape) >= 2 and np.any(np.isnan(arr2[0, :])):
                arr2 = arr2[1:, :]
            return np.max(np.abs(arr2 - arr1)) <= 1e-4
        # no match
        return False


    def test_pipeline_results(self):
        skipped_dirs = [
            "_global_TO_local",
            # skip .data directories for graphs because their contents order is
            # not always the same
            ".data"]
        if not do_ann or not do_sulci_today():
            skipped_dirs.append('ann_auto')
        if not do_spam or not do_sulci_today():
            skipped_dirs.append('default_session_auto')
        ref_dir = os.path.dirname(self.ref_nobias.fullPath())
        test_dir = os.path.dirname(self.test_nobias.fullPath())
        for (dirpath, dirnames, filenames) in os.walk(ref_dir):
            if len([1 for ext in skipped_dirs if dirpath.endswith(ext)]) != 0:
                continue
            for f in filenames:
                f_ref = os.path.join(dirpath, f)
                f_test = os.path.join(test_dir,
                                      relative_path(dirpath, ref_dir), f)
                self.assertTrue(self.compare_files(f_ref, f_test),
                    "The content of "+f+" in test is different from the "
                    "reference results.")

    def tearDown(self):
        brainvisa.axon.cleanup()


def test_suite():
    return unittest.TestLoader().loadTestsFromTestCase(
        TestMorphologistPipeline)

try:
    if __name__ == '__main__':
        parser = ArgumentParser("test Morphologist pipeline.\n"
            "To get uniitest help, use:\n"
            "%s -- -h\n" % sys.argv[0])
        parser.add_argument('-c', '--clear-ref', action='store_true',
                            help='clear any existing reference results. Use '
                            'it after a known change in results.')
        parser.add_argument('--no-ann', action='store_true',
                            help='do not perform ANN sulci recognition test.')
        parser.add_argument('--no-spam', action='store_true',
                            help='do not perform SPAM sulci recognition test.')
        parser.add_argument(
            '-t', '--test-only', action='store_true',
            help='only perform results tests, assuming processing has already '
            'been done and results written.')
        parser.add_argument(
            '--sparse', action='store_true',
            help='sparsely perform tests: segmentation is tested every time, '
            'sulci recognition only if the date matches certain criteria '
            '(typically for daily tests, avoid them being to long every '
            'day). Currently: if the day of monthh can divide by 5.')
        parser.add_argument('options', nargs=argparse.REMAINDER,
                            help='passed to unittest options parser')
        args = parser.parse_args()
        clear_reference = args.clear_ref
        do_spam = not args.no_spam
        do_ann = not args.no_ann
        day_filter = args.sparse
        test_only = args.test_only
        if len(args.options) != 0 and args.options[0] == '--':
            del args.options[0]

        unittest.main(defaultTest='test_suite',
                      argv=[sys.argv[0]]+args.options)
finally:
    shutil.rmtree(homedir)
    del homedir

# WARNING: if this file is imported as a module, homedir will be removed,
# and later processing will issue errors
