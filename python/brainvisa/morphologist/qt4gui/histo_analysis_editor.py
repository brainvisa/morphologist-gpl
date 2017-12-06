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

'''Histo analysis editor.
'''


import sip
sip.setapi('QString', 2)
import anatomist.api as anatomist
from soma import aims
# anatomist may be replaced by another implementation (brainvisa.anatomist)
import numpy
from brainvisa.morphologist.qt4gui import histo_analysis_widget
from soma.qt_gui.qt_backend import Qt
from soma.qt_gui.qt_backend.QtGui import QDialog, QWidget, QVBoxLayout, \
    QHBoxLayout, \
    QGridLayout, QPushButton, QLabel, QLineEdit, QDoubleValidator, QSlider, \
    QPixmap, QImage, QColor, QPalette, QSplitter
from soma.qt_gui.qt_backend import QtCore
from soma.qt_gui.qt_backend.QtCore import pyqtSignal as qtSignal
from soma.qt_gui.qt_backend.QtCore import pyqtSlot as qtSlot


class HistoAnalysisEditorWidget(QDialog):

    '''Histo analysis editor dialog. Provides histo and G/W matters
    ranges view (HistoAnalysisWidget), an Anatomist view of the MRI data
    with color overlays, and interactive modification of G/W matters
    ranges is supported. Editable text boxes also represent the analysis.
    '''

    def __init__(self, hdata, mri_corrected=None, parent=None):
        '''Builds a HistoAnalysisEditorWidget, with given histo analysis data,
        and a corrected MRI filename.
        hdata is a HistoData object.
        '''
        QDialog.__init__(self, parent)
        self._mri_corrected = None
        self._mri_corrected_diskitem = mri_corrected
        self._tex_max = 0
        self._fusion2d = None
        self._color_mri = None
        self._palette = None
        self._gmedit = None
        self._gsedit = None
        self._wmedit = None
        self._wsedit = None
        self._color_slider = None
        self._color_label = None
        self._colormap_widget = None

        vlay = QVBoxLayout(self)
        fwid = QSplitter(self)
        fwid.setObjectName('histo_form')
        vlay.addWidget(fwid)
        lwid = QWidget(fwid)
        llay = QVBoxLayout(lwid)
        self.hwid = histo_analysis_widget.HistoAnalysisWidget(lwid)
        self.hwid.show_toolbar(True)
        self.hwid.set_histo_data(hdata)
        self.hwid.set_editable(True)
        self.hwid.draw_histo()
        llay.addWidget(self.hwid)

        self._insert_text_editors(lwid)

        if mri_corrected is not None:
            self._insert_ana_window(fwid)
            self.hwid.histo_analysis_changed.connect(self.update_palette)

        hb = QWidget(self)
        vlay.addWidget(hb)
        hlay = QHBoxLayout(hb)
        okb = QPushButton('Save && exit', hb)
        rsb = QPushButton('Restore saved values', hb)
        ccb = QPushButton('Cancel', hb)
        hlay.addWidget(okb)
        hlay.addWidget(rsb)
        hlay.addWidget(ccb)
        okb.pressed.connect(self.done_accept)
        rsb.pressed.connect(self.restore_saved_han)
        ccb.pressed.connect(self.reject)
        okb.pressed.connect(self.closed)
        ccb.pressed.connect(self.closed)
        # prevent auto-buttons from inappropriately closing the dialog
        okb.setAutoDefault(False)
        okb.setDefault(False)
        rsb.setAutoDefault(False)
        rsb.setDefault(False)
        ccb.setAutoDefault(False)
        ccb.setDefault(False)

    def __del__(self):
        del self._fusion2d
        del self._color_mri
        del self._mri_corrected
        a = anatomist.Anatomist()
        # remove the custom palette from the global list
        if self._palette is not None:
            a.palettes().erase(self._palette.getInternalRep())

    def set_histo_data(self, hdata, nbins=100):
        '''Set or update histogram data.
        hdata should be of type HistoData, or None
        '''
        self.hwid.set_histo_data(hdata, nbins)
        self.hwid.draw_histo()
        self.hwid.histo_analysis_changed.emit(0, 0, 0, 0)

    def set_bias_corrected_image(self, mri_corrected):
        '''Set or update the bias corrected image.
        mri_corrected is a file name.
        '''
        self._mri_corrected_diskitem = mri_corrected
        # add widget if it is not already present
        do_connect = True
        fwid = self.findChild(QWidget, 'histo_form')
        if fwid.findChild(QWidget, 'corrected_mri_view'):
            do_connect = False
        self._insert_ana_window(fwid)
        if do_connect:
            self.hwid.histo_analysis_changed.connect(self.update_palette)

    def clear(self):
        self.hwid.clear()
        self.set_bias_corrected_image(None)

    def _make_palette_colors(self):
        '''Recompute the color overlays palette after histo analysis change'''
        ncolors = 200  # num of colors in the palette
        nstdg = 2.5  # num of stdev displayed as light color for gray
        nstdw = 3.  # num of stdev displayed as light color for white
        han = self.hwid.histodata.han
        if han[0][0] is None or self._palette is None:
            return  # no han
        hmax = max( ( han[0][0] + han[0][1] ), ( han[1][0] + han[1][1] ) ) \
            * 1.3
        factor = ncolors / (hmax + 1.)
        l = [int(round((han[0][0] - nstdg * han[0][1]) * factor)),
             int(round((han[0][0] + nstdg * han[0][1]) * factor)) + 1,
             int(round((han[0][0] - han[0][1]) * factor)),
             int(round((han[0][0] + han[0][1]) * factor)) + 1]
        l[0] = max(0, l[0])
        l[2] = max(0, l[2])
        l[1] = min(ncolors, l[1])
        l[3] = min(ncolors, l[3])
        # colors
        empty = (0, 0, 0)
        white_matter = (255, 0, 0)
        wm_neg = (255, 150, 150)
        wm_pos = (150, 60, 60)
        grey_matter = numpy.array((60, 255, 60))
        gm_neg = numpy.array((60, 150, 60))
        gm_pos = numpy.array((180, 255, 180))
        # different colors for overlaps
        gm_wm = (255, 255, 0)
        gm_wm_neg = (150, 255, 0)
        gm_wm_pos = (128, 255, 0)
        gm_pos_wm = (255, 192, 128)
        gm_pos_wm_neg = (255, 255, 150)
        gm_pos_wm_pos = (80, 192, 0)
        gm_neg_wm = (255, 150, 0)
        gm_neg_wm_neg = (192, 128, 0)
        gm_neg_wm_pos = (150, 150, 0)
        pal = numpy.zeros((ncolors, 3), dtype=int)
        pal[l[0]: l[2]] = gm_neg
        pal[l[2]: l[3]] = grey_matter
        pal[l[3]: l[1]] = gm_pos
        l = [int(round((han[1][0] - nstdw * han[1][1]) * factor)),
             int(round((han[1][0] + nstdw * han[1][1]) * factor)) + 1,
             int(round((han[1][0] - han[1][1]) * factor)),
             int(round((han[1][0] + han[1][1]) * factor)) + 1]
        l[0] = max(0, l[0])
        l[2] = max(0, l[2])
        l[1] = min(ncolors, l[1])
        l[3] = min(ncolors, l[3])
        p = pal[l[0]: l[2]]  # should be wm_neg
        try:
            p[numpy.all(p == grey_matter, axis=1)] = gm_wm_neg
        except IndexError:
            pass
        try:
            p[numpy.all(p == gm_pos, axis=1)] = gm_pos_wm_neg
        except IndexError:
            pass
        try:
            p[numpy.all(p == gm_neg, axis=1)] = gm_neg_wm_neg
        except IndexError:
            pass
        try:
            p[numpy.all(p == empty, axis=1)] = wm_neg
        except IndexError:
            pass
        p = pal[l[3]: l[1]]  # should be wm_pos
        try:
            p[numpy.all(p == grey_matter, axis=1)] = gm_wm_pos
        except IndexError:
            pass
        try:
            p[numpy.all(p == gm_pos, axis=1)] = gm_pos_wm_pos
        except IndexError:
            pass
        try:
            p[numpy.all(p == gm_neg, axis=1)] = gm_neg_wm_pos
        except IndexError:
            pass
        try:
            p[numpy.all(p == empty, axis=1)] = wm_pos
        except IndexError:
            pass
        p = pal[l[2]: l[3]]  # should be wm
        try:
            p[numpy.all(p == grey_matter, axis=1)] = gm_wm
        except IndexError:
            pass
        try:
            p[numpy.all(p == gm_pos, axis=1)] = gm_pos_wm
        except IndexError:
            pass
        try:
            p[numpy.all(p == gm_neg, axis=1)] = gm_neg_wm
        except IndexError:
            pass
        try:
            p[numpy.all(p == empty, axis=1)] = white_matter
        except IndexError:
            pass
        # force last color to be black
        pal[-1, :] = 0
        if self._palette is not None:
            self._palette.setColors(numpy.ravel(pal))
        maxVal = hmax / self._tex_max
        if self._color_mri is not None:
            self._color_mri.setPalette(palette=self._palette, minVal=0,
                                       maxVal=maxVal)
        if self._colormap_widget is not None:
            img = QImage(pal.shape[0], 1, QImage.Format_RGB32)
            for x in xrange(pal.shape[0]):
                img.setPixel(x, 0, QColor(pal[x, 0], pal[x, 1], pal[x, 2]
                                          ).rgb())
            pix = QPixmap.fromImage(img)
            self._colormap_widget.setPixmap(pix)
            self._colormap_widget.setFixedHeight(10)
            self._colormap_widget.setScaledContents(True)

    def _insert_ana_window(self, fwid):
        '''Builds the Anatomist axial view with color overlays. A slider
        allows to change the overlay mixing rate.s
        '''
        a = anatomist.Anatomist()
        if fwid.findChild(QWidget, 'corrected_mri_view'):
            awin = fwid.findChild(QWidget, 'awindow_for_corr')
            awin = a.AWindow(a, awin, refType='WeakShared')
        else:
            wid = QWidget()
            wid.setObjectName('corrected_mri_view')
            if isinstance(fwid, Qt.QSplitter):
                fwid.addWidget(wid)
            else:
                if fwid.layout() is None:
                    fwid.setLayout(QVBoxLayout())
                fwid.layout().addWidget(wid)
            lay = QVBoxLayout()
            wid.setLayout(lay)
            awin = a.createWindow('Axial', options={'hidden': 1})
            awin.setObjectName('awindow_for_corr')
            lay.addWidget(awin.getInternalRep())
            # avoid referential button to become the default button in dialog
            rbut = awin.findChildren(QPushButton)
            for but in rbut:
                but.setAutoDefault(False)
                but.setDefault(False)
            # colormap
            self._colormap_widget = QLabel(wid)
            lay.addWidget(self._colormap_widget)
            # color slider
            bwid = QWidget(wid)
            lay.addWidget(bwid)
            hlay = QHBoxLayout(bwid)
            hlay.addWidget(QLabel('Mixing:', bwid))
            self._color_slider = QSlider(Qt.Qt.Horizontal, bwid)
            hlay.addWidget(self._color_slider)
            self._color_slider.setRange(0, 100)
            self._color_slider.setSliderPosition(50)
            self._color_slider.valueChanged.connect(
                self._color_mixing_changed)
            self._color_label = QLabel('100', bwid)
            hlay.addWidget(self._color_label)
            self._color_label.setFixedWidth(
                self._color_label.sizeHint().width())
            self._color_label.setText('50')
        # display objects
        self._fusion2d = None  # delete previous objects
        self._mri_corrected = None
        self._color_mri = None
        if self._mri_corrected_diskitem is not None:
            self._mri_corrected = a.loadObject(self._mri_corrected_diskitem,
                                               duplicate=True)
            self._color_mri = a.duplicateObject(self._mri_corrected)
            awin.setReferential(self._mri_corrected.referential)
            self._palette = a.createPalette('histo_analysis')
            self._tex_max = \
                self._mri_corrected.getInfos()['texture']['textureMax']
            self._make_palette_colors()
            fusion = a.fusionObjects([self._mri_corrected, self._color_mri],
                                     method='Fusion2DMethod')
            awin.addObjects(fusion)
            a.execute('TexturingParams', objects=[fusion], texture_index=1,
                      mode='linear_A_if_B_black', rate=0.5)
            bb = [aims.Point3df(x[:3])
                  for x in self._mri_corrected.boundingbox()]
            p = (bb[0] + bb[1]) / 2
            awin.setPosition(p, awin.getReferential())
            self._fusion2d = fusion

    def _insert_text_editors(self, lwid):
        '''Text displays and edition of G/W peaks and stdev'''
        lbwid = QWidget(lwid)
        lwid.layout().addWidget(lbwid)
        glay = QGridLayout(lbwid)
        glay.addWidget(QLabel('Gray peak:', lbwid), 0, 0)
        self._gmedit = QLineEdit(lbwid)
        glay.addWidget(self._gmedit, 0, 1)
        glay.addWidget(QLabel('std:', lbwid), 0, 2)
        self._gsedit = QLineEdit(lbwid)
        glay.addWidget(self._gsedit, 0, 3)
        glay.addWidget(QLabel('White peak:', lbwid), 1, 0)
        self._wmedit = QLineEdit(lbwid)
        glay.addWidget(self._wmedit, 1, 1)
        glay.addWidget(QLabel('std:', lbwid), 1, 2)
        self._wsedit = QLineEdit(lbwid)
        glay.addWidget(self._wsedit, 1, 3)
        self._gmedit.setValidator(
            QDoubleValidator(0, 1e6, 1, self._gmedit))
        self._gsedit.setValidator(
            QDoubleValidator(0, 1e6, 1, self._gsedit))
        self._wmedit.setValidator(
            QDoubleValidator(0, 1e6, 1, self._wmedit))
        self._wsedit.setValidator(
            QDoubleValidator(0, 1e6, 1, self._wsedit))
        self.update_text_values()
        self._gmedit.editingFinished.connect(self._text_edited)
        self._gsedit.editingFinished.connect(self._text_edited)
        self._wmedit.editingFinished.connect(self._text_edited)
        self._wsedit.editingFinished.connect(self._text_edited)

    def update_text_values(self):
        '''Fills the histo analysis values in text boxes'''
        han = self.hwid.histodata.han
        self._gmedit.blockSignals(True)
        self._gsedit.blockSignals(True)
        self._wmedit.blockSignals(True)
        self._wsedit.blockSignals(True)
        if han[0][0] is not None:
            self._gmedit.setText('%.1f' % han[0][0])
            self._gsedit.setText('%.1f' % han[0][1])
            self._wmedit.setText('%.1f' % han[1][0])
            self._wsedit.setText('%.1f' % han[1][1])
        self._gmedit.blockSignals(False)
        self._gsedit.blockSignals(False)
        self._wmedit.blockSignals(False)
        self._wsedit.blockSignals(False)

    def update_palette(self, gmean=None, gstd=None, wmean=None, wstd=None):
        '''Updates views when histo analysis values have changed after manual
        modification on the histo view.
        '''
        self._make_palette_colors()
        self.update_text_values()

    def done_accept(self):
        '''Save the new analysis and quit the edition dialog'''
        hdata = self.hwid.histodata
        histo_analysis_widget.save_back_histo_analysis(
            hdata.han_filename, hdata.han)
        self.accept()

    def restore_saved_han(self):
        '''Reload .han file and update the view accordingly'''
        han = histo_analysis_widget.load_histo_analysis(
            self.hwid.histodata.han_filename)
        # set individually because we may already be in a hwid callback
        # which holds references to the internal han
        self.hwid.histodata.han[0][0] = han[0][0]
        self.hwid.histodata.han[0][1] = han[0][1]
        self.hwid.histodata.han[1][0] = han[1][0]
        self.hwid.histodata.han[1][1] = han[1][1]
        self.hwid.redraw_histo_analysis()
        self.update_palette()

    def _text_edited(self):
        '''Update views after manual edition of text boxes'''
        han = ((float(self._gmedit.text()), float(self._gsedit.text())),
               (float(self._wmedit.text()), float(self._wsedit.text())))
        # set individually because we may already be in a hwid callback
        # which holds references to the internal han
        self.hwid.histodata.han[0][0] = han[0][0]
        self.hwid.histodata.han[0][1] = han[0][1]
        self.hwid.histodata.han[1][0] = han[1][0]
        self.hwid.histodata.han[1][1] = han[1][1]
        self.hwid.redraw_histo_analysis()
        self.update_palette()

    def _color_mixing_changed(self, value):
        '''Update anatomist view after overlay colors mixing rate has changed.
        '''
        self._color_label.setText(str(value))
        if self._fusion2d is not None:
            a = anatomist.Anatomist()
            a.execute('TexturingParams', objects=[self._fusion2d],
                      texture_index=1, rate=1. - value * 0.01)

    def awindow(self):
        a = anatomist.Anatomist()
        awin = self.findChild(QWidget, 'awindow_for_corr')
        if awin is not None:
            awin = a.AWindow(a, awin, refType='WeakShared')
            return awin

    def setPalette(self, palette):
        super(HistoAnalysisEditorWidget, self).setPalette(palette)
        self.hwid.setPalette(palette)
        awin = self.awindow()
        if awin is not None:
            awin.setPalette(palette)
            color = palette.color(QPalette.Window)
            color = [color.red(), color.green(), color.blue(), color.alpha()]
            awin.anatomistinstance.execute('WindowConfig',
                                           windows=[awin], light={'background': color})

    @qtSlot()
    def close(self):
        self.emit(self.closed)

    closed = qtSignal()
    '''emitted when the dialog is cancelled, or closed'''


def create_histo_editor(hdata=None, mri_corrected=None):
    '''Create a HistoAnalysisEditorWidget window and set data in it'''
    wid = HistoAnalysisEditorWidget(hdata, mri_corrected)
    wid.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    wid.show()
    return wid
