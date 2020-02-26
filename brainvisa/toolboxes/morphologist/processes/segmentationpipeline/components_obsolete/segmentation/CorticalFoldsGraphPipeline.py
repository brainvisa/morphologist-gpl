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

name = 'Cortical Fold Graph (3.1+)'
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
    'graph_version', OpenChoice('3.1', '3.2'),
    'graph', WriteDiskItem('Cortical folds graph', 'Graph'),
    'commissure_coordinates', ReadDiskItem('Commissure coordinates',
                                           'Commissure coordinates'),
    'Talairach_transform',
    ReadDiskItem('Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
                 'Transformation matrix'),
)


# Default values
def initialization(self):
    def linkSide(proc, dummy):
        p = ReadDiskItem('CSF+GREY Mask', 'GIS image')
        return p.findValue(proc.mri_corrected,
                           requiredAttributes={'side': proc.side.lower()})

    def linkGraphVersion(proc, dummy):
        p = WriteDiskItem('Cortical folds graph', 'Graph')
        return p.findValue(proc.hemi_cortex,
                           requiredAttributes={'labelled': 'No',
                                               'graph_version': proc.graph_version})

    eNode = SerialExecutionNode(self.name, parameterized=self)
    eNode.addChild('GraphStructure',
                   ProcessExecutionNode('graphstructure_3_1', optional=1))
    eNode.addChild('SulciVoronoi',
                   ProcessExecutionNode('SulciVoronoi', optional=1))
    eNode.addChild('CorticalFoldsGraphThickness',
                   ProcessExecutionNode('CorticalFoldsGraphThickness',
                                        optional=1))
    #self.clearLinksTo( eNode.parseParameterString( 'CorticalFoldsGraphThickness.hemi_cortex' ) )
    #self.clearLinksTo( eNode.parseParameterString( 'CorticalFoldsGraphThickness.output_graph' ) )
    eNode.GraphStructure.clearLinksTo('Talairach_transform')
    eNode.GraphStructure.clearLinksTo('hemi_cortex')
    eNode.GraphStructure.clearLinksTo('split_mask')
    eNode.GraphStructure.clearLinksTo('graph')
    eNode.SulciVoronoi.clearLinksTo('hemi_cortex')
    eNode.CorticalFoldsGraphThickness.clearLinksTo('hemi_cortex')
    eNode.CorticalFoldsGraphThickness.clearLinksTo('output_graph')
    eNode.CorticalFoldsGraphThickness.clearLinksTo('sulci_voronoi')
    eNode.addLink('GraphStructure.side', 'side')
    eNode.addLink('side', 'GraphStructure.side')
    eNode.addLink('GraphStructure.mri_corrected', 'mri_corrected')
    eNode.addLink('mri_corrected', 'GraphStructure.mri_corrected')
    eNode.addLink('GraphStructure.split_mask', 'split_mask')
    eNode.addLink('split_mask', 'GraphStructure.split_mask')
    eNode.addLink('GraphStructure.hemi_cortex', 'hemi_cortex')
    eNode.addLink('hemi_cortex', 'GraphStructure.hemi_cortex')
    eNode.addLink('GraphStructure.skeleton', 'skeleton')
    eNode.addLink('skeleton', 'GraphStructure.skeleton')
    eNode.addLink('GraphStructure.roots', 'roots')
    eNode.addLink('roots', 'GraphStructure.roots')
    eNode.addLink('GraphStructure.graph_version', 'graph_version')
    eNode.addLink('graph_version', 'GraphStructure.graph_version')
    eNode.addLink('GraphStructure.graph', 'graph')
    eNode.addLink('graph', 'GraphStructure.graph')
    eNode.addLink('GraphStructure.commissure_coordinates',
                  'commissure_coordinates')
    eNode.addLink('commissure_coordinates',
                  'GraphStructure.commissure_coordinates')
    eNode.addLink('GraphStructure.Talairach_transform', 'Talairach_transform')
    eNode.addLink('Talairach_transform', 'GraphStructure.Talairach_transform')

    eNode.addLink('SulciVoronoi.graph', 'graph')
    eNode.addLink('graph', 'GraphStructure.graph')
    eNode.addLink('SulciVoronoi.hemi_cortex', 'hemi_cortex')
    eNode.addLink('hemi_cortex', 'SulciVoronoi.hemi_cortex')
    eNode.addLink('CorticalFoldsGraphThickness.graph', 'graph')
    eNode.addLink('graph', 'CorticalFoldsGraphThickness.graph')
    eNode.addLink('CorticalFoldsGraphThickness.hemi_cortex', 'hemi_cortex')
    eNode.addLink('hemi_cortex', 'CorticalFoldsGraphThickness.hemi_cortex')
    eNode.addLink('CorticalFoldsGraphThickness.output_graph', 'graph')
    eNode.addLink('graph', 'CorticalFoldsGraphThickness.output_graph')
    eNode.addLink('SulciVoronoi.sulci_voronoi',
                  'CorticalFoldsGraphThickness.sulci_voronoi')
    eNode.addLink('CorticalFoldsGraphThickness.sulci_voronoi',
                  'SulciVoronoi.sulci_voronoi')
    self.setExecutionNode(eNode)

    self.linkParameters('split_mask', 'mri_corrected')
    self.linkParameters('hemi_cortex', ('split_mask', 'side'), linkSide)
    self.linkParameters('skeleton', 'hemi_cortex')
    self.linkParameters('graph', ('skeleton', 'graph_version'),
                        linkGraphVersion)
    self.linkParameters('roots', 'skeleton')
    self.linkParameters('commissure_coordinates', 'mri_corrected')
    self.linkParameters('Talairach_transform', 'split_mask')
    self.setOptional('commissure_coordinates')
