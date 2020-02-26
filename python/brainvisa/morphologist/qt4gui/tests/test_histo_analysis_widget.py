# WARNING: This test requires morphologist-ui

from __future__ import absolute_import
import os
import sys
import unittest
import numpy

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
sip.setapi('QDate', 2)
sip.setapi('QDateTime', 2)
sip.setapi('QTextStream', 2)
sip.setapi('QTime', 2)
sip.setapi('QUrl', 2)
from soma.qt_gui.qt_backend import QtGui, QtCore, QtTest
from morphologist.tests.gui import TestGui
from morphologist.core.study import Study
from morphologist.intra_analysis import IntraAnalysis
from brainvisa.morphologist.qt4gui.histo_analysis_widget import load_histo_data, create_histo_view


class TestHistoAnalysisWidget(TestGui):

    def __init__(self, *args, **kwargs):
        super(TestHistoAnalysisWidget, self).__init__(*args, **kwargs)

    def setUp(self):
        hanfile = '/neurospin/lnao/Panabase/cati-dev-prod/morphologist/bv_database/test/hyperion/t1mri/default_acquisition/default_analysis/nobias_hyperion.han'
        hisfile = hanfile[:-3] + 'his'
        self.han = load_histo_data(hanfile, hisfile)

    @TestGui.start_qt_and_test
    def test_create_histo_widget(self):
        win = create_histo_view()
        self.keep_widget_alive(win)
        win.set_histo_data(self.han)
        self.assertEqual(len(win.bins), 100)
        self.assertEqual(win.bins[1], 3.03)
        self.assertEqual(len(win.bdata), 100)
        self.assertEqual(win.bdata[0], 6587799)
        self.assertEqual(win.histodata.han, ([41.0, 8.0], [69.0, 4.0]))
        win.close()


if __name__ == '__main__':
    qApp = QtGui.QApplication(sys.argv)
    suite = \
        unittest.TestLoader().loadTestsFromTestCase(TestHistoAnalysisWidget)
    unittest.TextTestRunner(verbosity=2).run(suite)
