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

from brainvisa.processes import *
from brainvisa import registration
from brainvisa.tools import aimsGlobals
from soma import aims
from soma.aims import apctools
import numpy
import glob
import threading
from soma.qt_gui.qtThread import MainThreadLife
try:
    from soma.utils.functiontools import partial
except ImportError:
    # axon 4.4
    from soma.functiontools import partial

name = 'Import MNI CIVET Segmentation'
roles = ('importer',)
userLevel = 3

signature = Signature(
    'input_raw_t1_mri', ReadDiskItem('Raw T1 MRI',
        'Aims readable volume formats'),
    'input_bias_corrected', ReadDiskItem('T1 MRI Bias Corrected',
        'Aims readable volume formats'),
    'input_brain_mask', ReadDiskItem('T1 Brain Mask',
        'Aims readable volume formats'),
    'input_grey_white', ReadDiskItem('Grey White Mask',
        'Aims readable volume formats'),
    'use_civet_segmentations_in_mni_space', Boolean(),
    'input_T1_to_MNI_transformation',
      ReadDiskItem('MINC transformation matrix',
                   'MINC transformation matrix'),
    'input_white_mesh_left', ReadDiskItem('Hemisphere white mesh',
                                          'aims mesh formats'),
    'input_white_mesh_right', ReadDiskItem('Hemisphere white mesh',
                                          'aims mesh formats'),
    'input_pial_mesh_left', ReadDiskItem('Hemisphere mesh',
                                        'aims mesh formats'),
    'input_pial_mesh_right', ReadDiskItem('Hemisphere mesh',
                                          'aims mesh formats'),
    'grey_white_classif_from_meshes', Boolean(),

    'output_raw_t1_mri', WriteDiskItem('Raw T1 MRI',
        'Aims writable volume formats'),
    'output_bias_corrected', WriteDiskItem('T1 MRI Bias Corrected',
        'Aims writable volume formats'),
    'output_T1_to_Talairach_transformation',
      WriteDiskItem('Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
        'Transformation matrix'),
    'output_ACPC', WriteDiskItem('Commissure coordinates',
      'Commissure coordinates'),
    'output_brain_mask', WriteDiskItem('T1 Brain Mask',
        'Aims writable volume formats'),
    'output_left_grey_white', WriteDiskItem('Left Grey White Mask',
        'Aims writable volume formats'),
    'output_right_grey_white', WriteDiskItem('Right Grey White Mask',
        'Aims writable volume formats'),
    'use_t1pipeline', Choice(('graphically', 0), ('in batch', 1),
        ('don\'t use it', 2)),
    'transform_Talairach_to_MNI', ReadDiskItem('Transformation matrix',
                                               'Transformation matrix'),
)


