#!/usr/bin/env python2
'''HistoAnalysisWidget QWidget class, plus some helper classes, namely
HistoData objects, which binds histogram data, histogram analysis, and their
filenames.
'''

from __future__ import print_function
import re
import os
import math
import numpy
from soma.qt_gui.qt_backend import QtGui, QtCore
from soma.qt_gui.qt_backend import init_matplotlib_backend
init_matplotlib_backend()
from matplotlib import pyplot
import matplotlib.ticker


class EnhancedSciFormatter(matplotlib.ticker.ScalarFormatter):

    '''An enhanced ScalarFormatter. The default ScalarFormatter in matplotlib
    does not do what we want (nor what I understand of what it should do, in
    the documentation). Here we want 'normal' numbers for small numbers
    (ie "125"), or scientific notation for large ones ("1.2e6").
    This is used to display tick labels on the Y axis of the histogram.
    '''

    def __init__(self, useOffset=True, useMathText=None, useLocale=None):
        matplotlib.ticker.ScalarFormatter.__init__(self)

    def pprint_val(self, value):
        '''overload of the Formatter.pprint_val() method which is used by
        the Matplotlib rendering engine on axes.
        '''
        ln10 = math.log(10)
        if value == 0 or \
                (abs(value) > math.exp(self._powerlimits[0] * ln10)
                 and abs(value) < math.exp(self._powerlimits[1] * ln10)):
            return '%1.0f' % value
        exponent = int(math.log10(abs(value)))
        return '%1.1fe%d' % (value / math.exp(exponent * ln10), exponent)

    def get_offset(self):
        '''Offset is disabled (not print on the top of the axis) because we
        already include it in the "normal" ticks labels
        '''
        return ''


class HistoData(object):

    '''Histogram + histo analysis data, with filenames
    '''

    def __init__(self, histo_filename=None, han_filename=None,
                 histo_data=None, histo_analysis=None):
        self.histo_filename = histo_filename
        self.han_filename = han_filename
        self.data = histo_data
        if histo_analysis is None:
            self.han = [[None, None], [None, None]]
        else:
            self.han = histo_analysis

    def reload(self):
        '''Reload data using the file names'''
        # clear data
        self.han = [[None, None], [None, None]]
        self.data = None
        # reload han
        if self.han_filename:
            han = load_histo_analysis(self.han_filename)
            self.han = han
        # reload histo
        if self.histo_filename:
            data = numpy.loadtxt(self.histo_filename, dtype=int)
            self.data = data


