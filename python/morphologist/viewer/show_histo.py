# -*- coding: utf-8 -*-
from __future__ import print_function

from __future__ import absolute_import
import os
try:
    from traits.api import ListStr, HasTraits, File, Float, Instance, Enum, Str
except ImportError:
    from enthought.traits.api import ListStr, HasTraits, File, Float, Instance, Enum, Str

from soma.controller import Controller, add_trait
#import anatomist.api as ana


class ShowHisto(Controller):
    print('class show histo')
    name = 'ShowHisto'

    def __init__(self, *args, **kwargs):
        HasTraits.__init__(self)
        add_trait(self, 'histo_analysis', File(exists=True))
        self.histo_analysis = kwargs['histo_analysis']
        add_trait(self, 'histo', File(exist=True))
        self.histo = kwargs['histo']

    def create_histo_widget(hdata):
        try:
            from morphologist_common.gui import histo_analysis_widget
        except:
            raise ValidationError(
                'morphologist_common.gui.histo_analysis_widget '
                'module cannot be imported')
        hwid = histo_analysis_widget.HistoAnalysisWidget(None)
        hwid.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        hwid.show_toolbar(True)
        hwid.set_histo_data(hdata, nbins=100)
        hwid.layout().addWidget(QtGui.QLabel(
            '<table><tr><td>Gray peak: </td><td><b>%.1f</b></td>'
            '<td> , std: </td><td><b>%.1f</b></td></tr>'
            '<tr><td>White peak: </td><td><b>%.1f</b></td>'
            '<td> , std: </td><td><b>%.1f</b></td></tr></table>'
            % (hdata.han[0][0], hdata.han[0][1], hdata.han[1][0], hdata.han[1][1]),
            hwid))
        hwid.draw_histo()
        hwid.show()

    def command(self):
        try:
            from morphologist_common.gui import histo_analysis_widget
        except:
            raise ValidationError(
                'morphologist_common.gui.histo_analysis_widget '
                'module cannot be imported')
            hdata = histo_analysis_widget.load_histo_data(
                self.histo_analysis, self.histo)
            hwid = create_histo_widget(hdata)
    # hwid.takeAppRef()
    #controller_widget._viewer_objects = [ hwid]

    def __call__(self):
        """ Function to call the execution """
        print('here call show volume')
        self.command()