def initialization(self):

    def initSubject(self, proc):
        value = self.output_raw_t1_mri
        if self.input_raw_t1_mri is not None \
                and isinstance(self.input_raw_t1_mri, DiskItem):
            value=self.input_raw_t1_mri.hierarchyAttributes()
            if value.get("subject", None) is None:
                value["subject"] = os.path.basename(
                    self.input_raw_t1_mri.fullPath()).partition(".")[0]
        if value is None:
            value = self.output_raw_t1_mri
        return value

    def linknuc(self, proc):
        if self.input_raw_t1_mri is not None:
            return self.input_raw_t1_mri.fullName() + '_nuc.mnc'

    def linkimask(self, proc):
        if self.input_grey_white is not None:
            # if the G/W segmentation is available, don't use the mask
            # since the mask generally has the cerebellum removed
            # and SplitBrain will not work
            return None
        if self.input_raw_t1_mri is not None:
            v = self.signature['input_brain_mask'].findValue(
                self.input_raw_t1_mri)
            if v is not None:
                return v
            b = os.path.dirname(self.input_raw_t1_mri.fullPath())
            if os.path.basename(b) == 'native':
                b = os.path.dirname(b)
            b = os.path.join(b, 'mask')
            g = glob.glob(os.path.join(b, '*_mask.mnc*'))
            if len(g) == 1:
                return g[0]

    def linkigw(self, proc):
        if self.input_raw_t1_mri is not None:
            v = self.signature['input_grey_white'].findValue(
                self.input_raw_t1_mri)
            if v is not None:
                return v
            b = os.path.dirname(self.input_raw_t1_mri.fullPath())
            if os.path.basename(b) == 'native':
                b = os.path.dirname(b)
            b = os.path.join(b, 'classify')
            # the cls_clean image is skull-stripped, which is better
            g = glob.glob(os.path.join(b, '*_cls_clean.mnc*'))
            if len(g) == 0:
                # the classify image is not skull-stripped, and contains grey
                # and white matter labels in the external head parts (scalp,
                # fat, etc)
                g = glob.glob(os.path.join(b, '*_classify.mnc*'))
            if len(g) == 0:
                bfinal = os.path.join(b, 'temp')
                gfinal = glob.glob(os.path.join(bfinal,
                                                '*_final_classify.mnc*'))
                if len(gfinal) != 0:
                  g = gfinal
            if len(g) == 1:
                return g[0]

    def linkitrans(self, proc):
        if self.input_raw_t1_mri is not None:
            v = self.signature['input_T1_to_MNI_transformation'].findValue(
                self.input_raw_t1_mri)
            if v is not None:
                return v
            b = os.path.dirname(self.input_raw_t1_mri.fullPath())
            if os.path.basename(b) == 'native':
                b = os.path.dirname(b)
            b = os.path.join(b, 'transforms', 'linear')
            g = glob.glob(os.path.join(b, '*_t1_tal.xfm'))
            if len(g) == 1:
                return g[0]

    def linkmesh(mesh_type, hemisphere, self, proc):
        if self.input_raw_t1_mri is not None:
            b = os.path.dirname( self.input_raw_t1_mri.fullPath() )
            if os.path.basename( b ) == 'native':
                b = os.path.dirname( b )
            b = os.path.join(b, 'surfaces')
            g = glob.glob(os.path.join(b, '*_%s_surface_%s_*.obj'
                                      % (mesh_type, hemisphere)))
            if len(g) != 0:
                return g[0]

    def linkusegwmeshes(self, proc):
        if self.input_white_mesh_left is not None \
                and self.input_white_mesh_right is not None \
                and self.input_pial_mesh_left is not None \
                and self.input_pial_mesh_right is not None:
            return True
        else:
            return False

    self.setOptional('input_raw_t1_mri', 'input_bias_corrected',
        'input_brain_mask', 'input_grey_white',
        'input_T1_to_MNI_transformation',
        'input_white_mesh_left', 'input_white_mesh_right',
        'input_pial_mesh_left', 'input_pial_mesh_right')
    self.setOptional('output_brain_mask', 'output_left_grey_white',
        'output_right_grey_white', 'output_T1_to_Talairach_transformation',
        'output_ACPC')

    self.linkParameters('input_bias_corrected', 'input_raw_t1_mri', linknuc)
    self.linkParameters('input_grey_white', 'input_raw_t1_mri', linkigw)
    self.linkParameters('input_brain_mask',
                        ('input_raw_t1_mri', 'input_grey_white'), linkimask)
    self.linkParameters('input_T1_to_MNI_transformation', 'input_raw_t1_mri',
                        linkitrans)
    self.linkParameters('input_white_mesh_left', 'input_raw_t1_mri',
                        partial(linkmesh, 'white', 'left'))
    self.linkParameters('input_white_mesh_right', 'input_raw_t1_mri',
                        partial(linkmesh, 'white', 'right'))
    self.linkParameters('input_pial_mesh_left', 'input_raw_t1_mri',
                        partial(linkmesh, 'gray', 'left'))
    self.linkParameters('input_pial_mesh_right', 'input_raw_t1_mri',
                        partial(linkmesh, 'gray', 'right'))
    self.linkParameters("output_raw_t1_mri", "input_raw_t1_mri", initSubject)
    self.linkParameters('output_bias_corrected', 'output_raw_t1_mri')
    self.linkParameters('output_T1_to_Talairach_transformation',
                        'output_raw_t1_mri')
    self.linkParameters('output_ACPC', 'output_raw_t1_mri')
    self.linkParameters('output_brain_mask', 'output_bias_corrected')
    self.linkParameters('output_left_grey_white', 'output_brain_mask')
    self.linkParameters('output_right_grey_white', 'output_left_grey_white')
    self.linkParameters('grey_white_classif_from_meshes',
                        ['input_white_mesh_left', 'input_pial_mesh_left',
                         'input_pial_mesh_left', 'input_pial_mesh_right'],
                        linkusegwmeshes)
    self.transform_Talairach_to_MNI \
        = signature['transform_Talairach_to_MNI'].findValue(
            {'filename_variable': 'talairach_TO_spm_template_novoxels'})


