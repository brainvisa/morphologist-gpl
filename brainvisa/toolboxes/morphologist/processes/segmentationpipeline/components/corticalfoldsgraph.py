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
import registration

name = 'Hemisphere Cortical Folds Graph (3.1)'
userLevel = 0

# Argument declaration
signature = Signature(
    'skeleton', ReadDiskItem( 'Cortex Skeleton',
        'Aims readable volume formats' ),
    'roots', ReadDiskItem( 'Cortex Catchment Bassins',
        'Aims readable volume formats' ),
    'grey_white', ReadDiskItem( 'Grey White Mask',
        'Aims readable volume formats' ),
    'hemi_cortex', ReadDiskItem( 'CSF+GREY Mask',
        'Aims readable volume formats' ),
    'split_brain', ReadDiskItem( 'Split Brain Mask',
        'Aims readable volume formats' ),
    'white_mesh', ReadDiskItem( 'Hemisphere White Mesh', 'Aims mesh formats' ),
    'pial_mesh', ReadDiskItem( 'Hemisphere Mesh', 'Aims mesh formats' ),
    'commissure_coordinates', ReadDiskItem( 'Commissure coordinates',
                                            'Commissure coordinates' ),
    'talairach_transform', ReadDiskItem( \
        'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
        'Transformation matrix' ),
    'compute_fold_meshes', Boolean(),
    'allow_multithreading', Boolean(),
    'graph_version', Choice( '3.0', '3.1', '3.2' ),
    'graph', WriteDiskItem( 'Cortical folds graph', 'Graph' ),
    'sulci_voronoi', WriteDiskItem( 'Sulci Voronoi',
        'Aims writable volume formats' ),
    'write_cortex_mid_interface', Boolean(),
    'cortex_mid_interface', WriteDiskItem ( 'Grey White Mid-Interface Volume',
      'Aims writable volume formats' ),
 )

def buildNewSignature(self, graphversion):
    paramSignature = ['skeleton', ReadDiskItem( 'Cortex Skeleton',
                      'Aims readable volume formats' )]
    paramSignature += ['roots', ReadDiskItem( 'Cortex Catchment Bassins',
                       'Aims readable volume formats' )]
    
    if graphversion!='3.0':
        paramSignature += ['grey_white', ReadDiskItem( 'Grey White Mask',
                            'Aims readable volume formats' )]
        paramSignature += ['hemi_cortex', ReadDiskItem( 'CSF+GREY Mask',
                            'Aims readable volume formats' )]
        paramSignature += ['white_mesh', ReadDiskItem( 'Hemisphere White Mesh',
                            'Aims mesh formats' )]
        paramSignature += ['pial_mesh', ReadDiskItem( 'Hemisphere Mesh',
                            'Aims mesh formats' )]
    #else:
    paramSignature += ['split_brain', ReadDiskItem( 'Split Brain Mask',
                        'Aims readable volume formats' )]
    
    paramSignature += ['commissure_coordinates', ReadDiskItem( \
        'Commissure coordinates', 'Commissure coordinates' )]
    if graphversion!='3.0':
        paramSignature += ['talairach_transform', ReadDiskItem( \
            'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
            'Transformation matrix' )]
    paramSignature += ['compute_fold_meshes', Boolean()]
    
    if graphversion!='3.0':
        paramSignature += ['allow_multithreading', Boolean()]
    
    paramSignature += ['graph_version', Choice( '3.0', '3.1', '3.2' )]
    paramSignature += ['graph', WriteDiskItem( 'Cortical folds graph', 'Graph' )]
    
    if graphversion!='3.0':
        paramSignature += ['sulci_voronoi', WriteDiskItem( 'Sulci Voronoi',
                           'Aims writable volume formats' )]
        paramSignature += ['write_cortex_mid_interface', Boolean()]
        paramSignature += ['cortex_mid_interface', WriteDiskItem ( \
            'Grey White Mid-Interface Volume', 'Aims writable volume formats' )]
    
    signature = Signature( *paramSignature )
    self.changeSignature( signature )


