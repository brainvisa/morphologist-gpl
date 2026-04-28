from soma import aims, aimsalgo
import os
import os.path as osp
import csv
import numpy as np
import pandas as pd
import copy
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import SplineTransformer
import pickle
import json
import yaml
from functools import partial


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

    lhulla = l_graph.get('brain_hull_area')
    if lhulla is not None:
        res['left.hull_area'] = lhulla
    rhulla = r_graph.get('brain_hull_area')
    if rhulla is not None:
        res['right.hull_area'] = rhulla

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
                  'left.hull_area', 'right.hull_area',
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

def read_multiple_csv(csvs, sub_prefix=None, add_sub_prefix=None):
    '''
    Read multiple CSV files with compatible headers.

    The final header includes all fields of all files, with columns missing in
    some files filled with None values.

    Parameters
    ----------
    sub_prefix: str | dict
        prefix which should be removed from subjects IDs
    add_sub_prefix: dict
        dict of prefixes which should be prepended to subjects IDs, indexed by
        file name

    Returns
    -------
    hdr: list[str]
        list of header fields names
    table: list of list
        table elements. The 1st column is suposed to be the subject name and is
        left as a sting, others are converted to float.
    '''
    table = []
    hdr = {}

    if add_sub_prefix is None and isinstance(csvs, dict):
        add_sub_prefix = csvs

    for csv_file in csvs:
        if isinstance(sub_prefix, dict):
            prefix = sub_prefix.get(csv_file)
        else:
            prefix = sub_prefix
        print('read:', csv_file, ', prefix:', prefix)
        add_prefix = None
        if add_sub_prefix:
            add_prefix = add_sub_prefix.get(csv_file)
        with open(csv_file) as f:
            csv_reader = csv.reader(f, csv.Sniffer().sniff(f.readline()))
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
            for r, row in enumerate(csv_reader):
                trow = [None] * len(hdr)
                if len(row) != len(hdr2):
                    print('skipping corrupted row in', csv_file,
                          ', line:', r+2, ', cols:', len(row),
                          ', expecting', len(hdr2))
                    continue
                for i, v in enumerate(row):
                    c = hdr[hdr2[i]]
                    if c == 0:
                        if prefix and v.startswith(prefix):
                            v = v[len(prefix):]
                        if add_prefix is not None:
                            v = add_prefix + v
                        trow[c] = v
                    else:
                        trow[c] = float(v)
                table.append(trow)
    return list(hdr.keys()), table


