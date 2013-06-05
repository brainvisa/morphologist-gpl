import unittest
import os
import tempfile
import urllib
from shutil import rmtree
import filecmp

from soma import zipfile
from soma.path import relative_path
import brainvisa.axon
from brainvisa.processes import defaultContext
from brainvisa.data.writediskitem import WriteDiskItem
from brainvisa.configuration import neuroConfig
from brainvisa.data import neuroHierarchy


class TestMorphologistPipeline(unittest.TestCase):  
  
  def download_data(self):
    if not os.path.exists(self.tests_dir):
      os.mkdir(self.tests_dir)
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

  def create_test_database( self ):
    if not os.path.exists( self.database_directory ):
      print "* Create test database"
      os.makedirs( self.database_directory )
    database_settings = neuroConfig.DatabaseSettings( self.database_directory )
    database = neuroHierarchy.SQLDatabase( os.path.join(self.database_directory, "database.sqlite"), 
                                           self.database_directory, 
                                           'brainvisa-3.2.0',
                                           context=defaultContext(), 
                                           settings=database_settings )
    neuroHierarchy.databases.add( database )
    neuroConfig.dataPath.append( database_settings )
    database.clear( context=defaultContext() )
    database.update( context=defaultContext() )
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
    
  def setUp(self):
    tempdir=tempfile.gettempdir()
    self.tests_dir = os.path.join(tempdir, "tmp_tests_brainvisa")
    self.download_data()

    brainvisa.axon.initializeProcesses()
    self.database_directory = os.path.join( self.tests_dir, 'db_morphologist' )
    self.database=self.create_test_database()
    self.db_name = self.database.name
    t1 = self.import_data()
    
    pipeline=brainvisa.processes.getProcessInstance("morphologist")
    nodes=pipeline.executionNode()
    ac = [114.864585876, 118.197914124, 88.7999954224]
    pc = [116.197914124, 147.53125, 91.1999969482]
    ip = [118.197914124, 99.53125, 45.6000061035]
    nodes.child('TalairachTransformation').setSelected(0)
    nodes.child('HeadMesh').setSelected(0)
    nodes.HemispheresProcessing.LeftHemisphere.CorticalFoldsGraph.setSelected(0)
    nodes.HemispheresProcessing.RightHemisphere.CorticalFoldsGraph.setSelected(0)
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
    #nodes.child('CorticalFoldsGraph').fix_random_seed = True
    #nodes.child("SulciRecognition").setSelected(1)
    
    wd=pipeline.signature["t1mri_nobias"]
    self.ref_nobias = wd.findValue({"_database" : self.db_name, 
                                    "_format" : "NIFTI-1 image", 
                                    "center" : "test", "subject" : "sujet01",
                                    "analysis" : "default_analysis"})
    # if needed, run the pipeline a first time to get reference results 
    # in default_analysis
    if (not self.ref_nobias.isReadable()):
      print "* Run Morphologist to get reference results"
      defaultContext().runProcess(pipeline, t1mri=t1,
        t1mri_nobias=self.ref_nobias, Anterior_Commissure=ac,
        Posterior_Commissure=pc, Interhemispheric_Point=ip)

    # run the pipeline a second time to get test results
    self.test_nobias = wd.findValue({"_database" : self.db_name, 
                                     "_format" : "NIFTI-1 image", 
                                     "center" : "test", "subject" : "sujet01",
                                     "analysis" : "test"})
    if self.test_nobias.isReadable():
      rmtree(os.path.dirname(self.test_nobias.fullPath()))
    print "* Run Morphologist to get test results"
    defaultContext().runProcess(pipeline, t1mri=t1,
      t1mri_nobias=self.test_nobias, Anterior_Commissure=ac,
      Posterior_Commissure=pc, Interhemispheric_Point=ip)

    
  def test_pipeline_results(self):
    ref_dir = os.path.dirname(self.ref_nobias.fullPath())
    test_dir = os.path.dirname(self.test_nobias.fullPath())
    for (dirpath, dirnames, filenames) in os.walk(ref_dir):
      for f in filenames:
        if not f.endswith(".minf"):
          f_ref = os.path.join(dirpath, f)
          f_test = os.path.join(test_dir, relative_path(dirpath, ref_dir), f)
          self.assertTrue(filecmp.cmp(f_ref, f_test), 
                          "The content of "+f+" in test is different from the reference results.")
      
  def tearDown(self):
    brainvisa.axon.cleanup()
  
def test_suite():
  return unittest.TestLoader().loadTestsFromTestCase(TestMorphologistPipeline)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')