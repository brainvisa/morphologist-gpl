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
from brainvisa.configuration import neuroConfig
from brainvisa import anatomist
import numpy

if neuroConfig.gui:
    try:
        from brainvisa.morphologist.qt4gui import histo_analysis_editor
        # patch to use brainvisa.anatomist instead of the core anatomist
        histo_analysis_editor.anatomist = anatomist
        from brainvisa.morphologist.qt4gui.histo_analysis_editor \
            import create_histo_editor
        from brainvisa.morphologist.qt4gui.histo_analysis_widget \
            import load_histo_data
    except ImportError:
        pass

def validation():
    if not neuroConfig.gui:
        raise ValidationError( 'No GUI.' )
    anatomist.validation()
    try:
        import brainvisa.morphologist.qt4gui.histo_analysis_editor
    except:
        raise ValidationError(
            'brainvisa.morphologist.qt4gui.histo_analysis_editor ' \
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


def delInMainThread( lock, thing ):
    # wait for the lock to be released in the process thread
    lock.acquire()
    lock.release()
    # now the process thread should have removed its reference on thing:
    # we can safely delete it fom here, in the main thread.
    del thing # probably useless

def execution( self, context ):
    hdata = load_histo_data( self.histo_analysis.fullPath(),
        self.histo.fullPath() )
    hwid = mainThreadActions().call( create_histo_editor, hdata,
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

