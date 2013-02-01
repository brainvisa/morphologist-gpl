# -*- coding: utf-8 -*-
from brainvisa.snapbase.snapbase import detect_slices_of_interest
from brainvisa.snapbase.snapbase import SnapBase
from brainvisa.snapbase.snapbase.interface import Ui_attributes_window

class HippocampusSnapBase(SnapBase):

    def __init__(self, output_path):
        SnapBase.__init__(self, output_path)


class HippocampusLeftSnapBase(HippocampusSnapBase):

    def get_list_diskitems(self, verbose=True):

        db_dir = '/neurospin/tmp/operto/adni_x/adni_x/'

        dictdata = []
        ui_att_win = Ui_attributes_window()

        import os
        from glob import glob

        items = [('subject', [each for each in os.listdir(db_dir) if os.path.isdir(os.path.join(db_dir, each)) and each not in ['sacha_log_files', '.', '..']] )]

        from PyQt4 import QtGui, Qt
        window = QtGui.QDialog()
        ui_att_win.setupUi(window, items)
        ui_att_win.connect_signals(self)
        res = ui_att_win.window.exec_()


        if res == Qt.QDialog.Accepted:

            att = ui_att_win.get_attributes()

            hippos = glob(os.path.join(db_dir, att['subject'], '*', '*', '*', 'automatic', 'meshes', 'MRI', '%s_auto_lh.mesh'%att['subject']))

            for hippo in hippos:
                subject = os.path.split(hippo)[1][:-13]
                print subject
                dictdata.append(((subject, 'test_SACHA'),
                    {'hippo' : hippo}))

        return dictdata

    def get_views_of_interest(self):
        views = {}
        views['3D'] = [self.view_quaternions[view_name]
            for view_name in
                {'left': ['left', 'right', 'back left', 'front left', 'right bottom'],
                'right' : ['right', 'left', 'back right', 'front right', 'left bottom']}['left']]
        return views

    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        hippo = aims.read(diskitems['hippo'])
        return hippo


    def set_viewer(self, data, w):
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        hippo = data
        self.aobjects['hippo'] = a.toAObject(hippo)
        self.aobjects['hippo'].releaseAppRef()
        self.aobjects['hippo'].assignReferential(self.ref)
#        self.aobjects['hippo'].setMaterial(diffuse = [1, 0.1, 0.1, 1])

        # Load in Anatomist window
        window = a.AWindow(a, w)
        window.assignReferential( a.centralReferential()  )
        a.addObjects( self.aobjects['hippo'], [window] )

        return window

class HippocampusRightSnapBase(HippocampusSnapBase):

    def get_list_diskitems(self, verbose=True):

        db_dir = '/neurospin/tmp/operto/adni_x/adni_x/'

        dictdata = []
        ui_att_win = Ui_attributes_window()

        import os
        from glob import glob

        items = [('subject', [each for each in os.listdir(db_dir) if os.path.isdir(os.path.join(db_dir, each)) and each not in ['sacha_log_files', '.', '..']] )]

        from PyQt4 import QtGui, Qt
        window = QtGui.QDialog()
        ui_att_win.setupUi(window, items)
        ui_att_win.connect_signals(self)
        res = ui_att_win.window.exec_()


        if res == Qt.QDialog.Accepted:

            att = ui_att_win.get_attributes()

            hippos = glob(os.path.join(db_dir, att['subject'], '*', '*', '*', 'automatic', 'meshes', 'MRI', '%s_auto_rh.mesh'%att['subject']))

            for hippo in hippos:
                subject = os.path.split(hippo)[1][:-13]
                print subject
                dictdata.append(((subject, 'test_SACHA'),
                    {'hippo' : hippo}))

        return dictdata

    def get_views_of_interest(self):
        views = {}
        views['3D'] = [self.view_quaternions[view_name]
            for view_name in
                {'left': ['left', 'right', 'back left', 'front left', 'right bottom'],
                'right' : ['right', 'left', 'back right', 'front right', 'left bottom']}['right']]
        return views

    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        hippo = aims.read(diskitems['hippo'])
        return hippo


    def set_viewer(self, data, w):
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        hippo = data
        self.aobjects['hippo'] = a.toAObject(hippo)
        self.aobjects['hippo'].releaseAppRef()
        self.aobjects['hippo'].assignReferential(self.ref)
#        self.aobjects['hippo'].setMaterial(diffuse = [1, 0.1, 0.1, 1])

        # Load in Anatomist window
        window = a.AWindow(a, w)
        window.assignReferential( a.centralReferential()  )
        a.addObjects( self.aobjects['hippo'], [window] )

        return window


class HippocampusLabelSnapBase(SnapBase):

    def __init__(self, output_path):
        SnapBase.__init__(self, output_path)
        self._do_slice_rendering = True

    def get_slices_of_interest(self, data):

        slices = {}
        directions = ['C', 'S']

        # Unpacking data
        hippo, mri = data
        voxel_size = mri.header()['voxel_size']

        hippo_minmax = detect_slices_of_interest(hippo, directions)
        print hippo_minmax

        for d in directions :
            d_minmax = (hippo_minmax[d][0], hippo_minmax[d][1])

            #slices_list = range(d_minmax[0], d_minmax[1],
            #    (d_minmax[1]-d_minmax[0])/12)[0:12]
            slices_list = []
            nb_of_slices = {'S': 5, 'C':7}[d]
            for i in xrange(nb_of_slices):
                slices_list.append(d_minmax[0] + (1.0-(nb_of_slices - 1.0 - i)/(nb_of_slices-1.0))*(d_minmax[1]-d_minmax[0]))
            print slices_list
            # This converts each slice index into a list applicable to
                # Anatomist camera function
            slices[d] = [(i, self.__get_slice_position__(d, i, voxel_size)) for i in slices_list]

        return slices

    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        hippo = aims.read(diskitems['hippo'])
        mri = aims.read(diskitems['mri'])
        return hippo, mri


    def set_viewer(self, data, w):

        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        hippo, mri = data

        ana_hippo = a.toAObject(hippo)
        ana_mri = a.toAObject(mri)
        for each in ana_hippo, ana_mri:
            each.releaseAppRef()

        # Fusion of the two masks
        palette = a.getPalette('RAINBOW')
        ana_hippo.setPalette( palette )
        self.aobjects['hippo'] = a.fusionObjects( [ana_mri, ana_hippo], method='Fusion2DMethod' )
        a.execute("Fusion2DParams", object=self.aobjects['hippo'], mode='linear', rate = 0.7,
                      reorder_objects = [ ana_mri, ana_hippo] )

        # Load in Anatomist window
        window = a.AWindow(a, w)
        window.assignReferential( a.centralReferential()  )
        a.addObjects( self.aobjects['hippo'], [window] )

        return window