def buildGWimage(self, context, dims, input_white_mesh, input_pial_mesh,
                 mni_to_t1, grey_white, white_mesh,
                 pial_mesh):
    mesh_dir = os.path.dirname(white_mesh.fullPath())
    context.write('mesh_dir:', mesh_dir)
    if not os.path.exists(mesh_dir):
        context.write('create dir')
        safemkdir.makedirs(mesh_dir)
    white = aims.read(input_white_mesh.fullPath())
    aims.SurfaceManip.meshTransform(white, mni_to_t1)
    aims.write(white, white_mesh.fullPath())
    pial = aims.read(input_pial_mesh.fullPath())
    aims.SurfaceManip.meshTransform(pial, mni_to_t1)
    aims.write(pial, pial_mesh.fullPath())
    context.write('written:', pial_mesh)
    context.write('<font color="#60ff60">'
        + _t_('White/pial meshes imported.') + '</font>')

    if self.grey_white_classif_from_meshes \
            and hasattr(aims.SurfaceManip, 'rasterizeMesh'):
        gw_vol = aims.Volume(*dims, dtype='S16')
        gw_vol.fill(32737)
        aims.SurfaceManip.rasterizeMesh(white, gw_vol, 0)
        del white
        temp1 = context.temporary('gz compressed NIFTI-1 image')
        temp2 = context.temporary('gz compressed NIFTI-1 image')
        aims.write(gw_vol, temp1.fullPath())
        w_vol = gw_vol
        context.system('AimsConnectComp', '-i', temp1, '-o', temp2, '-c', 6,
                       '-n', 1, '-b')
        gw_vol.fill(32737)
        aims.SurfaceManip.rasterizeMesh(pial, gw_vol, 0)
        del pial
        aims.write(gw_vol, temp1.fullPath())
        gw_vol = aims.read(temp2.fullPath())
        gw = numpy.asarray(gw_vol)
        gw[gw==0] = 200
        gw[numpy.asarray(w_vol)==0] = 100 # mesh is in GM
        context.system('AimsConnectComp', '-i', temp1, '-o', temp2, '-c', 6,
                       '-n', 1, '-b')
        pial_cc = aims.read(temp2.fullPath())
        pial_a = numpy.asarray(pial_cc)
        gw[pial_a==1] = 0
        gw[gw==1] = 100
        aims.write(gw_vol, grey_white.fullPath())
        context.write('<font color="#60ff60">'
            + _t_('Grey/White classification imported from meshes.')
            + '</font>')


def import_t1(self, context, trManager):

    mridone = False
    t1aims2mni = None
    if self.input_raw_t1_mri is None and self.input_bias_corrected is not None:
        context.write(_t_('Taking bias corrected as raw T1 MRI.'))
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
        context.progress( 1, self.nsteps, self )
        if mridone:
            context.write('<font color="#60ff60">' \
                + _t_('Raw T1 MRI inserted.') + '</font>')
            if self.input_T1_to_MNI_transformation is not None:
              # import / convert transformation to MNI space
              context.write(_t_('import transformation'))
              m = []
              i = 0
              rl = False
              for l in open(
                    self.input_T1_to_MNI_transformation.fullPath(
                        )).xreadlines():
                  if l.startswith('Linear_Transform ='):
                      rl = True
                  elif rl:
                      if l.endswith(';\n'):
                          l = l[:-2]
                      m.append([float(x) for x in l.split()])
                      i += 1
                      if i == 3:
                          break
              t12mni = aims.AffineTransformation3d(
                  numpy.array(m + [[0., 0., 0., 1.]]))
              t1aims2t1 = aims.AffineTransformation3d(
                  aimsGlobals.aimsVolumeAttributes(
                      self.output_raw_t1_mri)['transformations' ][-1])
              t1aims2mni = t12mni * t1aims2t1
              acpcDI = neuroHierarchy.databases.getDiskItemFromUuid(
                  registration.talairachACPCReferentialId)
              mniReferential = trManager.referential(
                  registration.talairachMNIReferentialId)
              mniDI = neuroHierarchy.databases.getDiskItemFromUuid(
                  mniReferential.uuid())
              if self.output_T1_to_Talairach_transformation is not None:
                  trm = context.temporary('Transformation matrix')
                  aims.write(t1aims2mni, trm.fullPath())
                  context.runProcess(
                      'TalairachTransformationFromNormalization',
                      normalization_transformation=trm,
                      Talairach_transform
                          =self.output_T1_to_Talairach_transformation,
                      commissure_coordinates=self.output_ACPC,
                      t1mri=self.output_raw_t1_mri,
                      source_referential=trManager.referential(
                          self.output_raw_t1_mri ),
                      # normalized_referential=mniDI, # why doesn't this work ??
                  )
                  self.output_T1_to_Talairach_transformation.lockData()
    else:
        context.write('<font color="#a0a060">' + \
            _t_('Raw T1 MRI not written.') + '</font>')

    return mridone, t1aims2mni


