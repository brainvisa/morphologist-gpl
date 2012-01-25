# -*- coding: utf-8 -*-
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
import registration
import shfjGlobals
from soma import aims
import numpy
import glob
import threading

name = 'Import MNI CIVET Segmentation'
roles = ('importer',)
userLevel = 3

signature = Signature(
  'input_raw_t1_mri', ReadDiskItem( 'Raw T1 MRI',
      'Aims readable volume formats' ),
  'input_bias_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
      'Aims readable volume formats' ),
  'input_brain_mask', ReadDiskItem( 'T1 Brain Mask',
      'Aims readable volume formats' ),
  'input_grey_white', ReadDiskItem( 'Grey White Mask',
      'Aims readable volume formats' ),
  'input_T1_to_MNI_transformation',
    ReadDiskItem( 'MINC transformation matrix', 'MINC transformation matrix' ),

  'output_raw_t1_mri', WriteDiskItem( 'Raw T1 MRI',
      'Aims writable volume formats' ),
  'output_bias_corrected', WriteDiskItem( 'T1 MRI Bias Corrected',
      'Aims writable volume formats'),
  'output_T1_to_Talairach_transformation',
    WriteDiskItem( 'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
      'Transformation matrix'),
  'output_ACPC', WriteDiskItem( 'Commissure coordinates',
    'Commissure coordinates' ),
  'output_brain_mask', WriteDiskItem( 'T1 Brain Mask',
      'Aims writable volume formats' ),
  'output_left_grey_white', WriteDiskItem( 'Left Grey White Mask',
      'Aims writable volume formats' ),
  'output_right_grey_white', WriteDiskItem( 'Right Grey White Mask',
      'Aims writable volume formats' ),
  'use_t1pipeline', Choice( ( 'graphically', 0 ), ( 'in batch', 1 ),
      ( 'don\'t use it', 2 ) )
)

def initSubject( self, inp ):
  value=self.output_raw_t1_mri
  if self.input_raw_t1_mri is not None and isinstance(self.input_raw_t1_mri,
    DiskItem):
    value=self.input_raw_t1_mri.hierarchyAttributes()
    if value.get("subject", None) is None:
      value["subject"]=os.path.basename(self.input_raw_t1_mri.fullPath()\
        ).partition(".")[0]
  if value is None:
    value = self.output_raw_t1_mri
  return value

def initialization( self ):
  def linkimask( self, proc ):
    if self.input_grey_white is not None:
      # if the G/W segmentation is available, don't use the mask
      # since the mask generally has the cerebellum removed
      # and SplitBrain will not work
      return None
    if self.input_raw_t1_mri is not None:
      v = self.signature[ 'input_brain_mask' ].findValue(
        self.input_raw_t1_mri )
      if v is not None:
        return v
      b = os.path.dirname( self.input_raw_t1_mri.fullPath() )
      if os.path.basename( b ) == 'native':
        b = os.path.dirname( b )
      b = os.path.join( b, 'mask' )
      g = glob.glob( os.path.join( b, '*_mask.mnc*' ) )
      if len(g) == 1:
        return g[0]
  def linkigw( self, proc ):
    if self.input_raw_t1_mri is not None:
      v = self.signature[ 'input_grey_white' ].findValue(
        self.input_raw_t1_mri )
      if v is not None:
        return v
      b = os.path.dirname( self.input_raw_t1_mri.fullPath() )
      if os.path.basename( b ) == 'native':
        b = os.path.dirname( b )
      bfinal = os.path.join( b, 'temp' )
      gfinal = glob.glob( os.path.join( bfinal, '*_final_classify.mnc*' ) )
      if len( gfinal ) != 0:
        g = gfinal
      else:
        b = os.path.join( b, 'classify' )
        g = glob.glob( os.path.join( b, '*_classify.mnc*' ) )
      if len(g) == 1:
        return g[0]
  def linkitrans( self, proc ):
    if self.input_raw_t1_mri is not None:
      v = self.signature[ 'input_T1_to_MNI_transformation' ].findValue(
        self.input_raw_t1_mri )
      if v is not None:
        return v
      b = os.path.dirname( self.input_raw_t1_mri.fullPath() )
      if os.path.basename( b ) == 'native':
        b = os.path.dirname( b )
      b = os.path.join( b, 'transforms', 'linear' )
      g = glob.glob( os.path.join( b, '*_t1_tal.xfm' ) )
      if len(g) == 1:
        return g[0]

  self.setOptional( 'input_raw_t1_mri', 'input_bias_corrected',
    'input_brain_mask', 'input_grey_white', 'input_T1_to_MNI_transformation' )
  self.setOptional( 'output_brain_mask', 'output_left_grey_white',
    'output_right_grey_white', 'output_T1_to_Talairach_transformation',
    'output_ACPC' )

  self.linkParameters( 'input_bias_corrected', 'input_raw_t1_mri' )
  self.linkParameters( 'input_grey_white', 'input_raw_t1_mri', linkigw )
  self.linkParameters( 'input_brain_mask', ( 'input_raw_t1_mri',
    'input_grey_white' ), linkimask )
  self.linkParameters( 'input_T1_to_MNI_transformation', 'input_raw_t1_mri',
    linkitrans )
  self.linkParameters( "output_raw_t1_mri", "input_raw_t1_mri", self.initSubject )
  self.linkParameters( 'output_bias_corrected', 'output_raw_t1_mri' )
  self.linkParameters( 'output_T1_to_Talairach_transformation',
    'output_raw_t1_mri' )
  self.linkParameters( 'output_ACPC', 'output_raw_t1_mri' )
  self.linkParameters( 'output_brain_mask', 'output_bias_corrected' )
  self.linkParameters( 'output_left_grey_white', 'output_brain_mask' )
  self.linkParameters( 'output_right_grey_white', 'output_left_grey_white' )


