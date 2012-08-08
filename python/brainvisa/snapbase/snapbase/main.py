# -*- coding: utf-8 -*-
import os, sys
if not sys.modules.has_key('brainvisa.axon'):
    from brainvisa import axon
    axon.initializeProcesses()

from brainvisa.data import neuroHierarchy
from brainvisa.configuration import neuroConfig

from PyQt4 import QtGui, Qt, QtCore

main_window = None
qt_app = None
database = None
preferences = {}

# Display help message box
class HelpWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setModal(True)

    def setupUi(self, parent):
        self.setObjectName('helpbox')
        self.setWindowTitle('SnapBase v0.2 introduction')
        self.resize(348, 571)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        help_file = '%s/doc/index.html'%os.path.split(__file__)[0]
        from PyQt4 import QtWebKit
        self.qte2 = QtWebKit.QWebView(self)
        self.qte2.load(Qt.QUrl(help_file))
        self.qte = QtGui.QPushButton("bonjour", self)
        self.qte.setMinimumSize(QtCore.QSize(200,31))
        self.setMinimumSize(QtCore.QSize(200,31))
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.qte)


def display_help_msgbox():
    global gui, main_window
    #gui.helpbox.parent.setEnabled(False)
    gui.helpbox = HelpWindow(main_window)
    gui.helpbox.setupUi(main_window)
    gui.helpbox.show()

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

def brainmask_snap_base():
    global main_window, qt_app, database, preferences
    from examples import splitbrain
    snap = splitbrain.BrainMaskSnapBase(preferences)
    snap.snap_base(database, main_window = main_window, qt_app = qt_app )

def comparison_snap_base():
    global main_window, qt_app, database, preferences
    from examples import splitbrain
    compar_type, ok = Qt.QInputDialog.getItem(None,
            'which segmentation ?',
            'select grey matter / white matter / brain mask',
            ['Grey matter', 'White matter', 'Brain mask'],
            0, False)
    if ok:
        item, ok = Qt.QInputDialog.getItem(None,
                'Which database',
                'which db',
                neuroHierarchy.databases._databases.keys(), 0, False)
        if ok and item != database.directory:
            preferences['T1 db'] = item
            preferences['comparison type'] = compar_type
            snap = splitbrain.SPMComparisonSnapBase(preferences)
            snap.snap_base(database, main_window = main_window, qt_app = qt_app )

def raw_snap_base():
    global main_window, qt_app, database, preferences
    from examples import raw
    snap = raw.RawSnapBase(preferences)
    snap.snap_base(database, main_window = main_window, qt_app = qt_app )

def tablet_snap_base():
    global main_window, qt_app, database, preferences
    from examples import raw
    snap = raw.TabletSnapBase(preferences)
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

def thickness_snap_base():
    global main_window, qt_app, database, preferences
    from examples import mesh

    side, ok = Qt.QInputDialog.getItem(None,
            'Which hemisphere',
            'Left of right hemisphere',
            ['left','right'], 0, False)
    if ok:
        mesh_choice, ok_mesh = Qt.QInputDialog.getItem(None,
                'Which mesh',
                'Hemi or white',
                ['hemi', 'white'], 0, False)
        if ok_mesh:
            if side == 'left':
                if mesh_choice == 'hemi':
                    snap = mesh.LeftHemiThicknessSnapBase(preferences)
                elif mesh_choice == 'white':
                    snap = mesh.LeftWhiteThicknessSnapBase(preferences)
            elif side == 'right':
                if mesh_choice == 'hemi':
                    snap = mesh.RightHemiThicknessSnapBase(preferences)
                elif mesh_choice == 'white':
                    snap = mesh.RightWhiteThicknessSnapBase(preferences)
    if ok and ok_mesh:
        snap.snap_base(database, main_window = main_window, qt_app = qt_app )

