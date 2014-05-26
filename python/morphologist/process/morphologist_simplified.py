# -*- coding: utf-8 -*-
import os
try:
    from traits.api import ListStr,HasTraits,File,Float,Instance,Enum,Str,Bool
except ImportError:
    from enthought.traits.api import ListStr,HasTraits,File,Float,Instance,Enum,Str,Bool

from capsul.process import Process
import soma.fom
import subprocess
#from soma.gui.pipeline.viewer import *


class SimplifiedMorphologist(Process):
    """ Definition parameters of the process with traits and execution"""

    
    def __init__(self):
        super(SimplifiedMorphologist, self).__init__() 
        HasTraits.__init__(self) 
  
        #Input/Output
        #~ self.viewer_path = [ 'soma.gui.viewer' ]
        #add_trait('t1mri',File(output=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))

        self.add_trait('t1mri',File(output=False))
        self.set_viewer( 't1mri', 'soma.gui.pipeline.viewer.show_volume.ShowVolume')

        #Parameters
        self.add_trait('perform_segmentation',Bool(True))
        self.add_trait('method_ACPC',Enum('Manually','SPM Normalization'))


        #Commissure Coordinates
        self.add_trait('commissure_coordinates',File(output=True))
          ##SPM Normalization
        self.add_trait('anatomical_template', File(output=False,hidden=True))
        self.add_trait('job_file',File(output=True,hidden=True))
        self.add_trait('transformations_information',File(output=True,hidden=True))
        self.add_trait('normalized_t1mri',File(output=True,hidden=True))
        self.add_trait('talairach_MNI_transform',File(output=True,hidden=True))
        self.add_trait('source_referential',File(output=False,hidden=True))
        self.add_trait('normalized_referential',File(output=False,hidden=True))
        self.add_trait('tal_to_normalized_transform',File(output=False,hidden=True))
        #Bias Correction
        self.add_trait('t1mri_nobias', File(output=True))
        self.set_viewer( 't1mri_nobias', 'soma.gui.pipeline.viewer.show_t1mri_nobias.ShowT1mriNobias',mri='t1mri',mask='t1mri_nobias')
        self.add_trait('hfiltered',File(output=True,hidden=True))
        self.add_trait('white_ridges',File(output=True,hidden=True))
        #self.set_viewer( 'white_ridges', 'soma.gui.viewer.show_white_ridges.ShowWhiteRidges',t1mri=self.t1mri,palette="random",mode="linear_on_defined",rate=0.3,wintype="Axial")
        self.add_trait('variance',File(output=True,hidden=True))
        self.add_trait('edges',File(output=True,hidden=True))
        self.add_trait('field',File(output=True,hidden=True))
        self.add_trait('meancurvature',File(output=True,hidden=True))

        #Histogram Analysis
        self.add_trait('histo',File(output=True,hidden=True))
        self.add_trait('histo_analysis',File(output=True))
        self.set_viewer('histo_analysis', 'soma.gui.pipeline.viewer.show_histo.ShowHisto',histo='histo',histo_analysis='histo_analysis')
        #Brain Mask Segmentation
        self.add_trait('brain_mask',File(output=True))
        self.set_viewer('brain_mask', 'soma.gui.pipeline.viewer.show_brain_mask.ShowBrainMask',mri_corrected='t1mri_nobias',mask='brain_mask')
        #Split Brain Mask
        self.add_trait('split_brain',File(output=True))
        self.set_viewer('split_brain', 'soma.gui.pipeline.viewer.show_label_image.ShowLabelImage',image='t1mri_nobias',mask='split_brain')
        self.add_trait('split_template',File(output=False,hidden=True))
        #Talairach Transformation      
        self.add_trait('talairach_ACPC_transform',File(output=True,hidden=True))
        #Grey/White Classification
        self.add_trait('left_grey_white',File(output=True))
        self.set_viewer('left_grey_white', 'soma.gui.pipeline.viewer.show_label_image.ShowLabelImage',image='t1mri_nobias',mask='left_grey_white')
        self.add_trait('right_grey_white',File(output=True))
        self.set_viewer('right_grey_white', 'soma.gui.pipeline.viewer.show_label_image.ShowLabelImage',image='t1mri_nobias',mask='right_grey_white')

        self.add_trait('perform_meshes_and_graphs',Bool(True))
        #Grey/White Surface           
        self.add_trait('left_hemi_cortex',File(output=True,hidden=True))
        self.add_trait('left_white_mesh',File(output=True))
        self.set_viewer('left_white_mesh', 'soma.gui.pipeline.viewer.show_white_matter.ShowWhiteMatter',white_mesh='left_white_mesh',side='left')
        self.add_trait('right_hemi_cortex',File(output=True,hidden=True))
        self.add_trait('right_white_mesh',File(output=True))
        self.set_viewer('right_white_mesh', 'soma.gui.pipeline.viewer.show_white_matter.ShowWhiteMatter',white_mesh='right_white_mesh',side='right',mri_corrected='t1mri_nobias')
        #Spherical Hemispheres Surface     
        self.add_trait('left_pial_mesh',File(output=True))
        self.set_viewer('left_pial_mesh', 'soma.gui.pipeline.viewer.show_hemi.ShowHemi',hemi_mesh='left_pial_mesh',side='left',mri_corrected='t1mri_nobias')
        self.add_trait('right_pial_mesh',File(output=True))
        self.set_viewer('right_pial_mesh', 'soma.gui.pipeline.viewer.show_hemi.ShowHemi',hemi_mesh='right_pial_mesh',side='right',mri_corrected='t1mri_nobias')
        #Cortical Folds Graph
          ##Left
        self.add_trait('left_graph',File(output=True))
        self.add_trait('left_skeleton',File(output=True,hidden=True))
        self.add_trait('left_roots',File(output=True,hidden=True))
        self.add_trait('left_sulci_voronoi',File(output=True,hidden=True))
        self.add_trait('left_cortex_mid_interface',File(output=True,hidden=True))
          ##Right
        self.add_trait('right_graph',File(output=True))
        self.add_trait('right_skeleton',File(output=True,hidden=True))
        self.add_trait('right_roots',File(output=True,hidden=True))
        self.add_trait('right_sulci_voronoi',File(output=True,hidden=True))
        self.add_trait('right_cortex_mid_interface',File(output=True,hidden=True))
        #Sulci Recognition
        self.add_trait('labels_translation_map',File(output=False,hidden=True))

        self.add_trait('perform_sulci_SPAM_recognition',Bool(False))
          ##Left
        self.add_trait('left_labelled_graph',File(output=True))
        self.add_trait('left_posterior_probabilities',File(output=True,hidden=True))
        self.add_trait('left_labels_priors',File(output=False,hidden=True))
            ###Global
            #show descriptive model
        self.add_trait('left_global_model',File(output=False,hidden=True))
        self.add_trait('left_tal_to_global_transform',File(output=True,hidden=True))
        self.add_trait('left_t1_to_global_transform',File(output=True,hidden=True))
            ###Local
            #show descriptive model
        self.add_trait('left_local_model',File(output=False,hidden=True))
        self.add_trait('left_local_referentials',File(output=False,hidden=True))
        self.add_trait('left_direction_priors',File(output=False,hidden=True))
        self.add_trait('left_angle_priors',File(output=False,hidden=True))
        self.add_trait('left_translation_priors',File(output=False,hidden=True))
        self.add_trait('left_global_to_local_transforms',File(output=True,hidden=True))
          ##Right        
        self.add_trait('right_labelled_graph',File(output=True))
        self.add_trait('right_posterior_probabilities',File(output=True,hidden=True))
        self.add_trait('right_labels_priors',File(output=False,hidden=True))
            ###Global            
        self.add_trait('right_global_model',File(output=False,hidden=True))
        self.add_trait('right_tal_to_global_transform',File(output=True,hidden=True))
        self.add_trait('right_t1_to_global_transform',File(output=True,hidden=True))
            ###Local
        self.add_trait('right_local_model',File(output=False,hidden=True))
        self.add_trait('right_local_referentials',File(output=False,hidden=True))
        self.add_trait('right_direction_priors',File(output=False,hidden=True))
        self.add_trait('right_angle_priors',File(output=False,hidden=True))
        self.add_trait('right_translation_priors',File(output=False,hidden=True))
        self.add_trait('right_global_to_local_transforms',File(output=True,hidden=True))


