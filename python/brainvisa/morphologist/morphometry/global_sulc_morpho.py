from soma import aims, aimsalgo
import tempfile
import os
import csv
import numpy as np


removed_labels = ['ventricle']

def global_sulcal_morphometry(l_graph, r_graph, remove_nonfold=True,
                              label_att='label'):
    ''' Record global hemisphere and brain stats from sulcal graphs.

    Graph files may be given either as :class:`~soma.aims.Graph` objects
    instances, or as filenames (.arg files).
    '''

    res = {}

    if isinstance(l_graph, str):
        try:
            l_graph = aims.read(l_graph)
        except FileNotFoundError:
            l_graph = {}
    if isinstance(r_graph, str):
        try:
            r_graph = aims.read(r_graph)
        except FileNotFoundError:
            r_graph = {}

    lrawfolds = l_graph.get('folds_area')
    lreffolds = l_graph.get('reffolds_area')
    lrawhull = l_graph.get('brain_hull_area')
    lrefhull = l_graph.get('refbrain_hull_area')
    rrawfolds = r_graph.get('folds_area')
    rreffolds = r_graph.get('reffolds_area')
    rrawhull = r_graph.get('brain_hull_area')
    rrefhull = r_graph.get('refbrain_hull_area')

    if lrawfolds is not None and lrawhull is not None:
        lrawSI = lrawfolds / lrawhull
        res['left.gi_native_space'] = lrawSI
    if lreffolds is not None and lrefhull is not None:
        lrefSI = lreffolds / lrefhull
        res['left.gi_talairach_space'] = lrefSI

    if rrawfolds is not None and rrawhull is not None:
        rrawSI = rrawfolds / rrawhull
        res['left.gi_native_space'] = rrawSI
    if rreffolds is not None and rrefhull is not None:
        rrefSI = rreffolds / rrefhull
        res['left.gi_talairach_space'] = rrefSI

    if lrawfolds is not None and rrawfolds is not None \
            and lrawhull is not None and rrawhull is not None:
        rawSI = (lrawfolds + rrawfolds) / (lrawhull + rrawhull)
        res['both.gi_native_space'] = rawSI
    if lreffolds is not None and rreffolds is not None \
            and lrefhull is not None and rrefhull is not None:
        refSI = (lreffolds + rreffolds) / (lrefhull + rrefhull)
        res['both.gi_talairach_space'] = refSI

    lgm = l_graph.get('GM_volume')
    lcsf = l_graph.get('CSF_volume')
    rgm = r_graph.get('GM_volume')
    rcsf = r_graph.get('CSF_volume')
    if lgm is not None:
        res['left.GM'] = lgm
    if rgm is not None:
        res['right.GM'] = rgm
        if lgm is not None:
            res['both.GM'] = lgm + rgm
    if lcsf is not None:
        res['left.CSF'] = lcsf
    if rcsf is not None:
        res['right.CSF'] = rcsf
        if lcsf is not None:
            res['both.CSF'] = lcsf + rcsf

    lhullv = l_graph.get('brain_hull_volume')
    lbrain = None
    rbrain = None
    if lhullv is not None and lcsf is not None:
        lbrain = lhullv - lcsf
        res['left.brain_volume'] = lbrain
    rhullv = r_graph.get('brain_hull_volume')
    if rhullv is not None and rcsf is not None:
        rbrain = rhullv - rcsf
        res['right.brain_volume'] = rbrain
    if lbrain is not None and rbrain is not None:
        res['both.brain_volume'] = lbrain + rbrain

    if remove_nonfold:
        labels_to_remove = set(removed_labels)
        labels_to_remove.update(['%s_left' % x for x in removed_labels])
        labels_to_remove.update(['%s_right' % x for x in removed_labels])

    length = [0., 0.]
    depth = [0., 0.]
    depth_mass = [0, 0]
    thick_mass = [0, 0]
    thickness = [0., 0.]
    opening = [0., 0.]
    open_mass = [0, 0]
    fold_skel = [0, 0]
    fold_skel_label = [0, 0]

    for side, graph in enumerate((l_graph, r_graph)):
        if hasattr(graph, 'vertices'):
            for v in graph.vertices():
                skel = v.get('ss_point_number', 0)
                skel += v.get('bottom_point_number', 0)
                skel += v.get('other_point_number', 0)
                skip = (remove_nonfold
                        and v.get(label_att) in labels_to_remove)
                if not skip:
                    vmass = v.get('point_number')
                    if vmass is None:
                        continue
                    vdepth = v.get('mean_depth')
                    if vdepth is not None:
                        depth[side] += vdepth * vmass
                        depth_mass[side] += vmass
                    vthick = v.get('thickness_mean')
                    if vthick is not None:
                        thickness[side] += vthick * vmass
                        thick_mass[side] += vmass
                    csf = v.get('CSF_volume')
                    surf = v.get('surface_area')
                    if csf is not None and surf is not None:
                        opening[side] += csf / surf * vmass
                        open_mass[side] += vmass

                for e in v.edges():
                    if e.getSyntax() == 'hull_junction':
                        skel += e.get('point_number', 0)
                        if not skip:
                            vlen = e['length']
                            length[side] += vlen
                fold_skel[side] += skel
                if not skip:
                    fold_skel_label[side] += skel

    if length[0] != 0.:
        res['left.fold_length'] = length[0]
    if length[1] != 0.:
        res['right.fold_length'] = length[1]
        if length[0] != 0.:
            res['both.fold_length'] = length[0] + length[1]

    if depth_mass[0] != 0.:
        res['left.mean_depth'] = depth[0] / depth_mass[0]
    if depth_mass[1] != 0.:
        res['right.mean_depth'] = depth[1] / depth_mass[1]
        if depth_mass[0] != 0.:
            res['both.mean_depth'] \
                = (depth[0] + depth[1]) / (depth_mass[0] + depth_mass[1])

    if thick_mass[0] != 0.:
        res['left.mean_thickness'] = thickness[0] / thick_mass[0]
    if thick_mass[1] != 0.:
        res['right.mean_thickness'] = thickness[1] / thick_mass[1]
        if thick_mass[0] != 0.:
            res['both.mean_thickness'] \
                = (thickness[0] + thickness[1]) / (thick_mass[0]
                                                   + thick_mass[1])

    if open_mass[0] != 0.:
        res['left.mean_opening'] = opening[0] / open_mass[0]
    if open_mass[1] != 0.:
        res['right.mean_opening'] = opening[1] / open_mass[1]
        if open_mass[0] != 0.:
            res['both.mean_opening'] \
                = (opening[0] + opening[1]) / (open_mass[0] + open_mass[1])

    if fold_skel[0] != 0:
        res['left.skel_points'] = fold_skel[0]
    if fold_skel[1] != 0:
        res['right.skel_points'] = fold_skel[1]
        if fold_skel[0] != 0:
            res['both.skel_points'] = fold_skel[0] + fold_skel[1]
            res['log_ratio.skel_points'] = np.log(fold_skel[0] / fold_skel[1])

    if fold_skel_label[0] != 0:
        res['left.skel_labelled_points'] = fold_skel_label[0]
    if fold_skel_label[1] != 0:
        res['right.skel_labelled_points'] = fold_skel_label[1]
        if fold_skel_label[0] != 0:
            res['both.skel_labelled_points'] = fold_skel_label[0] \
                + fold_skel_label[1]
            res['log_ratio.skel_labelled_points'] \
                = np.log(fold_skel_label[0] / fold_skel_label[1])

    return res


