# -*- coding: utf-8 -*-
def create_simple_qt_app(main_window):

    from PyQt4 import QtGui, QtCore, Qt

    size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
        QtGui.QSizePolicy.Expanding)
    size_policy.setHorizontalStretch(0)
    size_policy.setVerticalStretch(0)

    main_window.setObjectName('main_window')
    main_window.setSizePolicy(size_policy)
    main_window.setMaximumSize(QtCore.QSize(1250, 950))
    main_window.setMinimumSize(QtCore.QSize(100, 75))
    main_window.resize(QtCore.QSize(1250, 950))

    central_widget = QtGui.QWidget(main_window)
    main_window.setCentralWidget(central_widget)
    central_widget.setSizePolicy(size_policy)
    central_widget.setObjectName('central_widget')
    central_layout = QtGui.QVBoxLayout(central_widget)
    central_layout.setSpacing(5)
    central_layout.setMargin(5)
    central_layout.setMargin(0)
    central_layout.setObjectName('central_layout')

    main_window.show()

    return central_layout, central_widget, size_policy


def autocrop(img, bgcolor):
    ''' Crops an image given a background color '''

    from PIL import Image, ImageChops

    if img.mode == "RGBA":
            img_mode = "RGBA"
    elif img.mode != "RGB":
            img_mode = "RGB"
            img = img.convert("RGB")
    else:
            img_mode = "RGB"
    bg = Image.new(img_mode, img.size, bgcolor)
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    return img.crop(bbox)


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


def get_snapshot(qgl):
    ''' From a QGL widget, returns a PIL screenshot '''

    # Converting to PIL image
    qimg = qgl.grabFrameBuffer()
    pil_im = qt_to_pil_image(qimg)
    # Cropping
    cropped_im = autocrop(pil_im, (0,0,0))

    return cropped_im


def detect_slices_of_interest(data, slice_directions=['A'], threshold = 0):
    '''
    Returns a set of slices of interest : { 'S': [5,10,15,20],
                                            'A': [10,11,12,13] }
    '''

    d = data.arraydata()
    _, n_slices_ax, n_slices_co, n_slices_sa = d.shape
    slices_minmax = {}
    for direction in slice_directions:
        if direction == 'A':
            first_nonempty_slice = 0
            last_nonempty_slice = n_slices_ax - 1
            s = d[0, first_nonempty_slice, :, :]
            while (s[s > threshold].size == 0):
                first_nonempty_slice += 1
                s = d[0, first_nonempty_slice, :, :]

            s = d[0, last_nonempty_slice, :, :]
            while (s[s > threshold].size == 0):
                last_nonempty_slice -= 1
                s = d[0, last_nonempty_slice, :, :]
            slices_minmax[direction] = (first_nonempty_slice, last_nonempty_slice)
        elif direction == 'S':
            first_nonempty_slice = 0
            last_nonempty_slice = n_slices_sa - 1
            s = d[0, :, :, first_nonempty_slice]
            while (s[s > threshold].size == 0):
                first_nonempty_slice += 1
                s = d[0, :, :, first_nonempty_slice]

            s = d[0, :, :, last_nonempty_slice]
            while (s[s > threshold].size == 0):
                last_nonempty_slice -= 1
                s = d[0, :, :, last_nonempty_slice]
            slices_minmax[direction] = (first_nonempty_slice, last_nonempty_slice)
        elif direction == 'C':
            first_nonempty_slice = 0
            last_nonempty_slice = n_slices_co - 1
            s = d[0, :, first_nonempty_slice, :]
            while (s[s > threshold].size == 0):
                first_nonempty_slice += 1
                s = d[0, :, first_nonempty_slice, :]

            s = d[0, :, last_nonempty_slice, :]
            while (s[s > threshold].size == 0):
                last_nonempty_slice -= 1
                s = d[0, :, last_nonempty_slice, :]
            slices_minmax[direction] = (first_nonempty_slice, last_nonempty_slice)
    return slices_minmax