def delInMainThread( lock, thing ):
  # wait for the lock to be released in the process thread
  lock.acquire()
  lock.release()
  # now the process thread should have removed its reference on thing:
  # we can safely delete it fom here, in the main thread.
  del thing # probably useless


def execution( self, context ):
  pi, p = context.getProgressInfo( self )
  pi.children = [ None ] * 3
  context.progress()

  nsteps = 8
  mridone = False
  nobiasdone = False
  maskdone = False
  t12mni = None
  t1aims2mni = None
  trManager = registration.getTransformationManager()
  mniReferential = trManager.referential(
    registration.talairachMNIReferentialId )

  if self.input_raw_t1_mri is None and self.input_bias_corrected is not None:
    context.write( _t_( 'Taking bias corrected as raw T1 MRI.' ) )
    self.input_raw_t1_mri = self.input_bias_corrected

  if self.output_raw_t1_mri is not None:
    context.write( _t_( 'importing raw T1 MRI...' ) )
    if self.input_raw_t1_mri is not None:
      context.runProcess( 'ImportT1MRI', input=self.input_raw_t1_mri,
        output=self.output_raw_t1_mri )
      mridone = True
    else:
      context.warning( _t_( 'output raw T1 MRI could not be written: ' \
        'no possible source' ) )
    context.progress( 1, nsteps, self )
    if mridone:
      context.write( '<font color="#60ff60">' \
        + _t_( 'Raw T1 MRI inserted.' ) + '</font>' )
      if self.input_T1_to_MNI_transformation is not None:
        # import / convert transformation to MNI space
        context.write( _t_( 'import transformation' ) )
        m = []
        i = 0
        rl = False
        for l in open( self.input_T1_to_MNI_transformation.fullPath() \
          ).xreadlines():
          if l.startswith( 'Linear_Transform =' ):
            rl = True
          elif rl:
            if l.endswith( ';\n' ):
              l = l[:-2]
            m.append( [ float(x) for x in l.split() ] )
            i += 1
            if i == 3:
              break
        t12mni = aims.AffineTransformation3d( numpy.array( m \
          + [[ 0., 0., 0., 1. ]] ) )
        t1aims2t1 = aims.AffineTransformation3d( \
          shfjGlobals.aimsVolumeAttributes( self.output_raw_t1_mri ) \
          [ 'transformations' ][-1] )
        t1aims2mni = t12mni * t1aims2t1
        acpcDI = neuroHierarchy.databases.getDiskItemFromUuid(
          registration.talairachACPCReferentialId )
        mniDI = neuroHierarchy.databases.getDiskItemFromUuid(
          mniReferential.uuid() )
        if self.output_T1_to_Talairach_transformation is not None:
          trm = context.temporary( 'Transformation matrix' )
          aims.write( t1aims2mni, trm.fullPath() )
          context.runProcess( 'TalairachTransformationFromNormalization',
            normalization_transformation=trm,
            Talairach_transform=self.output_T1_to_Talairach_transformation,
            Commissure_coordinates=self.output_ACPC,
            t1mri=self.output_raw_t1_mri,
            source_referential=trManager.referential( self.output_raw_t1_mri ),
            # normalized_referential=mniDI, # why doesn't this work ??
            )
          self.output_T1_to_Talairach_transformation.lockData()
  else:
    context.write( '<font color="#a0a060">' + \
      _t_( 'Raw T1 MRI not written.' ) + '</font>' )
  context.progress( 2, nsteps, self )

  if self.output_bias_corrected is not None:
    context.write( 'importing bias corrected MRI...' )
    if self.input_bias_corrected is not None:
      context.system( 'AimsFileConvert',
        '-i', self.input_bias_corrected,
        '-o', self.output_bias_corrected, '-t', 'S16',
        '-r', '--omin', 0, '--omax', 4095 )
      nobiasdone = True
      trManager.copyReferential( self.output_raw_t1_mri,
        self.output_bias_corrected )
      context.write( '<font color="#60ff60">' \
        + _t_( 'Bias corrected MRI inserted.' ) + '</font>' )
    else:
      context.warning( _t_( 'output_bias_corrected could not be written: no ' \
        'possible source' ) )
  else:
    context.write( '<font color="#a0a060">' + \
      _t_( 'Bias corrected MRI not written.' ) + '</font>' )
  context.progress( 3, nsteps, self )

  if self.output_brain_mask:
    context.write( _t_( 'importing brain mask...' ) )
    if self.input_brain_mask is not None:
      context.system( 'AimsFileConvert', '-o', self.output_brain_mask,
        '-i', self.input_brain_mask, '-t', 'S16' )
      context.system( 'cartoLinearComb.py', '-o', self.output_brain_mask,
        '-f', 'I1*255', '-i', self.output_brain_mask )
      maskdone = True
    elif self.input_grey_white is not None:
      # no brain mask. Use with the cortex segmentation
      context.write( 'importing mask from G/W segmentation...' )
      context.system( 'AimsFileConvert', '-o', self.output_brain_mask,
        '-i', self.input_grey_white, '-t', 'S16' )
      context.system( 'AimsThreshold', '-i', self.output_brain_mask,
        '-o', self.output_brain_mask, '-t', 1, '-b' )
      maskdone = True
    else:
      context.write( '<font color="#a0a060">' + \
        _t_( 'Brain mask not written: no possible source' ) + '</font>' )
    context.progress( 4, nsteps, self )

    if maskdone:
      # the mask is normalized, and has info to get to MNI space
      mref = trManager.referential( self.output_raw_t1_mri )
      tr = aims.AffineTransformation3d( shfjGlobals.aimsVolumeAttributes(
        self.output_brain_mask )[ 'transformations' ][-1] )
      context.write( '<font color="#60ff60">' \
        + _t_( 'Brain mask inserted.' ) + '</font>' )
      if t1aims2mni and ( self.output_bias_corrected is not None \
        or self.output_raw_t1_mri is not None ):
        # resample raw T1 and bias corrected image
        t12mask = tr.inverse() * t1aims2mni
        trm = context.temporary( 'Transformation Matrix' )
        aims.write( t12mask, trm.fullPath() )
        context.runProcess( 'transformAPC',
          Commissure_coordinates=self.output_ACPC,
          T1mri=self.output_raw_t1_mri, output_coordinates=self.output_ACPC,
          transformation=trm, destination_volume=self.output_brain_mask )
        self.output_ACPC.lockData()
        if nobiasdone:
          context.write( _t_(
            'Resampling bias corrected volume to the mask space...' ) )
          context.system( 'AimsResample', '-i', self.output_bias_corrected,
            '-o', self.output_bias_corrected, '-m', trm,
            '-r', self.output_brain_mask )
        if mridone:
          context.write( _t_(
            'Resampling raw T1 volume to the mask space...' ) )
          context.system( 'AimsResample', '-i', self.output_raw_t1_mri,
            '-o', self.output_raw_t1_mri, '-m', trm,
            '-r', self.output_brain_mask )
        # update the T1 -> ACPC transform
        t12acpc = aims.read( \
          self.output_T1_to_Talairach_transformation.fullPath() ) \
          * t12mask.inverse()
        aims.write( t12acpc,
          self.output_T1_to_Talairach_transformation.fullPath() )
      trManager.copyReferential( self.output_raw_t1_mri,
        self.output_brain_mask )
  context.progress( 5, nsteps, self )

  if mridone:
    self.output_raw_t1_mri.lockData()
  if nobiasdone:
    self.output_bias_corrected.lockData()
  if maskdone:
    self.output_brain_mask.lockData()

  t1pipeline = getProcessInstance( 'morphologist' )
  t1pipeline.mri = self.output_raw_t1_mri
  t1pipeline.mri_corrected = self.output_bias_corrected
  enode = t1pipeline.executionNode()
  npi, proc = context.getProgressInfo( enode, parent=pi )
  context.progress()
  enode.PrepareSubject.setSelected( False )
  if nobiasdone:
    enode.BiasCorrection.setSelected( False )
    enode.BiasCorrection.write_hfiltered = 'no'
    enode.BiasCorrection.write_wridges = 'no'
    enode.BiasCorrection.hfiltered = None
    enode.BiasCorrection.white_ridges = None
    enode.HistoAnalysis.use_hfiltered = False
    enode.HistoAnalysis.use_wridges = False
    enode.SplitBrain.Use_ridges = False
  if maskdone:
    enode.BrainSegmentation.setSelected( False )
  enode.TalairachTransformation.setSelected( False )
  enode.GreyWhiteClassification.setSelected( False )
  enode.GreyWhiteSurface.setSelected( False )
  enode.HemispheresMesh.setSelected( False )
  enode.HeadMesh.setSelected( False )
  enode.CorticalFoldsGraph.setSelected( False )

  context.write( _t_( 'Running a first pass of the missing T1 pipeline ' \
    'steps to recover bias correction, histogram analysis, brain split.' ) )
  if self.use_t1pipeline == 0:
    pv = mainThreadActions().call( ProcessView, t1pipeline )
    r = context.ask( 'run the pipeline, then click here', 'OK', 'Abort' )
    mainThreadActions().call( pv.close )
    # the following ensures pv is deleted in the main thread, and not
    # in the current non-GUI thread. The principle is the following:
    # - acquire a lock
    # - pass the pv object to something in the main thread
    # - the main thread waits on the lock while holding a reference on pv
    # - we delete pv in the process thread
    # - the lock is releasd from the pv thread
    # - now the main thread can go on, and del / release the ref on pv: it
    #   is the last ref on pv, so it is actually deleted there.
    lock = threading.Lock()
    lock.acquire()
    mainThreadActions().push( delInMainThread, lock, pv )
    del pv
    lock.release()
    if r != 0:
      raise UserInterruption( 'Aborted.' )
  elif self.use_t1pipeline == 1:
    context.runProcess( t1pipeline )
  else:
    context.write( '<font color="#a0a060">' \
      + _t_( 'Pipeline not run since the "use_t1pipeline" parameter ' \
        'prevents it' ) + '</font>')
  context.write( 'OK')
  context.progress( 6, nsteps, self )

  if self.output_right_grey_white is not None \
    or self.output_left_grey_white is not None:
    context.write( _t_( 'importing grey/white segmentation...' ) )
    if self.input_grey_white:
      gw = context.temporary( 'NIFTI-1 image', '3D Volume' )
      context.system( 'AimsFileConvert', '-i', self.input_grey_white,
        '-o', gw, '-t', 'S16' )
      context.system( 'AimsReplaceLevel', '-i', gw, '-o', gw,
        '-g', 1, '-n', 0, '-g', 2, '-n', 100, '-g', 3, '-n', 200 )
      clgm = context.temporary( 'NIFTI-1 image', '3D Volume' )
      ## apply little closing on GM
      #context.system( 'AimsReplaceLevel', '-i', gw, '-o', clgm,
        #'-g', 1, '-n', 0, '-g', 2, '-n', 100, '-g', 3, '-n', 0 )
      #context.system( 'AimsClosing', '-i', clgm, '-o', clgm, '-r', 1.3 )
      #context.system( 'AimsReplaceLevel', '-i', gw, '-o', gw,
        #'-g', 1, '-n', 0, '-g', 2, '-n', 200, '-g', 3, '-n', 200 )
      #context.system( 'AimsMask', '-i', gw,
          #'-o', gw, '-m', clgm, '-d', 100, '--inv' )
      mask = context.temporary( 'NIFTI-1 image' )
      if self.output_right_grey_white is not None:
        context.system( 'AimsThreshold',
          '-i', enode.SplitBrain._process.split_mask, '-o', mask, '-t', 1,
          '-m', 'eq' )
        context.system( 'AimsMask', '-i', gw,
          '-o', self.output_right_grey_white, '-m', mask )
        trManager.copyReferential( self.output_brain_mask,
          self.output_right_grey_white )
        self.output_right_grey_white.lockData()
      if self.output_left_grey_white is not None:
        context.system( 'AimsThreshold',
          '-i', enode.SplitBrain._process.split_mask, '-o', mask, '-t', 2,
          '-m', 'eq' )
        context.system( 'AimsMask', '-i', gw,
          '-o', self.output_left_grey_white, '-m', mask )
        trManager.copyReferential( self.output_brain_mask,
          self.output_left_grey_white )
        self.output_left_grey_white.lockData()
    else:
      context.write( '<font color="#a0a060">' + \
        _t_( 'G/W segmentation not written: no possible source' ) + '</font>' )
  context.progress( 7, nsteps, self )

  context.write( _t_( 'Now run the last part of the regular T1 pipeline.' ) )
  enode.PrepareSubject.setSelected( False )
  enode.BiasCorrection.setSelected( False )
  enode.HistoAnalysis.setSelected( False )
  enode.BrainSegmentation.setSelected( False )
  enode.SplitBrain.setSelected( False )
  enode.TalairachTransformation.setSelected( False )
  enode.GreyWhiteClassification.setSelected( False )
  enode.GreyWhiteSurface.setSelected( True )
  enode.HemispheresMesh.setSelected( True )
  enode.HeadMesh.setSelected( True )
  enode.CorticalFoldsGraph.setSelected( True )
  # we build 3.1 graphs by default.
  enode.CorticalFoldsGraph.CorticalFoldsGraph_3_1.setSelected( True )
  context.write( _t_( 'Running a second pass of the missing T1 pipeline ' \
    'steps to recover cortex, meshes and sulci graphs.' ) )
  if self.use_t1pipeline == 0:
    pv = mainThreadActions().call( ProcessView, t1pipeline )
    r = context.ask( 'run the pipeline, then click here', 'OK' )
    mainThreadActions().call( pv.close )
    # the following ensures pv is deleted in the main thread, and not
    # in the current non-GUI thread. The principle is the following:
    # - acquire a lock
    # - pass the pv object to something in the main thread
    # - the main thread waits on the lock while holding a reference on pv
    # - we delete pv in the process thread
    # - the lock is releasd from the pv thread
    # - now the main thread can go on, and del / release the ref on pv: it
    #   is the last ref on pv, so it is actually deleted there.
    lock = threading.Lock()
    lock.acquire()
    mainThreadActions().push( delInMainThread, lock, pv )
    del pv
    lock.release()
  elif self.use_t1pipeline == 1:
    context.runProcess( t1pipeline )
  else:
    context.write( '<font color="#a0a060">' \
      + _t_( 'Pipeline not run since the "use_t1pipeline" parameter ' \
        'prevents it' ) + '</font>')
  context.write( 'OK')
  self.output_T1_to_Talairach_transformation.unlockData()
  self.output_ACPC.unlockData()
  self.output_raw_t1_mri.unlockData()
  self.output_bias_corrected.unlockData()
  self.output_brain_mask.unlockData()
  self.output_left_grey_white.unlockData()
  self.output_right_grey_white.unlockData()
  context.progress( 8, nsteps, self )

