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
from brainvisa import shelltools
import shfjGlobals

name = 'Ana Do A Lot of Things from T1 MRI'
userLevel = 0

signature = Signature(
  'Processing_type', Choice("Do All","Cortical fold graph and all meshes", "Spherical Meshes Only","Grey/White Classification Only","Hemisphere Meshes Only","All meshes"), #, "Compress Results Only","Uncompress Results Only","Delete Results Only"),
  'Side', Choice("Both","Left","Right"),
  'T1mri', ReadDiskItem( "Raw T1 MRI", shfjGlobals.vipVolumeFormats ),
  'Contrast',Choice('High grey/white contrast','Low grey/white contrast'),
  'Bias_type',Choice('Standard bias field','High bias in Z direction'),
  'Compress_results',Boolean(),
  'lesion_mask', ReadDiskItem( '3D Volume', shfjGlobals.vipVolumeFormats),
  'mri_corrected', WriteDiskItem( 'T1 MRI Bias Corrected',
    'Aims writable volume formats' ),
  'histo_analysis', WriteDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'brain_mask', WriteDiskItem( 'T1 Brain Mask',
    'Aims writable volume formats' ),
  'Use_template', Boolean(), 
  'voronoi_template', ReadDiskItem( 'Hemispheres Template',
    shfjGlobals.vipVolumeFormats ),
  'brain_voronoi', WriteDiskItem( "Voronoi Diagram",
    'Aims writable volume formats' ),
  'Commissure_coordinates', ReadDiskItem( 'Commissure coordinates',
    'Commissure coordinates'),
  'left_grey_white', WriteDiskItem( 'Left Grey White Mask',
    'Aims writable volume formats' ),
  'right_grey_white', WriteDiskItem( 'Right Grey White Mask',
    'Aims writable volume formats' ),
  'left_hemi_cortex', WriteDiskItem( 'Left CSF+GREY Mask',
    'Aims writable volume formats' ),
  'right_hemi_cortex', WriteDiskItem( 'Right CSF+GREY Mask',
    'Aims writable volume formats' ),
  'left_hemi_mesh', WriteDiskItem( 'Left Hemisphere Mesh',
    'Aims mesh formats' ),
  'right_hemi_mesh', WriteDiskItem( 'Right Hemisphere Mesh',
    'Aims mesh formats' ),
  'left_white_mesh', WriteDiskItem( 'Left Hemisphere White Mesh',
    'Aims mesh formats' ),
  'right_white_mesh', WriteDiskItem( 'Right Hemisphere White Mesh',
                                     'Aims mesh formats' ),
  'head_mesh', WriteDiskItem( 'Head Mesh', 'Mesh Mesh' ), 
  'iterations', Integer(), 
  'rate', Float(),
  'Lskeleton', WriteDiskItem( 'Left Cortex Skeleton',
    'Aims writable volume formats' ),
  'Rskeleton', WriteDiskItem( 'Right Cortex Skeleton',
    'Aims writable volume formats' ),
  'Lroots', WriteDiskItem( 'Left Cortex Catchment Bassins',
    'Aims writable volume formats'),
  'Rroots', WriteDiskItem( 'Right Cortex Catchment Bassins',
    'Aims writable volume formats' ),
  'Lgraph', WriteDiskItem( 'Left Cortical folds graph', 'Graph' ),
  'Rgraph', WriteDiskItem( 'Right Cortical folds graph', 'Graph' ),
  'compute_fold_meshes', Choice("Yes","No"),
  )


def initialization( self ):
  self.Contrast = 'High grey/white contrast'
  self.Bias_type = 'Standard bias field'
  self.Compress_results = 0
  self.linkParameters( 'mri_corrected', 'T1mri' )
  self.linkParameters( 'histo_analysis', 'mri_corrected' )
  self.linkParameters( 'brain_mask', 'histo_analysis' )
  self.findValue( 'voronoi_template', {} )
  self.Use_template = 1
  self.setOptional('voronoi_template')
  self.setOptional('Commissure_coordinates')
  self.setOptional('lesion_mask')
  self.linkParameters( 'brain_voronoi', 'brain_mask' )
  self.linkParameters( 'Commissure_coordinates', 'T1mri' )
  self.linkParameters( 'left_grey_white', 'brain_voronoi' )
  self.linkParameters( 'right_grey_white', 'brain_voronoi' )
  self.linkParameters( 'left_hemi_cortex', 'left_grey_white' )
  self.linkParameters( 'right_hemi_cortex', 'right_grey_white' )
  self.linkParameters( 'left_hemi_mesh', 'left_hemi_cortex' )
  self.linkParameters( 'right_hemi_mesh', 'right_hemi_cortex' )
  self.linkParameters( 'left_white_mesh', 'left_hemi_mesh' )
  self.linkParameters( 'right_white_mesh', 'right_hemi_mesh' )
  self.linkParameters( 'head_mesh', 'brain_mask' )
  self.setOptional( 'head_mesh' )
  self.iterations = 10
  self.rate = 0.2
  self.linkParameters( 'Lskeleton', 'left_white_mesh' )
  self.linkParameters( 'Rskeleton', 'right_white_mesh' )
  self.linkParameters( 'Lroots', 'Lskeleton' )
  self.linkParameters( 'Rroots', 'Rskeleton' )
  self.linkParameters( 'Lgraph', 'Lroots' )
  self.linkParameters( 'Rgraph', 'Lroots' )
  self.compute_fold_meshes = "Yes"
  self.Side = "Both"
    