###THIS IS OLD VERSION JUST TO KEEP VIEWER IN MEMORY

          ##Talairach Transformation
        #add_trait('source_referential',File(exists=True,viewer='soma.gui.viewer.show_text'))
        #add_trait('normalized_referential',File(exists=True))
        #add_trait('tal_to_normalized_transform',File(exists=True))
        ##Bias Correction
        #add_trait('t1mri_nobias', File(exists=False,viewer='soma.gui.viewer.show_t1mri_nobias'))
        #add_trait('hfiltered',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        #add_trait('white_ridges',File(exists=False,viewer='soma.gui.viewer.show_white_ridge'))
        #add_trait('variance',File(exists=False,viewer='soma.gui.viewer.show_rainbow_volume'))
        #add_trait('edges',File(exists=False,viewer='soma.gui.viewer.show_rainbow_volume'))
        #add_trait('field',File(exists=False))
        #add_trait('meancurvature',File(exists=False))
        ##Histogram Analysis
        #add_trait('histo',File(exists=False))
        #add_trait('histo_analysis',File(exists=False,viewer='soma.gui.viewer.show_histo'))
        ##Brain Mask Segmentation
        #add_trait('brain_mask',File(exists=False,viewer='soma.gui.viewer.show_brain_mask'))
        ##Split Brain Mask
        #add_trait('split_brain',File(exists=False,viewer='soma.gui.viewer.show_split_brain'))
        #add_trait('split_template',File(exists=True,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        ##Talairach Transformation      
        #add_trait('talairach_ACPC_transform',File(exists=False,viewer='soma.gui.viewer.show_text'))
        ##Grey/White Classification
        #add_trait('left_grey_white',File(exists=False,viewer='soma.gui.viewer.show_grey_white'))
        #add_trait('right_grey_white',File(exists=False,viewer='soma.gui.viewer.show_grey_white'))
        ##Grey/White Surface           
        #add_trait('left_hemi_cortex',File(exists=False,viewer='soma.gui.viewer.show_grey_white'))
        #add_trait('left_white_mesh',File(exists=False,viewer='soma.gui.viewer.show_white_matter'))
        #add_trait('right_hemi_cortex',File(exists=False,viewer='soma.gui.viewer.show_grey_white'))
        #add_trait('right_white_mesh',File(exists=False,viewer='soma.gui.viewer.show_white_matter'))
        ##Spherical Hemispheres Surface     
        #add_trait('left_hemi_mesh',File(exists=False,viewer='soma.gui.viewer.show_hemi'))
        #add_trait('right_hemi_mesh',File(exists=False,viewer='soma.gui.viewer.show_hemi'))
        ##Cortical Folds Graph
          ###Left
        #add_trait('left_graph',File(exists=False,viewer='soma.gui.viewer.show_fold_graph'))
        #add_trait('left_skeleton',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        #add_trait('left_roots',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        #add_trait('left_sulci_voronoi',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        #add_trait('left_middle_cortex',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
          ###Right
        #add_trait('right_graph',File(exists=False))
        #add_trait('right_skeleton',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        #add_trait('right_roots',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        #add_trait('right_sulci_voronoi',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        #add_trait('right_middle_cortex',File(exists=False,viewer='soma.gui.viewer.show_volume.ShowVolume'))
        ##Sulci Recognition
        #add_trait('labels_translation_map',File(exists=True,viewer='soma.gui.viewer.show_text'))
          ###Left
        #add_trait('left_labelled_graph',File(exists=False,viewer='soma.gui.viewer.show_fold_graph'))
        #add_trait('left_posterior_probabilities',File(exists=False,viewer='soma.gui.viewer.show_text'))
        #add_trait('left_labels_priors',File(exists=True))
            ####Global
            ##show descriptive model
        #add_trait('left_global_model',File(exists=True))
        #add_trait('left_tal_to_global_transform',File(exists=False,viewer='soma.gui.viewer.show_text'))
        #add_trait('left_t1_to_global_transform',File(exists=False,viewer='soma.gui.viewer.show_text'))
            ####Local
            ##show descriptive model
        #add_trait('left_local_model',File(exists=True))
        #add_trait('left_local_referentials',File(exists=True))
        #add_trait('left_direction_priors',File(exists=True))
        #add_trait('left_angle_priors',File(exists=True))
        #add_trait('left_translation_priors',File(exists=True))
        #add_trait('left_global_to_local_transforms',File(exists=False))
          ###Right        
        #add_trait('right_labelled_graph',File(exists=False,viewer='soma.gui.viewer.show_fold_graph'))
        #add_trait('right_posterior_probabilities',File(exists=False))
        #add_trait('right_labels_priors',File(exists=True))
            ####Global            
        #add_trait('right_global_model',File(exists=True))
        #add_trait('right_tal_to_global_transform',File(exists=False))
        #add_trait('right_t1_to_global_transform',File(exists=False))
            ####Local
        #add_trait('right_local_model',File(exists=True))
        #add_trait('right_local_referentials',File(exists=True))
        #add_trait('right_direction_priors',File(exists=True))
        #add_trait('right_angle_priors',File(exists=True))
        #add_trait('right_translation_priors',File(exists=True))
        #add_trait('right_global_to_local_transforms',File(exists=False))
        #add_trait('nomenclature',File(exists=True))
    
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

