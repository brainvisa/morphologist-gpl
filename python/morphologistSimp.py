# -*- coding: utf-8 -*-
import os
try:
    from traits.api import ListStr,HasTraits,File,Float,Instance,Enum,Str,Bool
except ImportError:
    from enthought.traits.api import ListStr,HasTraits,File,Float,Instance,Enum,Str,Bool

from soma.pipeline.process import Process
from soma.controller import Controller,add_trait
import soma.fom
import subprocess
from soma.gui.viewer import *

       
class SimplifiedMorphologist(Process):
    """ Definition parameters of the process with traits and execution"""

    
    def __init__(self):  
        super(SimplifiedMorphologist, self).__init__() 
        HasTraits.__init__(self) 
  
    #Input/Output
        self.name_process = 'morphologistSimp.SimplifiedMorphologist'  
        #~ self.viewer_path = [ 'soma.gui.viewer' ]
	#add_trait(self,'t1mri',File(output=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))    
	
	add_trait(self,'t1mri',File(output=False))   
        self.set_viewer( 't1mri', 'soma.gui.pipeline.viewer.show_volume.ShowVolume')

        #Parameters
	add_trait(self,'perform_segmentation',Bool(True))
        add_trait(self,'method_ACPC',Enum('Manually','SPM Normalization'))       


        #Commissure Coordinates
        add_trait(self,'commissure_coordinates',File(output=True))
          ##SPM Normalization
        add_trait(self,'anatomical_template', File(output=False))
        add_trait(self,'job_file',File(output=True))
        add_trait(self,'transformations_information',File(output=True))
        add_trait(self,'normalized_t1mri',File(output=True))
        add_trait(self,'talairach_MNI_transform',File(output=True))
        add_trait(self,'source_referential',File(output=False))
        add_trait(self,'normalized_referential',File(output=False))
        add_trait(self,'tal_to_normalized_transform',File(output=False))
        #Bias Correction
        add_trait(self,'t1mri_nobias', File(output=True))
	self.set_viewer( 't1mri_nobias', 'soma.gui.pipeline.viewer.show_t1mri_nobias.ShowT1mriNobias',mri='t1mri',mask='t1mri_nobias')
        add_trait(self,'hfiltered',File(output=True))
        add_trait(self,'white_ridges',File(output=True,))
	#self.set_viewer( 'white_ridges', 'soma.gui.viewer.show_white_ridges.ShowWhiteRidges',t1mri=self.t1mri,palette="random",mode="linear_on_defined",rate=0.3,wintype="Axial")
        add_trait(self,'variance',File(output=True))
        add_trait(self,'edges',File(output=True))
        add_trait(self,'field',File(output=True))
        add_trait(self,'meancurvature',File(output=True)) 
	      
        #Histogram Analysis
        add_trait(self,'histo',File(output=True))
        add_trait(self,'histo_analysis',File(output=True))
	self.set_viewer('histo_analysis', 'soma.gui.pipeline.viewer.show_histo_analysis.ShowHistoAnalysis',histo='histo',histo_analysis='histo_analysis')
        #Brain Mask Segmentation
        add_trait(self,'brain_mask',File(output=True))
        #Split Brain Mask
        add_trait(self,'split_brain',File(output=True))
	self.set_viewer('split_brain', 'soma.gui.pipeline.viewer.show_label_image.ShowLabelImage',image='histo',mask='histo_analysis')
        add_trait(self,'split_template',File(output=False))
        #Talairach Transformation      
        add_trait(self,'talairach_ACPC_transform',File(output=True))
        #Grey/White Classification
        add_trait(self,'left_grey_white',File(output=True))
        add_trait(self,'right_grey_white',File(output=True))  
	
	add_trait(self,'perform_meshes_and_graphs',Bool(True))
        #Grey/White Surface           
        add_trait(self,'left_hemi_cortex',File(output=True))
        add_trait(self,'left_white_mesh',File(output=True))       
        add_trait(self,'right_hemi_cortex',File(output=True))
        add_trait(self,'right_white_mesh',File(output=True))     
        #Spherical Hemispheres Surface     
        add_trait(self,'left_pial_mesh',File(output=True))
        add_trait(self,'right_pial_mesh',File(output=True))
        #Cortical Folds Graph
          ##Left
        add_trait(self,'left_graph',File(output=True))
        add_trait(self,'left_skeleton',File(output=True))
        add_trait(self,'left_roots',File(output=True))
        add_trait(self,'left_sulci_voronoi',File(output=True))
        add_trait(self,'left_cortex_mid_interface',File(output=True))
          ##Right
        add_trait(self,'right_graph',File(output=True))
        add_trait(self,'right_skeleton',File(output=True))
        add_trait(self,'right_roots',File(output=True))
        add_trait(self,'right_sulci_voronoi',File(output=True))
        add_trait(self,'right_cortex_mid_interface',File(output=True))
        #Sulci Recognition
        add_trait(self,'labels_translation_map',File(output=False))
	
	add_trait(self,'perform_sulci_SPAM_recognition',Bool(False))
          ##Left
        add_trait(self,'left_labelled_graph',File(output=True))         
        add_trait(self,'left_posterior_probabilities',File(output=True))
        add_trait(self,'left_labels_priors',File(output=False))
            ###Global
            #show descriptive model
        add_trait(self,'left_global_model',File(output=False))                     
        add_trait(self,'left_tal_to_global_transform',File(output=True))
        add_trait(self,'left_t1_to_global_transform',File(output=True))
            ###Local
            #show descriptive model
        add_trait(self,'left_local_model',File(output=False))
        add_trait(self,'left_local_referentials',File(output=False))
        add_trait(self,'left_direction_priors',File(output=False))
        add_trait(self,'left_angle_priors',File(output=False))
        add_trait(self,'left_translation_priors',File(output=False))
        add_trait(self,'left_global_to_local_transforms',File(output=True))
          ##Right        
        add_trait(self,'right_labelled_graph',File(output=True))
        add_trait(self,'right_posterior_probabilities',File(output=True))                 
        add_trait(self,'right_labels_priors',File(output=False))
            ###Global            
        add_trait(self,'right_global_model',File(output=False))
        add_trait(self,'right_tal_to_global_transform',File(output=True))       
        add_trait(self,'right_t1_to_global_transform',File(output=True))   
            ###Local
        add_trait(self,'right_local_model',File(output=False))
        add_trait(self,'right_local_referentials',File(output=False))
        add_trait(self,'right_direction_priors',File(output=False))
        add_trait(self,'right_angle_priors',File(output=False))
        add_trait(self,'right_translation_priors',File(output=False))       
        add_trait(self,'right_global_to_local_transforms',File(output=True))  
       
       
