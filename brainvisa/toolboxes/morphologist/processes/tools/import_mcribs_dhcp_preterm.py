# -*- coding: utf-8 -*-
from __future__ import print_function
from brainvisa.processes import *
from brainvisa import registration
from brainvisa.processing import fsl_run
from soma import aims, aimsalgo
import os.path as osp
import numpy as np


name = 'Import MCRIBS dHCP preterm subject into a brainvisa database'
userLevel = 2


signature = Signature(
    'session_dir', ReadDiskItem('Directory', 'Directory'),
    't1mri', WriteDiskItem('Raw T1 MRI', 'aims writable volume formats'),
    'normalization_type', Choice('mcribs_fsl', 'morphologist',
                                 'in_source_image'),
    'normalization_source_image',
    ReadDiskItem('Raw T1 MRI', 'aims readable volume formats'),
    'input_normalization',
    ReadDiskItem('Transform Raw T1 MRI to Talairach-MNI template-SPM',
                 'Transformation matrix'),
    'use_fsl', Boolean(),
    'referential', WriteDiskItem('Referential of Raw T1 MRI', 'Referential'),
    't1mri_nobias', WriteDiskItem('T1 MRI Bias Corrected',
                                  'aims writable volume formats'),
    'split_brain', WriteDiskItem('Split Brain Mask',
                                 'Aims writable volume formats'),
    'skull_stripped', WriteDiskItem('Raw T1 MRI Brain Masked',
                                    'Aims writable volume formats'),
    'skull_stripped_template', ReadDiskItem(
        'anatomical Template',
        ['NIFTI-1 image', 'MINC image', 'SPM image'],
        requiredAttributes={'skull_stripped': 'yes'}),
    'template_to_mni_transform', ReadDiskItem('Transformation matrix',
                                              'Transformation matrix'),
    'mni_transform', WriteDiskItem(
        'Transform Raw T1 MRI to Talairach-MNI template-SPM',
        'Transformation matrix'),
    'normalized_referential', ReadDiskItem('Referential', 'Referential'),
    'talairach_transformation', WriteDiskItem(
        'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
        'Transformation matrix'),
    'spm_transformation', WriteDiskItem("SPM2 normalization matrix",
                                        'Matlab file'),
    'normalized_t1mri', WriteDiskItem("Raw T1 MRI",
                                      ['NIFTI-1 image', 'SPM image'],
                                      {"normalization": "SPM"}),
    'commissure_coordinates', WriteDiskItem('Commissure coordinates',
                                            'Commissure coordinates'),
    'histo_analysis', WriteDiskItem('Histo Analysis', 'Histo Analysis'),
    'histo', WriteDiskItem('Histogram', 'Histogram'),
    'left_grey_white', WriteDiskItem('Left Grey White Mask',
                                     'Aims writable volume formats'),
    'right_grey_white', WriteDiskItem('Right Grey White Mask',
                                      'Aims writable volume formats'),
    'left_white_mesh', WriteDiskItem('Left Hemisphere White Mesh',
                                     'Aims mesh formats'),
    'right_white_mesh', WriteDiskItem('Right Hemisphere White Mesh',
                                      'Aims mesh formats'),
    'left_pial_mesh', WriteDiskItem('Left Hemisphere Mesh',
                                    'Aims mesh formats'),
    'right_pial_mesh', WriteDiskItem('Right Hemisphere Mesh',
                                     'Aims mesh formats'),
    'transform_chain_ACPC_to_Normalized', ListOf(
        ReadDiskItem('Transformation', 'Transformation matrix')),
    'acpc_referential', ReadDiskItem('Referential', 'Referential'),
    'histo_undersampling', Choice('2', '4', '8', '16', '32', 'auto',
                                  'iteration'),
    'run_morphologist', Choice('run', 'show', 'none'),
)


