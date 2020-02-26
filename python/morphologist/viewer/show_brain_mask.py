# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
import os
try:
    from traits.api import ListStr, HasTraits, File, Float, Instance, Enum, Str
except ImportError:
    from enthought.traits.api import ListStr, HasTraits, File, Float, Instance, Enum, Str

from soma.controller import Controller, add_trait
import soma.fom
import anatomist.api as ana


class ShowBrainMask(Controller):
    name = 'ShowBrainMask'
    print('classshow brain mask')

    def __init__(self, *args, **kwargs):
        HasTraits.__init__(self)
        add_trait(self, 'mask', File(exists=True))
        self.mask = kwargs['mask']
        add_trait(self, 'mri_corrected', File(exists=True))
        self.mri_corrected = kwargs['mri_corrected']

    def anatomist_instance(self):
        a = ana.Anatomist()
        a.createControlWindow()
        win = a.getControlWindow()
        if win is not None:
            win.enableClose(False)
        return a

    def mask_on_mri(self, palette, mode, rate, wintype="Axial"):
        print('function mask_on_mri')
        a = self.anatomist_instance()
        mri = a.loadObject(self.mri_corrected)
        mri.takeAppRef()
        duplicate = False
        if palette is not None:
            duplicate = True
        mask = a.loadObject(self.mask, duplicate=True)
        mask.takeAppRef()
        mask.setPalette(palette)
        fusion = a.fusionObjects([mri, mask], method='Fusion2DMethod')
        fusion.takeAppRef()
        a.execute("Fusion2DParams", object=fusion, mode=mode,
                  rate=rate, reorder_objects=[mri, mask])
        window = a.createWindow(wintype)
        window.assignReferential(mri.referential)
        window.addObjects([fusion])
        window.takeAppRef()
        # return {'mri' : mri, 'mask' : mask, 'fusion' : fusion, 'window' : window}

    def command(self):
        self.mask_on_mri("GREEN-ufusion", "linear_A_if_B_white", 0.7)

    def __call__(self):
        """ Function to call the execution """
        print('here call show volume')
        self.command()