def parsefilepath(filepath):
  import re, os

  print filepath
  files_dict = { 'raw': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P=subject).nii.gz'),
                 'acpc': os.path.join('(?P<database>[\w -/]+)' ,'(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P=subject).APC'),
                 'nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'nobias_(?P=subject).nii.gz'),
                 'greywhite': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', '(?P<side>[LR]?)grey_white_(?P=subject).nii.gz'),
                 'brainmask': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'brain_(?P=subject).nii.gz'),
                 'split': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'voronoi_(?P=subject).nii.gz'),
                 'whitemeshes': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[LR]?)white.gii'),
                 'hemimeshes': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'segmentation', 'mesh', '(?P=subject)_(?P<side>[LR]?)hemi.gii'),
                 'sulci': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', '(?P<analysis>[\w -]+)', 'folds', '(?P<graph_version>[\d.]+)', '(?P<side>[LR]?)(?P=subject).arg'),
                 'spm_nobias': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'nobias_(?P=subject).nii'),
                 'spm_greymap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_grey_probamap.nii'),
                 'spm_whitemap': os.path.join('(?P<database>[\w -/]+)', '(?P<group>[\w -]+)', '(?P<subject>\w+)', '(?P<modality>\w+)', '(?P<acquisition>[\w -]+)', 'whasa_(?P<whasa_analysis>[\w -]+)', 'spm_preproc', 'unified_segmentation', '(?P=subject)_white_probamap.nii')}


  for datatype, path in files_dict.items():
    m = re.match(r"%s"%path, filepath)
    if m:
       return datatype, m.groupdict()