def initialization(self):
    def linkNormRef(proc, param):
        trManager = registration.getTransformationManager()
        if proc.mni_transform:
            s = proc.mni_transform.get('destination_referential', None)
            if s:
                return trManager.referential(s)
        return trManager.referential(registration.talairachMNIReferentialId)

    def linkACPC_to_norm(proc, param):
        trManager = registration.getTransformationManager()
        if proc.normalized_referential:
            try:
                id = proc.normalized_referential.uuid()
            except Exception:
                return []
            _mniToACPCpaths = trManager.findPaths(
                registration.talairachACPCReferentialId, id)
            for x in _mniToACPCpaths:
                return x
            else:
                return []

    self.setOptional('acpc_referential', 'template_to_mni_transform',
                     'normalization_source_image', 'input_normalization')
    self.linkParameters('referential', 't1mri')
    self.linkParameters('t1mri_nobias', 't1mri')
    self.linkParameters('split_brain', 't1mri')
    self.linkParameters('skull_stripped', 't1mri')
    self.linkParameters('mni_transform', 't1mri')
    self.linkParameters('talairach_transformation', 't1mri')
    self.linkParameters('spm_transformation', 't1mri')
    self.linkParameters('commissure_coordinates', 't1mri')
    self.linkParameters('normalized_t1mri', 't1mri')
    self.linkParameters('histo_analysis', 't1mri')
    self.linkParameters('histo', 't1mri')
    self.linkParameters('left_grey_white', 't1mri')
    self.linkParameters('right_grey_white', 't1mri')
    self.linkParameters('left_white_mesh', 't1mri')
    self.linkParameters('right_white_mesh', 't1mri')
    self.linkParameters('left_pial_mesh', 't1mri')
    self.linkParameters('right_pial_mesh', 't1mri')
    self.linkParameters('normalized_referential',
                        'mni_transform', linkNormRef)
    self.linkParameters('transform_chain_ACPC_to_Normalized',
                        'normalized_referential', linkACPC_to_norm)
    self.skull_stripped_template = '/neurospin/grip/external_databases/dHCP_CR_JD_2018/Projects/denis/release3_templates/template_t2.nii.gz'
    #self.skull_stripped_template \
        #= self.signature['skull_stripped_template'].findValue({
            #'_database': os.path.normpath(os.path.join(
                #neuroConfig.getSharePath(),
                #'brainvisa-share-%s.%s'
                    #% tuple(versionString().split('.')[:2]))),
            #'Size': '2 mm'})
    trManager = registration.getTransformationManager()
    self.acpc_referential = trManager.referential(
        registration.talairachACPCReferentialId)
    self.histo_undersampling = 'auto'


