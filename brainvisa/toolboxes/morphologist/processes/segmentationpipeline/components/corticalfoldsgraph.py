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
from brainvisa import registration

name = 'Hemisphere Cortical Folds Graph'
userLevel = 0

# Argument declaration
signature = Signature(
    'skeleton', ReadDiskItem('Cortex Skeleton',
                             'Aims readable volume formats'),
    'roots', ReadDiskItem('Cortex Catchment Bassins',
                          'Aims readable volume formats'),
    'grey_white', ReadDiskItem('Grey White Mask',
                               'Aims readable volume formats'),
    'hemi_cortex', ReadDiskItem('CSF+GREY Mask',
                                'Aims readable volume formats'),
    'split_brain', ReadDiskItem('Split Brain Mask',
                                'Aims readable volume formats'),
    'white_mesh', ReadDiskItem('Hemisphere White Mesh', 'Aims mesh formats'),
    'pial_mesh', ReadDiskItem('Hemisphere Mesh', 'Aims mesh formats'),
    'commissure_coordinates', ReadDiskItem('Commissure coordinates',
                                           'Commissure coordinates'),
    'talairach_transform', ReadDiskItem(
        'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
        'Transformation matrix'),
    'compute_fold_meshes', Boolean(),
    'allow_multithreading', Boolean(),
    'graph_version', Choice('3.0', '3.1', '3.2'),
    'graph', WriteDiskItem('Cortical folds graph', 'Graph'),
    'sulci_voronoi', WriteDiskItem('Sulci Voronoi',
                                   'Aims writable volume formats'),
    'write_cortex_mid_interface', Boolean(),
    'cortex_mid_interface', WriteDiskItem('Grey White Mid-Interface Volume',
                                          'Aims writable volume formats'),
)


def buildNewSignature(self, graphversion):
    if graphversion == '3.0':
        self.signature['grey_white'].userLevel = 100
        self.signature['hemi_cortex'].userLevel = 100
        self.signature['white_mesh'].userLevel = 100
        self.signature['pial_mesh'].userLevel = 100
        self.signature['split_brain'].userLevel = 0
        self.signature['talairach_transform'].userLevel = 100
        self.signature['allow_multithreading'].userLevel = 100
        self.signature['sulci_voronoi'].userLevel = 100
        self.signature['write_cortex_mid_interface'].userLevel = 100
        self.signature['cortex_mid_interface'].userLevel = 100
        self.setOptional('grey_white')
        self.setOptional('hemi_cortex')
        self.setOptional('white_mesh')
        self.setOptional('pial_mesh')
        self.setMandatory('split_brain')
        self.setMandatory('commissure_coordinates')
        self.setOptional('talairach_transform')
        self.setOptional('allow_multithreading')
        self.setOptional('sulci_voronoi')
        self.setOptional('write_cortex_mid_interface')
    else:
        self.signature['grey_white'].userLevel = 0
        self.signature['hemi_cortex'].userLevel = 0
        self.signature['white_mesh'].userLevel = 0
        self.signature['pial_mesh'].userLevel = 0
        self.signature['split_brain'].userLevel = 100
        self.signature['talairach_transform'].userLevel = 0
        self.signature['allow_multithreading'].userLevel = 0
        self.signature['sulci_voronoi'].userLevel = 0
        self.signature['write_cortex_mid_interface'].userLevel = 0
        self.signature['cortex_mid_interface'].userLevel = 0
        self.setMandatory('grey_white')
        self.setMandatory('hemi_cortex')
        self.setMandatory('white_mesh')
        self.setMandatory('pial_mesh')
        self.setOptional('split_brain')
        self.setOptional('commissure_coordinates')
        self.setMandatory('talairach_transform')
        self.setMandatory('allow_multithreading')
        self.setMandatory('sulci_voronoi')
        self.setMandatory('write_cortex_mid_interface')
    self.changeSignature(self.signature)


