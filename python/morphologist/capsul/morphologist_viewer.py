from __future__ import print_function

import traits.api as traits
import anatomist.capsul as acap
import math


class MorphologistView(acap.AnatomistMultipleViewsProcess):

    t1mri = traits.File(
        allowed_extensions=['.nii.gz', '.mnc.gz', '.nii', '.ima', '.dim',
                            '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.dcm',
                            '.mnc', ''])
    nobias = traits.File(
        allowed_extensions=['.nii.gz', '.mnc.gz', '.nii', '.ima', '.dim',
                            '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.dcm',
                            '.mnc', ''],
        optional=True)
    mask = traits.File(
        allowed_extensions=['.nii.gz', '.mnc.gz', '.nii', '.ima', '.dim',
                            '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.dcm',
                            '.mnc', ''],
        optional=True)
    split = traits.File(
        allowed_extensions=['.nii.gz', '.mnc.gz', '.nii', '.ima', '.dim',
                            '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.dcm',
                            '.mnc', ''],
        optional=True)
    gw_classif_l = traits.File(
        allowed_extensions=['.nii.gz', '.mnc.gz', '.nii', '.ima', '.dim',
                            '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.dcm',
                            '.mnc', ''],
        optional=True)
    gw_classif_r = traits.File(
        allowed_extensions=['.nii.gz', '.mnc.gz', '.nii', '.ima', '.dim',
                            '.vimg', '.vinfo', '.vhdr', '.img', '.hdr', '.dcm',
                            '.mnc', ''],
        optional=True)
    wmesh_l = traits.File(
        allowed_extensions=['.gii', '.mesh', '.obj', '.tri'],
        optional=True)
    wmesh_r = traits.File(
        allowed_extensions=['.gii', '.mesh', '.obj', '.tri'],
        optional=True)
    gmesh_l = traits.File(
        allowed_extensions=['.gii', '.mesh', '.obj', '.tri'],
        optional=True)
    gmesh_r = traits.File(
        allowed_extensions=['.gii', '.mesh', '.obj', '.tri'],
        optional=True)
    sulci_l = traits.File(
        allowed_extensions=['.arg'],
        optional=True)
    sulci_r = traits.File(
        allowed_extensions=['.arg'],
        optional=True)
    sulci_labelled_l = traits.File(
        allowed_extensions=['.arg'],
        optional=True)
    sulci_labelled_r = traits.File(
        allowed_extensions=['.arg'],
        optional=True)


    def create_anatomist_view(self):

        def check_file(filename):
            return filename not in ('', traits.Undefined, None) \
                and os.path.exists(filename)

        a = self.anatomist

        # should not be imported in the module to avoid loading Qt too early
        from soma.qt_gui.qt_backend import QtGui, QtCore
        from soma import aims

        block = None
        wins = []
        objects = []
        other = []
        kwargs = {}
        if self.is_interactive:
            block = a.createWindowsBlock(nbCols=self.view_layout_cols,
                                         nbRows=self.view_layout_rows)
        else:
            kwargs['no_decoration'] = True
            kwargs['options'] = {'hidden': True}

        wtypes = ['Axial', 'Coronal', 'Axial', 'Axial',
                  'Axial', '3D', '3D', None,
                  '3D', '3D', '3D', '3D']
        if self.view_layout_cols != 0:
            nc = min(self.view_layout_cols, len(wtypes))
            nl = int(math.ceil(float(len(wtypes)) / nc))
        elif self.view_layout_rows != 0:
            nl = min(self.view_layout_rows, len(wtypes))
            nc = int(math.ceil(float(len(wtypes)) / nl))
        else:
            nc = int(math.ceil(math.sqrt(len(wtypes))))
            nl = int(math.ceil(float(len(wtypes)) / nc))

        self.view_layout_position = [(0, 0)] * len(wtypes)
        j = 0
        for i, wtype in enumerate(wtypes):
            c = i % nc
            l = i / nc
            if wtype is None:
                # fill with emty widget
                if block:
                    wid = QtGui.QWidget()
                    block.internalWidget.widget.centralWidget().layout().\
                        addWidget(wid, l, c)
                    other.append(wid)
                continue
            win = a.createWindow(wtype, block=block, **kwargs)
            win.windowConfig(light={'background': [0,0,0,0]})
            wins.append(win)
            self.view_layout_position[j] = (l, c)
            j += 1

        wins[5].camera(view_quaternion=[0.63, 0.086, 0.11, 0.77],
                       slice_quaternion=[0.707, 0, 0, 0.707], zoom=1.5)
        wins[6].camera(view_quaternion=[0.63, 0.086, 0.11, 0.77],
                       slice_quaternion=[0.707, 0, 0, 0.707], zoom=1.5)
        wins[7].camera(view_quaternion=[0.5, 0.5, 0.5, 0.5])
        wins[8].camera(view_quaternion=[0.5, -0.5, -0.5, 0.5])
        wins[9].camera(view_quaternion=[0.5, -0.5, -0.5, 0.5])
        wins[10].camera(view_quaternion=[0.5, 0.5, 0.5, 0.5])

        t1mri = a.loadObject(self.t1mri)
        nobias = None
        mask = None
        mask_fus = None
        split = None
        split_fus = None
        gw_classif_l = None
        gw_classif_r = None
        gw_fus = None
        wmesh_l = None
        wmesh_r = None
        wmesh_g_l = None
        wmesh_g_r = None
        wmesh_l_fus = None
        wmesh_r_fus = None
        gmesh_l = None
        gmesh_r = None
        gmesh_l_fus = None
        gmesh_r_fus = None
        sulci_l = None
        sulci_r = None
        nomencl = None

        objects.append(t1mri)

        if check_file(self.nobias):
            t1mri = a.loadObject(self.nobias)
            nobias = a.loadObject(self.nobias, duplicate=True)
            nobias.setPalette('RAINBOW')
            objects += [t1mri, nobias]

        if check_file(self.split):
            mask = a.loadObject(self.split)
            mask.setPalette('RAINBOW')
            mask_fus = a.fusionObjects([t1mri, mask],
                                        method='Fusion2DMethod')
            a.execute('TexturingParams', objects=[mask_fus], texture_index=1,
                      rate=0.7)
            objects += [mask, mask_fus]

        elif check_file(self.mask):
            mask = a.loadObject(self.mask)
            mask.setPalette('GREEN-ufusion')
            mask_fus = a.fusionObjects([t1mri, mask],
                                       method='Fusion2DMethod')
            a.execute('TexturingParams', objects=[mask_fus], texture_index=1,
                      rate=0.7)
            objects += [mask, mask_fus]

        if check_file(self.gw_classif_l) \
                or check_file(self.gw_classif_r):
            gwf = [t1mri]
            if check_file(self.gw_classif_l):
                gw_classif_l = a.loadObject(self.gw_classif_l)
                gwf.append(gw_classif_l)
                gw_classif_l.setPalette('RAINBOW')
            if check_file(self.gw_classif_r):
                gw_classif_r = a.loadObject(self.gw_classif_r)
                gwf.append(gw_classif_r)
                gw_classif_r.setPalette('RAINBOW')
            gw_fus = a.fusionObjects(gwf, method='Fusion2DMethod')
            a.execute('TexturingParams', objects=[gw_fus], texture_index=1,
                      rate=0.6)
            if len(gwf) > 2:
                a.execute('TexturingParams', objects=[gw_fus],
                          texture_index=2, rate=0.5)
            objects += gwf[1:] + [gw_fus]
            del gwf

        if check_file(self.wmesh_l):
            wmesh_l = a.loadObject(self.wmesh_l)
            wmesh_g_l = a.loadObject(self.wmesh_l, duplicate=True)
            wmesh_g_l.setMaterial(diffuse=[.3, 1., .6, 1.])
            wmesh_l_fus = a.fusionObjects([wmesh_l],
                                          method='Fusion2DMeshMethod')
            wmesh_l_fus.setMaterial(diffuse=[0., 0., 1., 1.])
            objects += [wmesh_l, wmesh_g_l, wmesh_l_fus]
        if check_file(self.wmesh_r):
            wmesh_r = a.loadObject(self.wmesh_r)
            wmesh_g_r = a.loadObject(self.wmesh_r, duplicate=True)
            wmesh_g_r.setMaterial(diffuse=[.3, 1., .6, 1.])
            wmesh_r_fus = a.fusionObjects([wmesh_r],
                                          method='Fusion2DMeshMethod')
            wmesh_r_fus.setMaterial(diffuse=[0., 0., 1., 1.])
            objects += [wmesh_r, wmesh_g_r, wmesh_r_fus]

        if check_file(self.gmesh_l):
            gmesh_l = a.loadObject(self.gmesh_l)
            gmesh_l.setMaterial(diffuse=[.9, .8, .45, 1.])
            gmesh_l_fus = a.fusionObjects([gmesh_l],
                                          method='Fusion2DMeshMethod')
            gmesh_l_fus.setMaterial(diffuse=[1., 1., 0., 1.])
            objects += [gmesh_l, gmesh_l_fus]
        if check_file(self.gmesh_r):
            gmesh_r = a.loadObject(self.gmesh_r)
            gmesh_r.setMaterial(diffuse=[.9, .8, .45, 1.])
            gmesh_r_fus = a.fusionObjects([gmesh_r],
                                          method='Fusion2DMeshMethod')
            gmesh_r_fus.setMaterial(diffuse=[1., 1., 0., 1.])
            objects += [gmesh_r, gmesh_r_fus]

        nomencl = a.loadObject(aims.carto.Paths.findResourceFile(
            'nomenclature/hierarchy/sulcal_root_colors.hie'))
        print('nomencl:', nomencl)
        objects.append(nomencl)

        if check_file(self.sulci_labelled_l):
            sulci_l = a.loadObject(self.sulci_labelled_l)
            a.execute('GraphDisplayProperties', objects=[sulci_l],
                      nomenclature_property='label')
            objects.append(sulci_l)
        elif check_file(self.sulci_l):
            sulci_l = a.loadObject(self.sulci_l)
            objects.append(sulci_l)
        if check_file(self.sulci_labelled_r):
            sulci_r = a.loadObject(self.sulci_labelled_r)
            a.execute('GraphDisplayProperties', objects=[sulci_r],
                      nomenclature_property='label')
            objects.append(sulci_r)
        elif check_file(self.sulci_r):
            sulci_r = a.loadObject(self.sulci_r)
            objects.append(sulci_r)

        wins[0].addObjects(t1mri)
        if nobias:
            wins[1].addObjects(nobias)
        if mask_fus:
            print('display mask')
            wins[2].addObjects(mask_fus)
        if gw_fus:
            wins[3].addObjects(gw_fus)
        wobj = [t1mri] \
            + [o for o in [wmesh_l_fus, wmesh_r_fus, gmesh_l_fus, gmesh_r_fus]
               if o]
        wins[4].addObjects(wobj)
        wobj = [t1mri] + [o for o in [wmesh_g_l, wmesh_g_r] if o]
        wins[5].addObjects(wobj)
        wobj = [t1mri] + [o for o in [gmesh_l, gmesh_r] if o]
        wins[6].addObjects(wobj)
        wobj = [o for o in [wmesh_l, sulci_l] if o]
        wins[7].addObjects(wobj)
        wins[9].addObjects(wobj)
        wobj = [o for o in [wmesh_r, sulci_r] if o]
        wins[8].addObjects(wobj)
        wins[10].addObjects(wobj)

        wpos = (0.5, 0.33, 0.5)
        pos = [(b[0] * b[2] + b[1] * (1. - b[2]))
                                  for b in zip(*(t1mri.boundingbox()
                                                  + (wpos,)))]
        wins[0].moveLinkedCursor(pos)

        #import time
        #for i in range(15):
          #time.sleep(0.1)
          #QtGui.qApp.processEvents()

        if block is not None:
            objects.append(block)

        res = {'windows': wins, 'objects': objects}
        if other:
            res['other'] = other
        return res


