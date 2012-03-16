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


def detect_slices_of_interest(data, slice_directions=['A']):
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
            while (s[s!=0].size == 0):
                first_nonempty_slice += 1
                s = d[0, first_nonempty_slice, :, :]

            s = d[0, last_nonempty_slice, :, :]
            while (s[s!=0].size == 0):
                last_nonempty_slice -= 1
                s = d[0, last_nonempty_slice, :, :]
            slices_minmax[direction] = (first_nonempty_slice, last_nonempty_slice)
        elif direction == 'S':
            first_nonempty_slice = 0
            last_nonempty_slice = n_slices_sa - 1
            s = d[0, :, :, first_nonempty_slice]
            while (s[s!=0].size == 0):
                first_nonempty_slice += 1
                s = d[0, :, :, first_nonempty_slice]

            s = d[0, :, :, last_nonempty_slice]
            while (s[s!=0].size == 0):
                last_nonempty_slice -= 1
                s = d[0, :, :, last_nonempty_slice]
            slices_minmax[direction] = (first_nonempty_slice, last_nonempty_slice)
        elif direction == 'C':
            first_nonempty_slice = 0
            last_nonempty_slice = n_slices_co - 1
            s = d[0, :, first_nonempty_slice, :]
            while (s[s!=0].size == 0):
                first_nonempty_slice += 1
                s = d[0, :, first_nonempty_slice, :]

            s = d[0, :, last_nonempty_slice, :]
            while (s[s!=0].size == 0):
                last_nonempty_slice -= 1
                s = d[0, :, last_nonempty_slice, :]
            slices_minmax[direction] = (first_nonempty_slice, last_nonempty_slice)
    return slices_minmax


