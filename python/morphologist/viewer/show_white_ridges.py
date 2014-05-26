# -*- coding: utf-8 -*-
import os
try:
    from traits.api import ListStr,HasTraits,File,Float,Instance,Enum,Str,Int
except ImportError:
    from enthought.traits.api import ListStr,HasTraits,File,Float,Instance,Enum,Str,Int

from soma.controller import Controller,add_trait
import subprocess
import anatomist.api as ana

class ShowWhiteRidges(Controller):
    print 'viewer show white ridges'
    name='ShowWhiteRidges'
    def __init__(self,white_ridges,t1mri,palette="random",mode="linear_on_defined",rate=0.3,wintype="Axial"):
        HasTraits.__init__(self)
        add_trait(self,'white_ridges',File(exists=True))
	self.white_ridges=white_ridges
	add_trait(self,'t1mri',File(exist=True))
	self.t1mri=t1mri
	add_trait(self,'palette',Str(palette))
	add_trait(self,'mode',Str(mode))
	add_trait(self,'rate',Int(rate))
	print 'win',wintype
	add_trait(self,'wintype',Str(wintype))
	print 'wintype',self.wintype
    
    def anatomist_instance(self):
        a=ana.Anatomist()   
        a.createControlWindow()
        win=a.getControlWindow()
        if win is not None:
            win.enableClose(False)
        return a    
	
	
    def mask_on_mri(self):
	print 'function mask_on_mri'
	a=self.anatomist_instance()
	volume= a.loadObject(self.t1mri )
	duplicate=False
	if self.palette is not None:
	    duplicate=True
	mask = a.loadObject( self.white_ridges, duplicate=True)
	mask.setPalette( self.palette )
	fusion = a.fusionObjects( [volume, mask], method='Fusion2DMethod' )
	a.execute("Fusion2DParams", object=fusion, mode=self.mode, rate = self.rate, reorder_objects = [ volume, mask ] )
	print 'wintype here',self.wintype
	window = a.createWindow( self.wintype )
	window.assignReferential( volume.referential )
	window.addObjects( [fusion] )
	return {'mri' : volume, 'mask' : mask, 'fusion' : fusion, 'window' : window, 'mriFile' : self.t1mri, 'maskFile' : self.white_ridges}	
	
	

    def command(self):
	print 'function show white ridges'
	#controller_widget._viewer_objects=
	return self.mask_on_mri()
    
        
    def __call__( self):
        """ Function to call the execution """ 
        subprocess.check_call( self.command() )    