def brain_volumes(split_brain, left_grey_white, right_grey_white, left_csf,
                  right_csf):
    ''' Record global hemisphere and brain stats from segmented volumes.

    Volumes may be given either as :class:`~soma.aims.Volume_S16` objects
    instances, or as filenames (.nii files for instance).
    '''

    try:
        if isinstance(split_brain, str) and os.path.exists(split_brain):
            split_brain = aims.read(split_brain)
        if isinstance(left_grey_white, str) \
                and os.path.exists(left_grey_white):
            left_grey_white = aims.read(left_grey_white)
        if isinstance(right_grey_white, str) \
                and os.path.exists(right_grey_white):
            right_grey_white = aims.read(right_grey_white)
        if isinstance(left_csf, str) and os.path.exists(left_csf):
            left_csf = aims.read(left_csf)
        if isinstance(right_csf, str) and os.path.exists(right_csf):
            right_csf = aims.read(right_csf)
    except FileNotFoundError:
        return {}

    if split_brain is None or left_grey_white is None \
            or right_grey_white is None or left_csf is None \
            or right_csf is None:
        return {}

    # Morphological closing of the brain in order to obtain the CSF volume
    # inside sulci and thus compute an approximate TIV (ICV).
    morphm = aimsalgo.MorphoGreyLevel_S16()
    #morphm.setChamferMaskSize((3, 3, 3))
    border = morphm.neededBorderWidth()

    split_img = split_brain
    brain_closed_img = aims.Volume(split_img.getSize(), [border] * 3,
                                   dtype='S16')
    brain_closed_img.copyHeaderFrom(split_img.header())
    brain_closed_img.fill(0)
    brain_closed_img[split_img.np != 0] = 32767

    brain_closed_img = morphm.doClosing(brain_closed_img, 20)
    # On s'assure qu'il n'y a pas de trous surtout au niveau des ventricules.
    brain_closed_img.np[:] = 32767 - brain_closed_img.np
    brain_closed_img.fillBorder(32767)
    aims.AimsConnectedComponent(
        brain_closed_img, aims.Connectivity.CONNECTIVITY_6_XYZ, 0, True, 0,
        0, 1)
    brain_closed_img.np[:] = 32767 - brain_closed_img.np

    # Calcul des volumes
    if left_grey_white is not None and \
            right_grey_white is not None and \
            left_csf is not None and \
            right_csf is not None:
        lgw_img = left_grey_white
        rgw_img = right_grey_white
        lcsf_img = left_csf
        rcsf_img = right_csf
        eTIV_img = brain_closed_img

        vox_sizes = split_img.header()['voxel_size']
        vox_vol = vox_sizes[0]*vox_sizes[1]*vox_sizes[2]

        split_arr = split_img.np
        lgw_arr = lgw_img.np
        rgw_arr = rgw_img.np
        lcsf_arr = lcsf_img.np
        rcsf_arr = rcsf_img.np
        eTIV_arr = eTIV_img.np

        # Classify
        lgm_vox = (lgw_arr == 100)
        lwm_vox = (lgw_arr == 200)
        rgm_vox = (rgw_arr == 100)
        rwm_vox = (rgw_arr == 200)
        lcsf_vox = (lcsf_arr == 32767)
        rcsf_vox = (rcsf_arr == 32767)
        cerebellum_vox = (split_arr == 3)

        rh_vox = rgm_vox + rwm_vox
        lh_vox = lgm_vox + lwm_vox
        rh_closed_vox = rh_vox + rcsf_vox
        lh_closed_vox = lh_vox + lcsf_vox
        hemi_closed_vox = rh_closed_vox + lh_closed_vox

        brain_vox = (split_arr == 1) | (split_arr == 2) | (split_arr == 3)
        eTIV_vox = (eTIV_arr == 32767)

        # Calculation of the volumes
        lgm_vol = lgm_vox.sum()*vox_vol
        lwm_vol = lwm_vox.sum()*vox_vol
        rgm_vol = rgm_vox.sum()*vox_vol
        rwm_vol = rwm_vox.sum()*vox_vol
        rh_vol = rh_vox.sum()*vox_vol
        lh_vol = lh_vox.sum()*vox_vol
        cerebellum_vol = cerebellum_vox.sum()*vox_vol
        brain_vol = brain_vox.sum()*vox_vol
        rh_closed_vol = rh_closed_vox.sum()*vox_vol
        lh_closed_vol = lh_closed_vox.sum()*vox_vol
        hemi_closed_vol = hemi_closed_vox.sum()*vox_vol
        eTIV = eTIV_vox.sum()*vox_vol
    else:
        lgm_vol = 0.
        lwm_vol = 0.
        rgm_vol = 0.
        rwm_vol = 0.
        rh_vol = 0.
        lh_vol = 0.
        cerebellum_vol = 0.
        brain_vol = 0.
        rh_closed_vol = 0.
        lh_closed_vol = 0.
        hemi_closed_vol = 0.
        eTIV = 0.

    res = {}
    res['left.WM'] = lwm_vol
    res['right.WM'] = rwm_vol
    res['both.WM'] = lwm_vol + rwm_vol
    res['left.GM'] = lgm_vol
    res['right.GM'] = rgm_vol
    res['both.GM'] = lgm_vol + rwm_vol
    res['left.hemi_volume'] = lh_vol
    res['right.hemi_volume'] = rh_vol
    res['both.brain_volume'] = brain_vol
    res['both.hemi_closed_volume'] = hemi_closed_vol
    res['both.eTIV'] = eTIV
    res['both.cerebellum_stem_volume'] = cerebellum_vol

    return res


