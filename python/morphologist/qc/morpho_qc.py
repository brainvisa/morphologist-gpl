
'''
QC functions to check Morphologist brain segmentation and registration, from the hemispheres split image, or from the sulci graphs.
'''

from soma import aims
from soma import aimsalgo
import numpy as np


def get_mni_transform(vol):
    ''' Utility: get transform to ICBM152 space from the given volume
    '''
    hdr = vol.header()
    refs = hdr.get('referentials', [])
    iref = None
    if aims.StandardReferentials.mniTemplateReferentialID() in refs:
        iref = refs.index(aims.StandardReferentials.mniTemplateReferentialID())
    elif aims.StandardReferentials.mniTemplateReferential() in refs:
        iref = refs.index(aims.StandardReferentials.mniTemplateReferential())
    if iref is not None:
        tr = aims.AffineTransformation3d(hdr['transformations'][iref])
        return tr
    if aims.StandardReferentials.acPcReferentialID() in refs:
        iref = refs.index(aims.StandardReferentials.acPcReferentialID())
    elif aims.StandardReferentials.acPcReferential() in refs:
        iref = refs.index(aims.StandardReferentials.acPcReferential())
    if iref is None:
        raise KeyError('could not fond a transformation to ICBM152 space')
    tal_tr = aims.AffineTransformation3d(hdr['transformations'][iref])
    return aims.StandardReferentials.talairachToICBM() * tal_tr


def split_brain_overlaps(split_brain, split_template, icbm_template,
                         mni_tr=None):
    ''' Compute overlaps between a hemispheres split image (voronoi image from
    Morphologist), compared to the ICBM template brain mask, and the
    hemispheres split template of Morphologist.

    Comparisons are done in the hemispheres split template space, mainly
    because its field of view is smaller than the ICBM template (it cuts the
    cerebellum at half its height), and as the field of view of individual
    images is sometimes also cut the same way, we don't introduce a large
    mismatch by comparing to a full cerebellum.

    A first global comparison (whole brain) is done, using the ICBM template
    resampled in the split template space (as mentioned just above). Overlap,
    voxels outside the template mask, and "missing" (voxels of the template
    mask not used in the individual image) are recorded, and a jaccard
    coefficient is processed.

    Then almost the same is done for each hemisphere, using the hemispheres of
    the ICBM template. To do to, the split mask template of Morphologist is
    superimposed witht the ICBM template, and spread using a Voronoi diagram in
    order to fill the ICBM template mask.

    Results are returned as a "result" dict, with several keys:
    * 'global': global measurements
    * 'left_hemi', 'right_hemi': measurements per hemisphere
    For each a sub-directory records:

    'template_size':
        size (in voxels) of the template object to compare with
    'object size':
        size of the individual object (brain, or hemisphere)
    'union':
        size of the union of individual object and template object
    'overlap':
        size of the overlap between individual object and template object
    'outside':
        voxels of the individual object not inside the template object mask
    'missing':
        voxels of the template object not filled with the individual object
    'jaccard':
        jaccard coefficient = overap / union

    '''
    if isinstance(split_brain, str):
        split_brain = aims.read(split_brain)
    if isinstance(split_template, str):
        split_template = aims.read(split_template)
    if isinstance(icbm_template, str):
        icbm_template = aims.read(icbm_template)
    else:
        icbm_template = aims.Volume(icbm_template)  # copy before modification

    if mni_tr is None:
        mni_tr = get_mni_transform(split_brain)

    tpl_to_mni = get_mni_transform(split_template)
    icbm_tr = get_mni_transform(icbm_template)
    mni_to_tpl = tpl_to_mni.inverse()

    icbm_template[icbm_template.np != 0] = 1
    icbm_template = icbm_template.astype('S16')

    # ICBM in split template space (smaller field of view)

    resampler = aims.ResamplerFactory_S16().getResampler(0)
    icbm_to_tpl = mni_to_tpl * icbm_tr
    mni_in_tpl = aims.Volume(split_template)
    resampler.resample(icbm_template, icbm_to_tpl, 0, mni_in_tpl)

    vv = np.prod(split_template.getVoxelSize())  # voxel volume

    # # superimpose in split template space (smaller than ICBM)
    # vol[mni_in_tpl.np != 0] = 1

    # split_brain in split template space

    split_to_tpl = mni_to_tpl * mni_tr
    sb_in_tpl_l = aims.Volume(split_template)
    resampler.resample(split_brain, split_to_tpl, 0, sb_in_tpl_l)

    # closing
    sb_in_tpl = aims.Volume(sb_in_tpl_l)
    sb_in_tpl[sb_in_tpl.np != 0] = 32767
    mm = aimsalgo.MorphoGreyLevel_S16()
    sb_in_tpl = mm.doClosing(sb_in_tpl, 8)

    result = {}
    warnings = {}
    result['warnings'] = warnings

    # global: compare to MNI template in split template space
    tpl_sz = len(np.where(mni_in_tpl.np != 0)[0])
    sb_sz = len(np.where(sb_in_tpl.np != 0)[0])
    overlap = len(np.where(np.logical_and(sb_in_tpl.np != 0,
                                          mni_in_tpl.np != 0))[0])
    union = len(np.where(np.logical_or(sb_in_tpl.np != 0,
                                       mni_in_tpl.np != 0))[0])
    jaccard = overlap / union
    out = len(np.where(np.logical_and(sb_in_tpl.np != 0,
                                      mni_in_tpl.np == 0))[0])
    missing = len(np.where(np.logical_and(sb_in_tpl.np == 0,
                                          mni_in_tpl.np != 0))[0])

    rglob = {}
    result['global'] = rglob
    rglob['template_size'] = tpl_sz * vv
    rglob['object size'] = sb_sz * vv
    rglob['union'] = union * vv
    rglob['overlap'] = overlap * vv
    rglob['outside'] = out * vv
    rglob['missing'] = missing * vv
    rglob['jaccard'] = jaccard

    if jaccard < 0.7:
        warnings['global_jaccard'] = f'global jaccard is too low: {jaccard}'
    if out / tpl_sz > 0.15:
        warnings['global_outside'] = \
            f'global object too much outside: {out / tpl_sz}'
    if missing / tpl_sz > 0.15:
        warnings['global_missing'] = \
            f'global object too much missing: {missing / tpl_sz}'

    # project labels in icbm in split template space
    tpl2 = aims.Volume(split_template)
    tpl2[mni_in_tpl.np == 0] = 0  # mask with icbm
    tpl2[np.logical_and(mni_in_tpl.np != 0, tpl2.np == 0)] = 10
    # voronoi
    fm = aims.FastMarching()
    fm.doit(tpl2, [10], [1, 2, 3])
    tpl_mni = fm.voronoiVol()

    sb_in_tpl_l[np.logical_and(sb_in_tpl.np != 0, sb_in_tpl_l.np == 0)] = 10
    fm.doit(sb_in_tpl_l, [10], [1, 2, 3])
    sb_in_tpl = fm.voronoiVol()

    # per hemi
    for hemi, label in [['left', 2], ['right', 1]]:
        rhemi = {}
        result[f'{hemi}_hemi'] = rhemi

        tpl_sz = len(np.where(tpl_mni.np == label)[0])
        sb_sz = len(np.where(sb_in_tpl.np == label)[0])
        overlap = len(np.where(np.logical_and(sb_in_tpl.np == label,
                                              tpl_mni.np == label))[0])
        union = len(np.where(np.logical_or(sb_in_tpl.np == label,
                                           tpl_mni.np == label))[0])
        jaccard = overlap / union
        out = len(np.where(np.logical_and(sb_in_tpl.np == label,
                                          tpl_mni.np != label))[0])
        missing = len(np.where(np.logical_and(sb_in_tpl.np != label,
                                              tpl_mni.np == label))[0])

        rhemi['template_size'] = tpl_sz * vv
        rhemi['object size'] = sb_sz * vv
        rhemi['union'] = union * vv
        rhemi['overlap'] = overlap * vv
        rhemi['outside'] = out * vv
        rhemi['missing'] = missing * vv
        rhemi['jaccard'] = jaccard

        if jaccard < 0.7:
            warnings['global_jaccard'] = \
                f'global jaccard is too low: {jaccard}'
        if out / tpl_sz > 0.15:
            warnings['global_outside'] = \
                f'global object too much outside: {out / tpl_sz}'
        if missing / tpl_sz > 0.15:
            warnings['global_missing'] = \
                f'global object too much missing: {missing / tpl_sz}'

    return result


