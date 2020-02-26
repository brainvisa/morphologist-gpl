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

name = 'Graph Structure (3.0)'
userLevel = 2

# Argument declaration
signature = Signature(
    'side', Choice('Left', 'Right'),
    'mri_corrected', ReadDiskItem('T1 MRI Bias Corrected',
                                  'Aims readable volume formats'),
    'split_mask', ReadDiskItem('Split Brain Mask',
                               'Aims readable volume formats'),
    'hemi_cortex', ReadDiskItem('CSF+GREY Mask',
                                'Aims readable volume formats'),
    'skeleton', WriteDiskItem('Cortex Skeleton',
                              'Aims writable volume formats'),
    'roots', WriteDiskItem('Cortex Catchment Bassins',
                           'Aims writable volume formats'),
    'graph', WriteDiskItem('Cortical folds graph', 'Graph',
                           requiredAttributes={'graph_version': '3.0', 'labelled': 'No'}),
    'commissure_coordinates', ReadDiskItem('Commissure coordinates',
                                           'Commissure coordinates'),
    'compute_fold_meshes', Boolean(),
)


def initialization(self):
    def linkSide(proc, dummy):
        p = ReadDiskItem('CSF+GREY Mask', 'aims readable volume formats')
        return p.findValue(proc.mri_corrected,
                           requiredAttributes={'side': proc.side.lower()})

    self.linkParameters('split_mask', 'mri_corrected')
    self.linkParameters('hemi_cortex', ('split_mask', 'side'), linkSide)
    self.linkParameters('skeleton', 'hemi_cortex')
    self.linkParameters('graph', 'skeleton')
    self.linkParameters('roots', 'skeleton')
    self.linkParameters('commissure_coordinates', 'mri_corrected')
    self.compute_fold_meshes = True


def execution(self, context):
    context.write("Masking Bias corrected image with hemisphere masks...")
    lbraing = context.temporary('NIFTI-1 Image')
    rbraing = context.temporary('NIFTI-1 Image')
    if self.side == 'Left':
        braing = lbraing
    else:
        braing = rbraing
    context.system('VipMask', '-i', self.mri_corrected, "-m",
                   self.split_mask, "-o", lbraing, "-w", "t", "-l", 2)
    context.system('VipMask', '-i', self.mri_corrected, "-m",
                   self.split_mask, "-o", rbraing, "-w", "t", "-l", 1)

    context.write("Computing skeleton and buried gyrus watershed...")
    context.system("VipSkeleton", "-i", self.hemi_cortex,
                   "-so", self.skeleton, "-vo", self.roots,
                   "-g", braing, "-ve", "1", "-w", "t")

    context.write("Building Attributed Relational Graph...")
    graphd = context.temporary('Directory')
    graph = os.path.join(graphd.fullPath(), 'foldgraph')
    context.system("VipFoldArg", "-i", self.skeleton, "-v",
                   self.roots, "-o", graph)

    if self.compute_fold_meshes:
        mesh = 'y'
    else:
        mesh = 'n'
    attp = ["VipFoldArgAtt", "-i", self.skeleton, '-lh', lbraing, '-rh', rbraing,
            "-a", graph, "-P", self.commissure_coordinates, "-t", mesh]
    context.system(*attp)
    tgraph = context.temporary('Graph and Data')
    context.system("VipFoldArg", "-a", graph, "-o",
                   tgraph.fullName(), "-w", "g")
    context.system("AimsGraphConvert", "-i", tgraph, "-o", self.graph, "-b",
                   os.path.basename(self.graph.fullName()) + '.data', "-g")
    context.write('computing additional attributes')
    context.system('AimsGraphComplete', '-i', self.graph,
                   '--dversion', '3.0', '--mversion', '3.0')
    trManager = registration.getTransformationManager()
    trManager.copyReferential(self.mri_corrected, self.skeleton)
    trManager.copyReferential(self.mri_corrected, self.roots)
    trManager.copyReferential(self.mri_corrected, self.graph)
