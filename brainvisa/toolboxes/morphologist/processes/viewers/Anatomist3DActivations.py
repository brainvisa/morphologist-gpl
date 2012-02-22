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

from neuroProcesses import *
import shfjGlobals
from brainvisa import shelltools
from backwardCompatibleQt import *
from brainvisa import anatomist

name = 'Anatomist Show 3D Activations'
userLevel = 1

def validation():
  anatomist.validation()

signature = Signature(
  'activations', ReadDiskItem( 'fMRI activations', shfjGlobals.anatomistVolumeFormats ),
  'threshold', Number(),
  'minimumSize', Integer(),
  'mri', ReadDiskItem( 'T1 MRI',  shfjGlobals.anatomistVolumeFormats ),
  'show_mri', Choice("Yes","No"),
  'fmriTOmri', ReadDiskItem( 'Transformation matrix', 'Transformation matrix' ),
  'activ_transparency', Number(),
  'head_mesh', ReadDiskItem( 'Head mesh', shfjGlobals.anatomistMeshFormats ),
  'head_transparency', Number(),
  'brain_mesh', ReadDiskItem( 'Brain mesh', shfjGlobals.anatomistMeshFormats ),
  'brain_transparency', Number(),
)

def initialization( self ):
  self.threshold = 3.09
  self.minimumSize = 8
  self.show_mri = "Yes"
  self.linkParameters( 'mri', 'activations' )
  self.linkParameters( 'fmriTOmri', 'activations' )
  self.linkParameters( 'head_mesh', 'activations' )
  self.linkParameters( 'brain_mesh', 'activations' )
  self.setOptional( 'fmriTOmri', 'head_mesh', 'brain_mesh','head_transparency','brain_transparency' )
  self.activ_transparency = 1
  self.head_transparency = 0
  self.brain_transparency = 0.5


