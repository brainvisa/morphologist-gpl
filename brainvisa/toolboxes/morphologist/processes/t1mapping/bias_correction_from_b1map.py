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
from brainvisa.tools import aimsGlobals

name = 'Bias correction from B1 map'
userLevel = 0

signature = Signature(
    'biased_image',
        ReadDiskItem('3D Volume', 'aims readable volume formats'),
    'corrected_image',
        WriteDiskItem('3D Volume', 'aims writable volume formats'),
    'BAFI_amplitude_map',
        ReadDiskItem('4D Volume', 'aims readable volume formats'),
    'BAFI_phase_map',
        ReadDiskItem('4D Volume', 'aims readable volume formats'),
    'B1_map',
        ReadDiskItem('3D Volume', 'aims readable volume formats'),
    'DP_GRE_lowcontrast',
        ReadDiskItem('3D Volume', 'aims readable volume formats'),
    'correction_field',
        WriteDiskItem('3D Volume', 'aims writable volume formats'),
    'field_threshold', Float(),
)


def initialization(self):
    self.setOptional('BAFI_amplitude_map', 'BAFI_phase_map', 'B1_map',
                     'DP_GRE_lowcontrast', 'correction_field')
    self.field_threshold = 0


def execution(self, context):
    if self.B1_map is not None \
            and (self.BAFI_amplitude_map is not None
                 or self.BAFI_phase_map is not None):
        context.error('When B1_map is specified, BAFI images should not.')
    if (self.BAFI_amplitude_map is not None
        and (self.BAFI_phase_map is None
             or self.B1_map is not None)) \
              or (self.BAFI_phase_map is not None
        and (self.BAFI_amplitude_map is None
             or self.B1_map is not None)):
          context.error('When B1 should be rebuilt from BAFI, both BAFI '
            'images are needed, and the B1_map should be left empty.')
    from soma import aims, aimsalgo
    from soma.aimsalgo import t1mapping
    import numpy as np
    if self.B1_map is None:
        # build B1 map
        BAFI_amplitude = aims.read(self.BAFI_amplitude.fullPath())
        BAFI_phase = aims.read(self.BAFI_phase_map.fullPath())

        BAFI_data = t1mapping.BAFIData(BAFI_amplitude, BAFI_phase)
        BAFI_data.prescribed_flip_angle = 60.0  # degrees
        BAFI_data.echo_times = [3.061, 3.061, 4.5, 7.0]  # milliseconds
        BAFI_data.TR_factor = 5.0
        BAFI_data.tau = 1.2e-3  # RF pulse duration in seconds TODO check real value!!

        #B1map_array = np.abs(BAFI_data.make_B1_map())
        B1map_array = np.abs(BAFI_data.make_flip_angle_map())
        B1map_farray = np.asfortranarray(B1map_array.reshape(
            B1map_array.shape + (1,)))
        B1map_volume = aims.Volume(B1map_farray)
        #B1map_volume.header().update(BAFI_amplitude.header())
        B1map_volume.header()['voxel_size'] \
            = BAFI_amplitude.header()['voxel_size']
        B1map_volume.header()['transformations'] \
            = BAFI_amplitude.header()['transformations']
        #B1map_farray[np.asarray(BAFI_amplitude)[:,:,:,0]<50] = 1.
        B1map_farray[B1map_farray > 1.77] = 0

    else:
        b1map = aims.read(self.B1_map.fullPath())
        BAFI_data = t1mapping.BAFIData(None, None)

    # extrapolate / smooth and resample the B1 map

    b1map_corr = BAFI_data.fix_b1_map(
        b1map, smooth_type='median', gaussian=0, output_median=False)

    biased_vol = aims.read(self.biased_image.fullPath())
    if self.DP_GRE_lowcontrast is not None:
        dp_gre_low_contrast = aims.read(self.DP_GRE_lowcontrast.fullPath())
    else:
        dp_gre_low_contrast = None

    field_threshold = self.field_threshold
    if field_threshold == 0:
        field_threshold = None

    unbiased_vol, field = t1mapping.correct_bias(
        biased_vol, b1map, dp_gre_low_contrast=dp_gre_low_contrast,
        field_threshold=field_threshold)

    aims.write(unbiased_vol, self.corrected_image.fullPath())
    if self.correction_field is not None:
        aims.write(field, self.correction_field.fullPath())



