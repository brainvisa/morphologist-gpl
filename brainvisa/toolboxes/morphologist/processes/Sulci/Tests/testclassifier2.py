#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
#
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the 
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info". 
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.

from brainvisa.processes import *
import shfjGlobals
from soma import aims

name = 'Test Classifier'
userLevel = 2


signature = Signature(
    'input_data', ReadDiskItem( '2D image', shfjGlobals.aimsVolumeFormats ),
    'classifier', WriteDiskItem( 'Classifier',
                                 [ 'SVM classifier', 'MLP classifier' ] ), 
    'output_image', WriteDiskItem( 'Elevation map',
                                   shfjGlobals.aimsVolumeFormats ),
    )

def initialization( self ):
  self.input_data = '/tmp/gauss9.ima'
  self.classifier = '/tmp/gogo.svm'
  self.output_image = '/tmp/plop.ima'

  eNode = SerialExecutionNode( self.name, parameterized=self )
  eNode.addChild( 'create classifier', 
                  ProcessExecutionNode( 'createclassifier', optional = 1,
                                        selected = 1 ) )
  eNode.addChild( 'train classifier',
                  ProcessExecutionNode( 'trainclassifier', optional = 1,
                                        selected = 1 ) )
  self.setExecutionNode( eNode )


def execution( self, context ):
  try:
    r = aims.Reader( {} )
    im = r.read( self.input_data.fullPath() )
    if self.classifier.format.name == 'SVM classifier':
        context.write( 'SVM classifier' )
        svminput = context.temporary( 'Text file' )
        f = open( svminput.fullPath(), 'w' )
        for y in xrange( im.getSizeY() ):
            for x in xrange( im.getSizeX() ):
                val = im.value( x, y )
                if val:
                  f.write( '%d\t1:%f\t2:%f\n' % \
                           ( val-1, float(x)/im.getSizeX(),
                             float(y)/im.getSizeY() ) )
        f.close()
        context.system( 'svm-train', '-b', 1, '-c', self.C, '-g', self.sigma,
                        svminput, self.classifier )
    tests = context.temporary( 'Text file' )
    testout = context.temporary( 'Text file' )
    f = open( tests.fullPath(), 'w' )
    for y in xrange( im.getSizeY() ):
        for x in xrange( im.getSizeX() ):
            val = im.value( x, y )
            f.write( '%f\t%f\n' % ( float(x)/im.getSizeX(),
                                          float(y)/im.getSizeY() ) )
    f.close()
    moddi = context.temporary( 'Template model' )
    mod = moddi.fullPath()
    f = open( mod, 'w' )
    f.write( '''*BEGIN TREE top_adaptive
nb_learn_data      1
significant_labels unknown
void_label         unknown
weight             1

*BEGIN TREE ad_leaf
learn_state   2
nb_learn_data 1
work          mlp_work1

*BEGIN TREE sub_ad_svm
svm_mode                  decision
app_good_error_rate       0
error_rate                0
gen_bad_error_rate        0
gen_error_rate            0
gen_good_error_rate       0
global_gen_min_error      0
global_good_max_gen_error 0
global_good_min_gen_error 0
global_max_gen_error      0
global_min_gen_error      0
local_good_max_gen_error  0
local_good_min_gen_error  0
local_max_gen_error       0
local_min_gen_error       0
max_out                   1
min_out                   0
steps_since_gen_min       0
mean                      0 0
name                      mlp_work1
net                       ''' + os.path.basename( self.classifier.fullPath() ) + '''
nstats                    1
sigma                     1 1
usedinputs                0 1

*END

*BEGIN TREE fold_descriptor2
direction     1 0 0
e1e2          1 0 0
normal        1 0 0
nstats_E1E2   1
nstats_dir    1
nstats_normal 1

*END

*END

*END
''' )
    f.close()

    context.system( 'siTestNet', '-i', mod, '-d', tests, '-o',
                    testout )
    im2 = aims.Volume_FLOAT( im.getSizeX(), im.getSizeY() )
    f = open( testout.fullPath() )
    for y in xrange( im2.getSizeY() ):
        for x in xrange( im2.getSizeX() ):
            val = float( f.readline() )
            im2.setValue( val, x, y )
    f.close()
    #vs = im.header()[ 'voxel_size' ]
    #if vs:
    #    im2.header()[ 'voxel_size' ] = vs
    im2.header()[ 'voxel_size' ] = [ 1./im.getSizeX(),
                                             1./im.getSizeY(), 1, 1 ]
    w = aims.Writer()
    w.write( im2, self.output_image.fullPath() )

  except Exception, e:
    context.ask( 'Error: ' + str(e), 'OK' )
    raise

