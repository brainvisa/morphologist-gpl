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

def spm_snap_base():
    global main_window, qt_app, database, preferences
    from examples import splitbrain
    item, ok = Qt.QInputDialog.getItem(None,
            'Which database',
            'which db',
            neuroHierarchy.databases._databases.keys(), 0, False)
    if ok :
        preferences['db'] = item
        snap = splitbrain.SPMGreySnapBase(preferences)
        snap.snap_base(main_window = main_window, qt_app = qt_app )


def recompose(hippo_output_files, raw_output_files):
    from PIL import Image
    # recompose each subject's snapshot
    for h_path, r_path in zip(hippo_output_files, raw_output_files):
        direction = h_path[-5]
        print direction
        hippo = Image.open(h_path)
        raw = Image.open(r_path)
        w1, h1 = hippo.size
        w2, h2 = raw.size
        tile_w1, tile_h1 = int(hippo.size[0]/{'S':5.0,'C':7.0}[direction]), int(hippo.size[1]/1.0)
        print h1, w1, h2, w2
        views_images = []
        margin = 10
        for j in xrange(1):
            for i in xrange({'S':5,'C':7}[direction]):

                tile_hippo = hippo.crop((i*tile_w1, j*tile_h1, (i+1)*tile_w1, (j+1)*tile_h1))
                tile_raw = raw.crop((i*tile_w1, j*tile_h1, (i+1)*tile_w1, (j+1)*tile_h1))
                both_tiles = Image.new('RGBA', (tile_hippo.size[0] + 2 * margin, tile_hippo.size[1] * 2 + 4 * margin), 'white')
                both_tiles.paste(tile_hippo, (margin, margin))
                both_tiles.paste(tile_raw, (margin, tile_hippo.size[1] + 3 * margin))
                views_images.append(both_tiles)

        # Building the tiled image
        image_size = (max([im.size[0] for im in views_images]), max([im.size[1] for im in views_images]))
        grid_dim = {12 : (4,3), 5 : (5,1), 7:(7,1), 1 : (1,1), 3: (3,1), 20 : (4,5)}[len(views_images)]

        tiled_image = Image.new('RGBA', (grid_dim[0] * image_size[0], grid_dim[1] * image_size[1]), 'black')
        positions = [[j*image_size[0], i*image_size[1]] for i in xrange(grid_dim[1]) for j in xrange(grid_dim[0])]
        for i, pos in zip(views_images, positions):
            pos = [pos[j] + (image_size[j] - min(image_size[j], i.size[j]))/2.0 for j in xrange(len(pos))]
            tiled_image.paste(i, (int(pos[0]), int(pos[1])))
        tiled_image.save(r_path, 'PNG')

def create_pdf_report_masks(left_hipporaw_output_files, right_hipporaw_output_files):
    def __render_text(pixmap, text, font, pos=(50, 50), color='black'):
        '''
        Render text on a pixmap using Qt, color may be a string or a tuple of
        3 HSV values
        '''
        from PyQt4 import QtGui, QtCore, Qt
        qp = Qt.QPainter(pixmap)
        qp.setFont(font)
        if isinstance(color, str):
            qcol = QtGui.QColor(color)
        else:
            qcol = QtGui.QColor()
            qcol.setHsl(color[0], color[1], color[2])
        qp.setPen(qcol)
        qp.drawText(pos[0], pos[1], text)
        qp.end()

        return pixmap

    def qt_to_pil_image(qimg):
        ''' Converting a Qt Image or Pixmap to PIL image '''

        from PyQt4 import Qt
        from PIL import Image, ImageChops
        import cStringIO
        buffer = Qt.QBuffer()
        buffer.open(Qt.QIODevice.ReadWrite)
        qimg.save(buffer, 'PNG')
        strio = cStringIO.StringIO()
        strio.write(buffer.data())
        buffer.close()
        strio.seek(0)
        pil_im = Image.open(strio)
        return pil_im

    from PIL import Image
    all_images = []
    all_images.extend(left_hipporaw_output_files)
    all_images.extend(right_hipporaw_output_files)
    import string
    subjects = set()
    left_images_by_subject = {}
    right_images_by_subject = {}
    for each in left_hipporaw_output_files:
      subject = string.split(string.split(each, 'test_SACHA_')[1], '_sacha')[0]
      subjects.add(subject)
      left_images_by_subject.setdefault(subject, []).append(each)
    for each in right_hipporaw_output_files:
      subject = string.split(string.split(each, 'test_SACHA_')[1], '_sacha')[0]
      subjects.add(subject)
      right_images_by_subject.setdefault(subject, []).append(each)

    print subjects
    for subject in subjects:
        print subject
        print len(left_images_by_subject[subject]), len(right_images_by_subject[subject])
        if left_images_by_subject[subject][0][-5] == 'C':
            left_c = left_images_by_subject[subject][0]
            left_s = left_images_by_subject[subject][1]
        elif left_images_by_subject[subject][0][-5] == 'S':
            left_c = left_images_by_subject[subject][1]
            left_s = left_images_by_subject[subject][0]
        else:
            print 'ERROR left'

        if right_images_by_subject[subject][0][-5] == 'C':
            right_c = right_images_by_subject[subject][0]
            right_s = right_images_by_subject[subject][1]
        elif right_images_by_subject[subject][0][-5] == 'S':
            right_c = right_images_by_subject[subject][1]
            right_s = right_images_by_subject[subject][0]
        else:
            print 'ERROR right'

        left_c_im = Image.open(left_c)
        left_s_im = Image.open(left_s)
        right_c_im = Image.open(right_c)
        right_s_im = Image.open(right_s)
        w_left_c, h_left_c = left_c_im.size
        w_left_s, h_left_s = left_s_im.size
        w_right_c, h_right_c = right_c_im.size
        w_right_s, h_right_s = right_s_im.size

        margin_h = 500
        margin_w = 100
        whole_image = Image.new('RGB', (2 * max(w_left_s, w_left_c) + 4 * margin_w, 2 * max(h_left_s, h_left_c) + 4 * margin_h), 'white')

        whole_image.paste(right_s_im, (margin_w, margin_h))
        whole_image.paste(left_s_im, (max(w_right_s, w_right_c) + 2 * margin_w, margin_h) )
        whole_image.paste(right_c_im, (margin_w, h_right_s + 2 * margin_h) )
        whole_image.paste(left_c_im, (max(w_right_s, w_right_c) + 2* margin_w, h_right_s + 2 * margin_h) )

        from PyQt4 import Qt
        font = Qt.QFont('Times', 100)
        data = whole_image.convert('RGBA').tostring('raw', 'BGRA')
        qim = Qt.QImage(data, whole_image.size[0], whole_image.size[1], Qt.QImage.Format_ARGB32)
        pix = Qt.QPixmap.fromImage(qim)

        pix = __render_text(pix, '%s'%subject, font, (margin_w + max(w_right_s, w_right_c) - 100 , whole_image.size[1] - 200) )
        pix = __render_text(pix, 'droit', font, (margin_w , 200) )
        pix = __render_text(pix, 'gauche', font, (whole_image.size[0] - max(w_left_s, w_left_c) - margin_w, 200) )
        whole_image = qt_to_pil_image(pix)

        whole_image.save('/tmp/toto_%s.pdf'%subject, 'PDF')





