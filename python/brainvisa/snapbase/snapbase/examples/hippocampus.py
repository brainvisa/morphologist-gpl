# -*- coding: utf-8 -*-
from brainvisa.snapbase.snapbase import detect_slices_of_interest
from brainvisa.snapbase.snapbase import SnapBase

class HippocampusSnapBase(SnapBase):

    def __init__(self, output_path):
        SnapBase.__init__(self, output_path)

    def get_list_diskitems(self, verbose=True):

        dictdata = []
        lh = '/home/go231605/DB_BV_test/test_SACHA/s1/t1mri/acq1/sacha_default_analysis/automatic/meshes/MRI/s1_auto_lh.mesh'
        rh = '/home/go231605/DB_BV_test/test_SACHA/s1/t1mri/acq1/sacha_default_analysis/automatic/meshes/MRI/s1_auto_rh.mesh'
        dictdata.append((('s1', 'test_SACHA'),
            {'lh' : lh, 'rh' : rh}))
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

        left_hippo = aims.read(diskitems['lh'])
        right_hippo = aims.read(diskitems['rh'])
        return left_hippo, right_hippo


    def set_viewer(self, data, w):
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        lh, rh = data
        self.aobjects['lh'] = a.toAObject(lh)
        self.aobjects['lh'].releaseAppRef()
        self.aobjects['lh'].assignReferential(self.ref)
        self.aobjects['lh'].setMaterial(diffuse = [1, 0.1, 0.1, 1])
        self.aobjects['rh'] = a.toAObject(rh)
        self.aobjects['rh'].releaseAppRef()
        self.aobjects['rh'].assignReferential(self.ref)

        # Load in Anatomist window
        window = a.AWindow(a, w)
        window.assignReferential( a.centralReferential()  )
        a.addObjects( self.aobjects['lh'], [window] )
        a.addObjects( self.aobjects['rh'], [window] )

        return window

class HippocampusLabelSnapBase(SnapBase):

    def __init__(self, output_path):
        SnapBase.__init__(self, output_path)

    def get_list_diskitems(self, verbose=True):

        dictdata = []
        lh = '/home/go231605/DB_BV_test/test_SACHA/s1/t1mri/acq1/sacha_default_analysis/automatic/masks/LHA/s1_auto_lha.ima'
        mri = '/home/go231605/DB_BV_test/test_SACHA/s1/t1mri/acq1/sacha_default_analysis/automatic/subvolume/LHA/s1_auto_subvol_lha.ima'
        dictdata.append((('s1', 'test_SACHA'),
            {'lh' : lh, 'mri' : mri}))
        return dictdata


    def get_slices_of_interest(self, data):

        slices = {}
        directions = ['C', 'S']

        # Unpacking data
        splitbrain, mri = data
        voxel_size = mri.header()['voxel_size']

        splitbrain_minmax = detect_slices_of_interest(splitbrain, directions)

        for d in directions :
            d_minmax = (splitbrain_minmax[d][0], splitbrain_minmax[d][1])

            slices_list = range(d_minmax[0], d_minmax[1],
                (d_minmax[1]-d_minmax[0])/14)[1:13]
            # This converts each slice index into a list applicable to
                # Anatomist camera function
            slices[d] = [(i, self.__get_slice_position__(d, i, voxel_size)) for i in slices_list]

        return slices

    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        left_hippo = aims.read(diskitems['lh'])
        mri = aims.read(diskitems['mri'])
        return left_hippo, mri


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
