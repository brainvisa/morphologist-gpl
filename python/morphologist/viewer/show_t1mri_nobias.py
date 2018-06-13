# -*- coding: utf-8 -*-
import os
try:
    from traits.api import ListStr, HasTraits, File, Float, Instance, Enum, Str
except ImportError:
    from enthought.traits.api import ListStr, HasTraits, File, Float, Instance, Enum, Str

from soma.controller import Controller, add_trait
import anatomist.api as ana


class ShowT1mriNobias(Controller):
    name = 'ShowT1mriNobias'

    def __init__(self, *args, **kwargs):
        HasTraits.__init__(self)
        add_trait(self, 'mask', File(exists=True))
        self.mask = kwargs['mask']
        add_trait(self, 'mri', File(exist=True))
        self.mri = kwargs['mri']

    def anatomist_instance(self):
        a = ana.Anatomist()
        a.createControlWindow()
        win = a.getControlWindow()
        if win is not None:
            win.enableClose(False)
        return a

    def view_bias(self, volume, forceReload=False, duplicate=True, wintype="Axial"):
        a = self.anatomist_instance()
        obj = a.loadObject(volume, duplicate=True)
        obj.takeAppRef()
        # a.unregisterObject(obj)
        # a.registerObject(obj)
        obj.setPalette(a.getPalette("Rainbow2"))
        window = a.createWindow(wintype)
        window.assignReferential(obj.referential)
        window.addObjects([obj])
        window.takeAppRef()
        # return {"object" : obj, "window" : window, "file" : volume}

    def command(self):
        """ Function to execute the viewer"""
        #selfdestroy = []
        if self.mri is not None:
            #selfdestroy.append( self.view_bias( self.mri, forceReload = 1) )
            self.view_bias(self.mri, forceReload=1)
        #selfdestroy.append( self.view_bias( self.mask))
        self.view_bias(self.mask)

        # return selfdestroy

    def __call__(self):
        """ Function to call the execution """
        self.command()