def hippo_snap_base():

    global main_window, qt_app, database, preferences
    from examples import hippocampus

    hippo_choice, ok_hippo = Qt.QInputDialog.getItem(None,
            'Hippocampus mesh or mask ?',
            'Mesh or mask',
            ['left mesh', 'right mesh', 'left mask', 'right mask', 'all'], 0, False)
    dictdata = None

    if ok_hippo:
        if hippo_choice in ['left mask', 'all']:
            snap = hippocampus.HippocampusLabelLeftSnapBase(preferences)
            snap.snap_base(main_window = main_window, qt_app = qt_app )
            dictdata = snap.dictdata
            left_hippo_output_files = preferences['output_files']
            snap = hippocampus.HippocampusLabelRawLeftSnapBase(preferences)
            snap.snap_base(main_window = main_window, qt_app = qt_app, dictdata = dictdata )
            left_raw_output_files = preferences['output_files']

            recompose(left_hippo_output_files, left_raw_output_files)

        if hippo_choice in ['right mask', 'all']:
            snap = hippocampus.HippocampusLabelRightSnapBase(preferences)
            snap.snap_base(main_window = main_window, qt_app = qt_app)
            dictdata = snap.dictdata
            right_hippo_output_files = preferences['output_files']
            snap = hippocampus.HippocampusLabelRawRightSnapBase(preferences)
            snap.snap_base(main_window = main_window, qt_app = qt_app, dictdata = dictdata )
            right_raw_output_files = preferences['output_files']

            recompose(right_hippo_output_files, right_raw_output_files)

        if hippo_choice in ['left mesh']: #, 'all']:
            snap = hippocampus.HippocampusLeftSnapBase(preferences)
            snap.snap_base(main_window = main_window, qt_app = qt_app )
            left_hippo_meshes_output_files = preferences['output_files']
        if hippo_choice in ['right mesh']: #, 'all']:
            snap = hippocampus.HippocampusRightSnapBase(preferences)
            snap.snap_base(main_window = main_window, qt_app = qt_app )
            right_hippo_meshes_output_files = preferences['output_files']


        if hippo_choice in ['all']:
            # pdf generation
            create_pdf_report_masks(left_raw_output_files, right_raw_output_files)
            #create_pdf_report_meshes(left_hippo_meshes_output_files, right_hippo_meshes_output_files)




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
                    'create_poster_command' : 'montage -geometry +0+0 -background black -tile 10',
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
          'HippocampusLabelRightSnapBase', 'HippocampusLabelSnapBase', 'HippocampusLeftSnapBase', 'HippocampusRightSnapBase', 'HippocampusSnapBase',
          'SPMComparisonSnapBase', 'FibersSnapBase', 'SulciMultiViewSnapBase', 'SulciSingleViewSnapBase', 'WhiteThicknessSnapBase', 'HemiThicknessSnapBase']

    ordered_classes = ['RawSnapBase', 'TabletSnapBase', 'BrainMaskSnapBase',
         'SplitBrainSnapBase', 'GreyWhiteSnapBase',
         'MeshCutSnapBase', 'MeshSnapBase', 'ThicknessSnapBase', 'SulciSnapBase', 'FreesurferAsegSnapBase',
         'SPMGreySnapBase']

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

