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
from brainvisa import anatomist
import numpy

try:
    from morphologist.gui import histo_analysis_widget
except:
    pass

def validation():
    anatomist.validation()
    try:
        import morphologist.gui.histo_analysis_widget
    except:
        raise ValidationError( 'morphologist.gui.histo_analysis_widget ' \
            'module cannot be imported' )

name = 'Edit histo analysis'
userLevel = 0
roles = ( 'editor', )

signature = Signature(
    'histo_analysis', ReadDiskItem( 'Histo analysis', 'Histo Analysis' ),
    'histo', ReadDiskItem( 'Histogram', 'Histogram' ),
    'mri_corrected', ReadDiskItem( 'T1 MRI bias corrected',
        'Anatomist volume formats' ),
)


def initialization( self ):
    self.linkParameters( 'histo', 'histo_analysis' )
    self.linkParameters( 'mri_corrected', 'histo_analysis' )


class HistoAnalysisEditorWidget( QDialog ):

    def __init__( self, hdata, mri_corrected=None, parent=None ):
        '''Histo analysis editor dialog. Provides histo and G/W matters
        ranges view (HistoAnalysisWidget), an Anatomist view of the MRI data
        with color overlays, and interactive modification of G/W matters
        ranges is supported. Editable text boxes also represent the analysis.
        '''
        QDialog.__init__( self, parent )
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

        # FIXME: temporary
        #reload( histo_analysis_widget )

        vlay = QVBoxLayout( self )
        fwid = QWidget( self )
        vlay.addWidget( fwid )
        flay = QHBoxLayout( fwid )
        lwid = QWidget( fwid )
        flay.addWidget( lwid )
        llay = QVBoxLayout( lwid )
        self.hwid = histo_analysis_widget.HistoAnalysisWidget( lwid )
        self.hwid.set_histo_data( hdata )
        self.hwid.enable_modifications( True )
        self.hwid.draw_histo()
        llay.addWidget( self.hwid )

        self._insert_text_edtors( lwid )

        if mri_corrected is not None:
            self._insert_ana_window( fwid )
            self.hwid.histo_analysis_changed.connect( self.update_palette )

        hb = QWidget( self )
        vlay.addWidget( hb )
        hlay = QHBoxLayout( hb )
        okb = QPushButton( 'Save && exit', hb )
        rsb = QPushButton( 'Restore saved values', hb )
        ccb = QPushButton( 'Cancel', hb )
        hlay.addWidget( okb )
        hlay.addWidget( rsb )
        hlay.addWidget( ccb )
        okb.pressed.connect( self.done_accept )
        rsb.pressed.connect( self.restore_saved_han )
        ccb.pressed.connect( self.reject )
        # prevent auto-buttons from inappropriately closing the dialog
        okb.setAutoDefault( False )
        okb.setDefault( False )
        rsb.setAutoDefault( False )
        rsb.setDefault( False )
        ccb.setAutoDefault( False )
        ccb.setDefault( False )

    def __del__( self ):
        del self._fusion2d
        del self._color_mri
        del self._mri_corrected
        a = anatomist.Anatomist()
        # remove the custom palette from the global list
        a.palettes().erase( self._palette.getInternalRep() )

    def _make_palette_colors( self ):
        '''Recompute the color overlays palette after histo analysis change'''
        ncolors = 200 # num of colors in the palette
        nstd = 3 # num of stdev displayed as light color
        han = self.hwid.histodata.han
        hmax = max( ( han[0][0] + han[0][1] ), ( han[1][0] + han[1][1] ) ) \
            * 1.3
        factor = ncolors / ( hmax + 1. )
        l = [ int( round( ( han[0][0] - nstd * han[0][1] ) * factor ) ),
              int( round( ( han[0][0] + nstd * han[0][1] ) * factor ) ) + 1,
              int( round( ( han[0][0] - han[0][1] ) * factor ) ),
              int( round( ( han[0][0] + han[0][1] ) * factor ) ) + 1 ]
        l[0] = max( 0, l[0] )
        l[2] = max( 0, l[2] )
        l[1] = min( ncolors, l[1] )
        l[3] = min( ncolors, l[3] )
        empty = ( 0, 0, 0 )
        red = ( 255, 0, 0 )
        lightred = ( 255, 150, 150 )
        lightgreen = numpy.array( ( 150, 255, 150 ) )
        green = numpy.array( ( 0, 255, 0 ) )
        # different colors for overlaps
        lightyellow = ( 255, 255, 150 )
        yellow = ( 255, 255, 0 )
        orange = ( 255, 150, 0 )
        grnred = ( 150, 255, 0 )
        pal = numpy.zeros( ( ncolors, 3 ), dtype=int )
        pal[ l[0] : l[1] ] = lightred
        pal[ l[2] : l[3] ] = red
        l = [ int( round( ( han[1][0] - nstd * han[1][1] ) * factor ) ),
              int( round( ( han[1][0] + nstd * han[1][1] ) * factor ) ) + 1,
              int( round( ( han[1][0] - han[1][1] ) * factor ) ),
              int( round( ( han[1][0] + han[1][1] ) * factor ) ) + 1 ]
        l[0] = max( 0, l[0] )
        l[2] = max( 0, l[2] )
        l[1] = min( ncolors, l[1] )
        l[3] = min( ncolors, l[3] )
        p = pal[ l[0] : l[2] ]
        p[ numpy.all( p==red, axis=1 ) ] = orange
        p[ numpy.all( p==lightred, axis=1 ) ] = lightyellow
        p[ numpy.all( p==empty, axis=1 ) ] = lightgreen
        p = pal[ l[3] : l[1] ]
        p[ numpy.all( p==red, axis=1 ) ] = orange
        p[ numpy.all( p==lightred, axis=1 ) ] = lightyellow
        p[ numpy.all( p==empty, axis=1 ) ] = lightgreen
        p = pal[ l[2] : l[3] ]
        p[ numpy.all( p==red, axis=1 ) ] = yellow
        p[ numpy.all( p==lightred, axis=1 ) ] = grnred
        p[ numpy.all( p==empty, axis=1 ) ] = green
        # force last color to be black
        pal[ -1, : ] = 0
        self._palette.setColors( numpy.ravel( pal ) )
        maxVal = hmax / self._tex_max
        self._color_mri.setPalette( palette=self._palette, minVal=0,
            maxVal=maxVal )

    def _insert_ana_window( self, fwid ):
        '''Builds the Anatomist axial view with color overlays. A slider
        allows to change the overlay mixing rate.s
        '''
        wid = QWidget( fwid )
        fwid.layout().addWidget( wid )
        lay = QVBoxLayout( wid )
        a = anatomist.Anatomist()
        awin = a.createWindow( 'Axial' )
        awin.setParent( wid )
        lay.addWidget( awin.getInternalRep() )
        self._mri_corrected = a.loadObject( self._mri_corrected_diskitem,
            duplicate=True )
        self._color_mri = a.duplicateObject( self._mri_corrected )
        awin.setReferential( self._mri_corrected.referential )
        # avoid referential button to become the default button in dialog
        rbut = awin.findChildren( QPushButton )
        for but in rbut:
            but.setAutoDefault( False )
            but.setDefault( False )
        self._palette = a.createPalette( 'histo_analysis' )
        self._tex_max = \
            self._mri_corrected.getInfos()[ 'texture' ][ 'textureMax' ]
        self._make_palette_colors()
        fusion = a.fusionObjects( [ self._mri_corrected, self._color_mri ],
            method='Fusion2DMethod' )
        awin.addObjects( fusion )
        a.execute( 'TexturingParams', objects=[fusion], texture_index=1,
            mode='linear_A_if_B_black', rate=0.5 )
        bb = self._mri_corrected.boundingbox()
        p = ( bb[0] + bb[1] ) / 2
        awin.SetPosition( p, awin.getReferential() )
        self._fusion2d = fusion
        # color slider
        bwid = QWidget( wid )
        lay.addWidget( bwid )
        hlay = QHBoxLayout( bwid )
        hlay.addWidget( QLabel( 'Color:', bwid ) )
        self._color_slider = QSlider( Qt.Horizontal, bwid )
        hlay.addWidget( self._color_slider )
        self._color_slider.setRange( 0, 100 )
        self._color_slider.setSliderPosition( 50 )
        self._color_slider.valueChanged.connect( self._color_mixing_changed )
        self._color_label = QLabel( '100', bwid )
        hlay.addWidget( self._color_label )
        self._color_label.setFixedWidth( self._color_label.sizeHint().width() )
        self._color_label.setText( '50' )

    def _insert_text_edtors( self, lwid ):
        '''Text displays and edition of G/W peaks and stdev'''
        lbwid = QWidget( lwid )
        lwid.layout().addWidget( lbwid )
        glay = QGridLayout( lbwid )
        glay.addWidget( QLabel( 'Gray peak:', lbwid ), 0, 0 )
        self._gmedit = QLineEdit( lbwid )
        glay.addWidget( self._gmedit, 0, 1 )
        glay.addWidget( QLabel( 'std:', lbwid ), 0, 2 )
        self._gsedit = QLineEdit( lbwid )
        glay.addWidget( self._gsedit, 0, 3 )
        glay.addWidget( QLabel( 'White peak:', lbwid ), 1, 0 )
        self._wmedit = QLineEdit( lbwid )
        glay.addWidget( self._wmedit, 1, 1 )
        glay.addWidget( QLabel( 'std:', lbwid ), 1, 2 )
        self._wsedit = QLineEdit( lbwid )
        glay.addWidget( self._wsedit, 1, 3 )
        self._gmedit.setValidator(
            QDoubleValidator( 0, 1e6, 1, self._gmedit ) )
        self._gsedit.setValidator(
            QDoubleValidator( 0, 1e6, 1, self._gsedit ) )
        self._wmedit.setValidator(
            QDoubleValidator( 0, 1e6, 1, self._wmedit ) )
        self._wsedit.setValidator(
            QDoubleValidator( 0, 1e6, 1, self._wsedit ) )
        self.update_text_values()
        self._gmedit.editingFinished.connect( self._text_edited )
        self._gsedit.editingFinished.connect( self._text_edited )
        self._wmedit.editingFinished.connect( self._text_edited )
        self._wsedit.editingFinished.connect( self._text_edited )

    def update_text_values( self ):
        '''Fills the histo analysis values in text boxes'''
        han = self.hwid.histodata.han
        self._gmedit.blockSignals( True )
        self._gsedit.blockSignals( True )
        self._wmedit.blockSignals( True )
        self._wsedit.blockSignals( True )
        self._gmedit.setText( '%.1f' % han[0][0] )
        self._gsedit.setText( '%.1f' % han[0][1] )
        self._wmedit.setText( '%.1f' % han[1][0] )
        self._wsedit.setText( '%.1f' % han[1][1] )
        self._gmedit.blockSignals( False )
        self._gsedit.blockSignals( False )
        self._wmedit.blockSignals( False )
        self._wsedit.blockSignals( False )

    def update_palette( self, gmean=None, gstd=None, wmean=None, wstd=None ):
        '''Updates views when histo analysis values have changed after manual
        modification on the histo view.
        '''
        self._make_palette_colors()
        self.update_text_values()

    def done_accept( self ):
        '''Save the new analysis and quit the edition dialog'''
        hdata = self.hwid.histodata
        histo_analysis_widget.save_back_histo_analysis(
            hdata.han_filename, hdata.han )
        self.accept()

    def restore_saved_han( self ):
        '''Reload .han file and update the view accordingly'''
        han = histo_analysis_widget.load_histo_analysis(
            self.hwid.histodata.han_filename )
        # set individually because we may already be in a hwid callback
        # which holds references to the internal han
        self.hwid.histodata.han[0][0] = han[0][0]
        self.hwid.histodata.han[0][1] = han[0][1]
        self.hwid.histodata.han[1][0] = han[1][0]
        self.hwid.histodata.han[1][1] = han[1][1]
        self.hwid.redraw_histo_analysis()
        self.update_palette()

    def _text_edited( self ):
        '''Update views after manual edition of text boxes'''
        han = ( ( float( self._gmedit.text() ), float( self._gsedit.text() ) ),
            ( float( self._wmedit.text() ), float( self._wsedit.text() ) ) )
        # set individually because we may already be in a hwid callback
        # which holds references to the internal han
        self.hwid.histodata.han[0][0] = han[0][0]
        self.hwid.histodata.han[0][1] = han[0][1]
        self.hwid.histodata.han[1][0] = han[1][0]
        self.hwid.histodata.han[1][1] = han[1][1]
        self.hwid.redraw_histo_analysis()
        self.update_palette()

    def _color_mixing_changed( self, value ):
        '''Update anatomist view after overlay colors mixing rate has changed.
        '''
        self._color_label.setText( str( value ) )
        a = anatomist.Anatomist()
        a.execute( 'TexturingParams', objects=[self._fusion2d],
            texture_index=1, rate=1.-value*0.01 )