###THIS IS OLD VERSION JUSTE TO KEEP VIEWER IN MEMORY
       
          ##Talairach Transformation
        #add_trait(self,'source_referential',File(exists=True,viewer='soma.gui.viewer.show_text'))
        #add_trait(self,'normalized_referential',File(exists=True))
        #add_trait(self,'tal_to_normalized_transform',File(exists=True))
        ##Bias Correction
        #add_trait(self,'t1mri_nobias', File(exists=False,viewer='soma.gui.viewer.show_t1mri_nobias'))
        #add_trait(self,'hfiltered',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        #add_trait(self,'white_ridges',File(exists=False,viewer='soma.gui.viewer.show_white_ridge'))
        #add_trait(self,'variance',File(exists=False,viewer='soma.gui.viewer.show_rainbow_volume'))
        #add_trait(self,'edges',File(exists=False,viewer='soma.gui.viewer.show_rainbow_volume'))
        #add_trait(self,'field',File(exists=False))
        #add_trait(self,'meancurvature',File(exists=False))       
        ##Histogram Analysis
        #add_trait(self,'histo',File(exists=False))
        #add_trait(self,'histo_analysis',File(exists=False,viewer='soma.gui.viewer.show_histo'))
        ##Brain Mask Segmentation
        #add_trait(self,'brain_mask',File(exists=False,viewer='soma.gui.viewer.show_brain_mask'))
        ##Split Brain Mask
        #add_trait(self,'split_brain',File(exists=False,viewer='soma.gui.viewer.show_split_brain'))
        #add_trait(self,'split_template',File(exists=True,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        ##Talairach Transformation      
        #add_trait(self,'talairach_ACPC_transform',File(exists=False,viewer='soma.gui.viewer.show_text'))
        ##Grey/White Classification
        #add_trait(self,'left_grey_white',File(exists=False,viewer='soma.gui.viewer.show_grey_white'))
        #add_trait(self,'right_grey_white',File(exists=False,viewer='soma.gui.viewer.show_grey_white'))  
        ##Grey/White Surface           
        #add_trait(self,'left_hemi_cortex',File(exists=False,viewer='soma.gui.viewer.show_grey_white'))  
        #add_trait(self,'left_white_mesh',File(exists=False,viewer='soma.gui.viewer.show_white_matter'))       
        #add_trait(self,'right_hemi_cortex',File(exists=False,viewer='soma.gui.viewer.show_grey_white'))
        #add_trait(self,'right_white_mesh',File(exists=False,viewer='soma.gui.viewer.show_white_matter'))     
        ##Spherical Hemispheres Surface     
        #add_trait(self,'left_hemi_mesh',File(exists=False,viewer='soma.gui.viewer.show_hemi'))
        #add_trait(self,'right_hemi_mesh',File(exists=False,viewer='soma.gui.viewer.show_hemi'))
        ##Cortical Folds Graph
          ###Left
        #add_trait(self,'left_graph',File(exists=False,viewer='soma.gui.viewer.show_fold_graph'))
        #add_trait(self,'left_skeleton',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        #add_trait(self,'left_roots',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        #add_trait(self,'left_sulci_voronoi',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        #add_trait(self,'left_middle_cortex',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
          ###Right
        #add_trait(self,'right_graph',File(exists=False))
        #add_trait(self,'right_skeleton',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        #add_trait(self,'right_roots',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        #add_trait(self,'right_sulci_voronoi',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        #add_trait(self,'right_middle_cortex',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        ##Sulci Recognition
        #add_trait(self,'labels_translation_map',File(exists=True,viewer='soma.gui.viewer.show_text'))
          ###Left
        #add_trait(self,'left_labelled_graph',File(exists=False,viewer='soma.gui.viewer.show_fold_graph'))         
        #add_trait(self,'left_posterior_probabilities',File(exists=False,viewer='soma.gui.viewer.show_text'))
        #add_trait(self,'left_labels_priors',File(exists=True))
            ####Global
            ##show descriptive model
        #add_trait(self,'left_global_model',File(exists=True))                     
        #add_trait(self,'left_tal_to_global_transform',File(exists=False,viewer='soma.gui.viewer.show_text'))
        #add_trait(self,'left_t1_to_global_transform',File(exists=False,viewer='soma.gui.viewer.show_text'))
            ####Local
            ##show descriptive model
        #add_trait(self,'left_local_model',File(exists=True))
        #add_trait(self,'left_local_referentials',File(exists=True))
        #add_trait(self,'left_direction_priors',File(exists=True))
        #add_trait(self,'left_angle_priors',File(exists=True))
        #add_trait(self,'left_translation_priors',File(exists=True))
        #add_trait(self,'left_global_to_local_transforms',File(exists=False))
          ###Right        
        #add_trait(self,'right_labelled_graph',File(exists=False,viewer='soma.gui.viewer.show_fold_graph'))
        #add_trait(self,'right_posterior_probabilities',File(exists=False))                 
        #add_trait(self,'right_labels_priors',File(exists=True))
            ####Global            
        #add_trait(self,'right_global_model',File(exists=True))
        #add_trait(self,'right_tal_to_global_transform',File(exists=False))       
        #add_trait(self,'right_t1_to_global_transform',File(exists=False))   
            ####Local
        #add_trait(self,'right_local_model',File(exists=True))
        #add_trait(self,'right_local_referentials',File(exists=True))
        #add_trait(self,'right_direction_priors',File(exists=True))
        #add_trait(self,'right_angle_priors',File(exists=True))
        #add_trait(self,'right_translation_priors',File(exists=True))       
        #add_trait(self,'right_global_to_local_transforms',File(exists=False))  
        #add_trait(self,'nomenclature',File(exists=True))    
    
    def command( self ):
        """ Function to execute the process"""     
        list_params=[name+'='+str(getattr(self,name)) for name, trait in self.user_traits().iteritems()]
        args= ['python', '-m', 'brainvisa.axon.runprocess','morphologistProcess']      
        str_args=[str(x) for x in args]
        str_args=str_args+list_params
        return str_args
	
   
    def __call__( self ):
        """ Function to call the execution """
        subprocess.check_call( self.command() )
