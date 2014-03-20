# -*- coding: utf-8 -*-
try:
  from traits.api import File, Float, Int, Bool, Enum
except ImportError:
  from enthought.traits.api import File, Float, Int, Bool, Enum

from soma.process import Process
import subprocess	        
    
class ComputeBrainMask( Process ):
    def __init__( self, **kwargs ):
        super( ComputeBrainMask, self ).__init__( **kwargs )
        self.name_process = 'morphologistPipeline.ComputeBrainMask'
        self.add_trait( 't1mri', File() )
        self.add_trait( 'histo_analysis', File() )
        self.add_trait( 'variance', File() )
        self.add_trait( 'edges', File() )
        self.add_trait( 'white_ridges', File(optional=True) )
        self.add_trait( 'commissure_coordinates', File(optional=True) )
        self.add_trait( 'lesion_mask', File(optional=True) )
        self.add_trait( 'brain_mask_variant',  Enum('2010',
                           '2005 based on white ridge',
                           'Standard + (iterative erosion)',
                           'Standard + (selected erosion)',
                           'Standard + (iterative erosion) without regularisation',
                           'Robust + (iterative erosion)',
                           'Robust + (selected erosion)',
                           'Robust + (iterative erosion) without regularisation',
                           'Fast (selected erosion)') )
        self.add_trait( 'erosion_size', Enum( 1, 1.5, 1.8, 2, 2.5, 3, 3.5 ,4 ) )
        self.add_trait( 'visu', Enum('No', 'Yes') )
        self.add_trait( 'layer', Enum(0, 1, 2, 3, 4, 5) )
        self.add_trait( 'brain_mask_first_slice', Int(0) )
        self.add_trait( 'last_slice', Int(0) )
        self.add_trait( 'brain_mask', File( output=True ) )
        self.add_trait( 'fix_random_seed', Bool( False ) )
	
	
    def __call__(self):	
        command = [ 'VipGetBrain', '-i', self.t1mri_nobias,
                    '-berosion', self.erosion_size,
                    '-analyse', 'r',
                    '-hname', self.histo_analysis,
                    '-bname', self.brain_mask,
                    '-First', self.first_slice,
                    '-Last', self.last_slice,
                    '-layer', self.layer ]
        if self.commissure_coordinates is not None:
            command += ['-Points', self.commissure_coordinates]
        if self.lesion_mask is not None:
            command += ['-patho', self.lesion_mask]
        
        if self.brain_mask_variant == '2010':
            command += ['-m', 'V', '-Variancename', self.variance,
                        '-Edgesname', self.edges,
                        '-Ridge', self.white_ridges]
        elif self.brain_mask_variant == '2005 based on white ridge':
            command += ['-m', '5', '-Ridge', self.white_ridges]
        elif self.brain_mask_variant == 'Standard + (iterative erosion)':
            command += ['-m', 'Standard']
        elif self.brain_mask_variant == 'Standard + (selected erosion)':
            command += ['-m', 'standard']
        elif self.brain_mask_variant == 'Standard + (iterative erosion) without regularisation':
            command += ['-m', 'Standard','-niter', 0]
        elif self.brain_mask_variant == 'Robust + (iterative erosion)':
            command += ['-m', 'Robust']
        elif self.brain_mask_variant == 'Robust + (selected erosion)':
            command += ['-m', 'robust']
        elif self.brain_mask_variant == 'Robust + (iterative erosion) without regularisation':
            command += ['-m', 'Robust','-niter', 0]
        elif self.brain_mask_variant == 'Fast (selected erosion)':
            command += ['-m', 'fast']
        else:
            raise RuntimeError( _t_( 'Variant <em>%s</em> not implemented' ) % self.brain_mask_variant )
        if self.fix_random_seed:
            command += ['-srand', '10']
	    
	str_command=[str(x) for x in command]   
	print 'strcommand',str_command
        subprocess.check_call( str_command )
        
        #tm = registration.getTransformationManager()
        #tm.copyReferential(self.t1mri_nobias, self.brain_mask)
        
	
	#FIXME what to do with result?
        result = []
        if self.visu == 'Yes':
            result.append(context.runProcess('AnatomistShowBrainMask',
                self.brain_mask, self.t1mri_nobias))
            return result
	
	
