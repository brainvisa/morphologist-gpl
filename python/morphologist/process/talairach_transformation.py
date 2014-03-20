# -*- coding: utf-8 -*-
try:
  from traits.api import File, Float, Int, Bool, Enum
except ImportError:
  from enthought.traits.api import File, Float, Int, Bool, Enum

from soma.process import Process
import subprocess


    
    

class TalairachTransformation( Process ):
    def __init__( self, **kwargs ):
        super( TalairachTransformation, self ).__init__( **kwargs )
        self.name_process = 'morphologistPipeline.TalairachTransformation'
        self.add_trait( 'split_brain', File() )
        self.add_trait( 'commissure_coordinates', File() )
        self.add_trait( 'Talairach_transform', File( output=True) )
	
	
    #def __call__(self):
	#tmp = context.temporary( 'GIS image' )
	#trManager = registration.getTransformationManager()
	#acpcReferential = trManager.referential( 
	#registration.talairachACPCReferentialId )
	#if acpcReferential is None:
	    #context.warning( _t_( 'Talairach-AC/PC-Anatomist not found - maybe an installation problem ?' ) )
	#else:
	    #trManager.setNewTransformationInfo(
	    #self.Talairach_transform,
	    #source_referential = self.split_mask,
	    #destination_referential = acpcReferential )	