if __name__ == '__main__':
    from capsul.api import get_process_instance
    import os
    import sys

    mv = get_process_instance(MorphologistView)

    if 'PyQt4.QtGui' in sys.modules or 'PySide.QtGui' in sys.modules \
            or 'PyQt5.QtGui' in sys.modules:
        mv.is_interactive = True

    acq = '/home/riviere/data/baseessai/subjects/sujet01/t1mri/default_acquisition'
    if not os.path.exists(acq):
        acq = '/volatile/riviere/basetests-3.1.0/subjects/sujet01/t1mri/default_acquisition'
    mv.t1mri = os.path.join(acq, 'sujet01.nii')
    mv.nobias = os.path.join(acq, 'default_analysis', 'nobias_sujet01.nii')
    mv.mask = os.path.join(acq, 'default_analysis', 'segmentation',
                           'brain_sujet01.nii')
    mv.split = os.path.join(acq, 'default_analysis', 'segmentation',
                            'voronoi_sujet01.nii')
    mv.gw_classif_l = os.path.join(acq, 'default_analysis', 'segmentation',
                            'Lgrey_white_sujet01.nii')
    mv.gw_classif_r = os.path.join(acq, 'default_analysis', 'segmentation',
                            'Rgrey_white_sujet01.nii')
    mv.wmesh_l = os.path.join(acq, 'default_analysis', 'segmentation',
                            'mesh', 'sujet01_Lwhite.gii')
    mv.wmesh_r = os.path.join(acq, 'default_analysis', 'segmentation',
                            'mesh', 'sujet01_Rwhite.gii')
    mv.gmesh_l = os.path.join(acq, 'default_analysis', 'segmentation',
                            'mesh', 'sujet01_Lhemi.gii')
    mv.gmesh_r = os.path.join(acq, 'default_analysis', 'segmentation',
                            'mesh', 'sujet01_Rhemi.gii')
    mv.sulci_l = os.path.join(acq, 'default_analysis', 'folds', '3.1',
                              'Lsujet01.arg')
    mv.sulci_r = os.path.join(acq, 'default_analysis', 'folds', '3.1',
                              'Rsujet01.arg')
    mv.sulci_labelled_l = os.path.join(acq, 'default_analysis', 'folds', '3.1',
                                      'default_session_auto',
                                      'Lsujet01_default_session_auto.arg')
    mv.sulci_labelled_r = os.path.join(acq, 'default_analysis', 'folds', '3.1',
                                      'default_session_auto',
                                      'Rsujet01_default_session_auto.arg')

    mv.view_layout_cols = 4
    mv.output_width = 800
    mv.output_height = 800
    mv.output = '/tmp/morhsnap.jpg'

    res = mv()

