# Copyright CEA and IFR 49 (2000-2005)
#
#  This software and supporting documentation were developed by
#      CEA/DSV/SHFJ and IFR 49
#      4 place du General Leclerc
#      91401 Orsay cedex
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

name = 'Anatomist Show Fold Graph'
roles = ('viewer',)
userLevel = 0

def validation():
    anatomist.validation()

signature = Signature(
    'graph', ReadDiskItem( 'Cortical folds graph', 'Graph' ),
    'nomenclature', ReadDiskItem( 'Nomenclature', 'Hierarchy' ),
    'hemi_mesh', ReadDiskItem( 'Hemisphere Mesh', 'Anatomist mesh formats' ),
    'load_MRI', Choice("Yes","No"),
    'two_windows', Choice("Yes","No"),
    'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
      'Anatomist volume formats' )
    )

def initialization( self ):
    self.setOptional( 'nomenclature' )
    self.setOptional( 'mri_corrected' )
    self.setOptional( 'hemi_mesh' )
    self.load_MRI = "No"
    self.two_windows = "No"
    self.linkParameters( 'hemi_mesh', 'graph' )
    self.linkParameters( 'mri_corrected', 'graph' )
    self.nomenclature = self.signature[ 'nomenclature' ].findValue( {} )

def execution( self, context ):
    a = anatomist.Anatomist()
    selfdestroy = []
    if self.nomenclature is not None:
        ( hie, br ) = context.runProcess( 'AnatomistShowNomenclature',
                                          read=self.nomenclature )
        selfdestroy += ( hie, br )
    l = self.graph.get( 'automatically_labelled' )
    context.write( 'automatically_labelled:', l )
    nomenclatureprop = 'default'
    if l and l == 'Yes':
        nomenclatureprop = 'label'
        #a.setGraphParams( label_attribute='label', use_nomenclature=1 )
    else:
        l = self.graph.get( 'manually_labelled' )
        context.write( 'manually_labelled:', l )
        if l and l == 'Yes':
            nomenclatureprop = 'name'
            #a.setGraphParams( label_attribute='name', use_nomenclature=1 )
    graph = a.loadObject( self.graph )
    context.write( 'nomenclature_property:', nomenclatureprop )
    a.execute( 'GraphDisplayProperties', objects=[graph],
      nomenclature_property=nomenclatureprop )
    selfdestroy.append( graph )
    if self.load_MRI == "Yes":
        if self.mri_corrected is not None:
            anat = a.loadObject( self.mri_corrected )
            selfdestroy.append( anat )
    if self.hemi_mesh is not None:
        mesh = a.loadObject( self.hemi_mesh, duplicate=True )
        selfdestroy.append( mesh )
        mesh.setMaterial( a.Material(diffuse = [0.8, 0.8, 0.8, 0.5]) )
    win3 = a.createWindow( '3D' )
    graphRef=graph.referential
    win3.assignReferential( graphRef )
    selfdestroy.append( win3 )
    win3.addObjects( [graph], add_graph_nodes=True )
    if self.hemi_mesh is not None:
        win3.addObjects( [mesh] )
        if self.two_windows == "Yes":
            win2 = a.createWindow( '3D' )
            win2.assignReferential( graphRef )
            selfdestroy.append( win2 )
            win2.addObjects( [graph] )
        else :
            win2 = win3
    else:
        win2 = win3
    if self.load_MRI == "Yes":
        if self.mri_corrected is not None:
            win2.addObjects( [anat] )
    #if self.nomenclature is not None:
        #wg= a.getDefaultWindowsGroup()
        ## to see the graph elements, we have to select them. After that they remain visible even if they are deselected
        #wg.setSelectionByNomenclature( hie, ["unknown", "brain"] )
        #wg.toggleSelectionByNomenclature(hie, ["unknown", "brain"])
    return selfdestroy