def graphs_overlaps(lgraph, rgraph, split_template, icbm_template):
    ''' Compute overlaps between sulcal graphs, compared to the ICBM template
    brain mask, and the hemispheres split template of Morphologist.

    A sulci voxels image is computed in the hemispheres split space, and closed
    using a large closing distance (20 mm). Then the same procedure as
    split_brain_overlaps() is used for this closed image.

    Global Overlaps are normally lower than the ones from a hemispheres split
    image, since the cerebellum is missing in the sulcal graphs. For this
    reason, warning about global measurements are not included in the returned
    result, but only those for hemispheres.
    '''

    if isinstance(lgraph, str):
        lgraph = aims.read(lgraph)
    if isinstance(rgraph, str):
        rgraph = aims.read(rgraph)
    lbb = lgraph['boundingbox_max']
    rbb = rgraph['boundingbox_max']
    close = 20
    bb = [max(x, y) + close + 5 for x, y in zip(lbb, rbb)]
    gtal = aims.GraphManip.talairach(lgraph)
    gmni = aims.StandardReferentials.talairachToICBM() * gtal
    gvol = aims.Volume(bb, dtype='S16')
    gvol.header()['referentials'] \
        = [aims.StandardReferentials.mniTemplateReferentialID()]
    gvol.header()['transformations'] = [gmni.toVector()]
    gvol.header()['voxel_size'] = lgraph['voxel_size']
    gvol.fill(0)

    # print graphs
    c = aims.RawConverter_BucketMap_VOID_rc_ptr_Volume_S16()
    mm = aimsalgo.MorphoGreyLevel_S16()
    for graph, label in ((lgraph, 2), (rgraph, 1)):
        vol = aims.Volume(gvol)
        vol.fill(0)
        for v in graph.vertices():
            for bn in ('aims_ss', 'aims_bottom', 'aims_other'):
                bk = v.get(bn)
                if bk is not None:
                    c.printToVolume(bk, vol)
        for e in graph.edges():
            for bn in ('aims_junction', 'aims_cortical', 'aims_plidepassage'):
                bk = v.get(bn)
                if bk is not None:
                    c.printToVolume(bk, vol)
        vol[vol.np == 1] = 32767
        # close a large amount to fill the hemisphere
        vol = mm.doClosing(vol, close)
        gvol[vol.np != 0] = label

    result = split_brain_overlaps(gvol, split_template, icbm_template, gmni)
    # remove global warning since we miss the cerebellum
    for w in list(result['warnings'].keys()):
        if w.startswith('global_'):
            del result['warnings'][w]
    return result