def brain_surfaces(left_gm_mesh, right_gm_mesh, left_wm_mesh, right_wm_mesh):
    '''
    '''

    if isinstance(left_gm_mesh, str) and os.path.exists(left_gm_mesh):
        try:
            left_gm_mesh = aims.read(left_gm_mesh)
        except FileNotFoundError:
            left_gm_mesh = None
    if isinstance(right_gm_mesh, str) and os.path.exists(right_gm_mesh):
        try:
            right_gm_mesh = aims.read(right_gm_mesh)
        except FileNotFoundError:
            right_gm_mesh = None
    if isinstance(left_wm_mesh, str) and os.path.exists(left_wm_mesh):
        try:
            left_wm_mesh = aims.read(left_wm_mesh)
        except FileNotFoundError:
            left_wm_mesh = None
    if isinstance(right_wm_mesh, str) and os.path.exists(right_wm_mesh):
        try:
            right_wm_mesh = aims.read(right_wm_mesh)
        except FileNotFoundError:
            right_wm_mesh = None

    res = {}
    if left_gm_mesh:
        res['left.GM_area'] = aims.SurfaceManip.meshArea(left_gm_mesh)
    if right_gm_mesh:
        res['right.GM_area'] = aims.SurfaceManip.meshArea(right_gm_mesh)
        if left_gm_mesh:
            res['both.GM_area'] = res['left.GM_area'] + res['right.GM_area']
    if left_wm_mesh:
        res['left.WM_area'] = aims.SurfaceManip.meshArea(left_wm_mesh)
    if right_wm_mesh:
        res['right.WM_area'] = aims.SurfaceManip.meshArea(right_wm_mesh)
        if left_wm_mesh:
            res['both.WM_area'] = res['left.WM_area'] + res['right.WM_area']

    return res