def import_bias_corrected(self, context):

    nobiasdone = False
    if self.output_bias_corrected is not None:
        context.write('importing bias corrected MRI...')
        if self.input_bias_corrected is not None:
            if self.output_brain_mask is not None \
                    and self.use_civet_segmentations_in_mni_space \
                    and (self.input_brain_mask is not None
                         or self.input_grey_white is not None):
                nobias = context.temporary('gz compressed NIFTI-1 image')
            else:
                nobias = self.output_bias_corrected
            context.system('AimsFileConvert',
                '-i', self.input_bias_corrected,
                '-o', nobias, '-t', 'S16',
                '-r', '--omin', 0, '--omax', 4095)
            if nobias is self.output_bias_corrected:
                tm = registration.getTransformationManager()
                tm.copyReferential(self.output_raw_t1_mri,
                                   self.output_bias_corrected)
            nobiasdone = True
        else:
            context.warning(_t_('output_bias_corrected could not be written: '
              'no possible source'))
            nobias = None
    else:
        context.write('<font color="#a0a060">'
            + _t_('Bias corrected MRI not written.') + '</font>')

    return nobiasdone, nobias


def import_mask(self, context, t1aims2mni, mridone, nobiasdone, nobias,
                trManager):

    maskdone = False
    if self.output_brain_mask:
        context.write(_t_('importing brain mask...'))
        if self.input_brain_mask is not None:
            context.system('AimsFileConvert', '-o', self.output_brain_mask,
                '-i', self.input_brain_mask, '-t', 'S16')
            context.system('cartoLinearComb.py', '-o', self.output_brain_mask,
                '-f', 'I1*255', '-i', self.output_brain_mask)
            maskdone = True
        elif self.input_grey_white is not None:
            # no brain mask. Use with the cortex segmentation
            context.write('importing mask from G/W segmentation...')
            context.system('AimsFileConvert', '-o', self.output_brain_mask,
                '-i', self.input_grey_white, '-t', 'S16')
            context.system('AimsThreshold', '-i', self.output_brain_mask,
                '-o', self.output_brain_mask, '-t', 48, '-b', '-m', 'ge', '-p')
            maskdone = True
        else:
            context.write('<font color="#a0a060">'
                + _t_('Brain mask not written: no possible source')
                + '</font>')
        context.write('<font color="#60ff60">'
            + _t_('Brain mask inserted.') + '</font>')

        context.progress(4, self.nsteps, self)

        mask2t1 = None

        if maskdone and self.use_civet_segmentations_in_mni_space:
            # the mask is normalized, and has info to get to MNI space
            # but is resampled in a different resolution and FOV from the
            # original image. To keep the mask, we resample the T1/nobias
            # images to the mask space.
            mref = trManager.referential(self.output_raw_t1_mri)
            tr = aims.AffineTransformation3d(aimsGlobals.aimsVolumeAttributes(
                self.output_brain_mask)['transformations'][-1])
            if t1aims2mni and (self.output_bias_corrected is not None \
                    or self.output_raw_t1_mri is not None):
                # resample raw T1 and bias corrected image
                t12mask = tr.inverse() * t1aims2mni
                trm = context.temporary('Transformation Matrix')
                aims.write(t12mask, trm.fullPath())
                context.runProcess('transformAPC',
                    Commissure_coordinates=self.output_ACPC,
                    T1mri=self.output_raw_t1_mri,
                    output_coordinates=self.output_ACPC,
                    transformation=trm,
                    destination_volume=self.output_brain_mask)
                if nobiasdone:
                    context.write(_t_('Resampling bias corrected volume to '
                      'the mask space...'))
                    context.system('AimsResample', '-i', nobias,
                        '-o', self.output_bias_corrected, '-m', trm,
                        '-r', self.output_brain_mask)
                    trManager.copyReferential(self.output_raw_t1_mri,
                        self.output_bias_corrected)
                    context.write('<font color="#60ff60">'
                        + _t_('Bias corrected MRI inserted.') + '</font>')
                if mridone:
                    context.write(_t_(
                        'Resampling raw T1 volume to the mask space...'))
                    old_vs = aimsGlobals.aimsVolumeAttributes(
                        self.output_raw_t1_mri)['voxel_size']
                    new_vs = aimsGlobals.aimsVolumeAttributes(
                        self.output_brain_mask)['voxel_size']
                    temp = context.temporary('gz compressed NIFTI-1 image')
                    context.system(
                        'AimsFileConvert', '-i', self.output_raw_t1_mri,
                        '-o', temp)
                    context.system(
                        'AimsResample', '-i', temp,
                        '-o', self.output_raw_t1_mri, '-m', trm,
                        '-r', self.output_brain_mask)
                # update the T1 -> ACPC transform
                t12acpc = aims.read(
                    self.output_T1_to_Talairach_transformation.fullPath()) \
                    * t12mask.inverse()
                aims.write(t12acpc,
                    self.output_T1_to_Talairach_transformation.fullPath())
                # change .APC voxel size
                apc = apctools.apcRead(self.output_ACPC.fullPath())
                for pt in ('ac', 'pc', 'ih'):
                    ac = apc[pt]
                    ac[0] = int(round(ac[0] * old_vs[0] / new_vs[0]))
                    ac[1] = int(round(ac[1] * old_vs[1] / new_vs[1]))
                    ac[2] = int(round(ac[2] * old_vs[2] / new_vs[2]))
                apctools.apcWrite(apc, self.output_ACPC.fullPath())
                self.output_ACPC.lockData()
            trManager.copyReferential(
                self.output_raw_t1_mri, self.output_brain_mask)

        elif maskdone:
            # resample brain mask to native space
            self.output_ACPC.lockData()
            mref = trManager.referential(self.output_raw_t1_mri)
            tr = aims.AffineTransformation3d(aimsGlobals.aimsVolumeAttributes(
                self.output_brain_mask)['transformations'][-1])
            if t1aims2mni and (self.output_bias_corrected is not None \
                    or self.output_raw_t1_mri is not None):
                # resample mask
                if self.output_bias_corrected is not None:
                    native = self.output_bias_corrected
                else:
                    native = self.output_raw_t1_mri
                mask2t1 = t1aims2mni.inverse() * tr
                trm = context.temporary('Transformation Matrix')
                aims.write(mask2t1, trm.fullPath())
                context.write(_t_('Resampling brain mask volume to '
                  'native space...'))
                context.system('AimsResample',
                    '-i', self.output_brain_mask,
                    '-o', self.output_brain_mask, '-m', trm,
                    '-r', native, '-t', 'n')
                context.write('<font color="#60ff60">'
                    + _t_('Brain mask resampled.') + '</font>')
        trManager.copyReferential(
            self.output_raw_t1_mri, self.output_brain_mask)

    return maskdone, mask2t1


