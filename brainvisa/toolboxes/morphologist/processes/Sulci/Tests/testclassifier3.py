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
try:
  from soma import aims
except:
  def validation():
    raise RuntimeError( _t_( 'module <em>aims</em> not available' ) )

name = 'Test Classifier 3'
userLevel = 2


signature = Signature(
    'input_data', ReadDiskItem( '2D image', 'aims readable Volume Formats' ),
    'classifier', ReadDiskItem( 'Classifier',
                                 [ 'SVM classifier', 'MLP classifier' ] ), 
    'output_image', WriteDiskItem( 'Elevation map',
                                   'aims writable Volume Formats' ),
    )

def initialization( self ):
  self.input_data = '/tmp/gauss9.ima'
  self.classifier = '/tmp/gogo.svm'
  self.output_image = '/tmp/plop.ima'


def execution( self, context ):
  try:
    imdim = self.input_data.get( 'volume_dimension' )
    imvs = self.input_data.get( 'voxel_size' )
    tests = context.temporary( 'Text file' )
    testout = context.temporary( 'Text file' )
    f = open( tests.fullPath(), 'w' )
    for y in xrange( imdim[1] ):
        for x in xrange( imdim[0] ):
            f.write( '%f\t%f\n' % ( float(x)/imdim[0],
                                    float(y)/imdim[1] ) )
    f.close()
    modopts = None
    if self.classifier.format.name == 'SVM classifier':
        modtype = 'svm'
        modopts = self.classifier.get( 'svm_mode' )
        if modopts:
            context.write( 'svm mode: ', modopts )
            modopts = 'svm_mode                  ' + modopts + '\n'
    elif self.classifier.format.name == 'MLP classifier':
        modtype = 'mlp'
        modopts = 'eta                       0.15\n'
    else:
        raise 'Unknown/unsupported model type: ' + self.model.format.name
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

*BEGIN TREE sub_ad_''' + modtype + '\n' )
    if modopts:
        f.write( modopts )
    f.write( '''app_good_error_rate       0
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
    im2 = aims.Volume_FLOAT( imdim[0], imdim[1] )
    f = open( testout.fullPath() )
    vmin = None
    vmax = None
    for y in xrange( im2.getSizeY() ):
        for x in xrange( im2.getSizeX() ):
            val = float( f.readline() )
            im2.setValue( val, x, y )
            if vmin is None:
              vmin = val
              vmax = val
            else:
              if val < vmin:
                vmin = val
              if val > vmax:
                vmax = val
    f.close()
    im2.header()[ 'voxel_size' ] = imvs
    # im2.header()[ 'voxel_size' ] = [ 1./imdim[0], 1./imdim[1], 1, 1 ]
    w = aims.Writer()
    w.write( im2, self.output_image.fullPath() )
    if modtype == 'svm' and self.classifier.get( 'svm_mode' ) == 'decision':
      return [ imdim[0] * imvs[0], imdim[1] * imvs[1], vmin, vmax ]
    else:
      return [ imdim[0] * imvs[0], imdim[1] * imvs[1], 0, 1 ]

  except Exception, e:
    context.ask( 'Error: ' + str(e), 'OK' )
    raise