def sulcal_and_brain_morpho(
    left_graph, right_graph, split_brain, left_grey_white, right_grey_white,
    left_csf, right_csf, left_gm_mesh=None, right_gm_mesh=None,
    left_wm_mesh=None, right_wm_mesh=None,
    remove_nonfold=True, label_att='label'):
    ''' Record global hemisphere and brain stats from sulcal graphs and
    segmented volumes.
    The result is the addition of the results of
    :func:`global_sulcal_morphometry` and :func:`brain_volumes`.
    '''

    if left_graph is not None and right_graph is not None:
        res = global_sulcal_morphometry(
            left_graph, right_graph, remove_nonfold=remove_nonfold,
            label_att=label_att)
    else:
        res = {}
    if split_brain is not None:
        resv = brain_volumes(split_brain, left_grey_white, right_grey_white,
                             left_csf, right_csf)
        res.update(resv)
        sort_k = ('left.WM', 'right.WM', 'both.WM', 'left.GM', 'right.GM',
                  'both.GM','left.CSF', 'right.CSF', 'both.CSF',
                  'left.hemi_volume', 'right.hemi_volume', 'both.brain_volume',
                  'both.hemi_closed_volume', 'both.eTIV',
                  'both.cerebellum_stem_volume',
                  'left.brain_volume', 'right.brain_volume',
                  'left.skel_points', 'right.skel_points',
                  'left.skel_labelled_points', 'right.skel_labelled_points',
                  'log_ratio.skel_points', 'log_ratio.skel_labelled_points')
        res2 = {k: res[k] for k in sort_k if k in res}
        res2.update({k: v for k, v in res.items() if k not in sort_k})
        res = res2
    ress = brain_surfaces(left_gm_mesh, right_gm_mesh, left_wm_mesh,
                          right_wm_mesh)
    res.update(ress)

    return res