def execution( self, context ):
 if self.Commissure_coordinates is None:
    context.write('You have to set commissure coordinates with ---Prepare Subject for Anatomical Pipeline---')
    context.write('This is required if you want a robust behaviour of the pipeline!')
    context.write('If you really do not want to do it, use the brainVISA processes of the class Segmentation...')
 else:
   if self.Processing_type in ("Do All", "Cortical fold graph and all meshes","Spherical Meshes Only","Hemisphere Meshes Only","All meshes","Grey/White Classification Only") :
      context.runProcess( 'AnaT1toBrainMask',
                      T1mri=self.T1mri,
                      Contrast=self.Contrast,
                      Bias_type=self.Bias_type,
                      mri_corrected=self.mri_corrected,
                      histo_analysis=self.histo_analysis,
                      brain_mask = self.brain_mask,
                      Commissure_coordinates=self.Commissure_coordinates,
                      lesion_mask=self.lesion_mask)
      context.runProcess( 'AnaSplitBrainFromBrainMask',
                      mri_corrected = self.mri_corrected,
                      histo_analysis=self.histo_analysis,
                      brain_mask = self.brain_mask,
                      Use_template = self.Use_template,
                      brain_voronoi = self.brain_voronoi,
                      voronoi_template = self.voronoi_template,
                      Commissure_coordinates = self.Commissure_coordinates )
    
      if self.Processing_type in ("Do All","Grey/White Classification Only") :   
        context.runProcess( 'AnaComputeHemiGreyWhiteClassif',
                      mri_corrected = self.mri_corrected,
                      histo_analysis=self.histo_analysis,
                      Side = self.Side,
                      brain_voronoi = self.brain_voronoi,
                      left_grey_white = self.left_grey_white,
                      right_grey_white = self.right_grey_white)

      if self.Processing_type in ("Do All", "Cortical fold graph and all meshes","Hemisphere Meshes Only","All meshes") :

        context.runProcess( 'AnaGetOpenedHemiSurface',
                      mri_corrected = self.mri_corrected,
                      histo_analysis=self.histo_analysis,
                      brain_voronoi = self.brain_voronoi,
                      Side=self.Side,
                      left_hemi_cortex = self.left_hemi_cortex,
                      right_hemi_cortex = self.right_hemi_cortex,
                      left_hemi_mesh= self.left_hemi_mesh,
                      right_hemi_mesh = self.right_hemi_mesh)
        if self.Side in ('Left','Both') and \
               os.path.exists( self.left_hemi_cortex.fullPath() ):
          shelltools.touch( self.left_hemi_cortex.fullName() + '.loc' )
        if self.Side in ('Right','Both') and \
               os.path.exists( self.right_hemi_cortex.fullPath() ):
          shelltools.touch( self.right_hemi_cortex.fullName() + '.loc' )

      if self.Processing_type in ("Do All", "Cortical fold graph and all meshes", "Spherical Meshes Only","All meshes") :
        context.runProcess( 'AnaGetSphericalCorticalSurface',
                      mri_corrected = self.mri_corrected,
                      histo_analysis=self.histo_analysis,
                      brain_voronoi = self.brain_voronoi,
                      Side=self.Side,
                      left_white_mesh = self.left_white_mesh,
                      right_white_mesh = self.right_white_mesh,
                      iterations = self.iterations,
                      rate = self.rate )

      if self.head_mesh is not None and \
             self.Processing_type in ( "Do All",
                                       "Cortical fold graph and all meshes",
                                       "Spherical Meshes Only","All meshes" ):
        context.runProcess( 'headMesh',
                            mri_corrected = self.mri_corrected,
                            head_mesh = self.head_mesh,
                            histo_analysis = self.histo_analysis)

      if self.Processing_type in ("Do All",
                                  "Cortical fold graph and all meshes") :
        context.runProcess( 'AnaComputeCorticalFoldArg',
                      mri_corrected = self.mri_corrected,
                      histo_analysis=self.histo_analysis,
                      brain_voronoi = self.brain_voronoi,
                      Side=self.Side,
                      left_hemi_cortex = self.left_hemi_cortex,
                      right_hemi_cortex = self.right_hemi_cortex,
                      Lskeleton = self.Lskeleton,
                      Rskeleton = self.Rskeleton,
                      Lroots = self.Lroots,
                      Rroots = self.Rroots,
                      Lgraph = self.Lgraph,
                      Rgraph = self.Rgraph,
                      Commissure_coordinates = self.Commissure_coordinates,
                      compute_fold_meshes = self.compute_fold_meshes
                      )
        # extract transformation
        if self.Side in ( 'Both', 'Left' ):
          context.runProcess( 'graphToTalairach', read=self.Lgraph )
        else:
          context.runProcess( 'graphToTalairach', read=self.Rgraph )

   if self.Side in ('Left','Both'):
     if os.path.exists(self.left_hemi_cortex.fullName() + '.loc'):
       os.unlink( self.left_hemi_cortex.fullName() + '.loc' )
   if self.Side in ('Right','Both'):
     if os.path.exists(self.right_hemi_cortex.fullName() + '.loc'):
        os.unlink( self.right_hemi_cortex.fullName() + '.loc' )
