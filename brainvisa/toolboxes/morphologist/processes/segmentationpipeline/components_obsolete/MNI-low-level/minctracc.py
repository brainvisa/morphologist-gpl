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

#
from brainvisa.processes import *

name = 'Minctracc'
userLevel = 1

#########
# Attention il manque les parametres pour -nonmlinear
#########

signature = Signature(
    'source', ReadDiskItem('MINC image', 'MINC image'),
    'target', ReadDiskItem('MINC image', 'MINC image'),
    'transformed_source', WriteDiskItem('MINC image', 'MINC image'),
    'output_transfile', WriteDiskItem(
        'MINC transformation matrix', 'MINC transformation matrix'),
    'transformation_type', Choice('nonlinear', 'principal axis', '3 translations', '3 translations + 3 rotations',
                                  '3 translations + 3 rotations + global scale', '3 translation + 3 rotations + 3 scales',
                                  '3 translation + 3 rotations + 3 scales + 1 shear', '3 translation + 3 rotations + 3 scales + 3 shears'),
    'transformation_direction', Choice('Forward', 'Invert'),
    'initial_transformation', ReadDiskItem(
        'MINC transformation matrix', 'MINC transformation matrix'),
    # matrice identite ou sinon calcul centre des 2 images
    'estimation_init_transfo', Choice('Gravity_center', 'Identity'),
    'estimation_center', Choice('No', 'Yes'),
    'estimation_scales', Choice('No', 'Yes'),
    'estimation_translations', Choice('No', 'Yes'),
    'center', ListOf(Number()),
    'transformation_direction', Choice('Forward', 'Invert'),
    'rotation_type', Choice('Rotations', 'Quaternions'),
    #'feature_vol',ListOf( ??? ),
    'model_mask', ReadDiskItem('MINC image', 'MINC image'),
    'source_mask', ReadDiskItem('MINC image', 'MINC image'),
    'interpolation', Choice('trilinear', 'tricubic', 'nearest_neighbour'),
    'optimization_function', Choice('cross_correlation', 'normalized_difference',
                                    'stochastic_sign_change', 'variance_of_ratio', 'mutual_information'),
    'group_number', Integer(),
    'threshold', ListOf(Number()),
    'blur_pdf', Integer(),
    'speckle', Float(),
    'tol', ListOf(Number()),
    'w_translations', ListOf(Number()),
    'w_rotations', ListOf(Number()),
    'w_scales', ListOf(Number()),
    'w_shear', ListOf(Number()),
    #'matlab',????, # fichier matlab pour visu les minima
    #'num_steps',?????,
    #'measure',??????,
    'tol', Float(),
    'simplex', Float(),
    'num_steps', Integer(),
    'source_lattice', ReadDiskItem('MINC image', 'MINC image'),
    'model_lattice', ReadDiskItem('MINC image', 'MINC image'),
    'step', ListOf(Number()),
    'xstep', Integer(),
    'ystep', Integer(),
    'zstep', Integer(),
    'sub_lattice', Integer(),
    'lattice_diameter', ListOf(Number()),
    'max_def_magnitude', Float(),
    'param1', Choice('magnitude', 'optical_flow'),
    'param2', Choice('simplex', 'quadratic'),
    'smoothing', Choice('Global', 'Local'),
    'smoothing_direction', Choice('Isotropic', 'Anisotropic'),
    'super', Integer(),
    'iterations', Integer(),
    'weight', Float(),
    'stiffness', Float(),
    'similarity_cost_ratio', Float()
)


# Default values
def initialization(self):
    self.center = [-1.79769e+308, -1.79769e+308, -1.79769e+308]
    self.group_number = 256
    self.blur_pdf = 3
    self.threshold = [0, 0]
    self.speckle = 5
    self.w_translations = [1, 1, 1]
    self.w_rotations = [0.0174533, 0.0174533, 0.0174533]
    self.w_scales = [0.02, 0.02, 0.02]
    self.w_shear = [0.02, 0.02, 0.02]
    self.tol = 0.005
    self.simplex = 20
    self.step = [4, 4, 4]
    self.num_steps = 15
    self.xstep = 4
    self.ystep = 4
    self.zstep = 4
    self.lattice_diameter = [24, 24, 24]
    self.sub_lattice = 5
    self.max_def_magnitude = 50
    self.super = 2
    self.iterations = 4
    self.weight = 0.6
    self.stiffness = 0.5
    self.similarity_cost_ratio = 0.5
    self.sub_lattice = 5

    self.setOptional('initial_transformation')
    self.setOptional('source_lattice')
    self.setOptional('model_lattice')
    self.setOptional('center')
    self.setOptional('super')
    self.setOptional('model_mask')
    self.setOptional('source_mask')
    self.setOptional('transformed_source')