def read_covar_table(covar_csv, covariables, skip_invalid=False,
                     sub_prefix=None, add_sub_prefix=None, filter=None):
    '''
    Parameters
    ----------
    covar_csv: str
    covariables: list | dict
        if dict: {dataset: {var: {'var_in_file': name, 'filename': xxx,
                                  'interpret': func}}}
    skip_invalid: bool
    sub_prefix: str
    add_sub_prefix: str
        prefix which should be prepended to subjects IDs
    filter: dict
    '''
    with open(covar_csv) as f:
        dialect = csv.Sniffer().sniff(f.readline())
        sep = dialect.delimiter

    covar_table = pd.read_csv(covar_csv, sep=sep)

    if filter is not None:
        for k, v in filter.items():
            covar_table = covar_table.loc[covar_table[k] == v]
        covar_table.index = range(len(covar_table))
        covar_table = covar_table.copy()
    # 1st col should be subject
    scol = covar_table.columns[0]
    if str(covar_table[scol].dtype) != 'str':
        subs = [str(x) for x in covar_table[scol]]
        covar_table = covar_table.drop(scol, axis=1)
        covar_table.insert(0, scol, subs)
        covar_table = covar_table.copy()
    alt_covar = {'sex': 'gender'}
    var_transform = {}
    print('read file:', covar_csv)
    # print('covariables:', covariables)
    if isinstance(covariables, dict):
        # {dataset: {var: {'var_in_file': name, 'filename': xxx,
        #                  'interpret': func}}}
        alt_covar = {}
        for cv_set in covariables.values():
            for var, vdef in cv_set.items():
                if vdef['filename'] != covar_csv:
                    continue
                tvar = vdef['var_in_file']
                alt_covar[var] = tvar.lower()
                tr = vdef.get('interpret')
                if tr is not None:
                    var_transform[var] = tr
        cov = []
        for d in covariables.values():
            cov += [k for k in d if k not in cov]
        covariables = cov

    print('alt_covar:', alt_covar)
    alt_covar.update({v: k for k, v in alt_covar.items()})
    new_covar = {}
    missing = []
    lcol = [c.lower() for c in covar_table]
    for v in covariables:
        v = v.lower()
        if v in lcol:
            c = covar_table.columns[lcol.index(v)]
            new_covar[v] = [c, None]
        else:
            av = alt_covar.get(v)
            if av is not None and av in lcol:
                c = covar_table.columns[lcol.index(av)]
                new_covar[v] = [c, None]
            else:
                missing.append(v)
    if len(missing) != 0:
        print('Warning: missing covariates in', covar_csv, ':', missing)

    # todel = []
    # toadd = {}
    for v, cdef in new_covar.items():
        if v.lower() in {'age', }:
            cdef[1] = 'float'
            c = cdef[0]
            tcol = covar_table[c]
            print('age col:', str(tcol.dtype))
            if str(tcol.dtype) == 'str':
                new_age = []
                for i in range(len(tcol)):
                    age = tcol.iloc[i]
                    if '+' in age:
                        new_age.append(None)
                    elif '-' in age:
                        age1, age2 = age.split('-')
                        age = (float(age1) + float(age2)) / 2
                        new_age.append(age)
                    elif age in (None, ''):
                        new_age.append(None)
                    else:
                        new_age.append(float(age))
                # todel.append(v)
                # v = f'{v}_conv'
                # toadd[v] = cdef
                covar_table = covar_table.drop(c, axis=1)
                covar_table[c] = new_age
                covar_table = covar_table.copy()
        else:
            cdef[1] = 'cat'

    if skip_invalid:
        tcov = [x[0] for x in new_covar.values()]
        covar_table = covar_table.iloc[
            ~np.any(covar_table[tcov].isna(), axis=1)]
        covar_table = covar_table.copy()
        covar_table.index = range(covar_table.shape[0])

    for var, tvar in var_transform.items():
        col = new_covar.get(var, [var, None])[0]
        covar_table[col] = tr(covar_table[col])

    if sub_prefix is not None:
        sl = len(sub_prefix)
        subs = [s[sl:] if s.startswith(sub_prefix) else s
                for s in covar_table[covar_table.columns[0]]]
        sub_col = covar_table.columns[0]
        covar_table[sub_col] = subs
    if add_sub_prefix is not None:
        sub_col = covar_table.columns[0]
        covar_table[sub_col] = add_sub_prefix + covar_table[sub_col]

    return covar_table, new_covar


def read_covar_tables(covar_csvs, covariables, skip_invalid=False,
                      sub_prefix=None, add_sub_prefix=None):
    '''
    Parameters
    ----------
    covar_csvs: list[str] | dict
    covariables: list | dict
        if dict: {dataset: {var: {'var_in_file': name, 'filename': xxx,
                                  'interpret': func}}}
    skip_invalid: bool
    add_sub_prefix: dict
        dict of prefixes which should be prepended to subjects IDs, indexed by
        file name
    '''
    fmap = {}
    if isinstance(covariables, dict):
        for dataset, cv in covariables.items():
            for var, vdef in cv.items():
                fdef = fmap.setdefault(vdef['filename'], {})
                fdef['dataset'] = dataset
                fdef.setdefault('vars', []).append(var)
    tables = {}
    new_covars = {}
    if not isinstance(covar_csvs, dict):
        covar_csvs = {c: None for c in covar_csvs}
    for covar_csv, filt in covar_csvs.items():
        add_prefix = None
        fmdict = fmap.get(covar_csv, {})
        dataset = fmdict.get('dataset', len(tables))
        print('read', dataset, ':', covar_csv)
        if add_sub_prefix is not None:
            add_prefix = add_sub_prefix.get(covar_csv)
        table, new_covar = read_covar_table(covar_csv, covariables,
                                            skip_invalid=skip_invalid,
                                            sub_prefix=sub_prefix,
                                            add_sub_prefix=add_prefix,
                                            filter=filt)
        print('table:', len(table))
        tcov = [table.columns[0]] + [x[0] for x in new_covar.values()]
        table = table[tcov]
        table.columns = ['subject'] + list(new_covar.keys())
        new_covar = {k: [k, v[1]] for k, v in new_covar.items()}
        if dataset in tables:
            print('merge tables', fmdict['vars'], len(tables[dataset]), len(table))
            tables[dataset][fmdict['vars']] = table[fmdict['vars']]
        else:
            tables[dataset] = table
        new_covars.update(new_covar)

    # merge tables on subject col
    table = pd.concat(tables.values(), keys=['subject'] * len(tables))
    table.index = range(len(table))

    return table, new_covars