def sulci_snap_base():
    global main_window, qt_app, database, preferences
    from examples import sulci
    choice, ok_choice = Qt.QInputDialog.getItem(None,
        'single or multi view ?', 'single/multi',
        ['single', 'multi'], 0, False)
    if ok_choice:

        item, ok = Qt.QInputDialog.getItem(None,
                'Which hemisphere',
                'Left of right hemisphere',
                ['left','right'], 0, False)
        if ok:
            if item == 'left':
                if choice == 'multi':
                    snap = sulci.LeftSulciMultiViewSnapBase(preferences)
                elif choice == 'single':
                    snap = sulci.LeftSulciSingleViewSnapBase(preferences)
            elif item == 'right':
                if choice == 'multi':
                    snap = sulci.RightSulciMultiViewSnapBase(preferences)
                elif choice == 'single':
                    snap = sulci.RightSulciSingleViewSnapBase(preferences)
    if ok and ok_choice:
        snap.snap_base(database, main_window = main_window, qt_app = qt_app )

# Fiber Bundles (work in progress)

def fibers_snap_base():
    global main_window, qt_app, database, preferences
    from examples import fibers
    snap = fibers.FibersSnapBase(preferences)
    snap.snap_base(database, main_window = main_window, qt_app = qt_app )

# Various functions

def select_db(item, verbose=True):
    '''
    Setup the global variable database according to the selected item in
    the combobox.

    '''

    global database, preferences
    database = neuroHierarchy.databases._databases.items()[item][1]
    preferences['database_dir'] = database.directory
    print 'saving preferences'
    save_preferences(preferences)
    if not verbose:
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
    default_pref = {'output_path' : '/tmp/',
                    'filename_root' : 'snapshots_',
                    'database_dir' : '',
                    'create_poster' : False,
                    'create_poster_command' : 'montage -geometry +0+0 -background black -tile 10',
                    'remove_snapshots' : False,
                    'default_attributes' : ['subject', 'protocol', 'acquisition'],
                    'required_attributes' : {'graph_version' : '3.1'},
                    'display_success_msgbox' : False}
    for each in default_pref.keys():
        if minf_dict.has_key(each):
            preferences[each] = minf_dict[each]
        else:
            preferences[each] = default_pref[each]

    return preferences


def main():

    global main_window, gui, qt_app, database, preferences
    import interface, sys

    # Create Qt App and window
    qt_app = Qt.QApplication( sys.argv )
    qt_app.setQuitOnLastWindowClosed(True)
    main_window = QtGui.QMainWindow()
    gui = interface.Ui_main_window()
    gui.setupUi(main_window)

    # Connecting Qt Signals
    gui.greywhite_btn.clicked.connect(grey_white_snap_base)
    gui.whitemesh_btn.clicked.connect(white_mesh_snap_base)
    gui.hemimesh_btn.clicked.connect(hemi_snap_base)
    gui.splitbrain_btn.clicked.connect(splitbrain_snap_base)
    gui.sulci_btn.clicked.connect(sulci_snap_base)
    gui.raw_btn.clicked.connect(raw_snap_base)
    gui.fibers_btn.clicked.connect(fibers_snap_base)
    gui.comparison_btn.clicked.connect(comparison_snap_base)
    gui.tablet_btn.clicked.connect(tablet_snap_base)
    gui.brainmask_btn.clicked.connect(brainmask_snap_base)
    gui.btn_thickness.clicked.connect(thickness_snap_base)
    gui.btn_help.clicked.connect(display_help_msgbox)
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
    else:
        # Otherwise, create it and update all necessary
        preferences = load_preferences({})
        select_db(0)
        preferences['database_dir'] = database.directory
        save_preferences(preferences)
        msgBox = Qt.QMessageBox.information(None, 'SnapBase settings file created',
            'Settings will be stored in %s.\nSnapshots will be saved as %s<subject>_<view>.png. It can be edited in the settings file.'%(snapbase_settings_file, preferences['output_path']), Qt.QMessageBox.Ok)

    gui.set_default_status_msg('output path : %s'%preferences['output_path'])
    main_window.show()
    qt_app.exec_()
    neuroHierarchy.databases.currentThreadCleanup()
    qt_app = None
    QtGui.qApp = None