def import_grey_white(self, context, gw_from_meshes, t1pipeline, trManager,
                      mask2t1):

    have_gw = False
    if gw_from_meshes:
        return True
    if self.output_right_grey_white is not None \
            or self.output_left_grey_white is not None:
        context.write(_t_('importing grey/white segmentation...'))
        if self.input_grey_white:
            gw = context.temporary('NIFTI-1 image', '3D Volume')
            context.system('AimsFileConvert', '-i', self.input_grey_white,
                           '-o', gw, '-t', 'S16')
            context.system(
                'AimsReplaceLevel', '-i', gw, '-o', gw,
                '-g', 1, '-n', 0, '-g', 2, '-n', 100, '-g', 3, '-n', 200,
                '-g', 255, '-n', 200, '-g', 170, '-n', 100)
            clgm = context.temporary('NIFTI-1 image', '3D Volume')
            ## apply little closing on GM
            #context.system( 'AimsReplaceLevel', '-i', gw, '-o', clgm,
              #'-g', 1, '-n', 0, '-g', 2, '-n', 100, '-g', 3, '-n', 0 )
            #context.system( 'AimsClosing', '-i', clgm, '-o', clgm, '-r', 1.3 )
            #context.system( 'AimsReplaceLevel', '-i', gw, '-o', gw,
              #'-g', 1, '-n', 0, '-g', 2, '-n', 200, '-g', 3, '-n', 200 )
            #context.system( 'AimsMask', '-i', gw,
                #'-o', gw, '-m', clgm, '-d', 100, '--inv' )
            mask = context.temporary('NIFTI-1 image')
            enode = t1pipeline.executionNode()
            if mask2t1 is not None:
                # native space transform
                temp = context.temporary('Transformation matrix')
                aims.write(mask2t1, temp.fullPath())
                if mask2t1 is not None:
                    # resample to native space
                    context.system('AimsResample',
                                   '-i', gw, '-o', gw,
                                   '-m', temp, '-r', self.output_brain_mask,
                                   '-t', 'n')
            if self.output_left_grey_white is not None:
                context.system(
                    'AimsThreshold',
                    '-i', enode.SplitBrain._process.split_brain, '-o', mask,
                    '-t', 2, '-m', 'eq')
                context.system('AimsMask', '-i', gw,
                    '-o', self.output_left_grey_white, '-m', mask)
                trManager.copyReferential(self.output_brain_mask,
                    self.output_left_grey_white)
                self.output_left_grey_white.lockData()
            if self.output_right_grey_white is not None:
                context.system(
                    'AimsThreshold',
                    '-i', enode.SplitBrain._process.split_brain, '-o', mask,
                    '-t', 1, '-m', 'eq' )
                context.system(
                    'AimsMask', '-i', gw, '-o', self.output_right_grey_white,
                    '-m', mask)
                trManager.copyReferential(self.output_brain_mask,
                                          self.output_right_grey_white)
                self.output_right_grey_white.lockData()
            if self.output_right_grey_white is not None \
                    and self.output_left_grey_white is not None:
                have_gw = True
        else:
            context.write('<font color="#a0a060">'
                + _t_('G/W segmentation not written: no possible source')
                + '</font>')
    return have_gw


