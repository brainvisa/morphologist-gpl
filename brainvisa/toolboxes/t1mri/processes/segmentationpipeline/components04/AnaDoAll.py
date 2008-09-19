# Copyright CEA and IFR 49 (2000-2005)
#
#  This software and supporting documentation were developed by
#      CEA/DSV/SHFJ and IFR 49
#      4 place du General Leclerc
#      91401 Orsay cedex
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
  'Processing_type', Choice("Do All","Cortical fold graph and all meshes", "Spherical Meshes Only","Grey/White Classification Only","Hemisphere Meshes Only","All meshes", "Compress Results Only","Uncompress Results Only","Delete Results Only"),
  'Side', Choice("Both","Left","Right"),
  'T1mri', ReadDiskItem( "Raw T1 MRI", shfjGlobals.vipVolumeFormats ),  
  'Contrast',Choice('High grey/white contrast','Low grey/white contrast'),
  'Bias_type',Choice('Standard bias field','High bias in Z direction'),
  'Compress_results',Boolean(),
  'lesion_mask', ReadDiskItem( '3D Volume', shfjGlobals.vipVolumeFormats),
  'mri_corrected', WriteDiskItem( 'T1 MRI Bias Corrected', 'GIS image' ),
  'histo_analysis', WriteDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'brain_mask', WriteDiskItem( 'T1 Brain Mask', 'GIS Image' ),
  'Use_template', Boolean(), 
  'voronoi_template', ReadDiskItem( 'Hemispheres Template', shfjGlobals.vipVolumeFormats ),
  'brain_voronoi', WriteDiskItem( "Voronoi Diagram", 'GIS Image' ),
   'Commissure_coordinates', ReadDiskItem( 'Commissure coordinates','Commissure coordinates'),
  'left_grey_white', WriteDiskItem( 'Left Grey White Mask', 'GIS Image' ),
  'right_grey_white', WriteDiskItem( 'Right Grey White Mask', 'GIS Image' ),
  'left_hemi_cortex', WriteDiskItem( 'Left CSF+GREY Mask', 'GIS Image' ),
  'right_hemi_cortex', WriteDiskItem( 'Right CSF+GREY Mask', 'GIS Image' ),
  'left_hemi_mesh', WriteDiskItem( 'Left Hemisphere Mesh', 'MESH mesh' ),
  'right_hemi_mesh', WriteDiskItem( 'Right Hemisphere Mesh', 'MESH mesh' ),
  'left_white_mesh', WriteDiskItem( 'Left Hemisphere White Mesh', 'MESH mesh' ),
  'right_white_mesh', WriteDiskItem( 'Right Hemisphere White Mesh',
                                     'MESH mesh' ),
  'head_mesh', WriteDiskItem( 'Head Mesh', 'Mesh Mesh' ), 
  'iterations', Integer(), 
  'rate', Float(),
  'Lskeleton', WriteDiskItem( 'Left Cortex Skeleton', 'GIS image' ),
  'Rskeleton', WriteDiskItem( 'Right Cortex Skeleton', 'GIS Image' ),
  'Lroots', WriteDiskItem( 'Left Cortex Catchment Bassins', 'GIS image' ),
  'Rroots', WriteDiskItem( 'Right Cortex Catchment Bassins', 'GIS Image' ),
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
      if os.path.exists(self.mri_corrected.fullName() + '.ima.gz'):
        if  os.path.exists(self.mri_corrected.fullName() + '.loc'):     
          context.system("gunzip " + self.mri_corrected.fullName() + '.ima')
          context.system("gunzip " + self.mri_corrected.fullName() + '.dim')
      if os.path.exists(self.brain_mask.fullName() + '.ima.gz'):
        if  os.path.exists(self.brain_mask.fullName() + '.loc'):     
          context.system("gunzip " + self.brain_mask.fullName() + '.ima')
          context.system("gunzip " + self.brain_mask.fullName() + '.dim')
      context.runProcess( 'AnaT1toBrainMask',
                      T1mri=self.T1mri,
                      Contrast=self.Contrast,
                      Bias_type=self.Bias_type,
                      mri_corrected=self.mri_corrected,
                      histo_analysis=self.histo_analysis,
                      brain_mask = self.brain_mask,
                      Commissure_coordinates=self.Commissure_coordinates,
                      lesion_mask=self.lesion_mask)
      if os.path.exists(self.brain_voronoi.fullName() + '.ima.gz'):
        if  os.path.exists(self.brain_voronoi.fullName() + '.loc'):     
          context.system("gunzip " + self.brain_voronoi.fullName() + '.ima')
          context.system("gunzip " + self.brain_voronoi.fullName() + '.dim')
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

        if self.Side in ('Left','Both'):
          if os.path.exists(self.left_hemi_cortex.fullName() + '.ima.gz'):
            if  os.path.exists(self.left_hemi_cortex.fullName() + '.loc'):     
              context.system("gunzip " + self.left_hemi_cortex.fullName() + '.ima')
              context.system("gunzip " + self.left_hemi_cortex.fullName() + '.dim')
        if self.Side in ('Right','Both'):
          if os.path.exists(self.right_hemi_cortex.fullName() + '.ima.gz'):
            if  os.path.exists(self.right_hemi_cortex.fullName() + '.loc'):     
              context.system("gunzip " + self.right_hemi_cortex.fullName() + '.ima')
              context.system("gunzip " + self.right_hemi_cortex.fullName() + '.dim')
          
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

   if self.Compress_results or self.Processing_type=="Compress Results Only":
      if os.path.exists(self.mri_corrected.fullName() + '.ima'):
        context.system("gzip --force " + self.mri_corrected.fullName() + '.ima')
        context.system("gzip --force " + self.mri_corrected.fullName() + '.dim')
      if os.path.exists(self.brain_mask.fullName() + '.ima'):
        context.system("gzip --force " + self.brain_mask.fullName() + '.ima')
        context.system("gzip --force " + self.brain_mask.fullName() + '.dim')
      if os.path.exists(self.brain_voronoi.fullName() + '.ima'):
        context.system("gzip --force " + self.brain_voronoi.fullName() + '.ima')
        context.system("gzip --force " + self.brain_voronoi.fullName() + '.dim')

   if self.Side in ('Left','Both'):
     if os.path.exists(self.left_hemi_cortex.fullName() + '.loc'):
       os.unlink( self.left_hemi_cortex.fullName() + '.loc' )
     if self.Compress_results or self.Processing_type=="Compress Results Only":
          if os.path.exists(self.left_hemi_cortex.fullName() + '.ima'):
            context.system("gzip --force " + self.left_hemi_cortex.fullName() + '.ima')
            context.system("gzip --force " + self.left_hemi_cortex.fullName() + '.dim')
          if os.path.exists(self.Lskeleton.fullName() + '.ima'):
            context.system("gzip --force " + self.Lskeleton.fullName() + '.ima')
            context.system("gzip --force " + self.Lskeleton.fullName() + '.dim')
          if os.path.exists(self.Lroots.fullName() + '.ima'):
            context.system("gzip --force " + self.Lroots.fullName() + '.ima')
            context.system("gzip --force " + self.Lroots.fullName() + '.dim')
          if os.path.exists(self.left_grey_white.fullName() + '.ima'):
            context.system("gzip --force " + self.left_grey_white.fullName() + '.ima')
            context.system("gzip --force " + self.left_grey_white.fullName() + '.dim')          
   if self.Side in ('Right','Both'):
     if os.path.exists(self.right_hemi_cortex.fullName() + '.loc'):
        os.unlink( self.right_hemi_cortex.fullName() + '.loc' )
     if self.Compress_results or self.Processing_type=="Compress Results Only":
          if os.path.exists(self.right_hemi_cortex.fullName() + '.ima'):
            context.system("gzip --force " + self.right_hemi_cortex.fullName() + '.ima')
            context.system("gzip --force " + self.right_hemi_cortex.fullName() + '.dim')
          if os.path.exists(self.Rskeleton.fullName() + '.ima'):
            context.system("gzip --force " + self.Rskeleton.fullName() + '.ima')
            context.system("gzip --force " + self.Rskeleton.fullName() + '.dim')
          if os.path.exists(self.Rroots.fullName() + '.ima'):
            context.system("gzip --force " + self.Rroots.fullName() + '.ima')
            context.system("gzip --force " + self.Rroots.fullName() + '.dim')
          if os.path.exists(self.right_grey_white.fullName() + '.ima'):
            context.system("gzip --force " + self.right_grey_white.fullName() + '.ima')
            context.system("gzip --force " + self.right_grey_white.fullName() + '.dim')          

   if self.Processing_type=="Uncompress Results Only":
      if os.path.exists(self.mri_corrected.fullName() + '.ima.gz'):
        context.system("gunzip --force " + self.mri_corrected.fullName() + '.ima')
        context.system("gunzip --force " + self.mri_corrected.fullName() + '.dim')
      if os.path.exists(self.brain_mask.fullName() + '.ima.gz'):
        context.system("gunzip --force " + self.brain_mask.fullName() + '.ima')
        context.system("gunzip --force " + self.brain_mask.fullName() + '.dim')
      if os.path.exists(self.brain_voronoi.fullName() + '.ima.gz'):
        context.system("gunzip --force " + self.brain_voronoi.fullName() + '.ima')
        context.system("gunzip --force " + self.brain_voronoi.fullName() + '.dim')
      if self.Side in ('Right','Both'):
        context.system("gunzip --force " + self.brain_mask.parent.fullPath() + '/R*.dim.gz')
        context.system("gunzip --force " + self.brain_mask.parent.fullPath() + '/R*.ima.gz')
      if self.Side in ('Left','Both'):
        context.system("gunzip --force " + self.brain_mask.parent.fullPath() + '/L*.dim.gz')
        context.system("gunzip --force " + self.brain_mask.parent.fullPath() + '/L*.ima.gz')

   if self.Processing_type=="Delete Results Only":
     if os.path.exists(self.mri_corrected.fullName() + '.loc'):
       context.write("Sorry, I can not delete ",self.mri_corrected.fullName(),', which has been locked')
     elif os.path.exists(self.mri_corrected.fullName() + '.ima') or os.path.exists(self.mri_corrected.fullName() + '.ima.gz'):
       shelltools.rm( self.mri_corrected.fullName() + '.*' )
     else:
       context.write("Sorry ", self.mri_corrected.fullName(),' does not exist on fdisk')
     if os.path.exists(self.brain_mask.fullName() + '.loc'):
       context.write("Sorry, I can not delete ",self.brain_mask.fullName(),', which has been locked')
     elif os.path.exists(self.brain_mask.fullName() + '.ima') or os.path.exists(self.brain_mask.fullName() + '.ima.gz'):
       shelltools.rm( self.brain_mask.fullName() + '.*' )
     else:
       context.write("Sorry ", self.brain_mask.fullName(),' does not exist on fdisk')
     if os.path.exists(self.brain_voronoi.fullName() + '.loc'):
       context.write("Sorry, I can not delete ",self.brain_voronoi.fullName(),', which has been locked')
     elif os.path.exists(self.brain_voronoi.fullName() + '.ima') or os.path.exists(self.brain_voronoi.fullName() + '.ima.gz'):
       shelltools.rm( self.brain_voronoi.fullName() + '.*' )
     else:
       context.write("Sorry ", self.brain_voronoi.fullName(),' does not exist on fdisk')
     if self.Side in ('Right','Both'):
       shelltools.rm( os.path.join( self.brain_mask.parent.fullPath(), 
                                    'R*.dim' ) )
       shelltools.rm( os.path.join( self.brain_mask.parent.fullPath(), 
                                    'R*.ima' ) )
       shelltools.rm( os.path.join( self.brain_mask.parent.fullPath(),
                                    'R*.dim.gz' ) )
       shelltools.rm( os.path.join( self.brain_mask.parent.fullPath(),
                                    'R*.ima.gz' ) )
     if self.Side in ('Left','Both'):
       shelltools.rm( os.path.join( self.brain_mask.parent.fullPath(),
                                    'L*.dim' ) )
       shelltools.rm( os.path.join( self.brain_mask.parent.fullPath(),
                                    'L*.ima' ) )
       shelltools.rm( os.path.join( self.brain_mask.parent.fullPath(),
                                    'L*.dim.gz' ) )
       shelltools.rm( os.path.join( self.brain_mask.parent.fullPath(),
                                    'L*.ima.gz' ) )