class HistoAnalysisWidget(QtGui.QWidget):

    '''Histogram + white and gray analysis view. The view may be editable
    (see set_editable()).
    A Qt widget containing a Matplotlib graphical view.
    '''

    #: Used for histogram (bars) representation, in set_histo_view_mode()
    HISTO = 0
    #: Used for curve representation, in set_histo_view_mode()
    CURVE = 1

    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags(0)):
        QtGui.QWidget.__init__(self, parent, flags)
        self.histodata = HistoData()
        self.mfig = None
        self.bins = []
        self.bdata = []
        self.editable = False
        self._init_pos = None
        self._moveratio = 0
        self._moved_artist = None
        self._callbacks = []
        self._histo_plots = None
        self._plots = ((None, None, None), (None, None, None))
        self._pick = None
        self._histo_view_mode = self.CURVE

        # combine matplotlib / Qt
        lay = QtGui.QVBoxLayout(self)
        lay.setMargin(0)
        lay.setSpacing(0)
        self.mfig = pyplot.figure()
        if parent is not None:
            p = parent
        else:
            p = self
        self.mwidget = \
            pyplot._pylab_helpers.Gcf.get_fig_manager(self.mfig.number).window
        self.mwidget.setParent(self)
        self.setPalette(p.palette())
        lay.addWidget(self.mwidget)
        toolbar = self.findChild(QtGui.QToolBar)
        toolbar.hide()
        statusbar = self.mwidget.statusBar()
        statusbar.setSizeGripEnabled(False)
        font = statusbar.font()
        font.setPointSize(8)
        statusbar.setFont(font)

    # emitted whenever the histo analysis is modified interactively by the user
    histo_analysis_changed = QtCore.pyqtSignal(float, float, float, float)

    def setPalette(self, palette):
        '''reimplemented from QWidget to handle matplotlib widget and
        mainwindow status bar
        '''
        QtGui.QWidget.setPalette(self, palette)
        colorname = str(palette.color(QtGui.QPalette.Window).name())
        self.mfig.set_facecolor(colorname)
        self.mfig.set_edgecolor(colorname)
        self.mwidget.statusBar().setPalette(palette)
        if len(self.mfig.axes) != 0:
            axes = self.mfig.axes[0]
            textcolor = palette.color(QtGui.QPalette.WindowText)
            colorname = str(textcolor.name())
            labelsize = 7.
            try:  # exist only for matplotlib >= 1.2
                tick_params_attribute = axes.tick_params
            except AttributeError:
                xlabels = [labels.get_text()
                           for labels in axes.get_xticklabels()]
                ylabels = [labels.get_text()
                           for labels in axes.get_yticklabels()]
                axes.set_xticklabels(xlabels, color=colorname,
                                     fontsize=labelsize)
                axes.set_yticklabels(ylabels, color=colorname,
                                     fontsize=labelsize)
            else:
                axes.tick_params(colors=colorname)
                axes.tick_params(labelsize=labelsize)
            for axisline in axes.spines.itervalues():
                axisline.set_color(str(textcolor.name()))

    def set_binned_data(self, bdata):
        '''Set the internal data (nbins x 2 numpy array).
        No graphical update is performed.
        '''
        self.bdata = bdata

    def set_data(self, data, nbins=100):
        '''Bin data (N x 2 numpy array) and set binned data in the view.
        No graphical operation is performed.
        '''

        # rescale/bin histogram data to nbins bins
        dlen = data[-1, 0] + 1
        orig_bin_size = data[1, 0] - data[0, 0]
        bins = [(i * float(dlen) / nbins) for i in xrange(nbins)]
        bins.append(-1)
        self.bdata = [numpy.sum(data[bins[i] / orig_bin_size:
                                     bins[i + 1] / orig_bin_size, 1]) for i in xrange(len(bins) - 1)]
        self.bins = bins[: -1]

    def set_histo_analysis(self, han):
        '''Set the internal histo analysis. No graphical update is performed.
        '''
        self.histodata.han = han

    def set_histo_data(self, histo_data, nbins=100):
        '''set histogram and histo analysis data using a HistoData object'''
        if histo_data is None:
            self.histodata = HistoData()
            self.bins = []
            self.bdata = []
        else:
            self.histodata = histo_data
            self.set_data(histo_data.data, nbins=nbins)

    def set_histo_view_mode(self, mode):
        '''Set histogram rendering mode: HISTO (bars) or CURVE.
        '''
        self._histo_view_mode = mode

    def draw_histo(self):
        '''Draw or redraw completely the graphical parts: histogram and
        gray / white peaks with stdev. Should be called after set_data(),
        set_binned_data(), set_histo_analysis().
        '''
        if self.histodata.data is None:
            self.clear_view()
            return
        # height = max of non-background values
        if self._histo_view_mode == self.HISTO:
            height = max(self.bdata[len(self.bdata) / 20:])
        else:
            height = max(self.histodata.data[
                self.histodata.data.shape[0] / 20:, 1])
        gx = self.histodata.han[0][0]
        dgx = self.histodata.han[0][1]
        wx = self.histodata.han[1][0]
        dwx = self.histodata.han[1][1]
        gmean, gbg, gbgfn, gbgfp, wmean, wbg, wbgfn, wbgfp, gbbg, gbbgfn, gbbgfp, wbbg, wbbgfn, wbbgfp \
            = None, None, None, None, None, None, None, None, None, None, \
            None, None, None, None
        textcolor = self.palette().color(QtGui.QPalette.WindowText)

        if len(self.mfig.axes) == 0:
            # no axes yet. Create them
            bgcolor = self.palette().color(QtGui.QPalette.Base)
            axes = self.mfig.add_subplot(111, axisbg=str(bgcolor.name()))
        else:
            # use existing axes
            axes = self.mfig.axes[0]
            axes.clear()

        # fix colors
        colorname = str(textcolor.name())
        labelsize = 7.
        try:  # exist only for matplotlib >= 1.1
            tick_params_attribute = axes.tick_params
        except AttributeError:
            xlabels = [labels.get_text()
                       for labels in axes.get_xticklabels()]
            ylabels = [labels.get_text()
                       for labels in axes.get_yticklabels()]
            axes.set_xticklabels(xlabels, color=colorname,
                                 fontsize=labelsize)
            axes.set_yticklabels(ylabels, color=colorname,
                                 fontsize=labelsize)
        else:
            axes.tick_params(colors=colorname)
            axes.tick_params(labelsize=labelsize)
        for axisline in axes.spines.itervalues():
            axisline.set_color(colorname)

        # use our EnhancedSciFormatter for y ticks labels
        formatter = EnhancedSciFormatter()
        formatter.set_powerlimits((0, 3))
        axes.yaxis.set_major_formatter(formatter)
        # need also to force x formatter with matplotlib 0.99
        axes.xaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())

        # colors. Could become configurable one day.
        histo_color = '#3070d0'
        gray_color = '#50a050'
        white_color = '#a05050'
        dark_blue = '#000080'
        gray_light_color = '#40b040'
        white_light_color = '#b04040'
        gray_far_neg_color = '#408040'
        gray_far_pos_color = '#80ff80'
        white_far_neg_color = '#ff8080'
        white_far_pos_color = '#804040'
        white = '#ffffff'
        bgalpha = 0.3
        alpha = 0.5

        if gx is not None and dgx is not None:
            # draw gray peak background
            gsigma, gsmax, gabsc1, gabsc2, gabsc3 = self._get_gauss_absc()
            gdata1, gdata2, gdata3 = self._get_gauss(gsigma, gsmax, height)
            gbbg, gbbgfn, gbbgfp = self._plot_peak_background(gsigma, gsmax,
                                                              gx, dgx, gabsc1, gabsc2, gabsc3, gdata1, gdata2, gdata3,
                                                              colors=[white] * 3, edgecolors=[white] * 3, alpha=bgalpha)

        if wx is not None and dwx is not None:
            # draw white peak background
            wsigma, wsmax, wabsc1, wabsc2, wabsc3 = self._get_gauss_absc('W')
            wdata1, wdata2, wdata3 = self._get_gauss(wsigma, wsmax, height)
            wbbg, wbbgfn, wbbgfp = self._plot_peak_background(wsigma, wsmax,
                                                              wx, dwx, wabsc1, wabsc2, wabsc3, wdata1, wdata2, wdata3,
                                                              colors=[white] * 3, edgecolors=[white] * 3, alpha=bgalpha)

        if gx is not None and dgx is not None:
            colors = (gray_light_color, gray_far_neg_color,
                      gray_far_pos_color)
            edgecolors = (gray_color, ) * 3
            gbg, gbgfn, gbgfp = self._plot_peak_background(gsigma, gsmax,
                                                           gx, dgx, gabsc1, gabsc2, gabsc3, gdata1, gdata2, gdata3,
                                                           colors=colors, edgecolors=edgecolors, alpha=alpha)

        if wx is not None and dwx is not None:
            colors = (white_light_color, white_far_neg_color,
                      white_far_pos_color)
            edgecolors = (white_color, ) * 3
            wbg, wbgfn, wbgfp = self._plot_peak_background(wsigma, wsmax,
                                                           wx, dwx, wabsc1, wabsc2, wabsc3, wdata1, wdata2, wdata3,
                                                           colors=colors, edgecolors=edgecolors, alpha=alpha)

        # plot histogram
        if self._histo_view_mode == self.HISTO:
            pyplot.bar(
                self.bins, self.bdata, width=self.bins[1] - self.bins[0],
                color=histo_color, figure=self.mfig, axes=self.mfig.axes[0],
                edgecolor=dark_blue)
        else:  # curve draw
            self.mfig.axes[0].plot(self.histodata.data[:, 0],
                                   self.histodata.data[:, 1], '-', color=histo_color,
                                   linewidth=3.)

        if gx is not None and dgx is not None:
            # draw gray peak mean/sigma
            gmean = pyplot.plot([gx, gx], [0, height * 1.2], gray_color,
                                linewidth=2., figure=self.mfig, axes=axes)[0]

        if wx is not None and dwx is not None:
            # draw white peak mean/sigma
            wmean = pyplot.plot([wx, wx], [0, height * 1.2], white_color,
                                linewidth=2., figure=self.mfig, axes=axes)[0]

        # rescale histogram
        axes.set_ybound(0, height * 1.3)
        if wx is not None and dwx is not None:
            axes.set_xbound(0, (wx + dwx) * 1.3)

        self.mfig.canvas.draw()

        # keep track of correspondance between histo analysis elements and
        # matplotlib artists
        self._histo_plots = {}
        plots = ((gmean, gbbg, gbbgfn, gbbgfp, gbg, gbgfn, gbgfp),
                (wmean, wbbg, wbbgfn, wbbgfp, wbg, wbgfn, wbgfp))
        self._plots = plots
        for p in plots[0]:
            if p is not None:
                self._histo_plots[p] = [self.histodata.han[0], plots[0]]
        for p in plots[1]:
            if p is not None:
                self._histo_plots[p] = [self.histodata.han[1], plots[1]]
        self.set_editable(self.editable)

    def clear_view(self):
        '''remove all graphical elements'''
        if len(self.mfig.axes) != 0:
            self.mfig.clear()
            self.mfig.canvas.draw()

    def clear(self):
        '''clear both view and internal data'''
        self.clear_view()
        self.histodata = HistoData()
        self.bins = []
        self.bdata = []
        # self.editable = False
        self._init_pos = None
        self._moved_artist = None
        self._callbacks = []  # FIXME: remove all callbacks before
        self._histo_plots = None
        self._plots = ((None, None, None), (None, None, None))
        self._pick = None

    def redraw_histo_analysis(self):
        '''Redraw only the han part, not the histo itself'''
        for hmean in self._plots:
            han = self._histo_plots[hmean[0]]
            if han[0] is self.histodata.han[0]:  # gray
                peak = 'G'
            else:
                peak = 'W'
            artist = han[1][0]  # mean line (Line2D object)
            data = artist.get_data()
            artist.set_data([han[0][0], han[0][0]], data[1])
            sig0, smax, absc1, absc2, absc3 = self._get_gauss_absc(peak)
            absc = (absc1, absc2, absc3, absc1, absc2, absc3)
            wx = han[0][0]
            dwx = han[0][1]
            for i, artist in enumerate(han[1][1:]):
                # sigma polygon (Polygon object)
                data = artist.get_path().vertices
                data[:-1, 0] = absc[i] * dwx / sig0 + wx
                data[-1, 0] = data[0, 0]
        self.mfig.canvas.draw()

    def _move_han(self, han, posdiff):
        '''move an histogram analysis (gray or white) in han, and its plots in
        figure fig, of posdiff.
        '''
        artist = han[1][0]  # mean line (Line2D object)
        data = artist.get_data()
        artist.set_data(data[0] + posdiff, data[1])
        for artist in han[1][1:]:  # sigma polygons (Polygon objects)
            data = artist.get_path().vertices
            data += numpy.array([posdiff, 0])
        self.mfig.canvas.draw()
        han[0][0] += posdiff
        # emit a Qt signal to notify change
        hishan = self.histodata.han
        self.histo_analysis_changed.emit(hishan[0][0], hishan[0][1],
                                         hishan[1][0], hishan[1][1])

    def _get_gauss_absc(self, peak='G'):
        '''internal.'''
        # get gaussian arrays abscisses
        sigma = 10
        if peak != 'W':
            smax = 2.5
        else:
            smax = 3.
        absc1 = numpy.hstack(([-sigma],
                              numpy.array(
                                  range(-sigma, sigma + 1), dtype=float),
                              [sigma]))
        absc2 = numpy.hstack(([-int(sigma * smax)] * 3,
                              numpy.array(
                                  range(
                                      -int(
                                          sigma * smax), -sigma + 1), dtype=float),
                              [-sigma]))
        absc3 = numpy.hstack(([sigma],
                              numpy.array(
                                  range(
                                      sigma, int(
                                          sigma * smax) + 1), dtype=float),
                              [int(sigma * smax)] * 3))
        return sigma, smax, absc1, absc2, absc3

    def _get_gauss(self, sigma, smax, height):
        '''internal.'''
        # get gaussian values for the 3 polygons
        denom = 0.5 / numpy.power(sigma, 2)
        data1 = numpy.array([0.] +
                            [numpy.exp(-numpy.power(x, 2) * denom)
                             for x in xrange(-sigma, sigma + 1)]
                            + [0.]) * height * 1.2
        data2 = numpy.array([0., 0., 1.] +
                            [numpy.exp(-numpy.power(x, 2) * denom)
                             for x in xrange(-int(sigma * smax), -sigma + 1)]
                            + [0.]) * height * 1.2
        data3 = numpy.array([0.] +
                            [numpy.exp(-numpy.power(x, 2) * denom)
                             for x in xrange(sigma, int(sigma * smax) + 1)]
                            + [0., 1., 0.]) * height * 1.2
        return data1, data2, data3

    def _plot_peak_background(self, sigma, smax, x, dx, absc1, absc2, absc3,
                              data1, data2, data3, colors, edgecolors, alpha):
        '''internal.'''
        # plot gaussian parts
        axes = self.mfig.axes[0]
        bg = pyplot.fill(absc1 * dx / sigma + x, data1,
                         colors[0], edgecolor=edgecolors[0], figure=self.mfig,
                         axes=axes, alpha=alpha)
        fn = pyplot.fill(absc2 * dx / sigma + x, data2,
                         colors[1], edgecolor=edgecolors[1], figure=self.mfig,
                         axes=axes, alpha=alpha)
        fp = pyplot.fill(absc3 * dx / sigma + x, data3,
                         colors[2], edgecolor=edgecolors[2], figure=self.mfig,
                         axes=axes, alpha=alpha)
        return (bg[0], fn[0], fp[0])

    def _move_sigma(self, han, sigma):
        '''move an histogram analysis (gray or white) std value in han,
        and its plots in figure fig, set to sigma.
        '''
        if han[0] is self.histodata.han[0]:
            peak = 'G'
        else:
            peak = 'W'
        sig0, smax, absc1, absc2, absc3 = self._get_gauss_absc(peak)
        absc = (absc1, absc2, absc3, absc1, absc2, absc3)
        for i, artist in enumerate(han[1][1:]):
            # sigma polygon (Polygon object)
            data = artist.get_path().vertices
            data[:-1, 0] = absc[i] * sigma / sig0 + han[0][0]
            data[-1, 0] = absc[i][0] * sigma / sig0 + han[0][0]
        self.mfig.canvas.draw()
        han[0][1] = sigma
        # emit a Qt signal to notify change
        hishan = self.histodata.han
        self.histo_analysis_changed.emit(hishan[0][0], hishan[0][1],
                                         hishan[1][0], hishan[1][1])

    def _his_mouse_press(self, event):
        '''matplotlib callback for picker event, triggers the histo analysis
        interactive modification.
        '''
        if self._moved_artist is not None:
            # another artist is being processed yet.
            return
        fig = event.canvas.figure
        self._init_pos = event.mouseevent.xdata
        artist = event.artist
        self._moveratio = 0
        # disambiguate in case both the mean line and the stdev polygon
        # can be selected here
        tolerance = self.histodata.han[1][0] * 0.015
        if artist == self._histo_plots[ artist ][1][1] and \
                abs( self._init_pos - self._histo_plots[ artist ][0][0] ) \
                < tolerance:
            # discard this event: another one will be fired for the mean line
            return
        # select the best artist (mean line or stdev polygon)
        # if abs( self._init_pos - self._histo_plots[ artist ][0][0] ) < 5:
            # force using the mean line, not the std polygon, if we are close
            # to it
            # artist = self._histo_plots[ artist ][1][0]
        self._moved_artist = artist
        # install move / release callbacks
        self._callbacks = []
        self._callbacks.append(fig.canvas.mpl_connect('button_release_event',
                                                      self._his_mouse_release))
        self._callbacks.append(fig.canvas.mpl_connect('motion_notify_event',
                                                      self._his_mouse_move))
        self._callbacks.append(fig.canvas.mpl_connect('figure_leave_event',
                                                      self._his_mouse_release))

    def _his_mouse_release(self, event):
        '''matplotlib callback, ends dragging G/W analysis curves'''
        # move to the last position
        self._his_mouse_move(event)
        self._moveratio = 0
        # cleanup
        self._init_pos = None
        self._moved_artist = None
        # remove move / release callbacks
        for cid in self._callbacks:
            event.canvas.mpl_disconnect(cid)
        self._callbacks = []

    def _his_mouse_move(self, event):
        '''matplotlib callback, moves G/W analysis curves'''
        if event.xdata is None:
            # out of plot axes: do nothing
            return
        artist = self._moved_artist
        if artist is None:
            return
        han = self._histo_plots[artist]
        if artist == han[1][0]:  # mean line
            posdiff = event.xdata - self._init_pos
            self._move_han(han, posdiff)
            self._init_pos = event.xdata
        else:
            if self._moveratio == 0:
                self._moveratio = abs(self._init_pos - han[0][0]) / han[0][1]
            pos0 = abs(self._init_pos - han[0][0])
            sigma = abs(event.xdata - han[0][0]) / self._moveratio
            self._move_sigma(han, sigma)

    def show_toolbar(self, state):
        '''Activate or disable the toolbar display in the widget'''
        toolbar = self.findChild(QtGui.QToolBar)
        if state:
            toolbar.show()
        else:
            toolbar.hide()

    def set_editable(self, state=True):
        '''When editable, the gray and white peaks characteristics can be
        changed interactively: the user can drag the peak to move its position,
        or its standard deviation.
        '''
        self.editable = state
        if state:
            # set picker callback and activate interactive objects
            tolerance = 3.  # could become configurable.
            # tolerence seems to work only on line artists anyway.
            for p in self._plots[0]:
                if p is not None:
                    p.set_picker(tolerance)
            for p in self._plots[1]:
                if p is not None:
                    p.set_picker(tolerance)
            if self._pick is None:
                self._pick = self.mfig.canvas.mpl_connect('pick_event',
                                                          self._his_mouse_press)
            toolbar = self.findChild(QtGui.QToolBar)
            forcemode = (toolbar._active is not None)
        else:
            # unset picker callback and activate interactive objects
            for p in self._plots[0]:
                if p is not None:
                    p.set_picker(False)
            for p in self._plots[1]:
                if p is not None:
                    p.set_picker(False)
            self.mfig.canvas.mpl_disconnect(self._pick)
            self._pick = None
            toolbar = self.findChild(QtGui.QToolBar)
            forcemode = (toolbar._active != 'PAN')
        if forcemode:
            toolbar.pan()


