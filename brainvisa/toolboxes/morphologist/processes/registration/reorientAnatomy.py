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
from brainvisa import registration
from soma import aims
import numpy
from six.moves import range
from six.moves import zip

name = 'Reorient Anatomy'
userLevel = 0


signature = Signature(
    't1mri', ReadDiskItem('Raw T1 MRI', 'Aims readable volume formats'),
    'output_t1mri', WriteDiskItem(
        'Raw T1 MRI', 'Aims writable volume formats'),
    'transformation',
    ReadDiskItem('Transform Raw T1 MRI to Talairach-MNI template-SPM',
                 'Transformation matrix'),
    'output_transformation',
    WriteDiskItem('Transform Raw T1 MRI to Talairach-MNI template-SPM',
                  'Transformation matrix'),
    'commissures_coordinates', ReadDiskItem('Commissure coordinates',
                                            'Commissure coordinates'),
    'output_commissures_coordinates', WriteDiskItem('Commissure coordinates',
                                                    'Commissure coordinates'),
    'allow_flip_initial_MRI', Boolean(),
)


def linkCommissures(self, proc, dummy):
    if proc.commissures_coordinates is None:
        return None
    return proc.signature['output_commissures_coordinates'].findValue(
        proc.output_t1mri)


def initialization(self):
    self.linkParameters('output_t1mri', 't1mri')
    self.linkParameters('transformation', 't1mri')
    self.linkParameters('output_transformation', 'output_t1mri')
    self.linkParameters('commissures_coordinates', 't1mri')
    self.setOptional('commissures_coordinates',
                     'output_commissures_coordinates')
    self.linkParameters('output_commissures_coordinates',
                        ('output_t1mri', 'commissures_coordinates'),
                        self.linkCommissures)
    self.allow_flip_initial_MRI = False


def execution(self, context):
    M = aims.read(self.transformation.fullPath())
    # refs: A (anat initial)
    #       F (anat flipped)
    #       N (normalized)
    # transfos: M: A -> N (input trm)
    #           R: A -> F
    #           Q: F -> N (output trm)
    # M = QR
    # R is a flip: has only 1,-1 and 0s
    # Q is roughly aligned to -I (all axes flipped): Q ~ -I
    # R = Q.inverse * M
    # so R = "binarized" (-M)
    # Then Q = M * R.inverse
    r = -M
    #context.write( 'M:', M )
    #context.write( 'r:', r )
    R = aims.AffineTransformation3d()
    R.rotation().fill(0.)
    rot = r.rotation().np[:, :, 0, 0]
    # snap/binarize
    for c in range(3):
        i = int(round(numpy.argmax(numpy.abs(rot[:, c]))))
        R.rotation().setValue(numpy.sign(rot[i, c]), i, c)
    if R.isIdentity():
        context.write('<font color="#00c000">OK, the image seems to be in the '
                      'correct orientation.</font>')
        if self.output_t1mri != self.t1mri:
            context.runProcess('AimsConverter', self.t1mri, self.output_t1mri)
        if self.commissures_coordinates is not None \
                and self.output_commissures_coordinates is not None \
                and self.output_commissures_coordinates \
                != self.commissures_coordinates:
            open(self.output_commissures_coordinates.fullPath(),
                 'w').write(open(self.commissures_coordinates.fullPath()).read())
        if self.output_transformation != self.transformation:
            tr = aims.read(self.transformation.fullPath())
            aims.write(tr, self.output_transformation.fullPath())
        return

    if (self.t1mri == self.output_t1mri and
        (not self.allow_flip_initial_MRI or not self.t1mri.isWriteable())) or \
        (self.transformation == self.output_transformation and
         (not self.allow_flip_initial_MRI or
          not self.transformation.isWriteable())) or \
        (self.commissures_coordinates is not None and
         self.commissures_coordinates == self.output_commissures_coordinates and
         (not self.allow_flip_initial_MRI or
          not self.commissures_coordinates.isWriteable())):
        context.write('<b>Image needs to be flipped</b>, but it cannot be '
                      'written, so it will not change. Expect problems in '
                      'hemispheres separation and sulci recognition.')
        return
    context.write('<b><font color="#c00000">WARNING:</font> Flipping and '
                  're-writing image</b>')
    dims = self.t1mri.get('volume_dimension')[:3]
    vs = self.t1mri.get('voxel_size')[:3]
    dimm = [x*y for x, y in zip(dims, vs)]
    vs2 = [abs(x) for x in R.transform(vs)]
    dims2 = [abs(int(round(x))) for x in R.transform(dims)]
    #context.write( 'dims: ', str( dims ), ' -> ', str( dims2 ) )
    #context.write( 'vs: ', str( vs ), ' -> ', str( vs2 ) )
    s = aims.AffineTransformation3d(R)
    a = s.rotation()
    a[a.np > 0] = 0.
    #context.write( 's:', s )
    p = -(s.transform(dimm).np)
    #context.write( 'translation:', p )
    R.toMatrix()[:3, 3] = p
    context.write('apply resampling matrix:')
    context.write(R)

    mfile = context.temporary('Transformation matrix')
    aims.write(R, mfile.fullPath())
    context.log('Transformation', html='transformation: ' + str(R))

    context.system('AimsApplyTransform', '-i', self.t1mri,
                   '-o', self.output_t1mri, '-m', mfile,
                   '--sx', vs2[0], '--sy', vs2[1], '--sz', vs2[2],
                   '--dx', dims2[0], '--dy', dims2[1], '--dz', dims2[2])

    # new normalization matrix
    Q = M * R.inverse()
    context.write('new normalization matrix:')
    context.write(Q)
    aims.write(Q, self.output_transformation.fullPath())
    if self.commissures_coordinates is not None \
            and self.output_commissures_coordinates is not None:
        context.runProcess('transformAPC',
                           Commissures_coordinates=self.commissures_coordinates,
                           destination_volume=self.output_t1mri,
                           output_coordinates=self.output_commissures_coordinates,
                           transformation=mfile)