def build_normative_brain_vol_stats_from_files(csv_files, sub_prefix=None):
    '''
    Computes averages and std deviations for the given CSV files list.
    Same as build_normative_brain_vol_stats() but starts from a list of .csv
    filenames, and returns also the read data.

    Parameters
    ----------
    csv_files: list
        brain volumes files list

    Returns
    -------
    hdr: list of str
        columns names
    morph: list of list
        CSV data, all but the 1st col converted to float (1st column is
        normally the subject name)
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
    sub_prefix: str
        prefix which should be removed from subjects IDs
    '''
    hdr, morph = read_multiple_csv(csv_files, sub_prefix=sub_prefix)
    npmorph = np.array([row[1:] for row in morph], dtype=float)
    avg, std, sums, quantiles = build_normative_brain_vol_stats(npmorph)
    return hdr, morph, avg, std, sums, quantiles


def build_normative_brain_vol_stats(npmorph: np.ndarray):
    '''
    Computes averages and std deviations for the given data.

    Parameters
    ----------
    npmorph: np.ndaray
        brain volumes stats array (numpy array). Normally we use
        read_multiple_csv(), then take an array of numeric data (all columns
        except the first which is the subjects IDs)

    Returns
    -------
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
        # print([csv_files[r] for r in np.unique(nw[0])])
        print(npmorph[nw[0][0], nw[1][0]])
    return avg, std, sums, quantiles


def grid_data(X, nmin=100):
    '''regular bins grid'''
    nmin = np.min((nmin, X.shape[0]))
    grid = [[] for x in range(X.shape[1])]
    for c in range(X.shape[1]):
        for nbins in range(10, 0, -1):
            h = np.histogram(X[X.columns[c]], nbins)
            if np.all(h[0] >= nmin):
                break
        grid[c] = h[1]

    return grid


def grid_data2(X, perbin=500, max_rel_width=0.1, nmin=100):
    ''' grid dataset with bins of approx. the same number of samples in each.
    '''
    if isinstance(X, pd.DataFrame):
        X = X.to_numpy()
    xmin = np.min(X, axis=0)
    xmax = np.max(X, axis=0)
    # print('xmin:', xmin, ', xmax:', xmax)
    nbins = int(np.ceil(X.shape[0] / perbin))
    grid = [[] for x in range(X.shape[1])]
    for c in range(X.shape[1]):
        s = np.argsort(X[:, c])
        bins = [xmin[c]]
        for b in range(nbins):
            if b != nbins - 1:
                cut = int(X.shape[0] * (b + 1) / nbins)
                y = (X[s[cut], c] + X[s[cut + 1], c]) / 2
            else:
                cut = X.shape[0] - 1
                y = X[s[cut], c]
            w = y - bins[-1]
            if w > max_rel_width * (xmax[c] - xmin[c]):
                # print('bin too large', w, max_rel_width * (xmax[c] - xmin[c]), bins, s)
                if b == nbins - 1:
                    y0 = xmax[c]
                else:
                    y0 = (X[s[cut], c]
                          + X[s[int(X.shape[0] * b / nbins)], c]) / 2
                n0 = np.where(np.logical_and(X[:, c] >= bins[-1],
                                             X[:, c] < y0))[0].shape[0]
                if n0 >= nmin:
                    # new additional bin
                    bins.append(y0)
                else:
                    # merge with previous bin
                    bins[-1] = y0
                if b != nbins - 1:
                    n1 = np.where(np.logical_and(X[:, c] >= bins[-1],
                                                 X[:, c] < y))[0].shape[0]
                else:
                    n1 = np.where(X[:, c] >= bins[-1])[0].shape[0]
                if n1 >= nmin:
                    # new additional bin
                    bins.append(y)
                # else: # merge with next bin
            else:
                if y != bins[-1]:
                    bins.append(y)
                else:
                    bins[-1] = y
        grid[c] = bins

    return grid


def model(X, y):
    # spline fit model (finally unused for now)
    wh = np.unique(np.where(np.isnan(X))[0])
    wh2 = np.unique(np.where(np.isnan(y))[0])
    wh = np.unique(np.concatenate((wh, wh2)))
    ix = np.ones((X.shape[0], ), dtype=bool)
    ix[wh] = False
    X = X.iloc[ix]
    y = y[ix]
    model = make_pipeline(SplineTransformer(n_knots=4, degree=3),
                          Ridge(alpha=1e-3))
    model.fit(X, y)
    return model


def nd_iter(sizes):
    # iterate over all dimensions
    imax = [s - 1 for s in sizes]
    index = [0] * len(sizes)

    while index[0] >= 0:

        yield index

        j = len(index) - 1
        while index[j] == imax[j] and j >= 0:
            j -= 1
        if j >= 0:
            index[j] += 1
            for j in range(j+1, len(index)):
                index[j] = 0
        else:
            index[0] = -1


def model_distributions(covar_subtable, covariables, npmorph, hdr):
    print('covar:', covariables)
    # print('covar_subtable:', covar_subtable)
    X = covar_subtable[[x[0] for x in covariables.values()]]
    wh = np.unique(np.where(np.isnan(X))[0])
    ix = np.ones((X.shape[0], ), dtype=bool)
    ix[wh] = False
    X = X.iloc[ix]
    morph = npmorph[ix]
    print('valid values:', X.shape)

    grid = grid_data2(X, 300, 0.02)
    mod = {}

    mod['grid'] = {c: g for c, g in zip(covariables, grid)}
    # print('grid:', mod['grid'])

    for index in nd_iter([len(x) - 1 for x in grid]):
        print('    index:', index)
        xdata = X.copy()
        xdata.index = range(xdata.shape[0])
        for i in range(len(index)):
            bmin = grid[i][index[i]]
            bmax = grid[i][index[i] + 1]
            c = X.columns[i]
            if i == len(index) - 1:
                # print('   filter:', c, '>=', bmin, ', <=', bmax)
                xdata = xdata[np.logical_and(xdata[c] >= bmin,
                                             xdata[c] <= bmax)]
            else:
                # print('   filter:', c, '>=', bmin, ', <', bmax)
                xdata = xdata[np.logical_and(xdata[c] >= bmin,
                                             xdata[c] < bmax)]
            # print('xdata:', xdata.shape)
            y = morph[xdata.index]

        print('index:', index, ', data:', y.shape, ', init:', X.shape)
        avg, std, sums, quantiles = build_normative_brain_vol_stats(y)
        mod[tuple(index)] = {'averages': avg.astype(float),
                             'std': std.astype(float),
                             'N': sums.astype(int),
                             'quantiles': [x.astype(float) for x in quantiles]
                             }

    # the spline model was an optional attempt, which doesn't fit
    # the data closely enough at boundaries. Drop it for now.

    # models = {}
    # for c, col in enumerate(hdr[1:]):
    #     y = morph[:, c]
    #     # print(c, y)
    #     m = model(X, y)
    #     models[col] = {'model': m}
    #
    # mod['models'] = models

    return mod


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def save_stats(models, filename):
    ''' save stratified stats and possibly models '''
    mstrat = models.get('stratified', {})
    smodels = copy.deepcopy(models)
    for k, val in mstrat.items():
        key = str(json.dumps(k))
        keydir = '_'.join('-'.join(x) for x in k)
        smodels['stratified'][key] = smodels['stratified'][k]
        del smodels['stratified'][k]
        mods = val.get('models', {})
        if mods:
            dname = osp.join(filename.rsplit('.', 1)[0] + '.models', keydir)
            os.makedirs(dname, exist_ok=True)
            for feature, mdef in mods.items():
                mod = mdef.get('model')
                fname = osp.join(dname, f'model_{feature}.pickle')
                with open(fname, 'wb') as f:
                    pickle.dump(mod, f)
                rfname = osp.relpath(fname, osp.dirname(filename))
                smodels['stratified'][key]['models'][feature]['model'] = rfname
        for gk, gval in val.items():
            if gk in ('models', 'grid'):
                continue
            smodels['stratified'][key][str(json.dumps(gk))] \
                = smodels['stratified'][key][gk]
            del smodels['stratified'][key][gk]

    with open(filename, 'w') as f:
        json.dump(smodels, f, indent=4, cls=NumpyEncoder)


def load_stats(filename):
    ''' load normative stats '''
    with open(filename) as f:
        models = json.load(f)

    dname = osp.dirname(filename)

    mstrat = models.get('stratified', {})
    for k in list(mstrat.keys()):
        val = mstrat[k]
        key = tuple((tuple(t) for t in json.loads(k)))
        mstrat[key] = val
        del mstrat[k]
        mods = val.get('models', {})
        for feature, mdef in mods.items():
            fname = mdef.get('model')
            if fname is not None:
                fname = osp.join(dname, fname)
                with open(fname, 'rb') as f:
                    mod = pickle.load(f)
            mstrat[key]['models'][feature]['model'] = mod
        for gk in list(val.keys()):
            if gk in ('models', 'grid'):
                continue
            gval = val[gk]
            gkey = tuple(json.loads(gk))
            val[gkey] = gval
            del val[gk]

    return models


def build_stratified_normative_brain_vol_stats(
    datasets: dict
):
    '''
    Computes averages and std deviations for the given CSV files list.

    Parameters
    ----------
    datasets: dict
        result of read_datasets_def()
    '''
    def glob_dict(hdr, avg, std, sums, quantiles):
        gstats = {
            'columns': [c for c in hdr if c != 'subject'],
            'averages': list(avg.astype(float)),
            'std': list(std.astype(float)),
            'quantiles': [list(x) for x in quantiles],
            'N': [int(x) for x in sums],
        }
        return gstats

    covar_table = datasets['covar_table']
    covariables = datasets['variables_map']

    # 1. separate by categorial variables and continuous variables
    cat_var = {v: [] for v, cdef in covariables.items() if cdef[1] == 'cat'}
    for v in cat_var:
        values = np.unique(covar_table[covariables[v][0]])
        cat_var[v] = values
    print('cat_var:', cat_var)
    flt_var = {v: cdef for v, cdef in covariables.items()
               if cdef[1] != 'cat'}

    # 2. read brain data and filter out invalid subjects
    hdr = datasets['morphometry']['header']
    morph = datasets['morphometry']['table']

    subs = [x[0] for x in morph]
    valid = covar_table[covar_table.columns[0]].isin(subs)
    covar_table = covar_table.loc[valid]
    covar_table.index = range(len(covar_table.index))
    print('valid data:', covar_table.shape)
    subs = set(covar_table[covar_table.columns[0]])  # subject
    morph = [row for row in morph if row[0] in subs]
    npmorph = np.array([row[1:] for row in morph], dtype=float)
    m_sub_map = {row[0]: i for i, row in enumerate(morph)}

    # 3. ,stratify by categorical variable values
    models = {}
    mstrat = {}
    models['stratified'] = mstrat
    ci = list(cat_var.keys())
    cti = [covariables[k][0] for k in cat_var.keys()]
    for index in nd_iter([len(val) for val in cat_var.values()]):
        sub_stat = {ci[i]: cat_var[ci[i]][j] for i, j in enumerate(index)}
        print('cat index:', index, sub_stat)
        data = covar_table[cti[0]] == cat_var[ci[0]][index[0]]
        for i in range(1, len(index)):
            data &= covar_table[cti[i]] == cat_var[ci[i]][index[i]]
        data = covar_table.iloc[data]
        print('cat ndata:', data.shape)

        indices = [m_sub_map[covar_table.iloc[i]['subject']]
                   for i in data.index]
        m = model_distributions(data, flt_var, npmorph[indices], hdr)
        key = tuple((k, sub_stat[k]) for k in sub_stat)
        mstrat[key] = m

    # 4. add global, unstratified stats
    models['global'] = glob_dict(hdr,
                                 *build_normative_brain_vol_stats(npmorph))

    return models


def range_global_zstats(stat_models, indiv_morpho, morph_hdr, columns=None):
    ''' get Z stats for a sample from non-stratified normative stats '''

    norm_stat = stat_models.get('global')
    if norm_stat is None:
        # older global-only format
        norm_stat = stat_models

    if columns is None:
        columns = norm_stat.get('columns', [])
    ncols = {c: i for i, c in enumerate(columns)}
    col_ord = {j: ncols.get(morph_hdr[j + 1])
               for j in range(len(indiv_morpho[0]) - 1)}
    morph_z = [None] * (len(indiv_morpho[0]) - 1)
    avg = norm_stat.get('averages')
    if isinstance(avg, np.ndarray):
        avg = avg.tolist()
    std = norm_stat.get('std')
    if isinstance(std, np.ndarray):
        std = std.tolist()
    quantiles = norm_stat.get('quantiles')
    n_quant = None
    if quantiles:
        n_quant = np.zeros((len(quantiles), len(indiv_morpho[0]) - 1))
    if avg is not None and std is not None:
        # print('avg:', len(avg), ', quantiles:', len(quantiles))
        for i, mv in enumerate(indiv_morpho[0][1:]):
            if mv is None or np.isnan(mv):
                continue  # missing data
            c = col_ord.get(i)
            if c is not None:
                z0 = avg[c]
                zs = std[c]
                if z0 is not None and zs != 0:
                    z = (mv - z0) / zs
                    morph_z[i] = z
                if quantiles is not None:
                    if zs != 0:
                        n_quant[:, i] = [(q[c] - z0) / zs for q in quantiles]

    return {'z': morph_z, 'quantiles': n_quant}


def range_zstats(stat_models, indiv_morpho, morph_hdr, covariables):
    ''' get Z stats for a sample from normative stats (stratified or not) '''

    if not covariables or 'stratified' not in stat_models:
        zstat = range_global_zstats(stat_models, indiv_morpho, morph_hdr)
        zstat['mode'] = 'global'
        return zstat

    zstat = None
    strat = stat_models['stratified']
    cat_found = None
    for k, v in strat.items():
        cat_cov = dict(k)
        for c, cv in cat_cov.items():
            if covariables.get(c) != cv:
                break
        else:
            cat_found = cat_cov
            cat_model = v
            break

    if cat_found is None:
        zstat = range_global_zstats(stat_models, indiv_morpho, morph_hdr)
        zstat['mode'] = 'global'
        return zstat

    # print('found cat:', cat_found)
    flt_covar = {k: v for k, v in covariables.items() if k not in cat_found}
    grid = cat_model['grid']
    grid_i = []
    for gk, gv in grid.items():
        ind_v = covariables[gk]
        for i, v in enumerate(gv[:-1]):
            if (i == 0 or ind_v >= v) \
                    and (ind_v < gv[i+1] or i == len(gv) - 1):
                break
        grid_i.append(i)
    grid_i = tuple(grid_i)
    box = cat_model.get(grid_i)
    # print('box:', box)
    if box is not None:
        mode = 'stratified'
        zstat = range_global_zstats(box, indiv_morpho, morph_hdr,
                                    columns=stat_models['global']['columns'])
        std = box['std']
    else:
        mode = 'global_by_cat'
        zstat = range_global_zstats(stat_models, indiv_morpho, morph_hdr)
        std = stat_models['global']['std']
    # print('zstat for cat:', zstat)
    models = cat_model.get('models')
    if models is not None:
        # print('model avg:', )
        stat_cols = stat_models['global']['columns']
        cols = {i: (c, stat_cols.index(c)) for i, c in enumerate(morph_hdr[1:])
                if c in models}
        mod_avg = [None] * (len(morph_hdr) - 1)
        mod_z = [None] * (len(morph_hdr) - 1)
        for i, (c, j) in cols.items():
            mod_avg[i] = models[c]['model'].predict(
                np.array([list(flt_covar.values())]))[0]
            p = indiv_morpho[0][i + 1]
            if p is not None and not np.isnan(p):
                mod_z[i] = (indiv_morpho[0][i + 1] - mod_avg[i]) / std[j]

        zstat['models_avg'] = mod_avg
        zstat['models_z'] = mod_z

    zstat['mode'] = mode
    zstat['cat_bin'] = cat_found
    zstat['cont_bin_ind'] = grid_i

    return zstat


def test_normative(brain_volumes_files, normative_file, variables=None,
                   indiv_covar_files=None):
    import matplotlib.pyplot as plt

    covar_table = None
    if isinstance(brain_volumes_files, dict) \
            and 'morphometry' in brain_volumes_files:
        morph_hdr = brain_volumes_files['morphometry']['header']
        morph = brain_volumes_files['morphometry']['table']
        covar_table = brain_volumes_files['covar_table']
        new_covar = brain_volumes_files['variables_map']
    else:
        morph_hdr, morph = read_multiple_csv(brain_volumes_files,
                                             sub_prefix='sub-')
    pmorph = pd.DataFrame(morph, columns=morph_hdr)
    models = load_stats(normative_file)
    stat_cols = models['global']['columns']
    cols = {i: (c, stat_cols.index(c))
            for i, c in enumerate(morph_hdr[1:])
            if c in stat_cols}
    # print('cols:', cols)

    covar = {
        'sex': ['M', 'F'],
        'age': list(np.arange(8, 90, 0.5)),
    }

    if not variables:
        variables = [0, 1, 2]
    else:
        variables = list(variables)
    for i, v in enumerate(variables):
        if isinstance(v, int):
            variables[i] = morph_hdr[v + 1]

    if indiv_covar_files is not None:
        covar_table, new_covar = read_covar_tables(
            indiv_covar_files, list(covar.keys()), skip_invalid=True)

    nf = len(morph_hdr) - 1

    for sex in covar['sex']:
        if covar_table is not None:
            sel_p = covar_table[new_covar['sex'][0]] == sex
            xp = covar_table.iloc[sel_p][new_covar['age'][0]]
            sub = covar_table.iloc[sel_p]['subject']
            p = pmorph.iloc[pmorph['subject'].isin(sub)]
            sub = sub.iloc[sub.isin(p['subject'])]
            xp = xp.loc[sub.index]
            p = p[p.columns[1:]].to_numpy()
        else:
            xp = covar['age']
            p = np.zeros((len(xp), nf))
        ages = covar['age']
        z = np.zeros((len(ages), nf))
        mavg = np.zeros((len(ages), nf))
        mz = np.zeros(mavg.shape)
        gavg = np.zeros(mavg.shape)
        gstd = np.zeros(mavg.shape)
        bavg = np.zeros(mavg.shape)
        bstd = np.zeros(mavg.shape)
        for i, age in enumerate(ages):
            zstat = range_zstats(models, [morph[0]], morph_hdr,
                                 {'sex': sex, 'age': age})
            if covar_table is None:
                p[i] = morph[0][1:]
            z[i] = zstat['z']
            mod = zstat.get('models_avg')
            if mod is not None:
                mavg[i] = mod
                mz[i] = zstat['models_z']
            bindex = zstat['cont_bin_ind']
            box = models['stratified'][tuple(zstat['cat_bin'].items())][bindex]
            for j, feat in enumerate(morph_hdr[1:]):
                if j not in cols:
                    continue
                k = cols[j][1]
                bavg[i, j] = box['averages'][k]
                bstd[i, j] = box['std'][k]
                gavg[i, j] = models['global']['averages'][k]
                gstd[i, j] = models['global']['std'][k]
            # bstd[i] = (p[i] - bavg[i]) / z[i]

        for feat in variables:
            i = morph_hdr.index(feat) - 1
            fig, ax = plt.subplots()
            ax.set_xlabel(f'sex: {sex}, {feat} (age)')
            ax.plot(ages, gavg[:, i], color='yellow')
            ax.plot(ages, gavg[:, i] + gstd[:, i], '--', color='yellow')
            ax.plot(ages, gavg[:, i] - gstd[:, i], '--', color='yellow')

            ax.plot(ages, bavg[:, i], color='purple')
            ax.plot(ages, bavg[:, i] + bstd[:, i], '--', color='purple')
            ax.plot(ages, bavg[:, i] - bstd[:, i], '--', color='purple')

            ax.scatter(xp, p[:, i], color='green')

            if mod is not None:
                ax.plot(ages, mavg[:, i], color='orange')
                ax.plot(ages, mavg[:, i] + bstd[:, i], '--', color='orange')
                ax.plot(ages, mavg[:, i] - bstd[:, i], '--', color='orange')

            fig.tight_layout()
    plt.show()


value_transforms = {
    'months': lambda x: x / 12,
}


def dict_transform(d, values):
    tval = []
    for v in values:
        tval.append(d[v])
    return tval


def read_datasets_def(ds_filename, datasets=None):
    if isinstance(ds_filename, str):
        with open(ds_filename) as f:
            ds = yaml.safe_load(f)
    else:
        ds = ds_filename

    covar_files = {}
    # bmorph_files = []
    ds_variables = {}
    prefixes = {}

    if datasets is None:
        datasets = list(ds.keys())

    for dataset in datasets:
        dsd = ds[dataset]
        var = dsd['variables']
        vtrans = {}
        for var_d, vdesc in var.items():
            # variable: location
            vars = [v.strip() for v in var_d.split(',')]
            for loc, vdef in vdesc.items():
                # location: {var_repl: file}
                if isinstance(vdef, list):
                    vdef = vdef[0]  # FIXME
                print(dataset, vars, loc)
                for i, (k, fname) in enumerate(vdef.items()):
                    filt = None
                    if isinstance(fname, dict):
                        filt = fname.get('filter')
                        fname = fname['filename']
                    # k: var_repl or "var_repl (note)"
                    # or "var_repl (value1: repl1, value2: repl2...)"
                    print('   ', i, k)
                    if not osp.exists(fname):
                        break
                    if i >= len(vars):
                        break
                    var = vars[i]
                    if var in vtrans:
                        continue
                    k2 = [x.strip() for x in k.split('(', 1)]
                    print(var, loc, k2)
                    meaning = None
                    if len(k2) == 2:
                        meaningd = k2[1][:-1].strip()
                        meaningd = [m.strip() for m in meaningd.split(',')]
                        if len(meaningd) == 1:
                            meaning = meaningd[0]
                            meaning = value_transforms[meaning]
                        else:
                            meaning = {}
                            for m in meaningd:
                                m2 = [x.strip() for x in m.split(':', 1)]
                                try:
                                    m2[0] = float(m2[0])
                                except ValueError:
                                    pass
                                meaning[m2[0]] = m2[1]
                            meaning = partial(dict_transform, meaning)
                    d = {'var_in_file': k2[0],
                         'filename': fname}
                    if meaning is not None:
                        d['interpret'] = meaning
                    if filt is not None:
                        d['filter'] = filt
                    vtrans[var] = d
                    if fname not in covar_files:
                        covar_files[fname] = filt
                        prefixes[fname] = f'{dataset}_'

        ds_variables[dataset] = vtrans
        # print('var for ds', dataset, ':', vtrans)

    sub_prefix = 'sub-'
    covar_table, covar = read_covar_tables(
        covar_files, ds_variables, skip_invalid=True, sub_prefix=sub_prefix,
        add_sub_prefix=prefixes)
    # covar_table = None

    ds_def = {
        'raw_dataset_def': ds,
        'covar_files': covar_files,
        'dataset_variables': ds_variables,
        'covar_table': covar_table,
        'variables_map': covar,
    }

    # read brain volumes files
    morph_csvs = {}
    sub_prefixes = {}
    for dataset in datasets:
        dsd = ds[dataset]
        bmorph = dsd['brain_morphometry']
        if not isinstance(bmorph, dict):
            print('WARNING: no brain_morphometry file for', dataset)
            continue
        for loc, fldef in bmorph.items():
            if not isinstance(fldef, list):
                fldef = [fldef]
            ok = False
            for fdef in fldef:
                if isinstance(fdef, dict):
                    fname = fdef['filename']
                    prefix = fdef.get('sub-prefix', sub_prefix)
                else:
                    fname = fdef
                    prefix = sub_prefix
                if not osp.exists(fname):
                    ok = False
                    break
                ok = True
                morph_csvs[fname] = F'{dataset}_'
                sub_prefixes[fname] = prefix
            if ok:
                break
    hdr, morph = read_multiple_csv(morph_csvs, sub_prefix=sub_prefixes,
                                   add_sub_prefix=morph_csvs)
    ds_def['morphometry'] = {'header': hdr, 'table': morph}

    return ds_def


if __name__ == '__main__':
    from soma.qt_gui.qt_backend import Qt

    dataset_file = '/home/dr144257/data/datasets.yaml'

    bvfile = '/neurospin/dico/data/human/hcp/derivatives/morphologist-2023/morphometry/brain_volumes.csv'
    covar_csv = '/neurospin/dico/data/human/hcp/participants.csv'
    bvfiles = [bvfile]
    if not osp.exists(bvfile):
        bvfile = '/home/dr144257/data/hcp/3T_morphologist/morphometry/brain_volumes.csv'
        bvfiles = [bvfile, '/home/dr144257/data/ukb/morphometry/brain_volumes.csv']
        covar_csv = '/home/dr144257/data/hcp/participants.csv'
        covar_csvs = [covar_csv, '/home/dr144257/data/ukb/participants.tsv']
    # normative_file = '/home/dr144257/data/hcp/3T_morphologist/tables/BL/morphologist_normative_brain_volumes_stats.json'
    indiv_vol_file = '/volatile/home/dr144257/data/baseessai/subjects/sujet01/t1mri/default_acquisition/default_analysis/segmentation/brain_volumes_sujet01.csv'

    normative_file = '/home/dr144257/data/normative_data/all/morphologist_normative_brain_volumes_stats.json'

    make_stats = True
    save_stats = True
    if make_stats:
        ds_def = read_datasets_def('/home/dr144257/data/datasets.yaml')
        models = build_stratified_normative_brain_vol_stats(ds_def)
        if save_stats:
            save_stats(models, normative_file)
    else:
        models = load_stats(normative_file)

    app = Qt.QApplication.instance()
    if app is None:
        app = Qt.QApplication([])

    # test_normative([indiv_vol_file], normative_file)
    test_normative(ds_def, normative_file)

    app.exec()
