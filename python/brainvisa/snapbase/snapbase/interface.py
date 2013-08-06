# -*- coding: utf-8 -*-


from PyQt4 import QtCore, QtGui, Qt

class HoverButton(QtGui.QPushButton):
    def __init__(self, parent = None):
        QtGui.QPushButton.__init__(self, parent)
        self.setMouseTracking(True)

    def enterEvent(self, event):
       messages = {'greywhite_btn':'All Grey White Masks in the database',
             'mesh_btn':'All Hemisphere and White Meshes in the database',
             'splitbrain_btn':'All Split Brains in the database',
             'sulci_btn':'All Left Cortical Folds in the database',
             'raw_btn':'All Raw T1 MRI in the database',
             'fibers_btn':'All Labeled Fiber Bundles in the database',
             'tablet_btn':'All Raw T1 MRI (tablets) in the database',
             'brainmask_btn':'All T1 Brain Mask in the database',
             'thickness_btn':'All Cortical Thickness Maps in the database',
             'meshcut_btn' : 'All MeshCut',
             'spm_btn' : 'All SPM probability maps',
             'btn_help':'Display a comprehensive help message'}

       self.emit(Qt.SIGNAL('enter'), str(messages[self.objectName()]))

    def leaveEvent(self, event):
        self.emit(Qt.SIGNAL('leave'))


class HoverComboBox(QtGui.QComboBox):
    def __init__(self, parent = None):
        QtGui.QComboBox.__init__(self, parent)
        self.setMouseTracking(True)

    def enterEvent(self, event):
        self.emit(Qt.SIGNAL('enter'), str('Select the database to get processed'))

    def leaveEvent(self, event):
        self.emit(Qt.SIGNAL('leave'))

class Ui_attribute_widget(QtGui.QFrame):
    def __init__(self, parent, text='', items=[], _type='combo'):
        import locale

        QtGui.QWidget.__init__(self, parent)
        self._type = _type
        self.horiz_layout = QtGui.QHBoxLayout(self)
        self.att_lbl = QtGui.QLabel(self)
        self.att_lbl.setObjectName('att_lbl')
        self.att_lbl.setFrameShape(QtGui.QFrame.Box)
        self.att_lbl.setFrameShadow(QtGui.QFrame.Raised)
        self.att_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.att_lbl.setMinimumSize(QtCore.QSize(100,31))
        self.att_lbl.setText(text)
        self.horiz_layout.addWidget(self.att_lbl)

        if _type == 'combo':
            self.att_combo = QtGui.QComboBox(self)
            self.att_combo.setObjectName('att_combo')
            self.att_combo.setMinimumSize(QtCore.QSize(200,31))
            self.att_combo.addItem('< any >')

            locale.setlocale(locale.LC_ALL, "")
            items.sort(cmp=locale.strcoll)
            for each in items:
                self.att_combo.addItem(each)
            self.horiz_layout.addWidget(self.att_combo)


class Ui_fixed_attribute_widget(Ui_attribute_widget):
    def __init__(self, parent, text='', text2=''):
        Ui_attribute_widget.__init__(self, parent, text, [], 'label')

        self.att_lbl2 = QtGui.QLabel(self)
        self.att_lbl2.setObjectName('att_lbl2')
        self.att_lbl2.setMinimumSize(QtCore.QSize(200,31))
        self.att_lbl2.setText('<B>%s</B>'%text2)
        self.horiz_layout.addWidget(self.att_lbl2)

class FileDialogButton(QtGui.QPushButton):
   def opendialog(self, event):
       print 'toto'
       destDir = QtGui.QFileDialog.getExistingDirectory(None,
         'Open working directory',
         self.destdir,
         QtGui.QFileDialog.ShowDirsOnly)
       self.destdir = destDir
       print destDir

   def __init__(self, parent, startdir):
      QtGui.QPushButton.__init__(self, parent)
      self.destdir = startdir
      self.clicked.connect(self.opendialog)


