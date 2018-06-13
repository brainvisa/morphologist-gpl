# -*- coding: utf-8 -*-
#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
#
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.

from brainvisa.processes import *
from soma.qt_gui.qt_backend import QtGui
from soma.qt_gui.qtThread import MainThreadLife

try:
    from brainvisa.morphologist.qt4gui import histo_analysis_widget
except:
    pass


def validation():
    try:
        import brainvisa.morphologist.qt4gui.histo_analysis_widget
    except:
        raise ValidationError(
            'brainvisa.morphologist.qt4gui.histo_analysis_widget '
            'module cannot be imported')


name = 'Show histo analysis'
userLevel = 0
roles = ('viewer', )

signature = Signature(
    'histo_analysis', ReadDiskItem('Histo analysis', 'Histo Analysis'),
    'histo', ReadDiskItem('Histogram', 'Histogram'),
)


def initialization(self):
    self.linkParameters('histo', 'histo_analysis')


def create_histo_widget(self, hdata):
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
    return MainThreadLife(hwid)


def execution(self, context):
    hdata = histo_analysis_widget.load_histo_data(
        self.histo_analysis.fullPath(), self.histo.fullPath())
    hwid = mainThreadActions().call(self.create_histo_widget, hdata)
    return hwid
