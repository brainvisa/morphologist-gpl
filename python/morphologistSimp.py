# -*- coding: utf-8 -*-

try:
    from traits.api import ListStr,HasTraits,File,Float,Instance
except ImportError:
    from enthought.traits.api import ListStr,HasTraits,File,Float,Instance


class SimpMorpho(HasTraits):
    name = 'morphologist.SimplifiedMorphologist'
    
    def __init__(self):   
        HasTraits.__init__(self)  
        self.add_trait('t1mri',File(exists=True))
        self.add_trait('commissure_coordinates',File(exists=False))
        ####SPM Normalization
        #self.add_trait('anatomical_template', File(exists=True))
        self.add_trait('job_file',File(exists=False))
        self.add_trait('transformations_information',File(exists=False))
        self.add_trait('normalized_t1mri',File(exists=False))
        self.add_trait('talairach_MNI_transform',File(exists=False))
        ###Talairach Transformation
        ##self.source_referential=File(exists=True)
        ##self.add_trait('source_referential',self.source_referential)
        #self.normalized_referential=File(exists=True)
        #self.add_trait('normalized_referential',self.normalized_referential)

        ##Bias Correction
        #self.t1mri_nobias=File(exists=False)
        #self.add_trait('t1mri_nobias', self.t1mri_nobias)
        #self.hfiltered=File(exists=False)
        #self.add_trait('hfiltered',self.hfiltered)
        #self.white_ridges=File(exists=False)
        #self.add_trait('white_ridges',self.white_ridges)
        #self.variance=File(exists=False)
        #self.add_trait('variance',self.variance)
        #self.edges=File(exists=False)
        #self.add_trait('edges',self.edges)
        #self.field=File(exists=False)
        #self.add_trait('field',self.field)
        #self.meancurvature=File(exists=False)
        #self.add_trait('meancurvature',self.meancurvature)
        #self.histo_analysis=File(exists=False)
        #self.add_trait('histo_analysis',self.histo_analysis)
        #self.brain_mask=File(exists=False)
        #self.add_trait('brain_mask',self.brain_mask)
        #self.split_brain=File(exists=False)
        #self.add_trait('split_brain',self.split_brain)
        #self.talairach_ACPC_transform=File(exists=False)
        #self.add_trait('talairach_ACPC_transform',self.talairach_ACPC_transform)
        #self.left_grey_white=File(exists=False)
        #self.add_trait('left_grey_white',self.left_grey_white)
        #self.right_grey_white=File(exists=False)
        #self.add_trait('right_grey_white',self.right_grey_white)       
        #self.left_hemi_cortex=File(exists=False)
        #self.add_trait('left_hemi_cortex',self.left_hemi_cortex)
        #self.left_white_mesh=File(exists=False)      
        #self.add_trait('left_white_mesh',self.left_white_mesh)        
        #self.right_hemi_cortex=File(exists=False)
        #self.add_trait('right_hemi_cortex',self.right_hemi_cortex)
        #self.right_white_mesh=File(exists=False)
        #self.add_trait('right_white_mesh',self.right_white_mesh)
        #self.left_hemi_mesh=File(exists=False)
        #self.add_trait('left_hemi_mesh',self.left_hemi_mesh)
        #self.right_hemi_mesh=File(exists=False)
        #self.add_trait('right_hemi_mesh',self.right_hemi_mesh)
        #self.left_graph=File(exists=False)
        #self.add_trait('left_graph',self.left_graph)
        #self.left_skeleton=File(exists=False)
        #self.add_trait('left_skeleton',self.left_skeleton)
        #self.left_roots=File(exists=False)
        #self.add_trait('left_roots',self.left_roots)
        #self.right_roots=File(exists=False)
        #self.add_trait('right_roots',self.right_roots)
        #self.left_sulci_voronoi=File(exists=False)
        #self.add_trait('left_sulci_voronoi',self.left_sulci_voronoi)
        
        #self.left_posterior_probabilities=File(exists=False)
        #self.add_trait('left_posterior_probabilities',self.left_posterior_probabilities)
        
        #self.left_tal_to_global_transform=File(exists=False)
        #self.add_trait('left_tal_to_global_transform',self.left_tal_to_global_transform)
        #self.left_t1_to_global_transform=File(exists=False)
        #self.add_trait('left_t1_to_global_transform',self.left_t1_to_global_transform)

        
        #self.right_posterior_probabilities=File(exists=False)
        #self.add_trait('right_posterior_probabilities',self.right_posterior_probabilities)
        #self.right_tal_to_global_transform=File(exists=False)
        #self.add_trait('right_tal_to_global_transform',self.right_tal_to_global_transform)

        #self.right_t1_to_global_transform=File(exists=False)
        #self.add_trait('right_t1_to_global_transform',self.right_t1_to_global_transform)
        #self.right_global_to_local_transforms=File(exists=False)
        #self.add_trait('right_global_to_local_transforms',self.right_global_to_local_transforms)
        
        #self.left_global_to_local_transforms=File(exists=False)
        #self.add_trait('left_global_to_local_transforms',self.left_global_to_local_transforms)
        
        #self.right_middle_cortex=File(exists=False)
        #self.add_trait('right_middle_cortex',self.right_middle_cortex)
        #self.right_sulci_voronoi=File(exists=False)
        #self.add_trait('right_sulci_voronoi',self.right_sulci_voronoi)
        #self.right_graph=File(exists=False)
        #self.add_trait('right_graph',self.right_graph)
        #self.left_middle_cortex=File(exists=False)
        #self.add_trait('left_middle_cortex',self.left_middle_cortex)
        #self.right_skeleton=File(exists=False)
        #self.add_trait('right_skeleton',self.right_skeleton)
        
        #self.left_labelled_graph=File(exists=False)
        #self.add_trait('left_labelled_graph',self.left_labelled_graph)
        #self.right_labelled_graph=File(exists=False)
        #self.add_trait('right_labelled_graph',self.right_labelled_graph)
        


    def _t1mri_changed( self ,name, old, new):
        print '/////////////////////////////////////T1MRI CHANGED'
        print 'name',name
        print 'old',old
        print 'new',new 
        # Selection du fom morphologist-brainvisa-1.0
        # Appel à process_completion pour compléter les attributs
        #if self.t1mri is not None and self.t1mri is not self.t1mri_prec:
        #if  is not None:
            #self.t1mri_prec=self.t1mri
            #completion=soma.fom.process_completion( self.ptrait.name, 't1mri', str(self.t1mri),directories={ 
                                            #'spm' : '/here/is/spm',
                                            #'shared' : '/volatile/bouin/build/trunk/share/brainvisa-share-4.4' }) 
        #for key in completion:
            #setattr(self.ptrait,key,completion[key])
