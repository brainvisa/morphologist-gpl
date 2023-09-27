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

from __future__ import absolute_import
from brainvisa.processes import *
import math
from brainvisa.tools import aimsGlobals
from brainvisa import registration
from six.moves import range
from six.moves import zip
try:
    from brainvisa import anatomist
except:
    anatomist = None
from brainvisa import quaternion

name = 'Prepare Subject for Anatomical Pipeline'
userLevel = 0

signature = Signature(
    'T1mri', ReadDiskItem("Raw T1 MRI", 'aims readable Volume Formats'),
    'commissure_coordinates', WriteDiskItem(
        'Commissure coordinates', 'Commissure coordinates'),
    'Normalised', Choice('No', 'MNI from SPM',
                         'MNI from Mritotal', 'Marseille from SPM'),
    'Anterior_Commissure', Point3D(),
    'Posterior_Commissure', Point3D(),
    'Interhemispheric_Point', Point3D(),
    'Left_Hemisphere_Point', Point3D(),
    'allow_flip_initial_MRI', Boolean(),
    'reoriented_t1mri', WriteDiskItem('Raw T1 MRI',
                                      'aims writable volume formats'),
    'remove_older_MNI_normalization', Boolean(),
    'older_MNI_normalization',
    ReadDiskItem('Transform Raw T1 MRI to Talairach-MNI template-SPM',
                 'Transformation matrix'),
)


capsul_param_options = {
    'older_MNI_normalization': ['dataset=None'],
}


class APCReader(object):
    def __init__(self, key):
        self._key = key

    def __call__(self, values, process):
        acp = None
        if values.commissure_coordinates is not None:
            acp = values.commissure_coordinates
        # elif values.T1mri:
        #  acp = ReadDiskItem( 'Commissure coordinates','Commissure coordinates')\
        #    .findValue( values.T1mri )
        result = None
        key_mm = self._key + 'mm'
        if acp is not None and acp.isReadable():
            f = open(acp.fullPath())
            for l in f.readlines():
                l = l.split(':', 1)
                if len(l) == 2 and l[0] == key_mm:
                    return [float(i) for i in l[1].split()]
                if len(l) == 2 and l[0] == self._key and values.T1mri is not None:
                    vs = values.T1mri.get('voxel_size')
                    if vs:
                        pos = l[1].split()
                        if len(pos) == 3:
                            result = [float(i) * j for i, j in zip(pos, vs)]
        return result


def linkOldNormalization(self, proc, dummy):
        # this forced acquisition is meant to avoid confusion with a different one
        # when there is no older normalization in the same acquisition
    required = {}
    acquisition = self.T1mri.get('acquisition')
    if acquisition:
        required['acquisition'] = acquisition
    return self.signature['older_MNI_normalization'].findValue(
        self.T1mri, requiredAttributes=required)


def initialization(self):
    def linknorm(values, process):
        if values.T1mri and values.T1mri.get('normalized') == 'yes':
            return 'MNI from SPM'
        return 'No'

    self.linkParameters('commissure_coordinates', 'T1mri')
    self.Normalised = 'No'
    self.setOptional('Anterior_Commissure')
    self.setOptional('Posterior_Commissure')
    self.setOptional('Interhemispheric_Point')
    self.signature['Anterior_Commissure'].add3DLink(self, 'T1mri')
    self.signature['Posterior_Commissure'].add3DLink(self, 'T1mri')
    self.signature['Interhemispheric_Point'].add3DLink(self, 'T1mri')
    self.signature['Left_Hemisphere_Point'].add3DLink(self, 'T1mri')
    self.linkParameters('Anterior_Commissure',
                        'commissure_coordinates', APCReader('AC'))
    self.linkParameters('Posterior_Commissure',
                        'commissure_coordinates', APCReader('PC'))
    self.linkParameters('Interhemispheric_Point',
                        'commissure_coordinates', APCReader('IH'))
    self.setOptional('Left_Hemisphere_Point')
    self.allow_flip_initial_MRI = 0
    self.linkParameters('reoriented_t1mri', 'T1mri')
    self.linkParameters('Normalised', 'T1mri', linknorm)
    self.setOptional('older_MNI_normalization')
    self.linkParameters('older_MNI_normalization',
                        'T1mri', self.linkOldNormalization)


