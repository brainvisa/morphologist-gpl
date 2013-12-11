# -*- coding: utf-8 -*-
try:
  from traits.api import File, Float, Int, Bool, Enum
except ImportError:
  from enthought.traits.api import File, Float, Int, Bool, Enum

from soma.pipeline.process import Process
import subprocess




	
class HistoAnalysis( Process ):
    def __init__( self, **kwargs ):
        super( HistoAnalysis, self ).__init__( **kwargs )
    	self.name_process = 'morphologistPipeline.HistoAnalysis'
        self.add_trait( 't1mri_nobias', File() )
        self.add_trait( 'use_hfiltered', Bool( True ) )
        self.add_trait( 'hfiltered', File(optional=True) )
        self.add_trait( 'use_wridges', Bool( True ) )
        self.add_trait( 'white_ridges', File(optional=True) )
        self.add_trait( 'undersampling', Enum( 'iteration', 'auto', '32', '16', '8', '4', '2' ) )
        self.add_trait( 'histo_analysis', File( output=True ) )
        self.add_trait( 'histo', File( output=True) )
        self.add_trait( 'fix_random_seed', Bool( False ) )
	
	
    def __call__(self):
        command = [ 'VipHistoAnalysis',
                    '-i', self.t1mri_nobias,
                    '-o', self.histo_analysis,
                    '-Save', 'y' ]
	if self.use_hfiltered and self.hfiltered is not None:
	    command += ['-Mask', self.hfiltered]
	if self.use_wridges and self.white_ridges is not None:
	    command += ['-Ridge', self.white_ridges]
	if self.undersampling == 'iteration':
	    command += ['-mode', 'i']
	else:
	    command += ['-mode', 'a', '-u', self.undersampling]
	if self.fix_random_seed:
	    command += ['-srand', '10']
	 
	str_command=[str(x) for x in command]   
	print 'strcommand',str_command
        subprocess.check_call( str_command )