def create_histo_widget( self, hdata, mri_corrected ):
    wid = HistoAnalysisEditorWidget( hdata, mri_corrected )
    wid.setAttribute( QtCore.Qt.WA_DeleteOnClose )
    wid.show()
    return wid

def delInMainThread( lock, thing ):
    # wait for the lock to be released in the process thread
    lock.acquire()
    lock.release()
    # now the process thread should have removed its reference on thing:
    # we can safely delete it fom here, in the main thread.
    del thing # probably useless

def execution( self, context ):
    hdata = histo_analysis_widget.load_histo_data(
        self.histo_analysis.fullPath(), self.histo.fullPath() )
    hwid = mainThreadActions().call( self.create_histo_widget, hdata,
        self.mri_corrected )
    try:
        mainThreadActions().call( hwid.exec_ )
    finally:
        # the following ensures pv is deleted in the main thread, and not
        # in the current non-GUI thread. The principle is the following:
        # - acquire a lock
        # - pass the pv object to something in the main thread
        # - the main thread waits on the lock while holding a reference on pv
        # - we delete pv in the process thread
        # - the lock is releasd from the pv thread
        # - now the main thread can go on, and del / release the ref on pv: it
        #   is the last ref on pv, so it is actually deleted there.
        lock = threading.Lock()
        lock.acquire()
        mainThreadActions().push( delInMainThread, lock, hwid )
        del hwid
        lock.release()

