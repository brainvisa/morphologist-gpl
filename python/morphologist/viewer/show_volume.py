# -*- coding: utf-8 -*-
from __future__ import print_function

import os
try:
    from traits.api import ListStr, HasTraits, File, Float, Instance, Enum, Str
except ImportError:
    from enthought.traits.api import ListStr, HasTraits, File, Float, Instance, Enum, Str

from soma.controller import Controller, add_trait
import soma.fom
import anatomist.api as ana


class ShowVolume(Controller):
    print('class show volume')
    name = 'ShowVolume'

    def __init__(self, *args, **kwargs):
        HasTraits.__init__(self)
        add_trait(self, 'volume', File(exists=True))
        # add_trait(self,'t1mri',Str)
        self.volume = args[0]
        # print('t1mri',self.t1mri)

    def anatomist_instance(self):
        a = ana.Anatomist()
        a.createControlWindow()
        win = a.getControlWindow()
        if win is not None:
            win.enableClose(False)
        return a

    def command(self):
        """ Function to execute the viewer"""
        a = self.anatomist_instance()

        # au niveau du loadObject changer ref
        volume = a.loadObject(self.volume, forceReload=False, duplicate=True)
        volume.takeAppRef()
        # a.unregisterObject(volume)
        # a.registerObject(volume)
        axial = a.createWindow("Axial")
        axial.addObjects(volume)
        axial.takeAppRef()
        # a.unregisterWindow(axial)
        # a.registerWindow(axial)
        # return volume,axial

    def __call__(self):
        """ Function to call the execution """
        print('here call show volume')
        self.command()
        #soma.subprocess.check_call( self.command() )
