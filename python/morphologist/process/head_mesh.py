# -*- coding: utf-8 -*-
try:
  from traits.api import File, Float, Int, Bool, Enum
except ImportError:
  from enthought.traits.api import File, Float, Int, Bool, Enum

from soma.process import Process
import subprocess


class HeadMesh( Process ):
    def __init__( self, **kwargs ):
        super( HeadMesh, self ).__init__( **kwargs )
        self.name_process = 'morphologistPipeline.HeadMesh'
        self.add_trait( 't1mri_nobias', File() )
        self.add_trait( 'histo_analysis', File(optional=True) )
        self.add_trait( 'head_mesh', File( output=True) )
        self.add_trait( 'head_mask', File( optional=True,output=True) )
        self.add_trait( 'keep_head_mask', Bool( False ) )
        self.add_trait( 'remove_mask', File( optional=True) )
        self.add_trait( 'head_mesh_first_slice', Int( optional=True) )
        self.add_trait( 'threshold', Int( optional=True) )
        self.add_trait( 'closing', Float( optional=True) )
	
    def __call__(self):	
	#tm = registration.getTransformationManager()
	
	if self.head_mask is not None and self.keep_head_mask:
	    mask = self.head_mask
	else:
	    mask = context.temporary( 'NIFTI-1 image' )
	
	command = [ 'VipGetHead',
		    '-i', self.t1mri_nobias,
		    '-o', mask,
		    '-w', 't', '-r', 't' ]
	if self.remove_mask is not None:
	    command.extend(['-h', self.remove_mask])
	if self.histo_analysis is not None:
	    command.extend(['-hn',self.histo_analysis])
	if self.head_mesh_first_slice is not None:
	    command.extend(['-n', self.head_mesh_first_slice])
	if self.threshold is not None:
	    command.extend(['-t', self.threshold])
	if self.closing is not None:
	    command.extend([ '-c', self.closing])
	
	str_command=[str(x) for x in command]   
	print 'strcommand',str_command
        subprocess.check_call( str_command )
		
    
	#tm.copyReferential( self.t1mri_nobias, self.head_mesh )
	#if self.keep_head_mask:
	    #tm.copyReferential( self.t1mri_nobias, self.head_mask )
	
