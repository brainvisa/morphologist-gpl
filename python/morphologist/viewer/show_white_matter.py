# -*- coding: utf-8 -*-
import os
try:
    from traits.api import ListStr,HasTraits,File,Float,Instance,Enum,Str
except ImportError:
    from enthought.traits.api import ListStr,HasTraits,File,Float,Instance,Enum,Str

from soma.controller import Controller,add_trait
import soma.fom
import anatomist.api as ana                

class ShowWhiteMatter(Controller):
    name='ShowWhiteMatter'
    print 'classshow brain mask'   
    def __init__(self,*args,**kwargs):
        HasTraits.__init__(self)
	add_trait(self,'white_mesh',File(exists=True))
	self.white_mesh=kwargs['white_mesh']
	add_trait(self,'mri_corrected',File)
	if 'mri_corrected' in kwargs:
	    self.mri_corrected=kwargs['mri_corrected']
	add_trait(self,'side',Str)
	self.side=kwargs['side']
	#add_trait(self,'mri',File(exists=True))
	#self.mri=kwargs['mri']

    def anatomist_instance(self):
        a=ana.Anatomist()   
        a.createControlWindow()
        win=a.getControlWindow()
        if win is not None:
            win.enableClose(False)
        return a    
    

    def command( self):
        a = self.anatomist_instance()
	mesh = a.loadObject( self.white_mesh, duplicate=True )
	mesh.setMaterial( a.Material(diffuse = [0.3, 1, 0.6, 1] ) )
	mesh.takeAppRef()
	
	win3 = a.createWindow( 'Sagittal' )
	win3.assignReferential( mesh.referential )

	if self.side == 'right':
	    win3.camera( view_quaternion=[0.5, -0.5, -0.5, 0.5] )
	
	print 'corredt',self.mri_corrected
	if self.mri_corrected:
	    print 'ok mri corrected'
	    anat = a.loadObject( self.mri_corrected )
	    anat.takeAppRef()
	    win3.addObjects( [anat] )
	
	win3.addObjects( [mesh] )
    	win3.takeAppRef()
    
    def __call__( self):
        """ Function to call the execution """ 
	print 'here call show volume'
	self.command()
  
  
