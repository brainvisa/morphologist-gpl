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

include( 'base' )
import registration
include( 'registration' )

mesh_content = (
    "<subject>_brain", SetType( 'Brain Mesh' ), SetWeakAttr( 'side', 'both' ),
    "<subject>_Lhemi", SetType( 'Left Hemisphere Mesh' ), SetWeakAttr( 'side', 'left' ), SetPriorityOffset( +1 ),
    "<subject>_Rhemi", SetType( 'Right Hemisphere Mesh' ), SetWeakAttr( 'side', 'right' ), SetPriorityOffset( +1 ),
    "<subject>_Lwhite", SetType( 'Left Hemisphere White Mesh' ), SetWeakAttr( 'side', 'left' ), SetPriorityOffset( +1 ),
    "<subject>_Rwhite", SetType( 'Right Hemisphere White Mesh' ), SetWeakAttr( 'side', 'right' ), SetPriorityOffset( +1 ),
    "<subject>_Lwhite_inflated", SetType( 'Inflated Hemisphere White Mesh' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rwhite_inflated", SetType( 'Inflated Hemisphere White Mesh' ), SetWeakAttr( 'side', 'right' ),
    "<subject>_head", SetType( 'Head Mesh' ), SetWeakAttr( 'side', 'both' ), 
    "<subject>_Lmedian", SetType( 'Median Mesh' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rmedian", SetType( 'Median Mesh' ), SetWeakAttr( 'side', 'right' ), "<subject>_Lconformal", SetType( 'Conformal White Mesh' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rconformal", SetType( 'Conformal White Mesh' ), SetWeakAttr( 'side', 'right' ),
    "cortex_<subject>_mni", SetType( 'MNI Cortex Mesh' ), SetWeakAttr( 'side', 'both' ), ## utilise en lecture seulement
    "*", SetType( 'Mesh'),
)

segmentation_content = (
    "brain_<subject>", SetType( 'T1 Brain Mask' ), SetWeakAttr( 'side', 'both' ),
    "Rgrey_white_<subject>", SetType( 'Right Grey White Mask' ), SetWeakAttr( 'side', 'right' ),
    "Lgrey_white_<subject>", SetType( 'Left Grey White Mask' ), SetWeakAttr( 'side', 'left' ),
    "cortex_<subject>", SetType( 'Both CSF+GREY Mask' ), SetWeakAttr( 'side', 'both' ),
    "Lcortex_<subject>", SetType( 'Left CSF+GREY Mask' ), SetWeakAttr( 'side', 'left' ),
    "Rcortex_<subject>", SetType( 'Right CSF+GREY Mask' ), SetWeakAttr( 'side', 'right' ),
    "csf_<subject>", SetType( 'Both CSF Mask' ), SetWeakAttr( 'side', 'both' ),
    "Lcsf_<subject>", SetType( 'Left CSF Mask' ), SetWeakAttr( 'side', 'left' ),
    "Rcsf_<subject>", SetType( 'Right CSF Mask' ), SetWeakAttr( 'side', 'right' ),
    "Lskeleton_<subject>", SetType( 'Left Cortex Skeleton' ), SetWeakAttr( 'side', 'left' ),
    "Rskeleton_<subject>", SetType( 'Right Cortex Skeleton' ), SetWeakAttr( 'side', 'right' ),
    "Lroots_<subject>", SetType( 'Left Cortex Catchment Bassins' ), SetWeakAttr( 'side', 'left' ),
    "Rroots_<subject>", SetType( 'Right Cortex Catchment Bassins' ), SetWeakAttr( 'side', 'right' ),
    "voronoi_<subject>", SetType( 'Voronoi Diagram' ), SetWeakAttr( 'side', 'both' ),  
    "head_<subject>", SetType( "Head Mask" ),
    "<subject>_Lwhite_curv", SetType( 'White Curvature Texture' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rwhite_curv", SetType( 'White Curvature Texture' ), SetWeakAttr( 'side', 'right' ),
    "<subject>_Lwhite_depth", SetType( 'White Depth Texture' ), SetWeakAttr( 'side', 'left' ),
    "<subject>_Rwhite_depth", SetType( 'White Depth Texture' ), SetWeakAttr( 'side', 'right' ),
    "Lgw_interface_<subject>", SetType( 'Grey White Mid-Interface Volume' ),
    SetWeakAttr( 'side', 'left' ),
    "Rgw_interface_<subject>", SetType( 'Grey White Mid-Interface Volume' ),
    SetWeakAttr( 'side', 'right' ),

    'mesh',
    apply( SetContent, mesh_content),
)

t1mri_content = (
  "{acquisition}", SetDefaultAttributeValue( 'acquisition', default_acquisition ), SetNonMandatoryKeyAttribute( 'acquisition' ),
  SetContent(
      # t1mri before processing in acquisition level
      "<subject>", SetType( 'Raw T1 MRI' ), SetPriorityOffset( +1 ), SetWeakAttr("normalized", "no"), 
      "<subject>", SetType('Commissure coordinates'),
      "normalized_{normalization}_<subject>", SetType( 'Raw T1 MRI' ), SetWeakAttr("normalized", "yes"),
      "<subject>_sn", SetType("SPM2 normalization matrix"),
      "<subject>_fsl", SetType("FSL Transformation"),
      #      "r<subject>", SetType( 'Registered Raw T1 MRI with fMRI' ), SetWeakAttr( 'fMRI_register', 'Yes' ),
      #    "wr<subject>", SetType( 'Registered Raw T1 MRI with fMRI' ), SetWeakAttr( 'fMRI_register', 'Yes' ),
      'registration', SetContent(
        'RawT1-<subject>_<acquisition>_TO_unknown_atlas_WITH_bal', SetType("baladin Transformation"),
        'RawT1-<subject>_<acquisition>', SetType( 'Referential of Raw T1 MRI' ),
        'RawT1-<subject>_<acquisition>_TO_Talairach-ACPC', SetType( 'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist' ),
        'RawT1-<subject>_<acquisition>_TO_Talairach-MNI', SetType( 'Transform Raw T1 MRI to Talairach-MNI template-SPM'), SetWeakAttr('destination_referential', str(registration.talairachMNIReferentialId)),
      ),
      "{analysis}", SetDefaultAttributeValue( 'analysis', default_analysis ), SetNonMandatoryKeyAttribute( 'analysis' ),
        SetContent( # processing results in analysis
          "nobias_<subject>", SetType( 'T1 MRI Bias Corrected' ),
#          "basis_fornobias_<subject>", SetType( 'T1 MRI Basis for Bias Computation' ),
          "biasfield_<subject>", SetType( 'T1 MRI Bias Field' ),
          "whiteridge_<subject>", SetType( 'T1 MRI White Matter Ridges' ),
          "variance_<subject>", SetType( 'T1 MRI Variance' ),
          "edges_<subject>", SetType( 'T1 MRI Edges' ),
          "mean_curvature_<subject>", SetType( 'T1 MRI Mean Curvature' ),
          "hfiltered_<subject>", SetType( 'T1 MRI Filtered For Histo' ),
          "nobias_<subject>", SetType( 'Histo Analysis' ),
                    
          'segmentation', 
          apply( SetContent, segmentation_content), 
  
         'folds', SetContent( # sulci, gyri
            "{graph_version}", SetDefaultAttributeValue( 'graph_version', default_graph_version ), SetContent(
            "L<subject>", SetType( 'Left Cortical folds graph' ), SetWeakAttr( 'side', 'left', 'labelled', 'No', 'manually_labelled', 'No', 'automatically_labelled', 'No',  ),
            "R<subject>", SetType( 'Right Cortical folds graph' ), SetWeakAttr( 'side', 'right',  'labelled', 'No' ),
            )
         ),

         ## existe-t-il un rapport avec nuclear imaging? nuclei doit il etre dans t1mri ? :
         'nuclei', #SetWeakAttr( 'category', 'nuclei' ), #SetWeakAttr( 'category', 'deepnuclei' ), 
          SetContent(
            ## ces types ne sont utilises dans aucun process
            #  '<subject>_deep_nuclei_mask', SetType( 'Deep Nuclei Mask' ),
            #  '<subject>_deep_nuclei_graph', SetType( 'Deep Nuclei Graph' ),
            ## type Nucleus graph utilie par un process AnatomistShowNucleusGraph (viewer), entree, pas de writer
            "<subject>_deep_nuclei",SetType( 'Deep Nuclei Graph' ),SetWeakAttr( 'graph_type', 'NucleusArg') 
            #"<subject>-nucleus",SetType( 'Nucleus graph' ),SetWeakAttr( 'graph_type', 'NucleusArg') # -> Deep Nuclei Graph
          ),

        'ROI', SetContent(), 
      )# analysis
    )#acquisition
)#t1mri

insert( '{protocol}/{subject}',
  't1mri', SetWeakAttr( 'modality', 't1mri' ), 
    apply( SetContent, t1mri_content) 
)

#----------------- Registration -------------------------

#insertFirst( '{protocol}/{subject}/registration',
  #'RawT1-<subject>-{acquisition}', SetType( 'Referential of Raw T1 MRI' ),
  #'RawT1-<subject>_{acquisition}_TO_Talairach-ACPC', SetType( 'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist' ),
#)

#insertFirst( '{protocol}/registration',
  ### idem que pour subject/registration
  #'RawT1-{source.subject}-{source.acquisition}_TO_RawT1-{dest.subject}-{dest.acquisition}', SetType( 'Transform Raw T1 MRI to Raw T1 MRI' ),
#)