class Ui_setting_widget(QtGui.QFrame):
   def __init__(self, parent, text = '', item = []):
      import locale
      print text, item
      QtGui.QFrame.__init__(self, parent)

      self.horiz_layout = QtGui.QHBoxLayout(self)
      self.att_lbl = QtGui.QLabel(self)
      self.att_lbl.setObjectName('att_lbl')
      self.att_lbl.setFrameShape(QtGui.QFrame.Box)
      self.att_lbl.setFrameShadow(QtGui.QFrame.Raised)
      self.att_lbl.setAlignment(QtCore.Qt.AlignCenter)
      self.att_lbl.setMinimumSize(QtCore.QSize(100,31))
      self.att_lbl.setText(text)
      self.horiz_layout.addWidget(self.att_lbl)
      if isinstance(item, list):
         self.att_combo = QtGui.QComboBox(self)
         self.att_combo.setObjectName('att_combo')
         self.att_combo.setMinimumSize(QtCore.QSize(200,31))
         locale.setlocale(locale.LC_ALL, "")
         item.sort(cmp=locale.strcoll)
         for each in item:
            self.att_combo.addItem(each)
      elif isinstance(item, basestring):
         import os
         if os.path.exists(item):
            self.att_combo = FileDialogButton(self, item)
            self.att_combo.setObjectName('att_combo')
            self.att_combo.setMinimumSize(QtCore.QSize(200,31))
            self.att_combo.setText(item)
         else:
            self.att_combo = QtGui.QLineEdit(self)
            self.att_combo.setObjectName('att_combo')
            self.att_combo.setMinimumSize(QtCore.QSize(200,31))
            self.att_combo.setText(item)
      elif isinstance(item, bool):
         self.att_combo = QtGui.QCheckBox(self)
         self.att_combo.setObjectName('att_combo')
         self.att_combo.setChecked(item)
      else:
         print type(item)

      if hasattr(self, 'att_combo'):
         self.horiz_layout.addWidget(self.att_combo)
      else:
         return None


