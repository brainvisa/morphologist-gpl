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

from neuroProcesses import *
import shfjGlobals
from brainvisa import anatomist

name = 'Anatomist Show Superimposed Graphs'
userLevel = 1

def validation():
    anatomist.validation()

signature = Signature(
    'graph', ListOf( ReadDiskItem( 'Cortical folds graph', 'Graph' ) ),
    'nomenclature', ReadDiskItem( 'Nomenclature', 'Hierarchy' ), 
    'hemi_mesh', ReadDiskItem( 'Hemisphere Mesh', 'Anatomist mesh formats' ),
    )

def initialization( self ):
    def linkMesh( self, proc ):
        if len( self.graph ) > 0:
            di = ReadDiskItem( 'Hemisphere Mesh',
                               'MESH mesh' ).findValue( self.graph[0] )
            return di.fullPath()
    self.setOptional( 'nomenclature' )
    self.setOptional( 'hemi_mesh' )
    #self.linkParameters( 'hemi_mesh', 'graph', linkMesh )
    self.nomenclature = self.signature[ 'nomenclature' ].findValue( {} )

def execution( self, context ):
    a = anatomist.Anatomist()
    obj = []
    selfdestroy = []
    if self.nomenclature is not None:
        ( hie, br ) = context.runProcess( 'AnatomistShowNomenclature',
                                          read=self.nomenclature )
        selfdestroy += ( hie, br )
    if self.hemi_mesh is not None:
        self.graph.append( self.hemi_mesh )
    # Load each graph
    for g in self.graph:
        graph = a.loadObject( g )
        obj.append( graph )
    win3 = a.createWindow( '3D' )
    win3.addObjects( obj )
    selfdestroy.append( win3 )
    if self.nomenclature is not None:
        wg= a.getDefaultWindowsGroup()
        # to see the graph elements, we have to select them. After that they remain visible even if they are deselected
        wg.setSelectionByNomenclature( hie, ["unknown", "brain"] )
        wg.toggleSelectionByNomenclature(hie, ["unknown", "brain"])
    selfdestroy += obj
    return selfdestroy