class SnapBase():
    def __get_slice_position__(self, d, s, voxel_size=[1.0,1.0,1.0,1.0]):
        if d == 'A': res = [0,0,s*voxel_size[2],0]
        elif d == 'C': res = [0,s*voxel_size[1],0,0]
        elif d == 'S': res = [s*voxel_size[0],0,0,0]
        return res

    def __init__(self, preferences):
        self.aobjects = {}
        self.ref = None
        self.sulci_hierarchy = None
        self.fibers_hierarchy = None
        self.preferences = preferences
        self.fusion = None
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
                                                -0.82235800000000003]}

    def check_diskitems_ambiguity(self, db, options, verbose=True):

        if verbose:
            print 'checking ambiguity %s' %options
        # Get a first list of diskitems according to given options
        opt = {}
        for key, value in options.items():
            if value != '*':
                opt[key] = value
        diskitems = [dsk for dsk in db.findDiskItems(**opt)]

        # (If no diskitems then error)
        if len(diskitems) > 0 :
            # Consider only attributes that are common to all diskitems
            att = set(diskitems[0].attributes().keys())
            for dsk in diskitems:
                att = att.intersection(set(dsk.attributes().keys()))

            # Select attributes taking string-based values
            attributes = {}
            for each in att:
                if basestring in type(diskitems[0].get(each)).mro():
                    attributes[each] = set()
            # List all existing possible values for these attributes
            for each in attributes.keys():
                for dsk in diskitems:
                    attributes[each].add(dsk.get(each))

            # If any attribute is marked as '*' (like subjects or protocols,
            # which may all included regardless of their values), consider
            # that no filter is applied to that one.
            for key, value in options.items():
                if value == '*' and attributes.has_key(key):
                    if verbose:
                        print 'all values of attribute %s are included (%s)'%(key, value)
                    attributes.pop(key)

            # Consider remaining attributes: any attribute with only one
            # possible value is removed from filtering
            for key, value in attributes.items():
		if len(value) == 1:
		    attributes.pop(key)
                    if verbose:
                        print 'attribute %s has only one value and is ignored (%s)'%(key, value)

            # Check for attributes that may have one specific value per diskitem
            # (like an extra subject id)
            if len(attributes.items()) == 0:
                return True, options
            else :
                key, value = attributes.items()[0]
                res = []
                for each in value:
                    opt = {}
                    for k, v in options.items():
                        if v != '*':
                            opt[k] = v
                    opt.update({key: value})
                    res = [i for i in db.findDiskItems(**opt)]
                    if len(res) > 1:
                        from PyQt4 import QtGui, Qt, QtCore
                        v = [unicode(i) for i in list(value)]
                        item, ok = Qt.QInputDialog.getItem(None, 'Choose',
                             'beware of attribute %s'%key,
                             v, 0, False)
                        if ok:
                            ok = Qt.QMessageBox.information(None, 'Attribute %s'%key,
                                 'Your choice : %s'%item)
                            options[key] = item
                            return False, options
                        else:
                            ok = Qt.QMessageBox.information(None, 'Attribute %s'%key,
                                 'All values for this attribute will be included. '\
                                 'If ambiguity subsists, rerun the process from the beginning.')
                            options[key] ='*'
                            return False, options
        else:
            raise IndexError

        return diskitems, options

    def get_list_diskitems(self, database_checker, verbose=True):
        '''
        Returns a dict indexed by (subject, protocol), each item being a
        dict of relevant listitems referred to by their datatype.

        dictdata[('TOTO', 'Bordeaux')] = {'mesh': mesh_diskitem, ...}
        '''
        raise NotImplementedError

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
        import random
        for i in xrange(0, 360, 360 / len(centers)):
            colors[centers[len(colors.items())]] = \
                (int(i), int(90 + random.random() * 10), int(100)) #90 + random.random() * 10)

        print colors
        return colors


    def snap_base(self, database_checker, main_window = None, qt_app = None):

        import anatomist.direct.api as ana
        from PyQt4 import QtGui, QtCore, Qt
        from PIL import Image, ImageDraw, ImageFont
        import neuroHierarchy

        font = Qt.QFont('Times', 40)

        # Defining default quaternions for later
        slice_quaternions = {'A' : [0, 0, 0, 1],
                             'C' : [0.70710700000000004, 0, 0, 0.70710700000000004],
                             'S' : [-0.5, -0.5, -0.5, 0.5]}
        view_quaternions = {'A' : [1, 0, 0, 0],
                            'C' : [0.70710700000000004, 0, 0, 0.70710700000000004],
                            'S' : [0.5, 0.5, 0.5, 0.5]}


        # Do we have to run QApplication ?
        if Qt.qApp.startingUp():
            print 'Running QApp'
            qt_app = Qt.QApplication( sys.argv )
            runqt = True
        else:
            print 'Not running QApp'
            runqt = False

        # Get a list of dict containing needed files
        general_options = {}
        if self.preferences.has_key('side'):
            general_options = {'side' : self.preferences['side']}
        dictdata = self.get_list_diskitems(database_checker, general_options)
        print 'dictdata', dictdata

        # Create Anatomist window
        a = ana.Anatomist('-b')
        if runqt:
            main_window = MainWindow()
        central_layout, central_widget, size_policy = create_simple_qt_app(main_window)

        block = QtGui.QWidget(central_widget)
        block.setSizePolicy(size_policy)
        block.setObjectName('block')
        central_layout.addWidget(block)

        self.ref = a.createReferential()
        import os
	import neuroConfig
	sulci_hierarchy_path = os.path.join(neuroConfig.getSharePath(), neuroConfig.brainvisa_share.config.share, 'nomenclature/hierarchy/sulcal_root_colors.hie')
        fibers_hierarchy_path = '/neurospin/lnao/Panabase/fibres/pamela/atlas_faisceaux/faisceaux_longs.hie'
        from soma import aims
        self.sulci_hierarchy = a.toAObject(aims.read(sulci_hierarchy_path))
        self.fibers_hierarchy = a.toAObject(aims.read(fibers_hierarchy_path))

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

        if runqt:
            qt_app.processEvents()

        print 'Rendering %i subjects'%len(dictdata.items())
        output_files = []

        protocols = list(set([each[1] for each in dictdata.keys()]))
        colors_centers = self.__get_disinct_colors(protocols)