def execution(self, context):

    if len(self.center) != 3 \
            or len(self.threshold) != 2 \
            or len(self.w_translations) != 3 \
            or len(self.w_rotations) != 3 \
            or len(self.w_scales) != 3 \
            or len(self.w_shear) != 3 \
            or len(self.step) != 3 \
            or len(self.lattice_diameter) != 3:
        context.write('Error: center, threshold, w_translations, w_rotations, \
      w_scales, w_shear, step, or lattice_diameter has not the right number of parameters.')
        return

    option_list = []

    if self.initial_transformation is not None:
        option_list += ['-transformation',
                        self.initial_transformation.fullName()]
    else:
        if self.estimation_init_transfo == 'Identity':
            option_list += ['-identity']

    if self.estimation_center == 'Yes':
        option_list += ['-est_center']

    if self.estimation_scales == 'Yes':
        option_list += ['-est_scales']
    else:
        option_list += ['-center', self.center[0],
                        self.center[2], self.center[1]]

    if self.transformation_direction == 'Forward':
        option_list += ['-forward']
    else:
        option_list += ['-invert']

    if self.rotation_type == 'Rotations':
        option_list += ['-rotations']
    else:
        option_list += ['-quaternions']

    if self.model_mask is not None:
        option_list += ['-model_mask', self.model_mask.fullName()]

    if self.source_mask is not None:
        option_list += ['-source_mask', self.source_mask.fullName()]

    if self.interpolation == 'trilinear':
        option_list += ['-trilinear']

    if self.interpolation == 'tricubic':
        option_list += ['-tricubic']

    if self.interpolation == 'nearest_neighbour':
        option_list += ['-nearest_neighbour']

    if self.optimization_function == 'cross_correlation':
        option_list += ['-xcorr']

    if self.optimization_function == 'normalized_difference':
        option_list += ['-zscore']

    if self.optimization_function == 'stochastic_sign_change':
        option_list += ['-scc']

    if self.optimization_function == 'mutual_information':
        option_list += ['-mi']

    if self.smoothing == 'Local':
        option_list += ['-use_local']

    if self.smoothing_direction == 'Anisotropic':
        option_list += ['-use_nonisotropic']

    if self.super is None:
        option_list += ['-no_super']
    else:
        option_list += ['-super', self.super]

    if self.transformation_type == 'nonlinear':
        option_list += ['-nonlinear']

    if self.transformation_type == 'principal axis':
        option_list += ['-pat']

    if self.transformation_type == '3 translations':
        option_list += ['-lsq3']

    if self.transformation_type == '3 translations + 3 rotations':
        option_list += ['-lsq6']

    if self.transformation_type == '3 translations + 3 rotations + global scale':
        option_list += ['-lsq7']

    if self.transformation_type == '3 translation + 3 rotations + 3 scales':
        option_list += ['-lsq9']

    if self.transformation_type == '3 translation + 3 rotations + 3 scales + 1 shear':
        option_list += ['-lsq10']

    if self.transformation_type == '3 translation + 3 rotations + 3 scales + 3 shears':
        option_list += ['-lsq12']

    if self.source_lattice is not None:
        option_list += ['-source_lattice', self.source_lattice.fullPath()]

    if self.model_lattice is not None:
        option_list += ['-model_lattice', self.model_lattice.fullPath()]

    # if self.param1 == 'magnitude':
       # option_list += ['-use_magnitude']

    # if self.param2 == 'simplex'
       # option_list += ['-simplex']

    call_list = ['minctracc', '-clobber',
                 '-groups', self.group_number,
                 '-blur_pdf', self.blur_pdf,
                 '-threshold', self.threshold[0], self.threshold[1],
                 '-speckle', self.speckle,
                 '-tol', self.tol,
                 '-simplex', self.simplex,
                 '-w_translations', self.w_translations[0], self.w_translations[1], self.w_translations[2],
                 '-w_rotations', self.w_rotations[0], self.w_rotations[1], self.w_rotations[2],
                 '-w_scales', self.w_scales[0], self.w_scales[1], self.w_scales[2],
                 '-w_shear', self.w_shear[0], self.w_shear[1], self.w_shear[2],
                 '-num_steps', self.num_steps,
                 '-step', self.step[0], self.step[1], self.step[2],
                 '-xstep', self.xstep, '-ystep', self.ystep, '-zstep', self.zstep,
                 '-sub_lattice', self.sub_lattice,
                 '-lattice_diameter', self.lattice_diameter[0], self.lattice_diameter[1], self.lattice_diameter[2],
                 '-max_def_magnitude', self.max_def_magnitude,
                 '-iterations', self.iterations,
                 '-weight', self.weight,
                 '-stiffness', self.stiffness,
                 '-similarity_cost_ratio', self.similarity_cost_ratio]

    io = [self.source.fullPath(),
          self.target.fullPath(),
          self.output_transfile.fullPath()]

    context.system(*(call_list+option_list+io))

    if self.transformed_source is not None:
        if self.transformation_direction == 'Forward':
            command = ['mincresample', '-clobber', '-like', self.target.fullPath(),
                       self.source.fullPath(), self.transformed_source.fullPath()]
        else:
            command = ['mincresample', '-invert_transformation', '-clobber', '-like',
                       self.target.fullPath(), self.source.fullPath(), self.transformed_source.fullPath()]
        context.system(*command)