class SnapBase():
    def __get_slice_position__(self, d, s, voxel_size=[1.0,1.0,1.0,1.0]):
        if d == 'A': res = [0,0,s*voxel_size[2],0]
        elif d == 'C': res = [0,s*voxel_size[1],0,0]
        elif d == 'S': res = [s*voxel_size[0],0,0,0]
        return res

    def __init__(self, preferences = None):
        self._do_slice_rendering = False
        self.aobjects = {}
        self.ref = None
        self.sulci_hierarchy = None
        self.fibers_hierarchy = None
        self.preferences = preferences
        self.fusion = None
        self.options = {}
        self.view_quaternions = {'left' : [0.5, 0.5, 0.5, 0.5],
                            'right' : [0.5, -0.5, -0.5, 0.5],
                             'back left' : [-0.24415700000000001,
                                            -0.66425900000000004,
                                           -0.66440299999999997,
                                           -0.24024699999999999],
                            'back right' : [0.23693700000000001,
                                           -0.66650600000000004,
                                           -0.66561400000000004,
                                           0.237873],
                            'left bottom' : [-0.65499700000000005,
                                 -0.65245200000000003,
                                 -0.26732800000000001,
                                 -0.2717],
                            'right bottom' : [0.653748,
                                             -0.65495999999999999,
                                             -0.26623000000000002,
                                              0.26974500000000001],
                            'front left' : [-0.66398100000000004,
                                            -0.24052299999999999,
                                            -0.238736,
                                            -0.66654899999999995],
                            'front right' : [-0.664493,
                                            0.23544699999999999,
                                            0.24188200000000001,
                                            -0.666717],
                            'front top left' : [-0.42310900000000001,
                                                -0.17835200000000001,
                                                -0.33598600000000001,
                                                -0.82235800000000003],
                            'front top right' : [-0.42310900000000001,
                                                0.17835200000000001,
                                                0.33598600000000001,
                                                -0.82235800000000003],
                            'left top' : [-0.27245700359344499,
                               -0.27196499705314597,
                               -0.65204000473022505,
                               -0.65318101644516002],
                            'right top' : [-0.272103011608124,
                                    0.27079299092292802,
                                    0.65114599466323897,
                                    -0.65470701456069902],
                            'A' : [1, 0, 0, 0],
                            'C' : [0.70710700000000004, 0, 0, 0.70710700000000004],
                            'S' : [0.5, 0.5, 0.5, 0.5]}
        from PyQt4 import QtGui, QtCore, Qt


        # Defining default quaternions for later
        self.slice_quaternions = {'A' : [0, 0, 0, 1],
                             'C' : [0.70710700000000004, 0, 0, 0.70710700000000004],
                             'S' : [-0.5, -0.5, -0.5, 0.5]}


        # Do we have to run QApplication ?
        verbose = False
        if Qt.qApp.startingUp():
            if verbose :
                print 'Running QApp'
            self.qt_app = Qt.QApplication( sys.argv )
            self.runqt = True
        else:
            if verbose:
                print 'Not running QApp'
            self.runqt = False




    def get_slices_of_interest(self, data):
        '''
        For volume-based data, returns a dict containing a list of slices of
        interest

        dict = {'A' : [[0,0,s1], [0,0,s2], ...]
                'S' : [[0,s1,0], ...]}
        '''
        raise NotImplementedError

    def get_views_of_interest(self):
        '''
        For 3d models only, returns a dict containing a list of views of
        interest

        dict['3D'] = [[0.5, 0.5, 0.5, 0], ...]
        '''
        raise NotImplementedError

    def read_data(self, diskitems, data_type):
        '''
    print res, att_res
        Given a dictionary of diskitems for one subject,
        returns a tuple of relevant data
        '''

        raise NotImplementedError

    def set_viewer(self, ana_data, data_type, w):
        '''
        Performs relevant operations in Anatomist such as fusions,
        loading/setting colormaps, loading objects in windows
        '''
        raise NotImplementedError

    def ___remove_objects_from_viewer(self, w):
        ''' Remove objects from Anatomist window '''

        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        print 'removing from windows'
        window = a.AWindow(a, w)
        for key, obj in self.aobjects.items():
            window.removeObjects( obj )
            del obj

    def __render_text(self, pixmap, text, font, pos=(50, 50), color='white'):
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

    def __get_disinct_colors(self, centers):
        colors = {}
        print len(centers), 'colors'
        print centers
        import random
        for i in [each for each in xrange(0, 360, 360 / len(centers))][0:len(centers)]:
            colors[centers[len(colors.items())]] = \
                (int(i), int(90 + random.random() * 10), int(100)) #90 + random.random() * 10)

        print colors
        return colors

    def get_outfile_path(self, attributes):
        ''' builds and returns a path with proper file tree containing
        name of subject, type, hemisphere side/slice direction if provided'''
        import os, shutil, string

        id_translat = { 'RawSnapBase' : 'raw',
                       'TabletSnapBase' : 'tablet',
                       'SplitBrainSnapBase' :'split',
                       'BrainMaskSnapBase' : 'brain',
                       'GreyWhiteSnapBase' : 'GW',
                       'HippocampusSnapBase' : 'hippo'}
        if self.preferences.has_key('side'):
                id_translat.update({
                       'HemisphereMeshSnapBase' : 'hemi_%s'%string.upper(self.preferences['side'][0]),
                       'WhiteMeshSnapBase' : 'white%s'%string.upper(self.preferences['side'][0])})
        if self.preferences.has_key('side') and self.preferences.has_key('tex_type'):
                id_translat.update({
                       'HemiThicknessSnapBase' : 'hemi_%s_%s'%(self.preferences['tex_type'], string.upper(self.preferences['side'][0])),
                       'WhiteThicknessSnapBase' : 'white_%s_%s'%(self.preferences['tex_type'], string.upper(self.preferences['side'][0])),
                       })

        if self.preferences.has_key('singlemulti'):
            id_translat.update(
                {'SulciSingleViewSnapBase' : 'sulci_%s_%s'%(string.upper(self.preferences['side'][0]),self.preferences['singlemulti'])})
            id_translat.update(
                {'SulciMultiViewSnapBase' : 'sulci_%s_%s'%(string.upper(self.preferences['side'][0]),self.preferences['singlemulti'])})
        if self.preferences.has_key('side') and self.preferences.has_key('mesh'):
            id_translat.update({'Cortical Thickness' : 'thickness_%s_%s'%(string.upper(self.preferences['side'][0]), self.preferences['mesh'])})


        output_dir = self.preferences['output_path']
        filename_root = self.preferences['filename_root']

        assert(os.path.exists(output_dir))

        if id_translat.has_key(self.__class__.__name__):
            id_type = id_translat[self.__class__.__name__]
        else:
            id_type = string.replace(self.__class__.__name__, ' ', '_').lower()

        output_filename = '%s%s'%(filename_root, id_type)

        for att in attributes:
            output_filename = '%s_%s'%(output_filename, att)

        output_filename = '%s.png'%output_filename

        outfile_path = os.path.join(output_dir, output_filename)

        return outfile_path

    def get_acquisition(self, diskitems):
        acquisition_key = { 'RawSnapBase': 'mri',
               'TabletSnapBase' : 'mri',
               'SplitBrainSnapBase' : 'mri',
               'BrainMaskSnapBase' : 'mri',
               'GreyWhiteSnapBase' : 'mri',
               'WhiteMeshSnapBase' : 'mesh',
               'HemisphereMeshSnapBase' : 'mesh',
               'SulciSingleViewSnapBase' : 'mri',
               'SulciMultiViewSnapBase' : 'mri'}

        if self.__class__.__name__ not in ['HemiThicknessSnapBase', 'WhiteThicknessSnapBase'] and self.__class__.__name__ not in ['HippocampusLeftSnapBase', 'HippocampusRightSnapBase', 'HippocampusLabelLeftSnapBase', 'HippocampusLabelRightSnapBase', 'HippocampusLabelRawLeftSnapBase', 'HippocampusLabelRawRightSnapBase']:
            acquisition = diskitems[acquisition_key[self.__class__.__name__]].get('acquisition')
        elif self.__class__.__name__ not in ['HippocampusLeftSnapBase', 'HippocampusRightSnapBase', 'HippocampusLabelLeftSnapBase', 'HippocampusLabelRightSnapBase', 'HippocampusLabelRawRightSnapBase', 'HippocampusLabelRawLeftSnapBase']:
            acquisition = 'FS'
        else:
            acquisition = 'sacha'
        return acquisition

    def snap_base(self, main_window = None, qt_app = None, dictdata = None, verbose = False):

        import anatomist.direct.api as ana
        from PyQt4 import QtGui, QtCore, Qt
        from PIL import Image, ImageDraw, ImageFont
        from brainvisa.data import neuroHierarchy
        from brainvisa.data import diskItemBrowser as dib

        font = Qt.QFont('Times', 40)

        #===============================================
        # Get a list of dict containing needed files

        if dictdata == None:
            dictdata = self.get_list_diskitems()

        self.dictdata = dictdata

        print 'dictdata', dictdata

        # If no dictdata (e.g. closing the attributes window), then nothing happens
        if len(dictdata) == 0:
            return

        #===============================================
        # Create Anatomist window
        a = ana.Anatomist('-b')
        if main_window is None:
            main_window = QtGui.QMainWindow()
        central_layout, central_widget, size_policy = create_simple_qt_app(main_window)

        block = QtGui.QWidget(central_widget)
        block.setSizePolicy(size_policy)
        block.setObjectName('block')
        central_layout.addWidget(block)

        self.ref = a.createReferential()
        #===============================================
        # Load hierarchies
        import os, sys
        from brainvisa.configuration import neuroConfig
        sulci_hierarchy_path = os.path.join(neuroConfig.getSharePath(), neuroConfig.brainvisa_share.config.share, 'nomenclature/hierarchy/sulcal_root_colors.hie')
        #fibers_hierarchy_path = '/neurospin/lnao/Panabase/fibres/pamela/atlas_faisceaux/faisceaux_longs.hie'

        from soma import aims
        self.sulci_hierarchy = a.toAObject(aims.read(sulci_hierarchy_path))
        #self.fibers_hierarchy = a.toAObject(aims.read(fibers_hierarchy_path))

        #==================================================
        # Creates Anatomist Window
        c = ana.cpp.CreateWindowCommand('3D', -1, None, [], 1, block,
            2, 0, { '__syntax__' : 'dictionary',  'no_decoration' : 1} )
        a.execute(c)
        w = c.createdWindow()
        w.setSizePolicy(size_policy)
        w.setMinimumSize(QtCore.QSize(1250, 950))
        w.setWindowState(w.windowState() | QtCore.Qt.WindowFullScreen)

        central_layout.addWidget(w)
        a.execute( 'WindowConfig', windows=[w], cursor_visibility=0,
                            light={ 'background' : [ 0., 0., 0., 1. ] } )

        if self.runqt:
            self.qt_app.processEvents()

        #==================================================
        # Processes dictdatas and runs the snapshot iteration
        print 'Rendering %i items'%len(dictdata)
        output_files = []

        protocols = list(set([each[0][1] for each in dictdata]))
        colors_centers = self.__get_disinct_colors(protocols)

        # Iterating on subjects and data
        for (subject, protocol), diskitems in dictdata:
            main_window.statusBar().showMessage('%s %s'%(subject, protocol))
            # Reading data and converting to Anatomist object format
            data = self.read_data(diskitems)
            try:
                # Defining slices of interest
                views = self.get_slices_of_interest(data)
            except (TypeError, NotImplementedError):
                # Defining views of interest
                views = self.get_views_of_interest()

            # Prepares the viewer
            window = self.set_viewer(data, w)

            qgl = w.view().qglWidget()
            # Select the view and grab picture (views contains either slices or quaternions)
            for d in views.keys():
                views_images = []
                if d in ['A','C','S']:
                    # Setting the slice plane
                    window.camera(slice_quaternion = self.slice_quaternions[d],
                                  view_quaternion = self.view_quaternions[d],
                                  zoom = 0.818)

                    for s, slice_position in views[d]:
                        # Selecting the slice
                        a.execute( 'LinkedCursor', window=w, position=slice_position )
                        qt_app.processEvents()
                        w.refreshNow()

                        # Grabbing the snapshot
                        snapshot = get_snapshot(qgl)

                        # Rendering slice number
                        if self._do_slice_rendering:
                            data = snapshot.convert('RGBA').tostring('raw', 'BGRA')
                            qim = Qt.QImage(data, snapshot.size[0], snapshot.size[1], Qt.QImage.Format_ARGB32)
                            pix = Qt.QPixmap.fromImage(qim)
                            pix = self.__render_text(pix, '%i'%s, font, (100,100))
                            snapshot = qt_to_pil_image(pix)

                        views_images.append(snapshot)

                elif d == '3D':
                    for view_quaternion in views[d]:
                        # Setting up the camera
                        window.camera(view_quaternion = view_quaternion,
                                      zoom = 0.718)
                        qt_app.processEvents()
                        w.refreshNow()
                        # Grabbing the snapshot
                        snapshot = get_snapshot(qgl)
                        #snapshot = snapshot.transpose(Image.FLIP_LEFT_RIGHT)

                        views_images.append(snapshot)

                # Building the tiled image
                image_size = (max([im.size[0] for im in views_images]), max([im.size[1] for im in views_images]))
                grid_dim = {12 : (4,3), 5 : (5,1), 7:(7,1),  1 : (1,1), 3: (3,1), 20 : (4,5)}[len(views_images)]

                tiled_image = Image.new('RGBA', (grid_dim[0]*image_size[0], grid_dim[1]*image_size[1]), 'black')
                positions = [[j*image_size[0], i*image_size[1]] for i in xrange(grid_dim[1]) for j in xrange(grid_dim[0])]
                for i, pos in zip(views_images, positions):
                    pos = [pos[j] + (image_size[j] - min(image_size[j], i.size[j]))/2.0 for j in xrange(len(pos))]
                    tiled_image.paste(i, (int(pos[0]), int(pos[1])))

                # Rendering subject ID
                d_usr = ImageDraw.Draw(tiled_image)

                attributes = self.preferences['naming_attributes']
                attributes = [protocol, subject]
                #print diskitems
                acquisition = self.get_acquisition(diskitems)

                attributes.append(acquisition)
                if d != '3D':
                    attributes.append(d)

                outfile_path = self.get_outfile_path(attributes)
                output_files.append(outfile_path)
                tiled_image.save(outfile_path, 'PNG')

                # Rendering text
                pixmap = Qt.QPixmap(outfile_path)
                self.__render_text(pixmap, '%s'%subject, font, color=colors_centers[protocol])
                pixmap.save(outfile_path)

            #window.getInfos()
            print ''
            print self.aobjects
            self.___remove_objects_from_viewer(w)

        # Uncomment to keep the app running
        #if runqt:
        #    qt_app.exec_()


        print 'closing everything'
        neuroHierarchy.databases.currentThreadCleanup()

        if self.preferences.has_key('create_poster') and self.preferences.has_key('create_poster_command') and self.preferences['create_poster']:
            print 'generating poster'
            import string
            create_poster_command = self.preferences['create_poster_command']
            output_dir = os.path.split(self.preferences['output_path'])[0]
            os.system('%s %s %s'%(create_poster_command, string.join([i for i in output_files], ' '), os.path.join(output_dir, 'poster.jpg') ))

            if self.preferences.has_key('remove_snapshots') and self.preferences['remove_snapshots']:
                print 'removing ', string.join([i for i in output_files], ' ')
                os.system('rm -f %s'%string.join([i for i in output_files], ' '))


        # Keep track of the list of produced files but after saving preferences so it is not stored in the prefs
        self.preferences['output_files'] = output_files

        #main_window.close()
        if self.preferences['display_success_msgbox']:
            ok = Qt.QMessageBox.warning(None, 'Success.',
                '%d snapshots were succesfully created in %s.'%(len(output_files), self.preferences['output_path']), Qt.QMessageBox.Ok)

        main_window.emit(Qt.SIGNAL('finished()'))
        #sys.exit(0)