class Ui_settings_window(object):
    def get_results(self):
        res = {}
        for each in [e for e in self.frames if hasattr(e, 'att_combo')]:

           if isinstance(each.att_combo, QtGui.QComboBox):
              res[each.att_lbl.text()] = each.att_combo.currentText()
           elif isinstance(each.att_combo, QtGui.QLineEdit):
              res[each.att_lbl.text()] = each.att_combo.text()
           elif isinstance(each.att_combo, FileDialogButton):
              res[each.att_lbl.text()] = each.att_combo.destdir
           elif isinstance(each.att_combo, QtGui.QCheckBox):
              res[each.att_lbl.text()] = each.att_combo.isChecked()

        return res

    def clicked_on_ok(self):
        self.results = self.get_results()
        self.window.accept()

    def setupUi(self, window, items, exclude_items=[]): #, req_items=[]):
        window.setObjectName("window")
        window.setModal(True)
        window.setWindowTitle('Settings')

        self.window = window
        window.resize(348, 380)
        window.setMinimumSize(QtCore.QSize(548, 55*len(items) + 110))
        window.setMaximumSize(QtCore.QSize(548, 1000)) #55*len(items) + 110))
        font = Qt.QFont()
        font.setPointSize(8)
        self.central_widget = QtGui.QWidget(window)
        self.central_widget.setObjectName("central_widget")
        self.verticalLayout = QtGui.QVBoxLayout(self.central_widget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.frames = []
        for i, (k, item) in enumerate(items.items()):
           if not k in exclude_items:
            widget = Ui_setting_widget(self.central_widget, k, item)
            if not widget is None:
               self.frames.append(widget)
               self.frames[-1].setObjectName('frame%d'%i)
               self.frames[-1].setMinimumSize(QtCore.QSize(531, 50))
               self.frames[-1].setMaximumSize(QtCore.QSize(531, 50))
               self.frames[-1].setFrameShape(QtGui.QFrame.StyledPanel)
               self.frames[-1].setFrameShadow(QtGui.QFrame.Raised)

            self.verticalLayout.addWidget(self.frames[-1])


        self.ok_btn = QtGui.QPushButton(self.central_widget)
        self.ok_btn.setMinimumSize(QtCore.QSize(100, 40))
        self.verticalLayout.addWidget(self.ok_btn)

        icon = QtGui.QIcon()
        import os
        pix_dir = os.path.split(__file__)[0]
        import sys
        self.ok_btn.setText('OK')
        self.ok_btn.setObjectName('ok_btn')
        self.verticalLayout.addWidget(self.ok_btn, 0)

        self.title_lbl = QtGui.QLabel(self.central_widget)
        self.title_lbl.setFrameShape(QtGui.QFrame.Box)
        self.title_lbl.setFrameShadow(QtGui.QFrame.Raised)
        self.title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.title_lbl.setObjectName("title_lbl")
        self.title_lbl.setMinimumSize(QtCore.QSize(250,31))
        self.title_lbl.setFont(font)
        self.verticalLayout.addWidget(self.title_lbl)
        self.connect_signals()


    def connect_signals(self):
        self.ok_btn.clicked.connect(self.clicked_on_ok)

class Ui_attributes_window(object):
    def clicked_on_ok(self):
        self.window.accept()

    def change_event(self):

        print 'change_event'

    def get_attributes(self):
        att_res = {}
        for frame in self.frames:
            if frame._type == 'combo':
                att = frame.att_lbl.text()
                att_combo_value = frame.att_combo.currentText()
                if att_combo_value == '< any >':
                    att_res[att] = '*'
                else:
                    att_res[att] = att_combo_value
        return att_res

    def setupUi(self, window, items=[], req_items=[]):
        window.setObjectName("window")
        window.setModal(True)
        window.setWindowTitle('Select attributes')

        self.window = window
        window.resize(348, 380)
        window.setMinimumSize(QtCore.QSize(548, 55*(len(items)+len(req_items)) + 110))
        window.setMaximumSize(QtCore.QSize(548, 1000)) #55*len(items) + 110))
        font = Qt.QFont()
        font.setPointSize(8)
        self.central_widget = QtGui.QWidget(window)
        self.central_widget.setObjectName("central_widget")
        self.verticalLayout = QtGui.QVBoxLayout(self.central_widget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.frames = []
        for i, item in enumerate(items):
            self.frames.append(Ui_attribute_widget(self.central_widget, item[0], item[1]))
            self.frames[-1].setObjectName('frame%d'%i)
            self.frames[-1].setMinimumSize(QtCore.QSize(531, 50))
            self.frames[-1].setMaximumSize(QtCore.QSize(531, 50))
            self.frames[-1].setFrameShape(QtGui.QFrame.StyledPanel)
            self.frames[-1].setFrameShadow(QtGui.QFrame.Raised)
            self.verticalLayout.addWidget(self.frames[-1])
        for i, item in enumerate(req_items):
            self.frames.append(Ui_fixed_attribute_widget(self.central_widget, item[0], item[1]))
            self.frames[-1].setObjectName('frame%d'%i)
            self.frames[-1].setMinimumSize(QtCore.QSize(531, 50))
            self.frames[-1].setMaximumSize(QtCore.QSize(531, 50))
            self.frames[-1].setFrameShape(QtGui.QFrame.StyledPanel)
            self.frames[-1].setFrameShadow(QtGui.QFrame.Raised)
            self.verticalLayout.addWidget(self.frames[-1])

        self.ok_btn = HoverButton(self.central_widget)
        self.ok_btn.setMinimumSize(QtCore.QSize(100, 40))
        self.verticalLayout.addWidget(self.ok_btn)

        icon = QtGui.QIcon()
        import os
        pix_dir = os.path.split(__file__)[0]
        import sys
        self.ok_btn.setText('OK')
        self.ok_btn.setObjectName('ok_btn')
        self.verticalLayout.addWidget(self.ok_btn, 0)

        self.title_lbl = QtGui.QLabel(self.central_widget)
        self.title_lbl.setFrameShape(QtGui.QFrame.Box)
        self.title_lbl.setFrameShadow(QtGui.QFrame.Raised)
        self.title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.title_lbl.setObjectName("title_lbl")
        self.title_lbl.setMinimumSize(QtCore.QSize(250,31))
        self.title_lbl.setFont(font)
        self.verticalLayout.addWidget(self.title_lbl)


    def connect_signals(self, snap_base):
        self.ok_btn.clicked.connect(self.clicked_on_ok)

        self.snap_base = snap_base
        for frame in self.frames:
            if frame._type == 'combo':
                frame.att_combo.activated.connect(self.change_event)


class Ui_main_window(Qt.QObject):
    def __init__(self, parent = None):
        Qt.QObject.__init__(self, parent)

    def leave_status(self):
        self.statusbar.showMessage(self.statusbar.default_status_msg)
        self.statusbar.setToolTip(self.statusbar.default_status_msg)

    def enter_status(self, msg):
        self.statusbar.showMessage(msg)
        self.statusbar.setToolTip(msg)

    def set_default_status_msg(self, msg):
        self.statusbar.default_status_msg = msg

    def setupUi(self, main_window, default_status_msg=''):
        main_window.setObjectName("main_window")
        main_window.resize(348, 571)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(main_window.sizePolicy().hasHeightForWidth())
        main_window.setSizePolicy(sizePolicy)
        main_window.setMaximumSize(QtCore.QSize(348,571))
        font = Qt.QFont()
        font.setPointSize(8)
        self.central_widget = QtGui.QWidget(main_window)
        self.central_widget.setObjectName("central_widget")
        self.central_widget.setStyleSheet('color: white; background-color: black;')
        self.verticalLayout = QtGui.QVBoxLayout(self.central_widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.title_lbl = QtGui.QLabel(self.central_widget)
        self.title_lbl.setFrameShape(QtGui.QFrame.Box)
        self.title_lbl.setFrameShadow(QtGui.QFrame.Raised)
        self.title_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.title_lbl.setObjectName("title_lbl")
        self.title_lbl.setFont(font)
        self.verticalLayout.addWidget(self.title_lbl)
        self.widget = QtGui.QWidget(self.central_widget)
        self.widget.setObjectName("widget")
        self.gridLayout = QtGui.QGridLayout(self.widget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout.addWidget(self.widget)
        main_window.setCentralWidget(self.central_widget)
        self.menubar = QtGui.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 348, 23))
        self.menubar.setObjectName("menubar")
        main_window.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(main_window)
        self.statusbar.default_status_msg = default_status_msg
        self.statusbar.setObjectName("statusbar")
        self.statusbar.setFont(font)
        self.statusbar.setStyleSheet('color: white; background-color: black;')
        self.statusbar.setSizeGripEnabled(False)
        self.fileopen = QtGui.QPushButton()
        icon = QtGui.QIcon()
        import os
        pix_dir = os.path.split(__file__)[0]
        icon.addPixmap(QtGui.QPixmap(os.path.join(pix_dir, 'fileopen.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.fileopen.setIcon(icon)
        self.statusbar.addPermanentWidget(self.fileopen)
        main_window.setStatusBar(self.statusbar)
        self.settings = QtGui.QPushButton()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(pix_dir, 'settings.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.settings.setIcon(icon)
        self.statusbar.addPermanentWidget(self.settings)

        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        main_window.setWindowTitle(QtGui.QApplication.translate("main_window", "SnapBase v0.4", None, QtGui.QApplication.UnicodeUTF8))
        self.title_lbl.setText(QtGui.QApplication.translate("main_window", "SnapBase v0.4", None, QtGui.QApplication.UnicodeUTF8))

