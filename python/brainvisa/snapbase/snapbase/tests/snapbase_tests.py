#!/usr/bin/python
from brainvisa import axon
axon.initializeProcesses()
import neuroHierarchy

# Calling each function of the project
import sys
if sys.version_info < (2, 4):
    raise 'must use python 2.5 or greater'

try:
    import PIL
except ImportError, e:
    print 'PIL not installed'

db_test_path = sys.argv[1]
print db_test_path

#try:
if not True:
    from brainvisa import snapbase
    from brainvisa.snapbase.snapbase import interface
    from PyQt4 import Qt, QtCore, QtGui
    import os
    global preferences

    qt_app = Qt.QApplication(sys.argv)
    hb = interface.HoverButton()
    hcb = interface.HoverComboBox()

    from brainvisa.snapbase.snapbase import main

    preferences = main.load_preferences({})
    database = neuroHierarchy.databases._databases[db_test_path] #'/home/go231605/snapbase_dbtest']
    preferences['display_help_msgbox'] = False

    from brainvisa.snapbase.snapbase.examples import mesh, sulci, splitbrain, raw, greywhite

    # LeftWhiteMeshSnapBase
    snap = mesh.LeftWhiteMeshSnapBase(preferences)
    snap.snap_base(database, main_window = None, qt_app = qt_app )

    output_dir = os.path.split(preferences['output_path'])[0]
    print preferences['output_files']
    for output_file in preferences['output_files']:
        assert(os.path.exists(os.path.join(output_dir, output_file)))

    # RightWhiteMeshSnapBase
    snap = mesh.RightWhiteMeshSnapBase(preferences)
    snap.snap_base(database, main_window = None, qt_app = qt_app )

    output_dir = os.path.split(preferences['output_path'])[0]
    print preferences['output_files']
    for output_file in preferences['output_files']:
        assert(os.path.exists(os.path.join(output_dir, output_file)))

    # LeftHemisphereMeshSnapBase
    snap = mesh.LeftHemisphereMeshSnapBase(preferences)
    snap.snap_base(database, main_window = None, qt_app = qt_app )

    output_dir = os.path.split(preferences['output_path'])[0]
    print preferences['output_files']
    for output_file in preferences['output_files']:
        assert(os.path.exists(os.path.join(output_dir, output_file)))

    # RightHemisphereMeshSnapBase
    snap = mesh.RightHemisphereMeshSnapBase(preferences)
    snap.snap_base(database, main_window = None, qt_app = qt_app )

    output_dir = os.path.split(preferences['output_path'])[0]
    print preferences['output_files']
    for output_file in preferences['output_files']:
        assert(os.path.exists(os.path.join(output_dir, output_file)))

    # RawSnapBase
    snap = raw.RawSnapBase(preferences)
    snap.snap_base(database, main_window = None, qt_app = qt_app )

    output_dir = os.path.split(preferences['output_path'])[0]
    print preferences['output_files']
    for output_file in preferences['output_files']:
        assert(os.path.exists(os.path.join(output_dir, output_file)))

    # RawSnapBase
    snap = raw.RawSnapBase(preferences)
    snap.snap_base(database, main_window = None, qt_app = qt_app )

    output_dir = os.path.split(preferences['output_path'])[0]
    print preferences['output_files']
    for output_file in preferences['output_files']:
        assert(os.path.exists(os.path.join(output_dir, output_file)))

    # TabletSnapBase
    snap = raw.TabletSnapBase(preferences)
    snap.snap_base(database, main_window = None, qt_app = qt_app )

    output_dir = os.path.split(preferences['output_path'])[0]
    print preferences['output_files']
    for output_file in preferences['output_files']:
        assert(os.path.exists(os.path.join(output_dir, output_file)))

    # BrainMaskSnapBase
    snap = splitbrain.BrainMaskSnapBase(preferences)
    snap.snap_base(database, main_window = None, qt_app = qt_app )

    output_dir = os.path.split(preferences['output_path'])[0]
    print preferences['output_files']
    for output_file in preferences['output_files']:
        assert(os.path.exists(os.path.join(output_dir, output_file)))

    # GreyWhiteSnapBase
    snap = greywhite.GreyWhiteSnapBase(preferences)
    snap.snap_base(database, main_window = None, qt_app = qt_app )

    output_dir = os.path.split(preferences['output_path'])[0]
    print preferences['output_files']
    for output_file in preferences['output_files']:
        assert(os.path.exists(os.path.join(output_dir, output_file)))

    # LeftSulciSingleViewSnapBase
    snap = sulci.LeftSulciSingleViewSnapBase(preferences)
    snap.snap_base(database, main_window = None, qt_app = qt_app )

    output_dir = os.path.split(preferences['output_path'])[0]
    print preferences['output_files']
    for output_file in preferences['output_files']:
        assert(os.path.exists(os.path.join(output_dir, output_file)))

    # RightSulciSingleViewSnapBase
    snap = sulci.RightSulciSingleViewSnapBase(preferences)
    snap.snap_base(database, main_window = None, qt_app = qt_app )

    output_dir = os.path.split(preferences['output_path'])[0]
    print preferences['output_files']
    for output_file in preferences['output_files']:
        assert(os.path.exists(os.path.join(output_dir, output_file)))

    preferences = main.load_preferences({})
    # LeftSulciMultiViewSnapBase
    snap = sulci.LeftSulciMultiViewSnapBase(preferences)
    snap.snap_base(database, main_window = None, qt_app = qt_app )

    output_dir = os.path.split(preferences['output_path'])[0]
    print preferences['output_files']
    for output_file in preferences['output_files']:
        assert(os.path.exists(os.path.join(output_dir, output_file)))

    # RightSulciMultiViewSnapBase
    snap = sulci.RightSulciMultiViewSnapBase(preferences)
    snap.snap_base(database, main_window = None, qt_app = qt_app )

    output_dir = os.path.split(preferences['output_path'])[0]
    print preferences['output_files']
    for output_file in preferences['output_files']:
        assert(os.path.exists(os.path.join(output_dir, output_file)))

    neuroHierarchy.databases.currentThreadCleanup()

#except:
#    raise
#    print 'exception'