def load_histo_analysis(hanfile):
    '''parse histo analysis file (.han) to extract gray and white mean/std.
    Returns a tuple in the following shape:
    ( ( gray_mean, gray_stdev ), ( white_mean, white_stdev ) )
    '''
    r = re.compile('^.*mean:\s*(-?[0-9]+(\.[0-9]*)?)\s*sigma:\s'
                   '(-?[0-9]+(\.[0-9]*)?)\s*$')
    gmean, gsigma, wmean, wsigma = None, None, None, None
    for l in open(hanfile).xreadlines():
        l = l.strip()
        if l.startswith('gray:'):
            m = r.match(l)
            if m:
                gmean = float(m.group(1))
                gsigma = float(m.group(3))
        elif l.startswith('white:'):
            m = r.match(l)
            if m:
                wmean = float(m.group(1))
                wsigma = float(m.group(3))
    return [gmean, gsigma], [wmean, wsigma]


def save_back_histo_analysis(hanfile, han):
    '''parse an existing histo analysis file (.han) and save back gray and
    white mean/std.
    Saves a backup file .han~
    '''
    lines = []
    try:
        hanf = open(hanfile)
    except IOError:
        hanf = None
    if hanf:
        for l in hanf.xreadlines():
            l = l.strip()
            if l.startswith('gray:'):
                lines.append('gray: mean: %d sigma: %d' %
                            (int(round(han[0][0])), int(round(han[0][1]))))
            elif l.startswith('white:'):
                lines.append('white: mean: %d sigma: %d' %
                            (int(round(han[1][0])), int(round(han[1][1]))))
            else:
                lines.append(l)
        os.rename(hanfile, hanfile + '~')
        hanf.close()
    else:
        lines = ['sequence: unknown',
                 'csf: mean: -1 sigma: -1',
                 'gray: mean: %d sigma: %d'
                 % (int(round(han[0][0])), int(round(han[0][1]))),
                 'white: mean: %d sigma: %d'
                 % (int(round(han[1][0])), int(round(han[1][1]))),
                 'candidate 0: mean: -1 sigma: -1',
                 'candidate 1: mean: -1 sigma: -1',
                 'candidate 2: mean: -1 sigma: -1',
                 'candidate 3: mean: -1 sigma: -1',
                 'candidate 4: mean: -1 sigma: -1',
                 'candidate 5: mean: -1 sigma: -1',
                 'undersampling: 8']
    f = open(hanfile, 'w')
    for l in lines:
        f.write(l + '\n')