def initialization(self):
    def linkGraphVersion(proc, dummy):
        p = WriteDiskItem('Cortical folds graph', 'Graph')
        r = p.findValue(proc.skeleton,
                        requiredAttributes={'labelled': 'No',
                                            'graph_version': proc.graph_version})
        return r

    def linkVoronoi(self, proc):
        # Function just to link the image format from skeleton
        format = None
        if self.skeleton is not None:
            format = self.skeleton.format
        if format is None:
            return self.signature['sulci_voronoi'].findValue(self.graph)
        di = WriteDiskItem('Sulci Voronoi', str(format))
        return di.findValue(self.graph)

    def link_tal(self, proc):
        # a direct link to grey_white would refer to an analysis session
        # however talairach_transform is outside the analysis session and lies
        # next to the raw T1 acquisition. In rate (and probably erroneous)
        # cases when the acquisition and the analysis have a different
        # center attribute, talairach_transform should take it from the raw
        # T1 MRI.
        tal = None
        t1mri = ReadDiskItem(
            'Raw T1 MRI',
            'aims readable volume formats').findValue(self.grey_white)
        if t1mri is not None:
            tal = self.signature['talairach_transform'].findValue(t1mri)
        if tal is None:
            # fallback to grey_white
            tal = self.signature['talairach_transform'].findValue(
                self.grey_white)
        return tal

    self.graph_version = '3.1'
    self.addLink(None, 'graph_version', self.buildNewSignature)
    self.linkParameters('roots', 'skeleton')
    self.linkParameters('grey_white', 'skeleton')
    self.linkParameters('hemi_cortex', 'grey_white')
    self.linkParameters('split_brain', 'skeleton')
    self.linkParameters('white_mesh', 'grey_white')
    self.linkParameters('pial_mesh', 'white_mesh')
    self.linkParameters('commissure_coordinates', 'grey_white')
    self.linkParameters('talairach_transform', 'grey_white', link_tal)
    self.linkParameters(
        'graph', ('skeleton', 'graph_version'), linkGraphVersion)
    self.linkParameters('sulci_voronoi', ('graph', 'skeleton'), linkVoronoi)
    self.linkParameters('cortex_mid_interface', 'grey_white')
    self.setOptional('cortex_mid_interface')
    self.compute_fold_meshes = True
    self.allow_multithreading = True
    self.write_cortex_mid_interface = False


def execution(self, context):
    trManager = registration.getTransformationManager()

    side = self.skeleton.get('side')
    if side is not None:
        context.write("Building " + side +
                      " hemisphere attributed relational sulci graph...")
    else:
        context.write("Building attributed relational sulci graph...")

    graphd = context.temporary('Directory')
    graph = os.path.join(graphd.fullPath(), 'foldgraph')
    command = ['VipFoldArg',
               '-i', self.skeleton,
               '-v', self.roots,
               '-o', graph]
    if self.graph_version != '3.0':
        command += ['-w', 'g']
    context.system(*command)

    if self.graph_version == '3.0':
        if self.compute_fold_meshes:
            mesh = 'y'
        else:
            mesh = 'n'
        lhemi = context.temporary('NIFTI-1 Image')
        rhemi = context.temporary('NIFTI-1 Image')
        context.system('VipSingleThreshold', '-i',
                       self.split_brain, '-o', lhemi,
                       '-t', '2', '-c', 'b',
                       '-m', 'eq', '-w', 't')
        context.system('VipSingleThreshold', '-i',
                       self.split_brain, '-o', rhemi,
                       '-t', '1', '-c', 'b',
                       '-m', 'eq', '-w', 't')

        context.system('VipFoldArgAtt', '-i', self.skeleton,
                       '-lh', lhemi, '-rh', rhemi,
                       '-P', self.commissure_coordinates,
                       '-a', graph, '-t', mesh)
        tgraph = context.temporary('Graph and Data')
        context.system('VipFoldArg', '-a', graph, '-o',
                       tgraph.fullName(), '-w', 'g')
        context.system('AimsGraphConvert', '-i', tgraph, '-o', self.graph, '-b',
                       os.path.basename(self.graph.fullName()) + '.data', '-g')
        context.write('computing additional attributes')
        context.system('AimsGraphComplete', '-i', self.graph,
                       '--dversion', '3.0', '--mversion', '3.0')

    else:
        command = ['AimsFoldArgAtt', '-i', self.skeleton,
                   '-g', graph + '.arg', '-o', self.graph,
                   '-m', self.talairach_transform,
                   '--graphversion', self.graph_version]
        if not self.compute_fold_meshes:
            command += ['-n']
        if self.commissure_coordinates:
            command += ['--apc', self.commissure_coordinates]
        if not self.allow_multithreading:
            command += ['--threads', '1']
        context.system(*command)

        context.runProcess("sulcivoronoi",
                           graph=self.graph,
                           hemi_cortex=self.hemi_cortex,
                           sulci_voronoi=self.sulci_voronoi)
        context.runProcess("CorticalFoldsGraphThickness",
                           graph=self.graph,
                           hemi_cortex=self.hemi_cortex,
                           GW_interface=self.grey_white,
                           white_mesh=self.white_mesh,
                           hemi_mesh=self.pial_mesh,
                           output_graph=self.graph,
                           output_mid_interface=self.cortex_mid_interface,
                           sulci_voronoi=self.sulci_voronoi)

        trManager.copyReferential(self.skeleton, self.sulci_voronoi)
        if self.write_cortex_mid_interface is not None:
            trManager.copyReferential(self.skeleton, self.cortex_mid_interface)

    trManager.copyReferential(self.skeleton, self.graph)
