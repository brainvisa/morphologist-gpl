# -*- coding: utf-8 -*-


from PyQt4 import QtCore, QtGui, Qt

class HoverButton(QtGui.QPushButton):
    def __init__(self, parent = None):
        QtGui.QPushButton.__init__(self, parent)
        self.setMouseTracking(True)

    def enterEvent(self, event):
        if self.objectName() == 'greywhite_btn':
            self.emit(Qt.SIGNAL('enter'), str('All Grey White Masks in the database'))
        elif self.objectName() == 'whitemesh_btn':
            self.emit(Qt.SIGNAL('enter'), str('All Left Hemisphere White Meshes in the database'))
        elif self.objectName() == 'hemimesh_btn':
            self.emit(Qt.SIGNAL('enter'), str('All Left Hemisphere Meshes in the database'))
        elif self.objectName() == 'splitbrain_btn':
            self.emit(Qt.SIGNAL('enter'), str('All Split Brains in the database'))
        elif self.objectName() == 'sulci_btn':
            self.emit(Qt.SIGNAL('enter'), str('All Left Cortical Folds in the database'))
        elif self.objectName() == 'raw_btn':
            self.emit(Qt.SIGNAL('enter'), str('All Raw T1 MRI in the database'))
        elif self.objectName() == 'fibers_btn':
            self.emit(Qt.SIGNAL('enter'), str('All Labeled Fiber Bundles in the database'))
        elif self.objectName() == 'spm_btn':
            self.emit(Qt.SIGNAL('enter'), str('All Comparisons in the database'))
        elif self.objectName() == 'tablet_btn':
            self.emit(Qt.SIGNAL('enter'), str('All Raw T1 MRI (tablets) in the database'))
        elif self.objectName() == 'brainmask_btn':
            self.emit(Qt.SIGNAL('enter'), str('All T1 Brain Mask in the database'))
        elif self.objectName() == 'btn_thickness':
            self.emit(Qt.SIGNAL('enter'), str('All Cortical Thickness Maps in the database'))
        elif self.objectName() == 'btn_help':
            self.emit(Qt.SIGNAL('enter'), str('Display a comprehensive help message'))

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

    def enter_status(self, msg):
        self.statusbar.showMessage(msg)

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
        self.greywhite_btn = HoverButton(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.greywhite_btn.sizePolicy().hasHeightForWidth())
        self.greywhite_btn.setSizePolicy(sizePolicy)
        self.greywhite_btn.setMinimumSize(QtCore.QSize(100, 100))
        self.greywhite_btn.setText("")
        icon = QtGui.QIcon()
        import os
        pix_dir = os.path.split(__file__)[0]
        import sys
        icon.addPixmap(QtGui.QPixmap(os.path.join(pix_dir, 'greywhite.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.greywhite_btn.setIcon(icon)
        self.greywhite_btn.setIconSize(QtCore.QSize(90, 90))
        self.greywhite_btn.setObjectName("greywhite_btn")
        self.gridLayout.addWidget(self.greywhite_btn, 1, 1, 1, 1)
        self.hemimesh_btn = HoverButton(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.hemimesh_btn.sizePolicy().hasHeightForWidth())
        self.hemimesh_btn.setSizePolicy(sizePolicy)
        self.hemimesh_btn.setMinimumSize(QtCore.QSize(100, 100))
        self.hemimesh_btn.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(os.path.join(pix_dir, 'hemimesh.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.hemimesh_btn.setIcon(icon1)
        self.hemimesh_btn.setIconSize(QtCore.QSize(90, 90))
        self.hemimesh_btn.setObjectName("hemimesh_btn")
        self.gridLayout.addWidget(self.hemimesh_btn, 2, 0, 1, 1)
        self.whitemesh_btn = HoverButton(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.whitemesh_btn.sizePolicy().hasHeightForWidth())
        self.whitemesh_btn.setSizePolicy(sizePolicy)
        self.whitemesh_btn.setMinimumSize(QtCore.QSize(100, 100))
        self.whitemesh_btn.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(os.path.join(pix_dir, 'whitemesh.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.whitemesh_btn.setIcon(icon2)
        self.whitemesh_btn.setIconSize(QtCore.QSize(90, 90))
        self.whitemesh_btn.setObjectName("whitemesh_btn")
        self.gridLayout.addWidget(self.whitemesh_btn, 1, 2, 1, 1)
        self.splitbrain_btn = HoverButton(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitbrain_btn.sizePolicy().hasHeightForWidth())
        self.splitbrain_btn.setSizePolicy(sizePolicy)
        self.splitbrain_btn.setMinimumSize(QtCore.QSize(100, 100))
        self.splitbrain_btn.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(os.path.join(pix_dir, 'splitbrain.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.splitbrain_btn.setIcon(icon3)
        self.splitbrain_btn.setIconSize(QtCore.QSize(90, 90))
        self.splitbrain_btn.setObjectName("splitbrain_btn")
        self.gridLayout.addWidget(self.splitbrain_btn, 1, 0, 1, 1)
        self.sulci_btn = HoverButton(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sulci_btn.sizePolicy().hasHeightForWidth())
        self.sulci_btn.setSizePolicy(sizePolicy)
        self.sulci_btn.setMinimumSize(QtCore.QSize(100, 100))
        self.sulci_btn.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(os.path.join(pix_dir, 'sulci.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.sulci_btn.setIcon(icon4)
        self.sulci_btn.setIconSize(QtCore.QSize(90, 90))
        self.sulci_btn.setObjectName("sulci_btn")
        self.gridLayout.addWidget(self.sulci_btn, 2, 1, 1, 1)
        self.raw_btn = HoverButton(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.raw_btn.sizePolicy().hasHeightForWidth())
        self.raw_btn.setSizePolicy(sizePolicy)
        self.raw_btn.setMinimumSize(QtCore.QSize(100, 100))
        self.raw_btn.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(os.path.join(pix_dir, 'raw.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.raw_btn.setIcon(icon5)
        self.raw_btn.setIconSize(QtCore.QSize(90, 90))
        self.raw_btn.setObjectName("raw_btn")
        self.gridLayout.addWidget(self.raw_btn, 0, 0, 1, 1)
        self.fibers_btn = HoverButton(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fibers_btn.sizePolicy().hasHeightForWidth())
        self.fibers_btn.setSizePolicy(sizePolicy)
        self.fibers_btn.setMinimumSize(QtCore.QSize(100, 100))
        self.fibers_btn.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(os.path.join(pix_dir, 'fibers.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.fibers_btn.setIcon(icon6)
        self.fibers_btn.setIconSize(QtCore.QSize(90, 90))
        self.fibers_btn.setObjectName("fibers_btn")
        self.gridLayout.addWidget(self.fibers_btn, 2, 2, 1, 1)
        self.fibers_btn.setEnabled(False)
        self.spm_btn = HoverButton(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spm_btn.sizePolicy().hasHeightForWidth())
        self.spm_btn.setSizePolicy(sizePolicy)
        self.spm_btn.setMinimumSize(QtCore.QSize(100, 100))
        self.spm_btn.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(os.path.join(pix_dir, 'comparison.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.spm_btn.setIcon(icon7)
        self.spm_btn.setIconSize(QtCore.QSize(90, 90))
        self.spm_btn.setObjectName("spm_btn")
        self.gridLayout.addWidget(self.spm_btn, 3, 0, 1, 1)
        #self.spm_btn.setEnabled(False)
        self.tablet_btn = HoverButton(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tablet_btn.sizePolicy().hasHeightForWidth())
        self.tablet_btn.setSizePolicy(sizePolicy)
        self.tablet_btn.setMinimumSize(QtCore.QSize(100, 100))
        self.tablet_btn.setText("")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(os.path.join(pix_dir, 'tablet.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.tablet_btn.setIcon(icon8)
        self.tablet_btn.setIconSize(QtCore.QSize(90, 90))
        self.tablet_btn.setObjectName("tablet_btn")
        self.gridLayout.addWidget(self.tablet_btn, 0, 1, 1, 1)
        self.brainmask_btn = HoverButton(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.brainmask_btn.sizePolicy().hasHeightForWidth())
        self.brainmask_btn.setSizePolicy(sizePolicy)
        self.brainmask_btn.setMinimumSize(QtCore.QSize(100, 100))
        self.brainmask_btn.setText("")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(os.path.join(pix_dir, 'brainmask.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.brainmask_btn.setIcon(icon9)
        self.brainmask_btn.setIconSize(QtCore.QSize(90, 90))
        self.brainmask_btn.setObjectName("brainmask_btn")
        self.gridLayout.addWidget(self.brainmask_btn, 0, 2, 1, 1)
        self.btn_thickness = HoverButton(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_thickness.sizePolicy().hasHeightForWidth())
        self.btn_thickness.setSizePolicy(sizePolicy)
        self.btn_thickness.setMinimumSize(QtCore.QSize(100, 100))
        self.btn_thickness.setText("")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(os.path.join(pix_dir, 'thickness.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.btn_thickness.setIcon(icon9)
        self.btn_thickness.setIconSize(QtCore.QSize(90, 90))
        self.btn_thickness.setObjectName("btn_thickness")
        self.gridLayout.addWidget(self.btn_thickness, 3, 1, 1, 1)
        self.btn_hippo = HoverButton(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_hippo.sizePolicy().hasHeightForWidth())
        self.btn_hippo.setSizePolicy(sizePolicy)
        self.btn_hippo.setMinimumSize(QtCore.QSize(100, 100))
        self.btn_hippo.setText("")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(os.path.join(pix_dir, 'hippo.png')), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.btn_hippo.setIcon(icon9)
        self.btn_hippo.setIconSize(QtCore.QSize(90, 90))
        self.btn_hippo.setObjectName("btn_hippo")
        self.gridLayout.addWidget(self.btn_hippo, 4, 0, 1, 1)
        self.btn_help = HoverButton(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_help.sizePolicy().hasHeightForWidth())
        self.btn_help.setSizePolicy(sizePolicy)
        self.btn_help.setMinimumSize(QtCore.QSize(100, 33))
        self.btn_help.setText("?")
        self.btn_help.setObjectName("btn_help")
        self.gridLayout.addWidget(self.btn_help, 3, 2, 1, 1)
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
        main_window.setStatusBar(self.statusbar)

        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        main_window.setWindowTitle(QtGui.QApplication.translate("main_window", "SnapBase v0.3", None, QtGui.QApplication.UnicodeUTF8))
        self.title_lbl.setText(QtGui.QApplication.translate("main_window", "SnapBase v0.3", None, QtGui.QApplication.UnicodeUTF8))

    def connect_signals(self):
        ''' Connecting signals when the mouse enters/leaves any button '''

        self.greywhite_btn.connect(self.greywhite_btn, Qt.SIGNAL('enter'), self.enter_status)
        self.greywhite_btn.connect(self.greywhite_btn, Qt.SIGNAL('leave'), self.leave_status)
        self.whitemesh_btn.connect(self.whitemesh_btn, Qt.SIGNAL('enter'), self.enter_status)
        self.whitemesh_btn.connect(self.whitemesh_btn, Qt.SIGNAL('leave'), self.leave_status)
        self.hemimesh_btn.connect(self.hemimesh_btn, Qt.SIGNAL('enter'), self.enter_status)
        self.hemimesh_btn.connect(self.hemimesh_btn, Qt.SIGNAL('leave'), self.leave_status)
        self.splitbrain_btn.connect(self.splitbrain_btn, Qt.SIGNAL('enter'), self.enter_status)
        self.splitbrain_btn.connect(self.splitbrain_btn, Qt.SIGNAL('leave'), self.leave_status)
        self.sulci_btn.connect(self.sulci_btn, Qt.SIGNAL('enter'), self.enter_status)
        self.sulci_btn.connect(self.sulci_btn, Qt.SIGNAL('leave'), self.leave_status)
        self.raw_btn.connect(self.raw_btn, Qt.SIGNAL('enter'), self.enter_status)
        self.raw_btn.connect(self.raw_btn, Qt.SIGNAL('leave'), self.leave_status)
        self.fibers_btn.connect(self.fibers_btn, Qt.SIGNAL('enter'), self.enter_status)
        self.fibers_btn.connect(self.fibers_btn, Qt.SIGNAL('leave'), self.leave_status)
        self.tablet_btn.connect(self.tablet_btn, Qt.SIGNAL('enter'), self.enter_status)
        self.tablet_btn.connect(self.tablet_btn, Qt.SIGNAL('leave'), self.leave_status)
        self.spm_btn.connect(self.spm_btn, Qt.SIGNAL('enter'), self.enter_status)
        self.spm_btn.connect(self.spm_btn, Qt.SIGNAL('leave'), self.leave_status)
        self.brainmask_btn.connect(self.brainmask_btn, Qt.SIGNAL('enter'), self.enter_status)
        self.brainmask_btn.connect(self.brainmask_btn, Qt.SIGNAL('leave'), self.leave_status)
        self.btn_thickness.connect(self.btn_thickness, Qt.SIGNAL('enter'), self.enter_status)
        self.btn_thickness.connect(self.btn_thickness, Qt.SIGNAL('leave'), self.leave_status)
        self.btn_help.connect(self.btn_help, Qt.SIGNAL('enter'), self.enter_status)
        self.btn_help.connect(self.btn_help, Qt.SIGNAL('leave'), self.leave_status)
