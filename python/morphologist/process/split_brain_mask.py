# -*- coding: utf-8 -*-
try:
  from traits.api import File, Float, Int, Bool, Enum
except ImportError:
  from enthought.traits.api import File, Float, Int, Bool, Enum

try:
  from capsul.process import Process
  print '%s uses CAPSUL.' % __name__
except:
  from soma.process import Process
  print '%s uses Soma.' % __name__
import subprocess

class SplitBrainMask( Process ):
    def __init__( self, **kwargs ):
        super( SplitBrainMask, self ).__init__( **kwargs )
        self.name_process = 'morphologistPipeline.SplitBrainMask'
        self.add_trait( 'brain_mask', File() )
        self.add_trait( 't1mri_nobias', File() )
        self.add_trait( 'histo_analysis', File() )
        self.add_trait( 'commissure_coordinates', File() )
        self.add_trait( 'use_ridges', Bool( True) )
        self.add_trait( 'white_ridges', File() )
        self.add_trait( 'use_template', Bool( True) )
        self.add_trait( 'split_template', File() )
        self.add_trait( 'split_brain_mode', Enum( 'Watershed (2011)', 'Voronoi') )
        self.add_trait( 'split_brain_variant', Enum( 'regularized', 'GW Barycentre', 'WM Standard Deviation') )
        self.add_trait( 'bary_factor', Enum( 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1) )
        self.add_trait( 'mult_factor', Enum( 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4) )
        self.add_trait( 'initial_erosion', Float(2.0) )
        self.add_trait( 'cc_min_size', Int(500) )
        self.add_trait( 'split_brain', File( output=True ) )
        self.add_trait( 'fix_random_seed', Bool( False ) )
    
    def __call__( self ):     
	command = [ 'VipSplitBrain',
		    '-input',  self.t1mri_nobias,
		    '-brain', self.brain_mask,
		    '-analyse', 'r',
		    '-hname', self.histo_analysis,
		    '-output', self.split_brain,
		    '-mode', self.split_brain_mode,
		    '-erosion', self.initial_erosion,
		    '-ccsize', self.cc_min_size ]
	if self.commissure_coordinates:
	    command += ['-Points', self.commissure_coordinates]
	if self.split_brain_variant == 'regularized':
	    command += ['-walgo', 'r']
	elif self.split_brain_variant == 'GW Barycentre':
	    command += ['-walgo', 'b', '-Bary', self.bary_factor]
	elif self.split_brain_variant == 'WM Standard Deviation':
	    command += ['-walgo', 'c', '-Coef', self.mult_factor]
	if self.use_template:
	    command += ['-template', self.split_template, '-TemplateUse', 'y']
	else:
	    command += ['-TemplateUse', 'n']
	if self.use_ridges:
	    command += ['-Ridge', self.white_ridges]
	if self.fix_random_seed:
	    command += ['-srand', '10']
	
	str_command=[str(x) for x in command]   
	print 'strcommand',str_command
        subprocess.check_call( str_command )
	
	#tm = registration.getTransformationManager()
	#tm.copyReferential(self.t1mri_nobias, self.split_brain)