class HippocampusLabelLeftSnapBase(HippocampusLabelSnapBase):

    def __init__(self, output_path):
        HippocampusLabelSnapBase.__init__(self, output_path)

    def get_list_diskitems(self, verbose=True):

        db_dir = '/neurospin/tmp/operto/adni_x/adni_x/'

        dictdata = []
        ui_att_win = Ui_attributes_window()

        import os, string
        from glob import glob

        items = [('subject', [each for each in os.listdir(db_dir) if os.path.isdir(os.path.join(db_dir, each)) and each not in ['sacha_log_files', '.', '..']] )]

        from PyQt4 import QtGui, Qt
        window = QtGui.QDialog()
        ui_att_win.setupUi(window, items)
        ui_att_win.connect_signals(self)
        res = ui_att_win.window.exec_()


        if res == Qt.QDialog.Accepted:

            att = ui_att_win.get_attributes()

            hippos = glob(os.path.join(db_dir, att['subject'], '*', '*', '*', 'automatic', 'masks', 'LHA', '%s_auto_lha.ima'%att['subject']))
            mris = glob(os.path.join(db_dir, att['subject'], '*', '*', '*', 'automatic', 'subvolume', 'LHA', '%s_auto_subvol_lha.ima'%att['subject']))

            assert(len(hippos) == len(mris))

            for hippo, mri in zip(hippos, mris):
                subject = string.split(os.path.split(hippo)[1], '_auto_')[0]
                print subject
                dictdata.append(((subject, 'test_SACHA'),
                    {'hippo' : hippo, 'mri' : mri}))

        return dictdata


class HippocampusLabelRightSnapBase(HippocampusLabelSnapBase):

    def __init__(self, output_path):
        HippocampusLabelSnapBase.__init__(self, output_path)

    def get_list_diskitems(self, verbose=True):

        db_dir = '/neurospin/tmp/operto/adni_x/adni_x/'

        dictdata = []
        ui_att_win = Ui_attributes_window()

        import os, string
        from glob import glob

        items = [('subject', [each for each in os.listdir(db_dir) if os.path.isdir(os.path.join(db_dir, each)) and each not in ['sacha_log_files', '.', '..']] )]

        from PyQt4 import QtGui, Qt
        window = QtGui.QDialog()
        ui_att_win.setupUi(window, items)
        ui_att_win.connect_signals(self)
        res = ui_att_win.window.exec_()


        if res == Qt.QDialog.Accepted:

            att = ui_att_win.get_attributes()

            hippos = glob(os.path.join(db_dir, att['subject'], '*', '*', '*', 'automatic', 'masks', 'RHA', '%s_auto_rha.ima'%att['subject']))
            mris = glob(os.path.join(db_dir, att['subject'], '*', '*', '*', 'automatic', 'subvolume', 'RHA', '%s_auto_subvol_rha.ima'%att['subject']))

            assert(len(hippos) == len(mris))

            for hippo, mri in zip(hippos, mris):
                subject = string.split(os.path.split(hippo)[1],'_auto_')[0]
                print subject
                dictdata.append(((subject, 'test_SACHA'),
                    {'hippo' : hippo, 'mri' : mri}))

        return dictdata

class HippocampusLabelRawLeftSnapBase(HippocampusLabelLeftSnapBase):

    def __init__(self, output_path):
        HippocampusLabelLeftSnapBase.__init__(self, output_path)

    def set_viewer(self, data, w):

        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        hippo, mri = data

        ana_mri = a.toAObject(mri)
        for each in [ana_mri]:
            each.releaseAppRef()

        # Fusion of the two masks
        palette = a.getPalette('B-W LINEAR')
        ana_mri.setPalette( palette )
        self.aobjects['mri'] = ana_mri

        # Load in Anatomist window
        window = a.AWindow(a, w)
        window.assignReferential( a.centralReferential()  )
        a.addObjects( self.aobjects['mri'], [window] )

        return window



class HippocampusLabelRawRightSnapBase(HippocampusLabelRightSnapBase):

    def __init__(self, output_path):
        HippocampusLabelRightSnapBase.__init__(self, output_path)

    def set_viewer(self, data, w):

        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        hippo, mri = data

        ana_mri = a.toAObject(mri)
        for each in [ana_mri]:
            each.releaseAppRef()

        # Fusion of the two masks
        palette = a.getPalette('B-W LINEAR')
        ana_mri.setPalette( palette )
        self.aobjects['mri'] = ana_mri

        # Load in Anatomist window
        window = a.AWindow(a, w)
        window.assignReferential( a.centralReferential()  )
        a.addObjects( self.aobjects['mri'], [window] )

        return window
