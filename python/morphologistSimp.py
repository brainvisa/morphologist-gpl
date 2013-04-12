# -*- coding: utf-8 -*-

try:
    from traits.api import ListStr,HasTraits,File,Float,Instance
except ImportError:
    from enthought.traits.api import ListStr,HasTraits,File,Float,Instance

import soma.fom

class SimpMorpho(HasTraits):
    name = 'morphologist.SimplifiedMorphologist'
    
    def __init__(self):   
        HasTraits.__init__(self)  
        self.add_trait('t1mri',File(exists=True))
        #Commissure Coordinates
        self.add_trait('commissure_coordinates',File(exists=False))
          ##SPM Normalization
        self.add_trait('anatomical_template', File(exists=True))
        self.add_trait('job_file',File(exists=False))
        self.add_trait('transformations_information',File(exists=False))
        self.add_trait('normalized_t1mri',File(exists=False))
        self.add_trait('talairach_MNI_transform',File(exists=False))
        ###Talairach Transformation
        self.add_trait('source_referential',File(exists=True))
        self.add_trait('normalized_referential',File(exists=True))
        self.add_trait('tal_to_normalized_transform',File(exists=True))
        #Bias Correction
        self.add_trait('t1mri_nobias', File(exists=False))
        self.add_trait('hfiltered',File(exists=False))
        self.add_trait('white_ridges',File(exists=False))
        self.add_trait('variance',File(exists=False))
        self.add_trait('edges',File(exists=False))
        self.add_trait('field',File(exists=False))
        self.add_trait('meancurvature',File(exists=False))        
        #Histogram Analysis
        self.add_trait('histo_analysis',File(exists=False))
        #Brain Mask Segmentation
        self.add_trait('brain_mask',File(exists=False))
        #Split Brain Mask
        self.add_trait('split_brain',File(exists=False))
        self.add_trait('split_template',File(exists=True))
        #Talairach Transformation       
        self.add_trait('talairach_ACPC_transform',File(exists=False))
        #Grey/White Classification
        self.add_trait('left_grey_white',File(exists=False))
        self.add_trait('right_grey_white',File(exists=False))   
        #Grey/White Surface            
        self.add_trait('left_hemi_cortex',File(exists=False))   
        self.add_trait('left_white_mesh',File(exists=False) )        
        self.add_trait('right_hemi_cortex',File(exists=False))
        self.add_trait('right_white_mesh',File(exists=False))      
        #Spherical Hemispheres Surface      
        self.add_trait('left_hemi_mesh',File(exists=False))
        self.add_trait('right_hemi_mesh',File(exists=False))
        #Cortical Folds Graph
          ##Left
        self.add_trait('left_graph',File(exists=False))
        self.add_trait('left_skeleton',File(exists=False))
        self.add_trait('left_roots',File(exists=False))
        self.add_trait('left_sulci_voronoi',File(exists=False))
        self.add_trait('left_middle_cortex',File(exists=False))
          ##Right
        self.add_trait('right_graph',File(exists=False))
        self.add_trait('right_skeleton',File(exists=False))
        self.add_trait('right_roots',File(exists=False))
        self.add_trait('right_sulci_voronoi',File(exists=False))
        self.add_trait('right_middle_cortex',File(exists=False))
        #Sulci Recognition
        self.add_trait('labels_translation_map',File(exists=True))
          ##Left
        self.add_trait('left_labelled_graph',File(exists=False))          
        self.add_trait('left_posterior_probabilities',File(exists=False)) 
        self.add_trait('left_labels_priors',File(exists=True))
            ###Global 
        self.add_trait('left_global_model',File(exists=True))                      
        self.add_trait('left_tal_to_global_transform',File(exists=False))
        self.add_trait('left_t1_to_global_transform',File(exists=False))
            ###Local
        self.add_trait('left_local_model',File(exists=True))
        self.add_trait('left_local_referentials',File(exists=True))
        self.add_trait('left_direction_priors',File(exists=True))
        self.add_trait('left_angle_priors',File(exists=True))
        self.add_trait('left_translation_priors',File(exists=True))
        self.add_trait('left_global_to_local_transforms',File(exists=False))
          ##Right         
        self.add_trait('right_labelled_graph',File(exists=False))
        self.add_trait('right_posterior_probabilities',File(exists=False))                  
        self.add_trait('right_labels_priors',File(exists=True))
            ###Global             
        self.add_trait('right_global_model',File(exists=True))
        self.add_trait('right_tal_to_global_transform',File(exists=False))        
        self.add_trait('right_t1_to_global_transform',File(exists=False))    
            ###Local
        self.add_trait('right_local_model',File(exists=True))
        self.add_trait('right_local_referentials',File(exists=True))
        self.add_trait('right_direction_priors',File(exists=True))
        self.add_trait('right_angle_priors',File(exists=True))
        self.add_trait('right_translation_priors',File(exists=True))        
        self.add_trait('right_global_to_local_transforms',File(exists=False))       

        
    def _t1mri_changed( self ,name, old, new):

        completion=soma.fom.process_completion( 'morphologist-brainvisa-1.0', self.name, 't1mri', str(self.t1mri),directories={'spm' : '/here/is/spm','shared' : '/volatile/bouin/build/trunk/share/brainvisa-share-4.4' })  

        # Traits modifications
        for key in completion:
            setattr(self,key,completion[key])
            