# -- inter-subject part --

def read_multiple_csv(csv_list):
    '''
    Read multiple CSV files with compatible headers.

    The final header includes all fields of all files, with columns missing in
    some files filled with None values.

    Returns
    -------
    hdr: list of str
        list of header fields names
    table: list of list
        table elements. The 1st column is suposed to be the subject name and is
        left as a sting, others are converted to float.
    '''
    table = []
    hdr = {}
    for csv_file in csv_list:
        with open(csv_file) as f:
            csv_reader = csv.reader(f, csv.Sniffer().sniff(f.read(2048)))
            f.seek(0)
            hdr2 = next(iter(csv_reader))
            resized = False
            for col in hdr2:
                if col not in hdr:
                    hdr[col] = len(hdr)
                    resized = True
            if resized:
                nc = len(hdr)
                for row in table:
                    row += [None] * (nc - len(row))
            for row in csv_reader:
                row = [row[0]] + [float(x) for x in row[1:]]
                trow = [None] * len(hdr)
                for i, v in enumerate(row):
                    trow[hdr[hdr2[i]]] = v
                table.append(trow)
    return list(hdr.keys()), table


def build_normative_brain_vol_stats(csv_files):
    '''
    Computes averages and std deviations for the given CSV files list.

    Returns
    -------
    hdr: list of str
        columns names
    morph: list of list
        CSV data, all but the 1st col converted to float (1st column is normally the subject name)
    avg: numpy array
        averages for columns [1:]. Nan/None values are excluded from the
        average.
    std: numpy array
        std dev for columns [1:]
    sums: numpy array (1 line)
        number of elements in the average for each column, taking into account
        missing and discarded ones (NaN/None values)
    quantiles: numpy array (9 lines)
        quantiles for 0%, 1%, 10%, 20%, 50%, 80%, 90%, 99%, 100% of the
        population
    '''
    hdr, morph = read_multiple_csv(csv_files)
    npmorph = np.array([row[1:] for row in morph], dtype=float)
    wh = np.isnan(npmorph) != True
    avg = np.mean(npmorph, axis=0, where=wh)
    std = np.std(npmorph, axis=0, where=wh)
    sums = np.sum(wh, axis=0)
    quantiles = []
    for col in range(npmorph.shape[1]):
        mcol = npmorph[:, col]
        mcol2 = mcol[np.where(np.logical_not(np.isnan(mcol)))]
        if mcol2.shape[0] == 0:
            quantiles.append([0., 0., 0., 0., 0., 0., 0., 0., 0.])
        else:
            quantiles.append(
                np.quantile(mcol2,
                            q=[0., 0.01, 0.1, 0.2, 0.5, 0.8, 0.9, 0.99, 1.]))
    quantiles = np.array(quantiles).T
    if np.any(np.isnan(quantiles)):
        print('NaN in quantiles')
        print(quantiles)
        nw = np.where(np.isnan(npmorph))
        col = nw[1][0]
        print('col:', col, ', row:', np.unique(nw[0]))
        print([csv_files[r] for r in np.unique(nw[0])])
        print(npmorph[nw[0][0], nw[1][0]])
    return hdr, morph, avg, std, sums, quantiles