def execution(self, context):
    tm = registration.getTransformationManager()

    sessd = self.session_dir.fullPath()
    subjd = osp.dirname(sessd)

    subject = osp.basename(subjd)[4:]
    session = osp.basename(sessd)[4:]

    att = {
        'subject': subject,
        'session': session,
    }
    context.write(att)

    to_try = ['sub-%(subject)s_ses-%(session)s_desc-restore_T2w.nii.gz',
              'sub-%(subject)s_ses-%(session)s_desc-restore_T2w.nii',
              'sub-%(subject)s_ses-%(session)s_T2w_restore.nii.gz',
              'sub-%(subject)s_ses-%(session)s_T2w_restore.nii']
    for t2w_s in to_try:
        t2w = osp.join(sessd, 'anat',t2w_s % att)
        if osp.exists(t2w):
            break
    else:
        raise FileNotFoundError('The input T2w image cannot be found')
    context.write('T2w:', t2w)
    context.runProcess('ImportT1MRI', input=t2w, output=self.t1mri,
                       referential=self.referential)
    context.system('AimsFileConvert', self.t1mri, self.t1mri_nobias)
    tm.copyReferential(self.t1mri, self.t1mri_nobias)

    dseg = osp.join(sessd, 'anat',
                   'sub-%(subject)s_ses-%(session)s_desc-ribbon_dseg.nii'
                   % att)
    if not osp.exists(dseg):
        dseg += '.gz'
    use_all_labels = False
    if osp.exists(dseg):
        context.system('AimsFileConvert', dseg, self.left_grey_white,
                       '-t', 'S16')
        context.system('AimsReplaceLevel', '-i', self.left_grey_white,
                       '-o', self.split_brain,
                       '-g', 2, '-g', 3, '-g', 41, '-g', 42,
                       '-n', 2, '-n', 2, '-n', 1, '-n', 1)
    else:
        # no ribbon image, look for tissue_labels instead
        context.write('no "ribbon" image, using all_labels instead.')
        use_all_labels = True
        dseg = osp.join(
            sessd, 'anat',
            'sub-%(subject)s_ses-%(session)s_drawem_all_labels.nii'
            % att)
        if not osp.exists(dseg):
            dseg += '.gz'
        if not osp.exists(dseg):
            raise FileNotFoundError(
                'No ribbon / tissues segmentation image found')
        labels = {
            'rgm': [6, 8, 10, 12, 14, 16, 20, 22, 24, 26, 28, 30, 32, 34, 36,
                    38, ],
            'rwm': [2, 4, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62,
                    63, 65, 67, 69, 71, 73, 75, 77, 79, 81, 85, 86,
                    148, 184, 185 ],
            'lwm': [1, 3, 41, 43, 45, 47, 48, 49, 51, 53, 55, 57, 59, 61,
                    64, 66, 68, 70, 72, 74, 76, 78, 80, 82, 85, 87, ],
            'lgm': [5, 7, 9, 11, 13, 15, 21, 23, 25, 27, 29, 31, 33, 35, 37,
                    39, ],
        }
        context.system('AimsFileConvert', dseg, self.left_grey_white,
                       '-t', 'S16')
        seg = aims.read(self.left_grey_white.fullPath())
        aseg = aims.Volume(seg)
        seg.fill(0)
        repl = {l: 1 for l in labels['rgm']}
        repl.update({l: 1 for l in labels['rwm']})
        repl.update({l: 2 for l in labels['lgm']})
        repl.update({l: 2 for l in labels['lwm']})
        aims.Replacer_S16.replace(aseg, seg, repl)

        # labels 48, 84, 85 are not lateralized. We need to close the left
        # hemisphere and fill it
        ch = aims.Volume(seg.shape, [2, 2, 2], dtype='S16')
        ch.copyHeaderFrom(seg.header())
        ch.fill(0)
        ch[seg.np == 1] = 32767
        mm = aimsalgo.MorphoGreyLevel_S16()
        cl = mm.doClosing(ch, 10)
        for label in (48, 85):
            w = np.where(aseg.np == label)
            w2 = np.where(cl[w] == 32767)
            seg[tuple(y[w2] for y in w)] = 1
            aseg[tuple(y[w2] for y in w)] = 100 + label
            labels['rwm'].remove(label)

        ch.fill(0)
        ch[seg.np == 1] = 32767
        cl = mm.doErosion(ch, 2)
        ch.fill(0)
        ch[seg.np == 2] = 32767
        cl2 = mm.doErosion(ch, 2)
        ch.fill(0)
        ch[seg.np != 0] = 10
        ch[cl.np != 0] = 1
        ch[cl2.np != 0] = 2
        del cl, cl2
        fm = aims.FastMarching('6')
        fm.doit(ch, [10], [1, 2])
        seg = fm.voronoiVol()
        del ch

        aims.write(seg, self.split_brain.fullPath())

    tm.copyReferential(self.t1mri, self.split_brain)

    # normalization: several methods...

    if self.normalization_type == 'mcribs_fsl':
        # extract normalization transformation and AC/PC file

        template_to_t2_fsl = osp.join(
            sessd, 'xfm',
            'sub-%(subject)s_ses-%(session)s_from-serag40wk_to-T2w_mode-'
            'image.nii.gz' % att)
        if not osp.exists(template_to_t2_fsl):
            template_to_t2_fsl = osp.join(
                sessd, 'anat', 'xfms',
                'sub-%(subject)s_ses-%(session)s_std40w2anat.nii.gz' % att)
        if self.use_fsl:
            # if FSL is allowed/available, use fnirtfileutils to get a
            # deformation field without the affine part, and we will estimate
            # the affine .trm from the difference between warp fields (with and
            # without affine).
            tmp_templ_to_t2_wo_aff = context.temporary('NIFTI-1 image')
            context.write('get FSL warping field affine part...')
            cmd = ['fnirtfileutils',
                   '-r', t2w, '-o', tmp_templ_to_t2_wo_aff.fullPath(),
                   '-i', template_to_t2_fsl, '-f', 'field']
            fsl_run.run_fsl_command(context, cmd)
            context.system('cartoLinearComb.py', '-i', template_to_t2_fsl,
                           '-i', tmp_templ_to_t2_wo_aff.fullPath(),
                           '-o', tmp_templ_to_t2_wo_aff.fullPath(),
                           '-f', 'I1-I2')
            template_to_t2_fsl2 = tmp_templ_to_t2_wo_aff.fullPath()
        else:
            template_to_t2_fsl2 = template_to_t2_fsl

        # extract affine normalization to 40w babies template
        context.write('Estimate affine tranformation from FSL field(s)...')
        t2_to_template_name = context.temporary('Transformation matrix')
        cmd = ['-m', 'soma.aims.fsl_warp', '-i', template_to_t2_fsl2,
               '-s', self.skull_stripped_template, '-a', t2_to_template_name]
        context.pythonSystem(*cmd)

        # combine with baby template to MNI transform
        context.write('Write Talairach transform...')
        t2_to_template = aims.read(t2_to_template_name.fullPath())
        if self.template_to_mni_transform is not None:
            template_to_mni = aims.read(
                self.template_to_mni_transform.fullPath())
        else:
            template_to_mni = aims.read(
                self.skull_stripped_template.fullPath()
                + '.trmhdr?target=Talairach-MNI template-SPM')
        context.write('trans template to MNI:')
        context.write(template_to_mni)
        t2_to_mni = template_to_mni * t2_to_template
        aims.write(t2_to_mni, self.mni_transform.fullPath())

        # this alternative is less robust. Drop it.

        #context.write('running skull-stripped normalization')
        ## note: we are using split_brain.fullPath() (filename string) here because
        ## using directly the DiskItem would result in a type mismatch, and the
        ## parameter would be rejected and erased.
        #p = getProcessInstance('normalization_skullstripped')
        #p.t1mri = self.t1mri
        #p.brain_mask = self.split_brain.fullPath()
        #p.template = self.skull_stripped_template
        #p.skull_stripped = self.skull_stripped
        #p.transformation = self.mni_transform
        #p.talairach_transformation = self.talairach_transformation
        #p.commissure_coordinates = self.commissure_coordinates
        #en = p.executionNode()
        #en.Normalization.reoriented_t1mri = self.t1mri
        #en.TalairachFromNormalization.source_referential = self.referential
        #en.TalairachFromNormalization.transform_chain_ACPC_to_Normalized \
            #= self.transform_chain_ACPC_to_Normalized
        #en.TalairachFromNormalization.acpc_referential = self.acpc_referential
        #en.Normalization.NormalizeSPM.spm_transformation = self.spm_transformation
        #en.Normalization.NormalizeSPM.normalized_t1mri = self.normalized_t1mri

        #context.runProcess(p)

    elif self.normalization_type == 'morphologist':
        # read .trm from a source morphologist file, and write it back
        t2_to_mni = aims.read(self.input_normalization.fullPath())
        aims.write(t2_to_mni, self.mni_transform.fullPath())

    elif self.normalization_type == 'in_source_image':
        # read it in an image header
        t2_to_mni = aims.read(
            '{}.trmhdr?target=Talairach-MNI template-SPM'.format(
                self.normalization_source_image.fullPath()))
        aims.write(t2_to_mni, self.mni_transform.fullPath())

    else:
        # unknown normalization method
        raise ValueError(
            'unknown normalization method {}'.format(self.normalization_type))

    context.runProcess('TalairachTransformationFromNormalization',
                       normalization_transformation=self.mni_transform,
                       Talairach_transform=self.talairach_transformation,
                       commissure_coordinates=self.commissure_coordinates,
                       t1mri=self.t1mri,
                       source_referential=self.referential,
                       normalized_referential=self.normalized_referential,
                       transform_chain_ACPC_to_Normalized
                           =self.transform_chain_ACPC_to_Normalized,
                       acpc_referential=self.acpc_referential)

    context.write('Import segmentations...')
    if use_all_labels:
        seg.fill(0)
        repl = {l: 100 for l in labels['lgm']}
        repl.update({l: 200 for l in labels['lwm']})
        aims.Replacer_S16.replace(aseg, seg, repl)
        aims.write(seg, self.left_grey_white.fullPath())
        seg.fill(0)
        repl = {l: 100 for l in labels['rgm']}
        repl.update({l: 200 for l in labels['rwm']})
        aims.Replacer_S16.replace(aseg, seg, repl)
        aims.write(seg, self.right_grey_white.fullPath())

    else:
        context.system('AimsReplaceLevel', '-i', self.left_grey_white,
                       '-o', self.left_grey_white,
                       '-g', 2, '-g', 3, '-g', 41, '-g', 42,
                       '-n', 200, '-n', 100, '-n', 0, '-n', 0)
        context.system('AimsFileConvert', dseg, self.right_grey_white,
                       '-t', 'S16')
        context.system('AimsReplaceLevel', '-i', self.right_grey_white,
                       '-o', self.right_grey_white,
                       '-g', 2, '-g', 3, '-g', 41, '-g', 42,
                       '-n', 0, '-n', 0, '-n', 200, '-n', 100)
    tm.copyReferential(self.t1mri, self.left_grey_white)
    tm.copyReferential(self.t1mri, self.right_grey_white)

    context.runProcess('NobiasHistoAnalysis',
                       t1mri_nobias=self.t1mri_nobias,
                       use_hfiltered=False,
                       use_wridges=False,
                       histo_analysis=self.histo_analysis,
                       histo=self.histo,
                       undersampling=self.histo_undersampling)


    to_try = ['anat/sub-%(subject)s_ses-%(session)s_hemi-left_wm.surf.gii',
              'anat/Native/sub-%(subject)s_ses-%(session)s_left_white.surf.gii']
    for lhm_s in to_try:
        lhm = osp.join(sessd, lhm_s % att)
        if osp.exists(lhm):
            break
    else:
        raise FileNotFoundError('The input left white mesh cannot be found')
    context.write('lhm:', lhm)
    # meshes seem to be in scanner-based ref
    context.system('AimsApplyTransform', '-i', lhm, '-o', self.left_white_mesh,
                   '-d', '%s.trmhdr?index=0&inv=1' % self.t1mri.fullPath())
    mesh = aims.read(self.left_white_mesh.fullPath())
    aims.SurfaceManip.invertSurfacePolygons(mesh)
    aims.write(mesh, self.left_white_mesh.fullPath())
    tm.copyReferential(self.t1mri, self.left_white_mesh)

    to_try = ['anat/sub-%(subject)s_ses-%(session)s_hemi-right_wm.surf.gii',
              'anat/Native/sub-%(subject)s_ses-%(session)s_right_white.surf.gii']
    for rhm_s in to_try:
        rhm = osp.join(sessd, rhm_s % att)
        if osp.exists(rhm):
            break
    else:
        raise FileNotFoundError('The input right white mesh cannot be found')
    context.write('rhm:', rhm)
    context.system('AimsApplyTransform', '-i', rhm,
                   '-o', self.right_white_mesh,
                   '-d', '%s.trmhdr?index=0&inv=1' % self.t1mri.fullPath())
    mesh = aims.read(self.right_white_mesh.fullPath())
    aims.SurfaceManip.invertSurfacePolygons(mesh)
    aims.write(mesh, self.right_white_mesh.fullPath())
    tm.copyReferential(self.t1mri, self.right_white_mesh)

    to_try = ['anat/sub-%(subject)s_ses-%(session)s_hemi-left_pial.surf.gii',
              'anat/Native/sub-%(subject)s_ses-%(session)s_left_pial.surf.gii']
    for lhm_s in to_try:
        lhm = osp.join(sessd, lhm_s % att)
        if osp.exists(lhm):
            break
    else:
        context.warning('The input left pial mesh cannot be found')
    do_l_pial = True
    do_r_pial = True
    if osp.exists(lhm):
        context.system('AimsApplyTransform', '-i', lhm,
                       '-o', self.left_pial_mesh,
                       '-d', '%s.trmhdr?index=0&inv=1' % self.t1mri.fullPath())
        mesh = aims.read(self.left_pial_mesh.fullPath())
        aims.SurfaceManip.invertSurfacePolygons(mesh)
        aims.write(mesh, self.left_pial_mesh.fullPath())
        tm.copyReferential(self.t1mri, self.left_pial_mesh)
        do_l_pial = False

    to_try = ['anat/sub-%(subject)s_ses-%(session)s_hemi-right_pial.surf.gii',
              'anat/Native/sub-%(subject)s_ses-%(session)s_right_pial.surf.gii']
    for rhm_s in to_try:
        rhm = osp.join(sessd, rhm_s % att) 
        if osp.exists(rhm):
            break
    else:
        context.warning('The input right pial mesh cannot be found')
    if osp.exists(rhm):
        context.system('AimsApplyTransform', '-i', rhm,
                      '-o', self.right_pial_mesh,
                      '-d', '%s.trmhdr?index=0&inv=1' % self.t1mri.fullPath())
        mesh = aims.read(self.right_pial_mesh.fullPath())
        aims.SurfaceManip.invertSurfacePolygons(mesh)
        aims.write(mesh, self.right_pial_mesh.fullPath())
        tm.copyReferential(self.t1mri, self.right_pial_mesh)
        do_r_pial = False

    if self.run_morphologist in ('run', 'show'):

        mp = getProcessInstance('morphologist')
        en = mp.executionNode()
        en.PrepareSubject.setSelected(False)
        en.BiasCorrection.setSelected(False)
        en.HistoAnalysis.setSelected(False)
        en.BrainSegmentation.setSelected(False)
        en.Renorm.setSelected(False)
        en.SplitBrain.setSelected(False)
        en.TalairachTransformation.setSelected(False)
        en.HeadMesh.setSelected(False)

        lh = en.HemispheresProcessing.LeftHemisphere
        rh = en.HemispheresProcessing.RightHemisphere

        lh.GreyWhiteClassification.setSelected(False)
        lh.GreyWhiteMesh.setSelected(False)
        lh.PialMesh.setSelected(do_l_pial)
        rh.GreyWhiteClassification.setSelected(False)
        rh.GreyWhiteMesh.setSelected(False)
        rh.PialMesh.setSelected(do_r_pial)

        mp.t1mri = self.t1mri
        en.PrepareSubject.commissure_coordinates = self.commissure_coordinates
        mp.t1mri_nobias = self.t1mri_nobias
        mp.histo_analysis = self.histo_analysis
        mp.split_brain = self.split_brain
        lh.GreyWhiteClassification.grey_white = self.left_grey_white
        lh.CorticalFoldsGraph.white_mesh = self.left_white_mesh
        lh.CorticalFoldsGraph.pial_mesh = self.left_pial_mesh
        lh.CorticalFoldsGraph.talairach_transformation \
            = self.talairach_transformation

        if self.run_morphologist == 'show':
            from brainvisa.processing.qtgui.neuroProcessesGUI \
                import showProcess
            return mainThreadActions().call(showProcess, mp)
        else:
            context.runProcess(mp)

    else:

        context.write('<br/><b style="color: #008000">Done.</b> <b>You should '
                      'now run the Morphologist main pipeline</b> '
                      'with the following steps disabled:')
        context.write('''<ul><li>All steps before "Hemispheres processing"</li>
<li>In each hemisphere:
  <ul><li>"Grey White Classification"</li>
  <li>"Grey White Mesh"</li>
  <li>"Pial Mesh"</li></ul></ul><br/>
Or, <b>using Brainvisa >= 5.1.2</b>, run the commandline:<br/>
<tt>
axon-runprocess --enabledb morphologist t1mri=%s PrepareSubject.selected=False BiasCorrection.selected=False HistoAnalysis.selected=False BrainSegmentation.selected=False Renorm.selected=False SplitBrain.selected=False TalairachTransformation.selected=False HeadMesh.selected=False HemispheresProcessing.LeftHemisphere.GreyWhiteClassification.selected=False HemispheresProcessing.LeftHemisphere.GreyWhiteMesh.selected=False HemispheresProcessing.LeftHemisphere.PialMesh.selected=%s HemispheresProcessing.RightHemisphere.GreyWhiteClassification.selected=False HemispheresProcessing.RightHemisphere.GreyWhiteMesh.selected=False HemispheresProcessing.RightHemisphere.PialMesh.selected=%s
</tt>''' % (self.t1mri.fullPath(), str(do_l_pial), str(do_r_pial)))

