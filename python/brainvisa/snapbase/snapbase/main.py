# -*- coding: utf-8 -*-
import os, sys

from brainvisa.data import neuroHierarchy
from brainvisa.configuration import neuroConfig
#from brainvisa.data.sqlFSODatabase import SQLDatabase as SQLdb
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
        self.setWindowTitle('SnapBase v0.3 introduction')
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
        self.setMinimumSize(QtCore.QSize(200,231))
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.qte2)


def display_help_msgbox():
    global gui, main_window
    gui.helpbox = HelpWindow(main_window)
    gui.helpbox.setupUi(main_window)
    gui.helpbox.show()


# Fiber Bundles (work in progress)

def fibers_snap_base():
    global main_window, qt_app, database, preferences
    from examples import fibers
    snap = fibers.FibersSnapBase(preferences)
    snap.snap_base(main_window = main_window, qt_app = qt_app )


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
                    'create_poster' : False,
                    # 'create_poster_command' : 'montage -geometry +0+0 -background black -tile 10',
                    'create_poster_command' : 'python -m brainvisa.snapbase.snapbase.poster',
                    'remove_snapshots' : False,
                    'default_attributes' : ['subject', 'protocol', 'acquisition'],
                    'required_attributes' : {'graph_version' : '3.1'},
                    'naming_attributes' : ['subject', 'protocol', 'acquisition'],
                    'output_naming_template': "'%s_%s_%s'%(subject, protocol, acquisition)",
                    'display_success_msgbox' : False,
                    'display_fusion_on_meshcut': True,
                    'render_subjects_id': True}
    for each in default_pref.keys():
        if minf_dict.has_key(each):
            preferences[each] = minf_dict[each]
        else:
            preferences[each] = default_pref[each]

    return preferences

def set_output_path(event):
    global preferences, gui
    import os
    if os.path.exists(preferences['output_path']):
       pix_dir = preferences['output_path']
    else:
       pix_dir = os.path.expanduser('~')
    destDir = QtGui.QFileDialog.getExistingDirectory(None,
      'Open working directory',
      pix_dir,
      QtGui.QFileDialog.ShowDirsOnly)
    if destDir != '':
       preferences['output_path'] = destDir
       save_preferences(preferences)
       gui.set_default_status_msg('output path : %s'%preferences['output_path'])
       gui.statusbar.showMessage(gui.statusbar.default_status_msg)
       gui.statusbar.setToolTip(gui.statusbar.default_status_msg)

def set_settings(event):
   global preferences
   print 'set_settings'
   from PyQt4 import QtGui, QtCore, Qt
   from brainvisa.snapbase.snapbase.interface import Ui_settings_window
   window = QtGui.QDialog()
   s = Ui_settings_window()
   s.setupUi(window, items=preferences, exclude_items=['output_path', 'naming_attributes', 'required_attributes', 'default_attributes'])
   res = s.window.exec_()
   if res == QtGui.QDialog.Accepted:
      options = s.get_results()
      print options
      preferences.update(options)
      save_preferences(preferences)


def list_snap_modules():
   import inspect, imp, os, string
   direc = os.path.join(os.path.split(__file__)[0], 'examples')
   print direc
   snap_files = [each for each in os.listdir(direc) if os.path.isfile(os.path.join(direc, each)) and os.path.splitext(each)[1] == '.py']
   print snap_files
   modules = []
   classes = []
   root_module = ['brainvisa','snapbase','snapbase']
   root_module = string.join(root_module, '.')
   for snap_file in snap_files:
      print snap_file
      name = string.join([root_module, os.path.splitext(os.path.split(snap_file)[1])[0]], '.')
      print name
      m = imp.load_source(name, os.path.join(direc, snap_file))
      print m
      modules.append(m)
   return modules

def list_snap_classes(modules):
   import inspect
   classes = {}
   for m in modules:
      c = inspect.getmembers(m, inspect.isclass)
      for name, cla in c:
         if name.count('SnapBase') > 0:
            classes[name] = cla
   return classes

def on_finished():
   pass

class MainWindow(QtGui.QMainWindow):
   def __init__(self, parent = None):
      QtGui.QMainWindow.__init__(self, parent)

   def closeEvent(self, event):
      import sys
      neuroHierarchy.databases.currentThreadCleanup()
      sys.exit(0)

def main():

    global main_window, gui, qt_app, database, preferences
    import interface, sys
    old_interface = None
    # Create Qt App and window
    qt_app = Qt.QApplication( sys.argv )
    qt_app.setQuitOnLastWindowClosed(True)
    main_window = MainWindow()
    gui = interface.Ui_main_window()
    gui.setupUi(main_window)
    gui.fileopen.clicked.connect(set_output_path)
    gui.settings.clicked.connect(set_settings)
    main_window.connect(main_window, Qt.SIGNAL('finished()'), on_finished)

    modules = list_snap_modules()
    snap_classes = list_snap_classes(modules)

    # SnapBase settings
    import os, string
    from soma.minf import api as minf
    snapbase_settings_file = os.path.join(neuroConfig.homeBrainVISADir, 'snapbase_settings.minf')
    if os.path.exists(snapbase_settings_file):
        # If settings file exists, load it
        minf_dict = minf.readMinf(snapbase_settings_file)
        preferences = load_preferences(minf_dict[0])
        #database = neuroHierarchy.databases._databases[preferences['database_dir']]
        #preferences['database_dir'], database = neuroHierarchy.databases._databases.items()[0]
    else:
        # Otherwise, create it and update all necessary
        preferences = load_preferences({})
        #select_db(0)
        save_preferences(preferences)
        msgBox = Qt.QMessageBox.information(None, 'SnapBase settings file created',
            'Settings will be stored in %s.\nSnapshots will be saved in %s directory. It can be edited in the settings file.'%(snapbase_settings_file, preferences['output_path']), Qt.QMessageBox.Ok)

    gui.set_default_status_msg('output path : %s'%preferences['output_path'])

    # Setting up modules
    gui.modules = []

    #excluded_classes not necessary... yet
    excluded_classes = ['SnapBase', 'HippocampusLabelLeftSnapBase', 'HippocampusLabelRawLeftSnapBase', 'HippocampusLabelRawRightSnapBase',
          'HippocampusLabelRightSnapBase', 'HippocampusLabelSnapBase', 'HippocampusLeftSnapBase', 'HippocampusRightSnapBase',
          'FibersSnapBase', 'SulciMultiViewSnapBase', 'SulciSingleViewSnapBase', 'WhiteThicknessSnapBase', 'HemiThicknessSnapBase', 'FreesurferAsegSnapBase', 'SPMComparisonSnapBase']

    ordered_classes = ['RawSnapBase', 'TabletSnapBase', 'BrainMaskSnapBase',
         'SplitBrainSnapBase', 'GreyWhiteSnapBase',
         'MeshCutSnapBase', 'MeshSnapBase', 'ThicknessSnapBase', 'SulciSnapBase',
         'SPMSnapBase', 'HippocampusSnapBase', 'WhasaSnapBase']

    ordered_snap_classes = [(each, snap_classes[each]) for each in ordered_classes if each in snap_classes.keys()] # and not each in excluded_classes]

    for (name, c) in ordered_snap_classes:
         print name
         gui.modules.append(c(preferences))

    for snap in gui.modules:
       snap.main_window = main_window
       snap.qt_app = qt_app
       name = string.lower(snap.__class__.__name__.split('SnapBase')[0])

       snap.set_interface(gui, name)


    main_window.show()
    qt_app.exec_()