def initialization( self ):
    def linkGraphVersion( proc, dummy ):
        p = WriteDiskItem( 'Cortical folds graph', 'Graph' )
        r = p.findValue( proc.skeleton,
                            requiredAttributes = { 'labelled' : 'No',
                            'graph_version' : proc.graph_version } )
        return r
    
    def linkVoronoi( self, proc ):
        # this function just to link the image format from hemi_cortex
        format = None
        if self.skeleton is not None:
            format = self.skeleton.format
        if format is None:
            return self.signature['sulci_voronoi'].findValue( self.graph )
        di = WriteDiskItem( 'Sulci Voronoi', str( format ) )
        return di.findValue( self.graph )
    
    self.graph_version = '3.1'
    #self.addLink( None, 'graph_version', self.buildNewSignature )
    self.linkParameters( 'roots', 'skeleton' )
    self.linkParameters( 'grey_white', 'skeleton' )
    self.linkParameters( 'hemi_cortex', 'grey_white' )
    self.linkParameters( 'split_brain', 'skeleton' )
    self.linkParameters( 'white_mesh', 'grey_white' )
    self.linkParameters( 'pial_mesh', 'white_mesh' )
    self.linkParameters( 'commissure_coordinates', 'grey_white' )
    self.linkParameters( 'talairach_transform', 'grey_white' )
    self.linkParameters( 'graph', ( 'skeleton', 'graph_version' ), linkGraphVersion )
    self.linkParameters( 'sulci_voronoi', ( 'graph', 'skeleton' ), linkVoronoi )
    self.linkParameters( 'cortex_mid_interface', 'grey_white' )
    self.setOptional( 'commissure_coordinates' )
    self.setOptional( 'talairach_transform' )
    self.setOptional( 'sulci_voronoi' )
    self.setOptional( 'write_cortex_mid_interface' )
    self.setOptional( 'cortex_mid_interface' )
    self.compute_fold_meshes = True
    self.allow_multithreading = True
    self.write_cortex_mid_interface = False


def execution( self, context ):
    trManager = registration.getTransformationManager()
    
    context.write("Building Attributed Relational Graph...")
    graphd = context.temporary( 'Directory' )
    graph = os.path.join( graphd.fullPath(), 'foldgraph' )
    context.system( 'VipFoldArg', '-i',
                    self.skeleton, '-v',
                    self.roots, '-o',
                    graph, '-w', 'g' )
    
    if self.graph_version == '3.0':
        if self.compute_fold_meshes:
            mesh = 'y'
        else:
            mesh = 'n'
        lhemi = context.temporary( 'NIFTI-1 Image' )
        rhemi = context.temporary( 'NIFTI-1 Image' )
        context.system( 'VipSingleThreshold', '-i',
                        self.split_brain, '-o', lhemi,
                        '-t', '2', '-c', 'b',
                        '-m', 'eq', '-w', 't' )
        context.system( 'VipSingleThreshold', '-i',
                        self.split_brain, '-o', rhemi,
                        '-t', '1', '-c', 'b',
                        '-m', 'eq', '-w', 't' )
        
        context.system( 'VipFoldArgAtt', '-i', self.skeleton,
                        '-lh', lhemi, '-rh', rhemi,
                        '-P', self.commissure_coordinates,
                        '-a', graph, '-t', mesh )
        tgraph = context.temporary( 'Graph and Data' )
        context.system( 'VipFoldArg', '-a', graph, '-o', tgraph.fullName(), '-w', 'g' )
        context.system( 'AimsGraphConvert', '-i', tgraph, '-o', self.graph, '-b',
                        os.path.basename( self.graph.fullName() ) + '.data', '-g' )
        context.write( 'computing additional attributes' )
        context.system( 'AimsGraphComplete', '-i', self.graph,
                        '--dversion', '3.0', '--mversion', '3.0' )
        
    else:
        command = [ 'AimsFoldArgAtt', '-i', self.skeleton,
                    '-g', graph + '.arg', '-o', self.graph,
                    '-m', self.talairach_transform,
                    '--graphversion', self.graph_version ]
        if not self.compute_fold_meshes:
            command.extend( [ '-n' ] )
        if self.commissure_coordinates:
            command.extend( [ '--apc', self.commissure_coordinates ] )
        if not self.allow_multithreading:
            command.extend( [ '--threads', '1' ] )
        context.system( *command )
        
        context.runProcess("sulcivoronoi",
                            graph = self.graph,
                            hemi_cortex = self.hemi_cortex,
                            sulci_voronoi = self.sulci_voronoi)
        context.runProcess("CorticalFoldsGraphThickness",
                            graph = self.graph,
                            hemi_cortex = self.hemi_cortex,
                            GW_interface = self.grey_white,
                            white_mesh = self.white_mesh,
                            hemi_mesh = self.pial_mesh,
                            output_graph = self.graph,
                            output_mid_interface = self.cortex_mid_interface,
                            sulci_voronoi = self.sulci_voronoi)
        
        trManager.copyReferential( self.skeleton, self.sulci_voronoi )
        if self.write_cortex_mid_interface is not None:
            trManager.copyReferential( self.skeleton, self.cortex_mid_interface )
    
    trManager.copyReferential( self.skeleton, self.graph )