class UpdateActivation3D( QWidget ):
  def __init__( self, values, context, parent ):
    QWidget.__init__( self, parent )
    layout = QHBoxLayout( self )
    btn = QPushButton( 'Update', self )
    layout.addWidget( btn )
    btn.setSizePolicy( QSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed ) )
    self._context = context
    self._values = values
    QObject.connect( btn, SIGNAL( 'clicked()' ), self.update3D )
    self._executed = 0
    self.setSizePolicy( QSizePolicy( QSizePolicy.Minimum, QSizePolicy.Minimum ) )

  def buildThresholdedImage( self ):    
    # Build thresholded image and meshes if necessary
    if self._oldThreshold != self._values.threshold or self._oldMinimumSize != self._values.minimumSize:
      shelltools.rm( os.path.join( self._tmp.fullPath(), '*.mesh' ) )
      self._context.system( 'AimsThreshold', '-i', self._values.activations.fullPath(), '-o',
        os.path.join( self._tmp.fullPath(), 'thresholded.ima' ), '-m', 'gt', '-t', self._values.threshold )
      binary = os.path.join( self._tmp.fullPath(), 'binary.ima' )
      self._context.system( 'AimsThreshold', '-i', self._values.activations.fullPath(), '-o',
        os.path.join( self._tmp.fullPath(), 'binary.ima' ), '-m', 'gt', '-t', self._values.threshold, '-b' )
      self._context.system( 'VipConnexFilter', '-i', os.path.join( self._tmp.fullPath(), 'binary' ), 
        '-o', os.path.join( self._tmp.fullPath(), 'binary' ), '-s', self._values.minimumSize, '-c', '6', '-w', 't' )
      self._context.system( 'AimsMesh', '-i', binary,
        '-o', os.path.join( self._tmp.fullPath(), 'mesh' ) )
      self._oldThreshold = self._values.threshold
      self._oldMinimumSize = self._values.minimumSize
      return 1
    return 0
      
  def load3DObjects( self ):
      # Update 3D objects
      a = anatomist.Anatomist()
      d = self._tmp.fullPath()
      objects = []
      for f in os.listdir( d ):
          if f[ -5: ] == '.mesh':
              o = a.loadObject( os.path.join( d, f ), loadReferential=True )
              objects.append( o )
      if objects: 
          a.assignReferential( self._refFMRI, objects )
          self._objects3D = objects
      else:
          self._objects3D = None

  def update3D( self ):
    self._context.readUserValues()
    a = anatomist.Anatomist()
    #a.debug = 0
    if self._executed:
        if self.buildThresholdedImage():
            # Thresholded image has been modified ==> Reload meshes
            if self._objects3D is not None:
                a.deleteObjects( self._objects3D )
            self.load3DObjects()
            self._fmri.reload()
        # self._headShown = 0
        if self._objects3D is not None:
            self._window.addObjects( self._objects3D )

        # Load fusion IRM+activ in window 
        if self._values.show_mri is "Yes" and not self._mriShown:
            self._window.removeObjects( [self._fusion] )
            self._window.addObjects( [self._fusion] )
            self._mriShown = 1
            
        # Remove fusion IRM+activ from window 
        if self._values.show_mri is "No" and self._mriShown:
            self._window.removeObjects( [self._fusion] )
            self._mriShown = 0

        
        if self._values.head_mesh is not None and self._values.head_transparency > 0:
            if self._head is None:
                self._head = a.loadObject( self._values.head_mesh.fullPath())
                self._head.assignReferential( self._refMRI )
            else:
                # We need to remove the head then re-add it to the window
                # because the order is important (probleme with Z-buffer and
                # transparency)
                self._window.removeObjects( [self._head] )
                self._window.addObjects( [self._head] )
            if not self._headShown:
                self._window.addObjects( [self._head] )
                self._headShown = 1
            self._head.setMaterial( a.Material(diffuse = [ 0.8, 0.8, 0.8, self._values.head_transparency ]) )
        else:
            if self._headShown:
                self._window.removeObjects( [self._head] )
                self._headShown = 0
                
        if self._values.brain_mesh is not None and self._values.brain_transparency > 0:
            if self._brain is None:
                self._brain = a.loadObject( self._values.brain_mesh.fullPath() )
                self._brain.assignReferential( self._refMRI )
            else:
                # We need to remove the brain then re-add it to the window
                # because the order is important (probleme with Z-buffer and
                # transparency)
                self._window.removeObjects( [self._brain] )
                self._window.addObjects( [self._brain] )
            if not self._brainShown:
                self._window.addObjects( [self._brain] )
                self._brainShown = 1
            self._brain.setMaterial( a.Material(diffuse = [ 0.8, 0.8, 0.8, self._values.brain_transparency ]) )
        else:
            if self._brainShown:
                self._window.removeObjects( [self._brain] )
                self._brainShown = 0        

    else:
        self._tmp = self._context.temporary( 'Directory' )
        self._executed = 1
        self._oldThreshold = None
        self._oldMinimumSize = None
        self.buildThresholdedImage()

        # Open objects in Anatomist
        fmri = a.loadObject( os.path.join( self._tmp.fullPath(),
                                                "thresholded" ))
        fmri.setPalette( a.getPalette("actif_ret"), minVal = 0, maxVal = 1 )
        window = a.createWindow( '3D' )
        refFMRI = a.createReferential()
        fmri.assignReferential(refFMRI)
        mri = a.loadObject( self._values.mri.fullPath() )
        refMRI = a.createReferential()
        a.assignReferential(refMRI, [mri, window] )

        # Load fusion IRM+activ in window if required
        fusion = a.fusionObjects( [mri, fmri], "Fusion2DMethod" )
        if self._values.show_mri is "Yes":
            window.addObjects( [fusion] )
            self._mriShown = 1
        else:
            self._mriShown = 0
            
        # Load transformation
        if self._values.fmriTOmri is not None:
            self._trans = a.loadTransformation( self._values.fmriTOmri.fullPath(), refFMRI, refMRI)

        self._mri = mri
        self._fusion = fusion
        self._fmri = fmri
        self._window = window
        self._refFMRI = refFMRI
        self._refMRI = refMRI
        self.load3DObjects()
        
        if self._objects3D is not None:
            self._window.addObjects( self._objects3D )
        if self._values.head_mesh is not None and self._values.head_transparency > 0:
            self._head = a.loadObject( self._values.head_mesh.fullPath() )
            self._head.assignReferential( self._refMRI )
            self._head.setMaterial( a.Material(diffuse = [ 0.8, 0.8, 0.8, self._values.head_transparency ]) )
            self._window.addObjects( [self._head] )
            self._headShown = 1
        else:
            self._head = None
            self._headShown = 0
        if self._values.brain_mesh is not None and self._values.brain_transparency > 0:
            self._brain = a.loadObject( self._values.brain_mesh.fullPath() )
            self._brain.assignReferential( self._refMRI )
            self._brain.setMaterial( a.Material(diffuse = [ 0.8, 0.8, 0.8, self._values.brain_transparency ]) )
            self._window.addObjects( self._brain )
            self._brainShown = 1
        else:
            self._brain = None
            self._brainShown = 0
    if self._objects3D is not None:
        a.setMaterial( objects = self._objects3D, material = a.Material(diffuse=[ 1, 0, 0, self._values.activ_transparency ]) )

def inlineGUI( self, values, context, parent ):
  return UpdateActivation3D( values, context, parent )
    
def execution( self, context ):
    pass
