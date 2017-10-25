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
from brainvisa import anatomist

name = 'Anatomist Show Nucleus Graph'
roles = ('viewer',)
userLevel = 0

signature = Signature(
    'nucleus_graph', ReadDiskItem( 'Nucleus graph', 'Graph' ),
    'nucleus_nomenclature', ReadDiskItem( 'Nomenclature', 'Hierarchy' ),
    'load_MRI', Choice("Yes","No"),
    'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
        'Anatomist volume formats' ),
    'load_sulcus', Choice("Both","Left","Right","No"),
    'load_hemis', Choice("Yes","No"),
    'Lfold_graph', ReadDiskItem( 'Labelled Cortical folds graph',
        'Graph', requiredAttributes = {'side':'left',
                                       'labelled': 'Yes',
                                       'manually_labelled': 'Yes'} ),
    'Rfold_graph', ReadDiskItem( 'Labelled Cortical folds graph',
        'Graph', requiredAttributes = {'side':'right',
                                       'labelled': 'Yes',
                                       'manually_labelled': 'Yes'} ),
    'fold_nomenclature', ReadDiskItem( 'Nomenclature', 'Hierarchy' ),
    'Lhemi_mesh', ReadDiskItem( 'Left Hemisphere Mesh',
        'Anatomist mesh formats' ),
    'Rhemi_mesh', ReadDiskItem( 'Right Hemisphere Mesh',
        'Anatomist mesh formats' ),
    )

def validation():
    anatomist.validation()

def initialization( self ):
    def changehierarchy( self, proc ):
      if self.nucleus_graph is not None:
        return ReadDiskItem( 'Nomenclature', 'Hierarchy' ).findValue( self.nucleus_graph, requiredAttributes={ 'graph_type' : self.nucleus_graph.attributes()[ 'graph_type' ] }, debug=1 )
      else:
        return None
    self.setOptional( 'nucleus_nomenclature' )
    self.linkParameters( 'nucleus_nomenclature', 'nucleus_graph' ,changehierarchy)
    self.linkParameters( 'mri_corrected', 'nucleus_graph' )
    self.load_MRI = "No"
    self.setOptional( 'mri_corrected' )
    self.load_sulcus = "Left"
    self.setOptional( 'Lfold_graph' )
    self.setOptional( 'Rfold_graph' )
    self.linkParameters( 'Lfold_graph', 'nucleus_graph' )
    self.linkParameters( 'Rfold_graph', 'nucleus_graph' )
    self.setOptional( 'fold_nomenclature' )
    self.fold_nomenclature = self.signature[ 'fold_nomenclature' ].findValue( {} )
    self.load_hemis = "No"
    self.setOptional( 'Lhemi_mesh' )
    self.setOptional( 'Rhemi_mesh' )
    self.linkParameters( 'Lhemi_mesh', 'nucleus_graph' )
    self.linkParameters( 'Rhemi_mesh', 'nucleus_graph' )

def execution( self, context ):
    a = anatomist.Anatomist()
    selfdestroy = []
    br = None

    if self.nucleus_nomenclature is not None:
        ( hie, br ) = context.runProcess( 'AnatomistShowNomenclature',
                                          read=self.nucleus_nomenclature )
        selfdestroy += ( hie, br )

    nucleus_graph = a.loadObject( self.nucleus_graph )
    selfdestroy.append( nucleus_graph )
    win2 = a.createWindow( '3D' )
    win2.assignReferential( nucleus_graph.referential )
    selfdestroy.append( win2 )
    win2.addObjects( [nucleus_graph] )
        
    if self.load_MRI == "Yes":
        if self.mri_corrected is not None:
            anat = a.loadObject( self.mri_corrected )
            selfdestroy.append( anat )
            win2.addObjects( [anat] )

    if self.load_sulcus in ('Left','Right','Both'):
        if self.fold_nomenclature is not None:
            if self.nucleus_nomenclature is None:
                ( hie, br ) = \
                  context.runProcess( 'AnatomistShowNomenclature',
                                      read=self.fold_nomenclature )
                selfdestroy += ( hie, br )
            else:
                hie = a.loadObject( self.fold_nomenclature )
                br.addObjects( [hie] )
                selfdestroy.append( hie )
   
    if self.load_sulcus in ('Left','Both'):
        graph = a.loadObject( self.Lfold_graph )
        selfdestroy.append( graph )
        win2.addObjects( [graph] )
        if self.load_hemis == "Yes":
            if self.Lhemi_mesh is not None:
                mesh = a.loadObject( self.Lhemi_mesh )
                selfdestroy.append( mesh )
                win2.addObjects( [mesh] )
                mesh.setMaterial( a.Material(diffuse = [1, 0.6, 0.6, 0.6] ) )

    if self.load_sulcus in ('Right','Both'):
        graph = a.loadObject( self.Rfold_graph )
        selfdestroy.append( graph )
        win2.addObjects( [graph] )
        if self.load_hemis == "Yes":
            if self.Rhemi_mesh is not None:
                mesh = a.loadObject( self.Rhemi_mesh )
                selfdestroy.append( mesh )
                win2.addObjects( [mesh] )
                mesh.setMaterial( a.Material(diffuse = [1, 0.6, 0.6, 0.6] ) )

    return selfdestroy