def execution( self, context ):

    pi, p = context.getProgressInfo(self)
    #pi.children = [None] * 3
    context.progress()

    nsteps = 8
    self.nsteps = nsteps
    trManager = registration.getTransformationManager()

    mridone, t1aims2mni = self.import_t1(context, trManager)
    context.progress(1, nsteps, self)

    nobiasdone, nobias = self.import_bias_corrected(context)
    context.progress(2, nsteps, self)

    maskdone, mask2t1 = self.import_mask(context, t1aims2mni, mridone,
                                         nobiasdone, nobias, trManager)
    context.progress(4, nsteps, self)

    if mridone:
      self.output_raw_t1_mri.lockData()
    #if nobiasdone:
      #self.output_bias_corrected.lockData()
    if maskdone:
      self.output_brain_mask.lockData()

    t1pipeline = getProcessInstance('morphologist')
    t1pipeline.t1mri = self.output_raw_t1_mri
    t1pipeline.t1mri_nobias = self.output_bias_corrected
    enode = t1pipeline.executionNode()
    #npi, proc = context.getProgressInfo(enode, parent=pi)
    #context.progress()
    enode.PrepareSubject.setSelected(False)
    if hasattr(enode, 'Renorm'):
        enode.Renorm.setSelected(False)
    if nobiasdone:
        enode.BiasCorrection.mode = 'write_minimal without correction'
    if maskdone:
        enode.BrainSegmentation.setSelected(False)
    enode.TalairachTransformation.setSelected(False)
    enode.HeadMesh.setSelected(False)
    enode.HemispheresProcessing.setSelected(False)

    have_meshes = False
    gw_from_meshes = False
    if self.input_white_mesh_left and self.input_white_mesh_right \
            and self.input_pial_mesh_left and self.input_pial_mesh_right:
        have_meshes = True
        context.write('using meshes.')
        f = aims.Finder()
        if self.output_raw_t1_mri:
            f.check(self.output_raw_t1_mri.fullPath())
        else:
            f.check(self.output_bias_corrected.fullPath())
        dims = f.header()['volume_dimension'][:3]
        t1_to_tal \
            = aims.read(self.output_T1_to_Talairach_transformation.fullPath())
        tal_to_mni = aims.read(self.transform_Talairach_to_MNI.fullPath())
        mni_to_t1 = t1_to_tal.inverse() * tal_to_mni.inverse()
        gw_left \
            = enode.HemispheresProcessing.LeftHemisphere.GreyWhiteClassification.grey_white
        gw_right \
            = enode.HemispheresProcessing.RightHemisphere.GreyWhiteClassification.grey_white
        context.write('importing left hemisphere meshes')
        self.buildGWimage(
            context, dims, self.input_white_mesh_left,
            self.input_pial_mesh_left,
            mni_to_t1, gw_left,
            enode.HemispheresProcessing.LeftHemisphere.GreyWhiteMesh.white_mesh,
          enode.HemispheresProcessing.LeftHemisphere.PialMesh.pial_mesh)
        context.progress(5, nsteps, self)
        context.write('importing right hemisphere meshes')
        self.buildGWimage(
            context, dims, self.input_white_mesh_right,
            self.input_pial_mesh_right,
            mni_to_t1, gw_right,
            enode.HemispheresProcessing.RightHemisphere.GreyWhiteMesh.white_mesh,
            enode.HemispheresProcessing.RightHemisphere.PialMesh.pial_mesh)
        if self.grey_white_classif_from_meshes \
                and hasattr(soma.aims.SurfaceManip, 'rasterizeMesh'):
            gw_from_meshes = True
            enode.SplitBrain.setSelected(False)
            split = aims.read(gw_left.fullPath())
            split_a = numpy.asarray(split)
            split_a[split_a==200] = 1
            split_a[split_a==100] = 1
            gw_r = aims.read(gw_right.fullPath())
            gw_a = numpy.asarray(gw_r)
            split_a[gw_a==200] = 2
            split_a[gw_a==100] = 2
            del gw_a, gw_r, split_a
            aims.write(split, enode.SplitBrain.split_brain.fullPath())
            del split
            trManager.copyReferential(self.output_raw_t1_mri,
                                      enode.SplitBrain.split_brain)
            trManager.copyReferential(self.output_raw_t1_mri, gw_left)
            trManager.copyReferential(self.output_raw_t1_mri, gw_right)
            enode.SplitBrain.split_brain.lockData()
            gw_left.lockData()
            gw_right.lockData()
            context.progress(6, nsteps, self)

        trManager.copyReferential(
            self.output_raw_t1_mri,
            enode.HemispheresProcessing.LeftHemisphere.GreyWhiteMesh.white_mesh
        )
        trManager.copyReferential(
            self.output_raw_t1_mri,
            enode.HemispheresProcessing.RightHemisphere.GreyWhiteMesh.white_mesh)
        trManager.copyReferential(
            self.output_raw_t1_mri,
            enode.HemispheresProcessing.LeftHemisphere.PialMesh.pial_mesh)
        trManager.copyReferential(
            self.output_raw_t1_mri,
            enode.HemispheresProcessing.RightHemisphere.PialMesh.pial_mesh)
        enode.HemispheresProcessing.LeftHemisphere.GreyWhiteMesh.white_mesh.lockData()
        enode.HemispheresProcessing.RightHemisphere.GreyWhiteMesh.white_mesh.lockData()
        enode.HemispheresProcessing.LeftHemisphere.PialMesh.pial_mesh.lockData()
        enode.HemispheresProcessing.RightHemisphere.PialMesh.pial_mesh.lockData()

    if not gw_from_meshes:
        # if GW segmentation is built from meshes, we will run the pipeline
        # only once globally, at the end.
        # if GW segmentation is not built from meshes, we have to run the split
        # step before doing the next step.
        context.write(_t_('Running a first pass of the missing T1 pipeline '
            'steps to recover bias correction, histogram analysis, '
            'brain split.'))
        if self.use_t1pipeline == 0:
            pv = mainThreadActions().call(ProcessView, t1pipeline)
            r = context.ask('run the pipeline, then click here', 'OK', 'Abort')
            mainThreadActions().call(pv.close)
            # the following ensures pv is deleted in the main thread, and not
            # in the current non-GUI thread.
            mtobj = MainThreadLife(pv)
            del pv
            del mtobj
            if r != 0:
                raise context.UserInterruption()
        elif self.use_t1pipeline == 1:
          context.runProcess(t1pipeline)
        else:
          context.write(
            '<font color="#a0a060">'
            + _t_('Pipeline not run since the "use_t1pipeline" parameter '
                  'prevents it') + '</font>')
        context.write('OK')
        context.progress(5, nsteps, self)

        have_gw = self.import_grey_white(context, gw_from_meshes, t1pipeline,
                                         trManager, mask2t1)
        context.progress(6, nsteps, self)

        context.write(_t_('Now run the last part of the regular T1 pipeline.'))

        t1pipeline = getProcessInstance('morphologist')
        t1pipeline.t1mri = self.output_raw_t1_mri
        t1pipeline.t1mri_nobias = self.output_bias_corrected
        enode = t1pipeline.executionNode()

        enode.PrepareSubject.setSelected(False)
        if hasattr(enode, 'Renorm'):
            enode.Renorm.setSelected(False)
        enode.BiasCorrection.setSelected(False)
        enode.HistoAnalysis.setSelected(False)
        enode.BrainSegmentation.setSelected(False)

    enode.SplitBrain.setSelected(False)
    enode.HemispheresProcessing.setSelected(True)
    enode.TalairachTransformation.setSelected(False)
    if have_gw:
        enode.HemispheresProcessing.LeftHemisphere.GreyWhiteClassification.setSelected(False)
        enode.HemispheresProcessing.RightHemisphere.GreyWhiteClassification.setSelected(False)
    enode.HemispheresProcessing.LeftHemisphere.GreyWhiteTopology.setSelected(
        True)
    enode.HemispheresProcessing.RightHemisphere.GreyWhiteTopology.setSelected(
        True)
    enode.HemispheresProcessing.LeftHemisphere.GreyWhiteMesh.setSelected(
        True)
    enode.HemispheresProcessing.RightHemisphere.GreyWhiteMesh.setSelected(
        True)
    enode.HemispheresProcessing.LeftHemisphere.SulciSkeleton.setSelected(
        True)
    enode.HemispheresProcessing.RightHemisphere.SulciSkeleton.setSelected(
        True)
    enode.HemispheresProcessing.LeftHemisphere.PialMesh.setSelected(True)
    enode.HemispheresProcessing.RightHemisphere.PialMesh.setSelected(True)
    enode.HeadMesh.setSelected(True)
    enode.HemispheresProcessing.LeftHemisphere.CorticalFoldsGraph.setSelected(
        True)
    enode.HemispheresProcessing.RightHemisphere.CorticalFoldsGraph.setSelected(
        True)
    if have_meshes:
        enode.HemispheresProcessing.LeftHemisphere.GreyWhiteMesh.setSelected(
            False)
        enode.HemispheresProcessing.RightHemisphere.GreyWhiteMesh.setSelected(
            False)
        enode.HemispheresProcessing.LeftHemisphere.PialMesh.setSelected(False)
        enode.HemispheresProcessing.RightHemisphere.PialMesh.setSelected(False)

    context.write(_t_('Running a second pass of the missing T1 pipeline '
        'steps to recover cortex, meshes and sulci graphs.'))
    if self.use_t1pipeline == 0:
        pv = mainThreadActions().call(ProcessView, t1pipeline)
        r = context.ask('run the pipeline, then click here', 'OK')
        mainThreadActions().call(pv.close)
        # the following ensures pv is deleted in the main thread, and not
        # in the current non-GUI thread.
        mtobj = MainThreadLife(pv)
        del pv
        del mtobj
    elif self.use_t1pipeline == 1:
        context.runProcess(t1pipeline)
    else:
        context.write('<font color="#a0a060">'
            + _t_('Pipeline not run since the "use_t1pipeline" parameter '
                  'prevents it' ) + '</font>')
    context.write('OK')
    self.output_T1_to_Talairach_transformation.unlockData()
    self.output_ACPC.unlockData()
    self.output_raw_t1_mri.unlockData()
    self.output_bias_corrected.unlockData()
    self.output_brain_mask.unlockData()
    self.output_left_grey_white.unlockData()
    self.output_right_grey_white.unlockData()
    context.progress(8, nsteps, self)

