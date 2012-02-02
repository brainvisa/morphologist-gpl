
from brainvisa import axon
axon.initializeProcesses()

import neuroHierarchy
import neuroConfig


from PyQt4 import QtGui, Qt, QtCore
import sys

main_window = None
qt_app = None
database = None
preferences = {}


# Inheriting QMainWindow to implement closeEvent

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)

    def closeEvent(self, event):
        print 'closing everything'
        neuroHierarchy.databases.currentThreadCleanup()
        print 'saving preferences'
        save_preferences(preferences)
        sys.exit(0)


# Voxel-based data (without choice of hemisphere side)

def grey_white_snap_base():
    global main_window, qt_app, database, preferences
    from examples import greywhite
    snap = greywhite.GreyWhiteSnapBase(preferences)
    snap.snap_base(database, main_window = main_window, qt_app = qt_app )

def splitbrain_snap_base():
    global main_window, qt_app, database, preferences
    from examples import splitbrain
    snap = splitbrain.SplitBrainSnapBase(preferences)
    snap.snap_base(database, main_window = main_window, qt_app = qt_app )


# Mesh-based data (with choice of hemisphere side)

def white_mesh_snap_base():
    global main_window, qt_app, database, preferences
    from examples import mesh

    item, ok = Qt.QInputDialog.getItem(None,
            'Which hemisphere',
            'Left of right hemisphere',
            ['left','right'], 0, False)
    if ok:
        if item == 'left':
            snap = mesh.LeftWhiteMeshSnapBase(preferences)
        elif item == 'right':
            snap = mesh.RightWhiteMeshSnapBase(preferences)
        snap.snap_base(database, main_window = main_window, qt_app = qt_app )

def hemi_snap_base():
    global main_window, qt_app, database, preferences
    from examples import mesh

    item, ok = Qt.QInputDialog.getItem(None,
            'Which hemisphere',
            'Left of right hemisphere',
            ['left','right'], 0, False)
    if ok:
        if item == 'left':
            snap = mesh.LeftHemisphereMeshSnapBase(preferences)
        elif item == 'right':
            snap = mesh.RightHemisphereMeshSnapBase(preferences)
        snap.snap_base(database, main_window = main_window, qt_app = qt_app )

def sulci_snap_base():
    global main_window, qt_app, database, preferences
    from examples import sulci
    item, ok = Qt.QInputDialog.getItem(None,
            'Which hemisphere',
            'Left of right hemisphere',
            ['left','right'], 0, False)
    if ok:
        if item == 'left':
            preferences['side'] = 'left'
            snap = sulci.LeftSulciSnapBase(preferences)
        elif item == 'right':
            preferences['side'] = 'right'
            snap = sulci.RightSulciSnapBase(preferences)
    snap.snap_base(database, main_window = main_window, qt_app = qt_app )


# Various functions

def select_db(item):
    '''
    Setup the global variable database according to the selected item in
    the combobox.

    '''

    global database, preferences
    database = neuroHierarchy.databases._databases.items()[item][1]
    preferences['database_dir'] = database.directory
    msgBox = Qt.QMessageBox.information(None, 'Database selected',
        'Snapshots will be generated from the following database.\n%s'%database.directory, Qt.QMessageBox.Ok)


def save_preferences(pref):
    ''' Save preferences in $HOME/.brainvisa/snapbase_settings.minf '''

    import os
    from soma.minf import api as minf
    snapbase_settings_file = os.path.join(neuroConfig.homeBrainVISADir, 'snapbase_settings.minf')
    minf.writeMinf(snapbase_settings_file, (pref,))


def load_preferences(minf_dict):
    ''' Returns a directory built from .minf settings file '''

    preferences = {}
    default_pref = {'output_path' : '/tmp/snapshots',
                    'database_dir' : '',
                    'create_poster' : False,
                    'create_poster_command' : 'montage -geometry +0+0 -background black -tile 10',
                    'remove_snapshots' : False}
    for each in default_pref.keys():
        if minf_dict.has_key(each):
            preferences[each] = minf_dict[each]
        else:
            preferences[each] = default_pref[each]

    return preferences


def main():

    global main_window, qt_app, database, preferences
    from interface import *

    # Create Qt App and window
    qt_app = Qt.QApplication( sys.argv )
    qt_app.setQuitOnLastWindowClosed(True)
    main_window = MainWindow()
    gui = Ui_main_window()
    gui.setupUi(main_window)

    # Connecting Qt Signals
    gui.greywhite_btn.clicked.connect(grey_white_snap_base)
    gui.whitemesh_btn.clicked.connect(white_mesh_snap_base)
    gui.hemimesh_btn.clicked.connect(hemi_snap_base)
    gui.splitbrain_btn.clicked.connect(splitbrain_snap_base)
    gui.sulci_btn.clicked.connect(sulci_snap_base)
    gui.db_combobox.activated.connect(select_db)
    gui.connect_signals()

    # Initializes the combobox with databases
    for db in neuroHierarchy.databases.iterDatabases():
        gui.db_combobox.addItem(db.directory)

    # SnapBase settings
    import os
    from soma.minf import api as minf
    snapbase_settings_file = os.path.join(neuroConfig.homeBrainVISADir, 'snapbase_settings.minf')
    if os.path.exists(snapbase_settings_file):
        # If settings file exists, load it
        minf_dict = minf.readMinf(snapbase_settings_file)
        print minf_dict
        preferences = load_preferences(minf_dict[0])
        # Update combobox (same as select_db without confirmation popup)
        try:
            database = neuroHierarchy.databases._databases[preferences['database_dir']]
        except KeyError:
            if len(neuroHierarchy.databases._databases.items()) > 0:
                preferences['database_dir'], database = neuroHierarchy.databases._databases.items()[0]
            else:
                ok = Qt.QMessageBox.warning(None, 'No databases in BrainVisa.',
                'Please add at least one database in BrainVisa.', Qt.QMessageBox.Ok)
        item = gui.db_combobox.findText(preferences['database_dir'])
        gui.db_combobox.setCurrentIndex(item)
        gui.statusbar.showMessage('output_path = %s'%preferences['output_path'])
    else:
        # Otherwise, create it and update all necessary
        preferences = load_preferences({})
        select_db(0)
        preferences['database_dir'] = database.directory
        save_preferences(preferences)
        msgBox = Qt.QMessageBox.information(None, 'SnapBase settings file created',
            'Settings will be stored in %s.\nSnapshots will be saved as %s<subject>_<view>.png. It can be edited in the settings file.'%(snapbase_settings_file, preferences['output_path']), Qt.QMessageBox.Ok)

    main_window.show()
    qt_app.exec_()
    neuroHierarchy.databases.currentThreadCleanup()
