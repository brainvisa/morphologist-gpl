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

name = 'Correction Brain Mask from T1 MRI'
userLevel = 0

signature = Signature(
    'mri', ReadDiskItem("Raw T1 MRI", 'aims readable Volume Formats'),
    'brain_mask', WriteDiskItem('T1 Brain Mask',
                                'Aims writable volume formats'),
    'variant', Choice("Standard + (iterative erosion from 2mm)",
                      "Standard + (iterative erosion from 1.5mm)",
                      "Standard + (fixed 1.5mm erosion)",
                      "Standard + (fixed 2mm erosion)",
                      "Standard + (fixed 2.5mm erosion)",
                      "Standard + (fixed 3mm erosion)",
                      "Standard + (fixed 3.5mm erosion)",
                      "Standard + (fixed 4mm erosion)",
                      "Standard + (iterative erosion from 2mm) without regularisation",
                      "Robust + (iterative erosion from 2mm)",
                      "Robust + (iterative erosion from 1.5mm)",
                      "Robust + (fixed 1.5mm erosion)",
                      "Robust + (fixed 2mm erosion)",
                      "Robust + (fixed 2.5mm erosion)",
                      "Robust + (fixed 3mm erosion)",
                      "Robust + (fixed 3.5mm erosion)",
                      "Robust + (fixed 4mm erosion)",
                      "Robust + (iterative erosion from 2mm) without regularisation",
                      "Fast (1.5mm erosion)",
                      "Fast (2mm erosion)",
                      "Fast (2.5mm erosion)",
                      "Fast (3mm erosion)",
                      "Fast (3.5mm erosion)",
                      "Fast (4mm erosion)",
                      "Nothing"),
    'help', Choice("Nothing", "Mask visualization",
                   "Histogram analysis visualization"),
    'mri_corrected', ReadDiskItem('T1 MRI Bias Corrected',
                                  'Aims readable volume formats'),
    'histo_analysis', ReadDiskItem('Histo Analysis', 'Histo Analysis'),
    'Commissure_coordinates', ReadDiskItem('Commissure coordinates',
                                           'Commissure coordinates'),
    'lesion_mask', ReadDiskItem('3D Volume', 'aims readable Volume Formats'),
    'first_slice', Integer(),
    'last_slice', Integer(),
)


def initialization(self):
    self.linkParameters('mri_corrected', 'mri')
    self.linkParameters('histo_analysis', 'mri')
    self.linkParameters('brain_mask', 'mri')
    self.first_slice = 1
    self.last_slice = 3
    self.setOptional('Commissure_coordinates')
    self.setOptional('lesion_mask')
    self.linkParameters('Commissure_coordinates', 'mri')
    self.variant = "Robust + (iterative erosion from 2mm)"
    self.help = "Mask visualization"

# NB, les legeres differences sont liees a la discretisation avec des voxels de 1mm, SPM, MNI...*/


def execution(self, context):
    if self.variant == "Standard + (iterative erosion from 2mm)":
        context.runProcess('VipGetBrain', mode="standard+iterative", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=1,
                           erosion_size=2., first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Standard + (iterative erosion from 1.5mm)":
        context.runProcess('VipGetBrain', mode="standard+iterative", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=1,
                           erosion_size=1.5, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Standard + (fixed 1.5mm erosion)":
        context.runProcess('VipGetBrain', mode="standard", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=1,
                           erosion_size=1.5, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Standard + (fixed 2mm erosion)":
        context.runProcess('VipGetBrain', mode="standard", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=1,
                           erosion_size=2, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Standard + (fixed 2.5mm erosion)":
        context.runProcess('VipGetBrain', mode="standard", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=1,
                           erosion_size=2.5, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Standard + (fixed 3mm erosion)":
        context.runProcess('VipGetBrain', mode="standard", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=1,
                           erosion_size=3., first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Standard + (fixed 3.5mm erosion)":
        context.runProcess('VipGetBrain', mode="standard", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=1,
                           erosion_size=3.5, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Standard + (fixed 4mm erosion)":
        context.runProcess('VipGetBrain', mode="standard", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=1,
                           erosion_size=4, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Standard + (iterative erosion from 2mm) without regularisation":
        context.runProcess('VipGetBrain', mode="standard+iterative", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=0,
                           erosion_size=2., first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Robust + (iterative erosion from 2mm)":
        context.runProcess('VipGetBrain', mode="robust+iterative", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=1,
                           erosion_size=2., first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Robust + (iterative erosion from 1.5mm)":
        context.runProcess('VipGetBrain', mode="robust+iterative", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=1,
                           erosion_size=1.5, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Robust + (fixed 1.5mm erosion)":
        context.runProcess('VipGetBrain', mode="robust", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=1,
                           erosion_size=1.5, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Robust + (fixed 2mm erosion)":
        context.runProcess('VipGetBrain', mode="robust", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=1,
                           erosion_size=2, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Robust + (fixed 2.5mm erosion)":
        context.runProcess('VipGetBrain', mode="robust", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=1,
                           erosion_size=2.5, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Robust + (fixed 3mm erosion)":
        context.runProcess('VipGetBrain', mode="robust", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=1,
                           erosion_size=3., first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Robust + (fixed 3.5mm erosion)":
        context.runProcess('VipGetBrain', mode="robust", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=1,
                           erosion_size=3.5, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Robust + (fixed 4mm erosion)":
        context.runProcess('VipGetBrain', mode="robust", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=1,
                           erosion_size=4, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Robust + (iterative erosion from 2mm) without regularisation":
        context.runProcess('VipGetBrain', mode="robust+iterative", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=0,
                           erosion_size=2., first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Fast (1.5mm erosion)":
        context.runProcess('VipGetBrain', mode="fast", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=0,
                           erosion_size=1.5, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Fast (2mm erosion)":
        context.runProcess('VipGetBrain', mode="fast", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=0,
                           erosion_size=2, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Fast (2.5mm erosion)":
        context.runProcess('VipGetBrain', mode="fast", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=0,
                           erosion_size=2.5, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Fast (3mm erosion)":
        context.runProcess('VipGetBrain', mode="fast", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=0,
                           erosion_size=3, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Fast (3.5mm erosion)":
        context.runProcess('VipGetBrain', mode="fast", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=0,
                           erosion_size=3.5, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    elif self.variant == "Fast (4mm erosion)":
        context.runProcess('VipGetBrain', mode="fast", mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, brain_mask=self.brain_mask, regularization=0,
                           erosion_size=4, first_slice=self.first_slice, last_slice=self.last_slice, lesion_mask=self.lesion_mask, Commissure_coordinates=self.Commissure_coordinates)
    else:
        raise RuntimeError(
            _t_('Variant <em>%s</em> not implemented') % self.variant)
    result = []
    if self.help == "Mask visualization":
        result.append(context.runProcess('AnatomistShowBrainMask',
                                         self.brain_mask, self.mri_corrected))
    elif self.help == "Histogram analysis visualization":
        result.append(context.runProcess('VipHistoAnalysis',
                                         mri_corrected=self.mri_corrected, histo_analysis=self.histo_analysis, visu=1))
    return result
