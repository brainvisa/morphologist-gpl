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

include( 'base' )

insert( '.', 
  "nobias_<filename>", SetType( 'T1 MRI Bias Corrected' ),
  "mri_ext_<filename>", SetType( 'MRI Ext Edge Image' ),
  "nobias_<filename>", SetType( 'Histo Analysis' ),
  "<filename>", SetType('Commissure coordinates'),
  "LBottom_<filename>", SetType( 'Bottom Volume' ), SetWeakAttr( 'side', 'left' ),
  "RBottom_<filename>", SetType( 'Bottom Volume' ), SetWeakAttr( 'side', 'right' ),  
  "LHullJunction_<filename>", SetType( 'Hull Junction Volume' ), SetWeakAttr( 'side', 'left' ),
  "RHullJunction_<filename>", SetType( 'Hull Junction Volume' ), SetWeakAttr( 'side', 'right' ),
  "LSimpleSurface_<filename>", SetType( 'Simple Surface Volume' ), SetWeakAttr('side', 'left' ),
  "RSimpleSurface_<filename>", SetType( 'Simple Surface Volume' ), SetWeakAttr('side', 'right' ),
  "Lmoment_<filename>", SetType( 'Moment Vector' ), SetWeakAttr( 'side', 'left' ),
  "Rmoment_<filename>", SetType( 'Moment Vector' ), SetWeakAttr( 'side', 'right' ),
  "brain_<filename>", SetType( 'Brain Mask' ), SetWeakAttr( 'side', 'both' ),
  "Rgrey_white_<filename>", SetType( 'Right Grey White Mask' ), SetWeakAttr( 'side', 'both' ),
  "Lgrey_white_<filename>", SetType( 'Left Grey White Mask' ), SetWeakAttr( 'side', 'both' ),
  "cortex_<filename>", SetType( 'Both CSF+GREY Mask' ), SetWeakAttr( 'side', 'both' ),
  "Lcortex_<filename>", SetType( 'Left CSF+GREY Mask' ), SetWeakAttr( 'side', 'left' ),
  "Rcortex_<filename>", SetType( 'Right CSF+GREY Mask' ), SetWeakAttr( 'side', 'right' ),
  "Lskeleton_<filename>", SetType( 'Left Cortex Skeleton' ), SetWeakAttr( 'side', 'left' ),
  "Rskeleton_<filename>", SetType( 'Right Cortex Skeleton' ), SetWeakAttr( 'side', 'right' ),
  "Lroots_<filename>", SetType( 'Left Cortex Catchment Bassins' ), SetWeakAttr( 'side', 'left' ),
  "Rroots_<filename>", SetType( 'Right Cortex Catchment Bassins' ), SetWeakAttr( 'side', 'right' ),
  "voronoi_<filename>", SetType( 'Split Brain Mask' ), SetWeakAttr( 'side', 'both' ),
  "<filename>_Lwhite_curv", SetType( 'White Curvature Texture' ), SetWeakAttr( 'side', 'left' ),
  "<filename>_Rwhite_curv", SetType( 'White Curvature Texture' ), SetWeakAttr( 'side', 'right' ),
  "<filename>_Lwhite_sulci", SetType( 'Sulci White Texture' ), SetWeakAttr( 'side', 'left' ),
  "<filename>_Rwhite_sulci", SetType( 'Sulci White Texture' ), SetWeakAttr( 'side', 'right' ),
  "<filename>_Lwhite_gyri", SetType( 'Gyri White Texture' ), SetWeakAttr( 'side', 'left' ),
  "<filename>_Rwhite_gyri", SetType( 'Gyri White Texture' ), SetWeakAttr( 'side', 'right' ),
  "<filename>_Lwhite_gyri", SetType( 'Gyri White Volume' ), SetWeakAttr( 'side', 'left' ),
  "<filename>_Rwhite_gyri", SetType( 'Gyri White Volume' ), SetWeakAttr( 'side', 'right' ),

  "<filename>_brain", SetType( 'Brain Mesh' ), SetWeakAttr( 'side', 'both' ),
  "<filename>_Lhemi", SetType( 'Left Hemisphere Mesh' ), SetWeakAttr( 'side', 'left' ),
  "<filename>_Rhemi", SetType( 'Right Hemisphere Mesh' ), SetWeakAttr( 'side', 'right' ),
  "<filename>_Lwhite", SetType( 'Left Hemisphere White Mesh' ), SetWeakAttr( 'side', 'left' ),SetPriorityOffset(5),
  "<filename>_Rwhite", SetType( 'Right Hemisphere White Mesh' ), SetWeakAttr( 'side', 'right' ),SetPriorityOffset(5),
  "<filename>_Lwhite_inflated", SetType( 'Inflated Hemisphere White Mesh' ), SetWeakAttr( 'side', 'left' ),
  "<filename>_Rwhite_inflated", SetType( 'Inflated Hemisphere White Mesh' ), SetWeakAttr( 'side', 'right' ),
  "<filename>_Lwhite_fine", SetType( 'Left Fine Hemisphere White Mesh' ), SetWeakAttr( 'side', 'left' ),
  "<filename>_Rwhite_fine", SetType( 'Right Fine Hemisphere White Mesh' ), SetWeakAttr( 'side', 'right' ),
  "<filename>_head", SetType( 'Head Mesh' ), SetWeakAttr( 'side', 'both' ),
  "cortex_<filename>_mni", SetType( 'MNI Cortex Mesh' ), SetWeakAttr( 'side', 'both' ),
  "FCMunflip_<filename>",SetType( 'Roi Graph' ), SetWeakAttr( 'side', 'both' ),
  "Pons_<filename>",SetType( 'Roi Graph' ),SetWeakAttr( 'side', 'both' ),
  "<filename>-nucleus",SetType( 'Nucleus graph' ),SetWeakAttr( 'graph_type', 'NucleusArg'),
  "L<filename>", SetType( 'Cortical folds graph' ), SetWeakAttr( 'side', 'left', 'labelled', 'No' ),
  "L<filename>Base", SetType( 'Labelled Cortical folds graph' ), SetWeakAttr( 'side', 'left', 'labelled', 'Yes', 'manually_labelled', 'Yes', 'automatically_labelled', 'No' ),
  "L<filename>Auto", SetType( 'Labelled Cortical folds graph' ), SetWeakAttr( 'side', 'left', 'labelled', 'Yes', 'manually_labelled', 'No', 'automatically_labelled', 'Yes' ),
  "R<filename>", SetType( 'Cortical folds graph' ), SetWeakAttr( 'side', 'right',  'labelled', 'No' ),
  "R<filename>Base", SetType( 'Labelled Cortical folds graph' ), SetWeakAttr( 'side', 'right', 'labelled', 'Yes', 'manually_labelled', 'Yes', 'automatically_labelled', 'No' ),
  "R<filename>Auto", SetType( 'Labelled Cortical folds graph' ), SetWeakAttr( 'side', 'right', 'labelled', 'Yes', 'manually_labelled', 'No', 'automatically_labelled', 'Yes' ),
)
