
#!/usr/bin/env python

from soma import aims, aimsalgo
import argparse
import subprocess
import numpy as np
import tempfile
import os
import os.path as osp


def cortex_grad_map(cortex):
    ''' normal Gradient inside the cortex
    '''

    # dilate the ext of the cortex before growing a distance map in it
    cortex3 = aims.Volume(cortex)
    cortex3[cortex3.np == 255] = 32767
    cortex3[cortex3.np != 32767] = 0
    mm = aimsalgo.MorphoGreyLevel_S16()
    dil = mm.doDilation(cortex3, 5)
    dil[cortex.np == 0] = 0

    # cortex map with dilated GM
    cortex2 = aims.Volume(cortex)
    # cortex2[rast.np == 1] = 11
    cortex2[cortex2.np == 11] = 25
    cortex2[dil.np == 32767] = 11
    # aims.write(cortex2, '/tmp/cort.nii.gz')

    # 2. distance map inside GM
    fm = aims.FastMarching()
    dmap = fm.doit(cortex2, [255, 11], [0])
    dmap[dmap.np > 10] = 10.
    # aims.write(dmap, '/tmp/dmap.nii.gz')

    # 3. Gradient
    g = aimsalgo.AimsGradient_FLOAT()
    gx = g.X(dmap)
    gy = g.Y(dmap)
    gz = g.Z(dmap)
    # aims.write(gx, '/tmp/gx.nii.gz')

    return gx, gy, gz


def tex_to_sulci(vol, mesh, tex, binarize=None, clear_img=True,
                 norm_decal=1., npt=10):
    gradient = cortex_grad_map(vol)

    if clear_img:
        vol.fill(0)
    vert = mesh.vertex()
    norm = mesh.normal()
    vs = vol.getVoxelSize()[:3]

    for i, t in enumerate(tex[0]):
        if t != 0:
            print(i, ':', t)
            if binarize is not None:
                t = binarize
            nrm = norm[i]
            v = vert[i].np
            for d in range(npt):
                # p = (vert[i] + norm[i] * (norm_decal * d / npt)).np
                vi = np.round(v / vs).astype(int)
                vol.setValue(t, vi)
                # update direction and pos
                nrm = aims.Point3df(
                    gradient[0][vi[0], vi[1], vi[2], 0],
                    gradient[1][vi[0], vi[1], vi[2], 0],
                    gradient[2][vi[0], vi[1], vi[2], 0])
                if nrm != aims.Point3df(0):
                    nrm.normalize()
                # the gradient may sometimes push towards the bottom of
                # the sulcus. Add normal with a higher weight to fix it
                nrm += norm[i] * 1.5
                nrm.normalize()
                v += nrm.np * norm_decal / npt

    if binarize is not None:
        labels = [binarize]
    else:
        labels = np.unique(tex[0].np)

    mm = aimsalgo.MorphoGreyLevel_S16()
    for t in labels:
        v = aims.Volume(vol)
        v.fill(0)
        v[vol.np == t] = 32767
        cl = mm.doDilation(v, 2.)
        cl = mm.doErosion(cl, 1.)
        vol[cl.np != 0] = t

    tmp1 = tempfile.mkstemp(prefix='immortal_', suffix='.nii.gz')
    os.close(tmp1[0])
    todel = [tmp1[1]]
    tmp2 = tempfile.mkstemp(prefix='immortal2_', suffix='.nii.gz')
    os.close(tmp2[0])
    todel.append(tmp2[1])
    try:
        aims.write(vol, tmp1[1])
        subprocess.check_call([
            'VipSkeleton', '-i', tmp1[1], '-so', tmp2[1],
            '-sk', 's', '-fv', 'n', '-p', '0', '-c', 'n', '-k'
        ])
        vol2 = aims.read(tmp2[1])
    finally:
        for fn in todel:
            if osp.exists(fn):
                os.unlink(fn)
            if osp.exists(fn + '.minf'):
                os.unlink(fn + '.minf')

    vol[:] = vol2.np


def add_to_cortex(vol, gw):
    gw2 = aims.Volume(gw)
    vol[gw.np == 0] = 0
    gw2[vol.np != 0] = -103

    return gw2


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        'Folds imprints texture to cortex image immortals. '
        'Adds immortals to cortex image for input to skeletonization')
    parser.add_argument('-i', '--input', help='input imprints texture')
    parser.add_argument('-m', '--mesh', help='input white mesh')
    parser.add_argument('-c', '--cortex', help='input cortex volume')
    parser.add_argument('-o', '--output', help='output modified cortex')
    parser.add_argument('-I', '--immortals',
                        help='output immortals volume (optional)')
    # parser.add_argument_group()

    opts = parser.parse_args()
    tex_f = opts.input
    mesh_f = opts.mesh
    cort_f = opts.cortex
    out_cort_f = opts.output
    out_imm_f = opts.immortals

    tex = aims.read(tex_f)
    mesh = aims.read(mesh_f)
    cort = aims.read(cort_f)
    immortals = aims.Volume(cort)
    tex_to_sulci(immortals, mesh, tex, binarize=200, norm_decal=7., npt=50)
    cort2 = add_to_cortex(immortals, cort)
    aims.write(cort2, out_cort_f)
    if out_imm_f:
        aims.write(immortals, out_imm_f)

    # ---

    # bv python ~/brainvisa/src/perso/riviere/sandbox/dimples_in_graphs.py -i Rsub-CC00918XX19_ses-14031_sulci_manual.gii -m sub-CC00918XX19_ses-14031/t1mri/default_acquisition/default_analysis/segmentation/mesh/sub-CC00918XX19_ses-14031_Rwhite.gii -c sub-CC00918XX19_ses-14031/t1mri/default_acquisition/default_analysis/segmentation/Rcortex_sub-CC00918XX19_ses-14031.nii.gz -o segs/Rcortex_mod.nii.gz  # -I segs/immortals.nii.gz

    # VipSkeleton -i segs/Rcortex_mod.nii.gz -so segs/Rskel.nii.gz -vo segs/Rroots.nii.gz -g sub-CC00918XX19_ses-14031/t1mri/default_acquisition/default_analysis/segmentation/Rgrey_white_sub-CC00918XX19_ses-14031.nii.gz -ve 2 -sk w -k -im a

    # then, run BV process corticalfoldsgraph with min_vertex_size=3