def load_histo_data(hanfile, hisfile=None):
    '''load histogram (.his) and histo analysis (.han) data in a
    HistoData object. If hisfile is not provided, it is deduced from hanfile.
    '''
    han = load_histo_analysis(hanfile)
    if hisfile is None:
        hisfile = hanfile[: -3] + 'his'
    if os.path.exists(hisfile):
        data = numpy.loadtxt(hisfile, dtype=int)
    else:
        # poor fix
        data = numpy.array([[0, 1], [1, 1]], dtype=int)
    return HistoData(hisfile, hanfile, data, han)


def create_histo_view(parent=None):
    '''Instantiate a HistoAnalysisWidget and set it in its parent'''
    his_widget = HistoAnalysisWidget(parent)
    if parent is not None:
        parent.layout().addWidget(his_widget)
    return his_widget


if __name__ == '__main__':
    import sys
    # import os

    hanfile = '/volatile/riviere/basetests-3.1.0/subjects/sujet01/t1mri/default_acquisition/default_analysis/nobias_sujet01.han'
    # hanfile = os.path.join( os.getenv( 'HOME' ),
        #'data/baseessai/subjects/subject01/t1mri/default_acquisition/default_analysis/nobias_subject01.han' )

    # load histogram data
    histo_data = load_histo_data(hanfile)
    app = None
    if QtGui.QApplication.instance() is None:
        app = QtGui.QApplication(sys.argv)
    # histo analysis widget
    win = HistoAnalysisWidget()
    win.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    win.set_histo_data(histo_data, nbins=100)
    win.set_editable(True)
    win.draw_histo()
    win.show()

    # run Qt loop
    if app:
        app.exec_()

    print('current histo analysis is:')
    print(win.histodata.han)