def execution(self, context):
    ac = []
    pc = []
    ip = []
    lh = []
    acmm = self.Anterior_Commissure
    pcmm = self.Posterior_Commissure
    ipmm = self.Interhemispheric_Point
    if self.Normalised == 'No':
        atts = aimsGlobals.aimsVolumeAttributes(self.T1mri)
        vs = atts['voxel_size']
        #context.write( 'voxel size: ', vs )
        ac = self.Anterior_Commissure
        pc = self.Posterior_Commissure
        ip = self.Interhemispheric_Point
        lh = self.Left_Hemisphere_Point
        if not ac or len(ac) != 3 or not pc or len(pc) != 3 or not ip or \
                len(ip) != 3:
            raise RuntimeError(_t_('In non-normalized mode, the 3 points AC, PC '
                                   'and IP are mandatory (in mm)'))

        def vecproduct(v1, v2):
            return (v1[1] * v2[2] - v1[2] * v2[1],
                    v1[2] * v2[0] - v1[0] * v2[2],
                    v1[0] * v2[1] - v1[1] * v2[0])

        def dot(v1, v2):
            return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

        def norm(v):
            return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])

        def normalize(v):
            nrm = norm(v)
            if nrm == 0.:
                return v
            else:
                n = 1. / norm(v)
                return (v[0] * n, v[1] * n, v[2] * n)

        def vecscale(v, scl):
            return (v[0] * scl, v[1] * scl, v[2] * scl)

        # determine image orientation
        v1 = normalize((pc[0] - ac[0], pc[1] - ac[1], pc[2] - ac[2]))
        ia = (ac[0] - ip[0], ac[1] - ip[1], ac[2] - ip[2])
        v2u = normalize(ia)
        v3 = normalize(vecproduct(v1, v2u))
        v2 = normalize(vecproduct(v3, v1))

        # sanity check
        ipdot = dot(v1, ia)
        ipdist = norm((-ia[0] + ipdot * v1[0], -ia[1] + ipdot * v1[1],
                       -ia[2] + ipdot * v1[2]))
        if ipdist == 0:
            raise ValueError(_t_('AC, PC and IP are aligned, the interhemispheric'
                                 'plane orientation cannot be determined. Please chose IP upper in '
                                 'the brain.'))
        if ipdist < 30.:
            context.warning(_t_('IP is close to the AC-PC axis. This may be '
                                'an error, and in any case leads to a poor precision on the '
                                'determination of the interhemispheric plane. You should better '
                                'chose IP upper in the brain.'))

        # determine rotation between y axis and v1
        y = (0, 1, 0)
        n = vecproduct(y, v1)
        cosal = dot(y, v1)
        if norm(n) < 1e-5:
            if cosal > 0:
                r1 = quaternion.Quaternion((0, 0, 0, 1))
            else:
                r1 = quaternion.Quaternion((0, 0, 1, 0))  # flip z
        else:
            n = normalize(n)
            t = vecproduct(y, n)
            alpha = math.acos(cosal)
            if dot(t, v1) < 0:
                alpha = -alpha
            r1 = quaternion.Quaternion()
            r1.fromAxis(n, alpha)

        # apply r1 to ( v1, v2, v3 )
        v1_1 = r1.transform(v1)
        v2_1 = r1.transform(v2)
        v3_1 = r1.transform(v3)
        # now v1_1 should be aligned on y

        # determine rotation between z axis and v2
        z = (0, 0, 1)
        p = dot(z, v2_1)
        if p > 1.:
            p = 1.
        elif p < -1.:
            p = -1.
        alpha = math.acos(p)
        q = dot(normalize(vecproduct(z, v2_1)), y)
        if q >= 0:
            alpha = -alpha
        r2 = quaternion.Quaternion()
        r2.fromAxis(y, alpha)

        # apply r2 to ( v1, v2, v3 )
        v1_2 = r2.transform(v1_1)
        v2_2 = r2.transform(v2_1)
        v3_2 = r2.transform(v3_1)

        r3 = r1.compose(r2)
        trans = r3.rotationMatrix()

        # check x inversion
        if lh is None:
            context.warning(_t_('Left hemisphere point not specified - X axis '
                                'flip will not be checked'))
        else:
            x = (1, 0, 0)
            lvec = r3.transform((lh[0] - ac[0], lh[1] - ac[1], lh[2] - ac[2]))
            if dot(x, lvec) < 0:
                context.write(_t_('X is flipped'))
                trans[0] *= -1
                trans[1] *= -1
                trans[2] *= -1
                trans[3] *= -1
        #context.write( 'trans:', trans )

        # build binary flip matrix
        flipmat = [0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0, 1]
        dims = atts['volume_dimension'][:3]
        dims2 = (dims[0] * vs[0], dims[1] * vs[1], dims[2] * vs[2])
        imax = 0
        for i in range(1, 3):
            if abs(trans[i]) > abs(trans[imax]):
                imax = i
        if trans[imax] >= 0:
            flipmat[imax] = 1
        else:
            flipmat[imax] = -1
            flipmat[3] = dims2[imax]
        imax = 4
        for i in range(5, 7):
            if abs(trans[i]) > abs(trans[imax]):
                imax = i
        if trans[imax] >= 0:
            flipmat[imax] = 1
        else:
            flipmat[imax] = -1
            flipmat[7] = dims2[imax % 4]
        imax = 8
        for i in range(9, 11):
            if abs(trans[i]) > abs(trans[imax]):
                imax = i
        if trans[imax] >= 0:
            flipmat[imax] = 1
        else:
            flipmat[imax] = -1
            flipmat[11] = dims2[imax % 4]
        #context.write( 'flip matrix:', flipmat )
        needsflip = False
        if flipmat != [1, 0, 0, 0,  0, 1, 0, 0,  0, 0, 1, 0,  0, 0, 0, 1]:
            context.warning(_t_('Flip needed, with matrix:'))
            context.write('[', flipmat[0:4])
            context.write(' ', flipmat[4:8])
            context.write(' ', flipmat[8:12])
            context.write(' ', flipmat[12:16], ']')
            needsflip = True
        else:
            context.write(
                '<font color="#00c000">OK, the image seems to be in the correct orientation.</font>')

        if needsflip and not self.allow_flip_initial_MRI:
            context.write('<b>Image needs to be flipped</b>, but you did not '
                          'allow it, so it won\'t change. Expect problems in '
                          'hemispheres separation, and sulci recognition will '
                          'not work anyway.')
        if needsflip and self.allow_flip_initial_MRI:
            def matrixMult(m, p):
                return [m[0] * p[0] + m[1] * p[1] + m[2] * p[2] + m[3],
                        m[4] * p[0] + m[5] * p[1] + m[6] * p[2] + m[7],
                        m[8] * p[0] + m[9] * p[1] + m[10] * p[2] + m[11]]

            fliprot = flipmat[:3] + [0] + flipmat[4:7] + [0] + flipmat[8:11] \
                + [0, 0, 0, 0, 1]
            vs2 = [abs(x) for x in matrixMult(fliprot, vs)]
            dims = atts['volume_dimension'][:3]
            dims2 = (dims[0] * vs[0], dims[1] * vs[1], dims[2] * vs[2])
            dims3 = matrixMult(fliprot, dims2)
            dims4 = [int(round(abs(x) / y)) for x, y in zip(dims3, vs2)]

            #flip[9] = -min( 0, dims3[0] )
            #flip[10] = -min( 0, dims3[1] )
            #flip[11] = -min( 0, dims3[2] )

            context.write('<b><font color="#c00000">WARNING:</font> Flipping and '
                          're-writing source image</b>')
            context.write('voxel size orig :', vs)
            context.write('voxel size final:', vs2)
            context.write('dims orig :', dims)
            context.write('dims final:', dims4)
            context.write('transformation:', flipmat)

            mfile = context.temporary('Transformation matrix')
            mf = open(mfile.fullPath(), 'w')
            mf.write(' '.join([str(x) for x in flipmat[3:12:4]]) + '\n')
            mf.write(' '.join([str(x) for x in flipmat[:3]]) + '\n')
            mf.write(' '.join([str(x) for x in flipmat[4:7]]) + '\n')
            mf.write(' '.join([str(x) for x in flipmat[8:11]]) + '\n')
            mf.close()
            context.log('Transformation',
                        html='transformation: R = ' + str(flipmat[:3]
                                                          + flipmat[4:7] + flipmat[8:11])
                        + ', T = ' + str(flipmat[3:12:4]))

            context.system('AimsApplyTransform', '-i', self.T1mri.fullPath(),
                           '-o', self.reoriented_t1mri.fullPath(),
                           '-m', mfile.fullPath(),
                           '--sx', vs2[0], '--sy', vs2[1], '--sz', vs2[2],
                           '--dx', dims4[0], '--dy', dims4[1], '--dz', dims4[2],
                           '--type', 'nearest')

            acmm = matrixMult(flipmat, ac)
            pcmm = matrixMult(flipmat, pc)
            ipmm = matrixMult(flipmat, ip)
            context.write('new AC:', acmm)
            context.write('new PC:', pcmm)
            context.write('new IP:', ipmm)
            vs = vs2

            if self.T1mri == self.reoriented_t1mri:
                # reload image in Anatomist
                if anatomist:
                    # test if anatomist is started
                    a = anatomist.Anatomist(create=False)
                    if a:
                        object = a.getObject(self.T1mri.fullPath())
                        if object is not None:
                            a.reloadObjects([object])

        ac = [int(acmm[0] / vs[0] + 0.5), int(acmm[1] / vs[1] + 0.5),
              int(acmm[2] / vs[2] + 0.5)]
        pc = [int(pcmm[0] / vs[0] + 0.5), int(pcmm[1] / vs[1] + 0.5),
              int(pcmm[2] / vs[2] + 0.5)]
        ip = [int(ipmm[0] / vs[0] + 0.5), int(ipmm[1] / vs[1] + 0.5),
              int(ipmm[2] / vs[2] + 0.5)]

    # normalized case
    else:
        atts = aimsGlobals.aimsVolumeAttributes(self.T1mri)
        refs = atts.get('referentials')
        trans = atts.get('transformations')
        vs = atts['voxel_size']
        autonorm = False
        if refs and trans:
            for i in range(len(refs)):
                if refs[i] == 'Talairach-MNI template-SPM':
                    break
            if i >= len(refs):
                i = 0
            tr = trans[0]
            try:
                import soma.aims as aims
                a2t = aims.Motion(tr)
                t2a = a2t.inverse()
                acmm = t2a.transform([0, 0, 0])
                ac = [int(acmm[0] / vs[0]), int(acmm[1] / vs[1]),
                      int(acmm[2] / vs[2])]
                pcmm = t2a.transform([0, -28, 0])
                pc = [int(pcmm[0] / vs[0]), int(pcmm[1] / vs[1]),
                      int(pcmm[2] / vs[2])]
                ipmm = t2a.transform([0, -20, 60])
                ip = [int(ipmm[0] / vs[0]), int(ipmm[1] / vs[1]),
                      int(ipmm[2] / vs[2])]
                autonorm = True
            except Exception as e:
                context.warning(e)

        if not autonorm:
            if self.Normalised == 'MNI from SPM':
                ac = [77, 73, 88]
                pc = [77, 100, 83]
                ip = [76, 60, 35]
                acmm = ac
                pcmm = pc
                ipmm = ip
                # self.T1mri.setMinf( 'referential',
                # registration.talairachMNIReferentialId )
                # try:
                # self.T1mri.saveMinf()
                # except:
                # context.warning( 'could not set SPM/MNI normalized '
                #'referential to', self.T1mri.fullName() )
            elif self.Normalised == 'MNI from Mritotal':
                ac = [91, 88, 113]
                pc = [91, 115, 109]
                ip = [90, 109, 53]
                acmm = ac
                pcmm = pc
                ipmm = ip
            elif self.Normalised == 'Marseille from SPM':
                ac = [91, 93, 108]
                pc = [91, 118, 106]
                ip = [91, 98, 68]
                acmm = ac
                pcmm = pc
                ipmm = ip

    f = open(self.commissure_coordinates.fullPath(), 'w')
    f.write("AC: " + ' '.join([str(x) for x in ac]) + '\n')
    f.write("PC: " + ' '.join([str(x) for x in pc]) + '\n')
    f.write("IH: " + ' '.join([str(x) for x in ip]) + '\n')
    f.write("The previous coordinates, used by the system, are defined in "
            "voxels\n")
    f.write("They stem from the following coordinates in millimeters:\n")
    if self.Normalised == 'No':
        f.write("ACmm: " + ' '.join([str(x) for x in acmm]) + '\n')
        f.write("PCmm: " + ' '.join([str(x) for x in pcmm]) + '\n')
        f.write("IHmm: " + ' '.join([str(x) for x in ipmm]) + '\n')
    else:
        f.write("ACmm: " + ' '.join([str(x) for x in ac]) + '\n')
        f.write("PCmm: " + ' '.join([str(x) for x in pc]) + '\n')
        f.write("IHmm: " + ' '.join([str(x) for x in ip]) + '\n')
    f.close()

    # remove older MNI normalization
    if self.remove_older_MNI_normalization \
            and self.older_MNI_normalization is not None:
        try:
            db = neuroHierarchy.databases.database(
                self.older_MNI_normalization.get("_database"))
        except:  # running without databasing
            db = None
        for f in self.older_MNI_normalization.existingFiles():
            os.unlink(f)
        if db:
            db.removeDiskItem(self.older_MNI_normalization)

    # manage referential
    tm = registration.getTransformationManager()
    ref = tm.referential(self.T1mri)
    if ref is None:
        tm.createNewReferentialFor(self.T1mri)