#                        {'Bordeaux' : (255,255,255),
#                          'Lille' : (255, 0, 0),
#                          'Paris' : (0, 255, 0),
#                          'Toulouse' : (0, 0, 255),
#                          'Marseille' : (255, 0, 255)}

        # Iterating on subjects and data
        for (subject, protocol), diskitems in dictdata.items():

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
                    window.camera(slice_quaternion = slice_quaternions[d],
                                  view_quaternion = view_quaternions[d],
                                  zoom = 0.818)

                    for s, slice_position in views[d]:
                        # Selecting the slice
                        a.execute( 'LinkedCursor', window=w, position=slice_position )
                        qt_app.processEvents()
                        w.refreshNow()

                        # Grabbing the snapshot
                        snapshot = get_snapshot(qgl)

                        # Rendering slice number
                        if self.data_type == 'Grey White Mask' or self.data_type == 'Split Brain':
                            data = snapshot.convert('RGBA').tostring('raw', 'BGRA')
                            qim = Qt.QImage(data, snapshot.size[0], snapshot.size[1], Qt.QImage.Format_ARGB32)
                            pix = Qt.QPixmap.fromImage(qim)
                            pix = self.__render_text(pix, '%i'%s, font, (100,100))
                            snapshot = qt_to_pil_image(pix)

                        views_images.append(snapshot)

                elif d == '3D':
                    for view_quaternion in views[d]:
                        # Setting up the camera
                        #a.execute ('Camera', windows=[window], #observer_position = [30.0, 20.0, -20.0], windows=[window],
                        #    boundingbox_max = [72.8001, 50.887799999999999, 38.305599999999998],
                        #    boundingbox_min = [-72.8001, -50.887799999999999, -38.305599999999998])
#                            boundingbox_max = [ 102.579, 91.6496, 53.2049 ],
#                            boundingbox_min = [ -106.464, -79.7929, -36.3754 ], windows=[window] )
                        #boundingbox_max = window.getInfos()['boundingbox_max']
                        #boundingbox_min = window.getInfos()['boundingbox_min']
                        #print subject, 'bbmax', boundingbox_max, 'bbmin', boundingbox_min
                        window.camera(view_quaternion = view_quaternion,
                                      zoom = 0.718)
                        qt_app.processEvents()
                        w.refreshNow()
                        # Grabbing the snapshot
                        snapshot = get_snapshot(qgl)

                        views_images.append(snapshot)

                # Building the tiled image
                image_size = (max([im.size[0] for im in views_images]), max([im.size[1] for im in views_images]))
                grid_dim = {12 : (4,3), 5 : (2,3), 1 : (1,1), 3: (3,1)}[len(views_images)]

                tiled_image = Image.new('RGBA', (grid_dim[0]*image_size[0], grid_dim[1]*image_size[1]), 'black')
                positions = [[j*image_size[0], i*image_size[1]] for i in xrange(grid_dim[1]) for j in xrange(grid_dim[0])]
                for i, pos in zip(views_images, positions):
                    pos = [pos[j] + (image_size[j] - min(image_size[j], i.size[j]))/2.0 for j in xrange(len(pos))]
                    tiled_image.paste(i, (int(pos[0]), int(pos[1])))

                # Rendering subject ID
                d_usr = ImageDraw.Draw(tiled_image)

                outfile_path = '%s_%s_%s.png'%(self.preferences['output_path'], subject, d)
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

        if runqt:
            neuroHierarchy.databases.currentThreadCleanup()

        if self.preferences.has_key('create_poster') and self.preferences.has_key('create_poster_command') and self.preferences['create_poster']:
            print 'generating poster'
            import os, string
            create_poster_command = self.preferences['create_poster_command']
            output_dir = os.path.split(self.preferences['output_path'])[0]
            os.system('%s %s %s'%(create_poster_command, string.join([i for i in output_files], ' '), os.path.join(output_dir, 'poster.jpg') ))

            if self.preferences.has_key('remove_snapshots') and self.preferences['remove_snapshots']:
                print 'removing ', string.join([i for i in output_files], ' ')
                os.system('rm -f %s'%string.join([i for i in output_files], ' '))


        main_window.closeEvent(None)
