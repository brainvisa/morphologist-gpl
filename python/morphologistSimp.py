# -*- coding: utf-8 -*-
import os
try:
    from traits.api import ListStr,HasTraits,File,Float,Instance,Enum
except ImportError:
    from enthought.traits.api import ListStr,HasTraits,File,Float,Instance,Enum

from soma.controller import Controller,add_trait
import soma.fom
import subprocess



class SimpMorpho(Controller):
    """ Definition parameters of the process with traits and execution"""

    name = 'morphologistSimp.SimplifiedMorphologist'   
    def __init__(self):   
        HasTraits.__init__(self)        
    #Input/Output

        add_trait(self,'t1mri',File(exists=True,viewer='soma.gui.viewer.show_volume'))      
        #Parameters
        add_trait(self,'method_ACPC',Enum('Manually','SPM Normalization'))        
        #Commissure Coordinates
        add_trait(self,'commissure_coordinates',File(exists=False))
          ##SPM Normalization
        add_trait(self,'anatomical_template', File(exists=True, viewer='soma.gui.viewer.show_volume' ))
        add_trait(self,'job_file',File(exists=False))
        add_trait(self,'transformations_information',File(exists=False))
        add_trait(self,'normalized_t1mri',File(exists=False))
        add_trait(self,'talairach_MNI_transform',File(exists=False))
        ###Talairach Transformation
        add_trait(self,'source_referential',File(exists=True,viewer='soma.gui.viewer.show_text'))
        add_trait(self,'normalized_referential',File(exists=True))
        add_trait(self,'tal_to_normalized_transform',File(exists=True))
        #Bias Correction
        add_trait(self,'t1mri_nobias', File(exists=False,viewer='soma.gui.viewer.show_t1mri_nobias'))
        add_trait(self,'hfiltered',File(exists=False,viewer='soma.gui.viewer.show_volume'))
        add_trait(self,'white_ridges',File(exists=False,viewer='soma.gui.viewer.show_white_ridge'))
        add_trait(self,'variance',File(exists=False,viewer='soma.gui.viewer.show_rainbow_volume'))
        add_trait(self,'edges',File(exists=False,viewer='soma.gui.viewer.show_rainbow_volume'))
        add_trait(self,'field',File(exists=False))
        add_trait(self,'meancurvature',File(exists=False))        
        #Histogram Analysis
        add_trait(self,'histo',File(exists=False))
        add_trait(self,'histo_analysis',File(exists=False,viewer='soma.gui.viewer.show_histo'))
        #Brain Mask Segmentation
        add_trait(self,'brain_mask',File(exists=False,viewer='soma.gui.viewer.show_brain_mask'))
        #Split Brain Mask
        add_trait(self,'split_brain',File(exists=False,viewer='soma.gui.viewer.show_split_brain'))
        add_trait(self,'split_template',File(exists=True,viewer='soma.gui.viewer.show_volume'))
        #Talairach Transformation       
        add_trait(self,'talairach_ACPC_transform',File(exists=False,viewer='soma.gui.viewer.show_text'))
        #Grey/White Classification
        add_trait(self,'left_grey_white',File(exists=False,viewer='soma.gui.viewer.show_grey_white'))
        add_trait(self,'right_grey_white',File(exists=False,viewer='soma.gui.viewer.show_grey_white'))   
        #Grey/White Surface            
        add_trait(self,'left_hemi_cortex',File(exists=False,viewer='soma.gui.viewer.show_grey_white'))   
        add_trait(self,'left_white_mesh',File(exists=False,viewer='soma.gui.viewer.show_white_matter'))        
        add_trait(self,'right_hemi_cortex',File(exists=False,viewer='soma.gui.viewer.show_grey_white'))
        add_trait(self,'right_white_mesh',File(exists=False,viewer='soma.gui.viewer.show_white_matter'))      
        #Spherical Hemispheres Surface      
        add_trait(self,'left_hemi_mesh',File(exists=False,viewer='soma.gui.viewer.show_hemi'))
        add_trait(self,'right_hemi_mesh',File(exists=False,viewer='soma.gui.viewer.show_hemi'))
        #Cortical Folds Graph
          ##Left
        add_trait(self,'left_graph',File(exists=False,viewer='soma.gui.viewer.show_fold_graph'))
        add_trait(self,'left_skeleton',File(exists=False,viewer='soma.gui.viewer.show_volume'))
        add_trait(self,'left_roots',File(exists=False,viewer='soma.gui.viewer.show_volume'))
        add_trait(self,'left_sulci_voronoi',File(exists=False,viewer='soma.gui.viewer.show_volume'))
        add_trait(self,'left_middle_cortex',File(exists=False,viewer='soma.gui.viewer.show_volume'))
          ##Right
        add_trait(self,'right_graph',File(exists=False))
        add_trait(self,'right_skeleton',File(exists=False,viewer='soma.gui.viewer.show_volume'))
        add_trait(self,'right_roots',File(exists=False,viewer='soma.gui.viewer.show_volume'))
        add_trait(self,'right_sulci_voronoi',File(exists=False,viewer='soma.gui.viewer.show_volume'))
        add_trait(self,'right_middle_cortex',File(exists=False,viewer='soma.gui.viewer.show_volume'))
        #Sulci Recognition
        add_trait(self,'labels_translation_map',File(exists=True,viewer='soma.gui.viewer.show_text'))
          ##Left
        add_trait(self,'left_labelled_graph',File(exists=False,viewer='soma.gui.viewer.show_fold_graph'))          
        add_trait(self,'left_posterior_probabilities',File(exists=False,viewer='soma.gui.viewer.show_text')) 
        add_trait(self,'left_labels_priors',File(exists=True))
            ###Global 
            #show descriptive model
        add_trait(self,'left_global_model',File(exists=True))                      
        add_trait(self,'left_tal_to_global_transform',File(exists=False,viewer='soma.gui.viewer.show_text'))
        add_trait(self,'left_t1_to_global_transform',File(exists=False,viewer='soma.gui.viewer.show_text'))
            ###Local
            #show descriptive model
        add_trait(self,'left_local_model',File(exists=True))
        add_trait(self,'left_local_referentials',File(exists=True))
        add_trait(self,'left_direction_priors',File(exists=True))
        add_trait(self,'left_angle_priors',File(exists=True))
        add_trait(self,'left_translation_priors',File(exists=True))
        add_trait(self,'left_global_to_local_transforms',File(exists=False))
          ##Right         
        add_trait(self,'right_labelled_graph',File(exists=False,viewer='soma.gui.viewer.show_fold_graph'))
        add_trait(self,'right_posterior_probabilities',File(exists=False))                  
        add_trait(self,'right_labels_priors',File(exists=True))
            ###Global             
        add_trait(self,'right_global_model',File(exists=True))
        add_trait(self,'right_tal_to_global_transform',File(exists=False))        
        add_trait(self,'right_t1_to_global_transform',File(exists=False))    
            ###Local
        add_trait(self,'right_local_model',File(exists=True))
        add_trait(self,'right_local_referentials',File(exists=True))
        add_trait(self,'right_direction_priors',File(exists=True))
        add_trait(self,'right_angle_priors',File(exists=True))
        add_trait(self,'right_translation_priors',File(exists=True))        
        add_trait(self,'right_global_to_local_transforms',File(exists=False))   
        #add_trait(self,'nomenclature',File(exists=True))     
        
        
    def _t1mri_changed(self,name, old, new):
        """ Function call when t1mri paramater has changed, do the 
        completion of the others parameters then change their values
        
        Parameters
        name : name of the trait
        old: old value of the trait
        new: new value of the trait
        """
        completion=soma.fom.process_completion( 'morphologist-brainvisa-1.0', self.name, 't1mri', str(self.t1mri),directories={'spm' : '/here/is/spm','shared' : os.environ[ 'BRAINVISA_SHARE' ] + '/brainvisa-share-4.4' })         
        # Traits modifications
        for key in completion:
            self.trait(key).attributs=completion[key][1] 
            setattr(self,key,completion[key][0])             
 
         
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
