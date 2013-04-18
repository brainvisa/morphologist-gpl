# -*- coding: utf-8 -*-
from brainvisa.snapbase.snapbase import detect_slices_of_interest
from brainvisa.snapbase.snapbase import SnapBase

class RawSnapBase(SnapBase):

    def __init__(self, preferences):
        SnapBase.__init__(self, preferences)
        self._do_slice_rendering = True

    def get_list_diskitems(self, verbose=True):

        from brainvisa.snapbase.snapbase.diskItemBrowser import SnapBaseItemBrowser
        import neuroHierarchy

        id_type = 'Raw T1 MRI'
        d = SnapBaseItemBrowser(neuroHierarchy.databases, required={'_type': id_type})
        res = d.exec_()
        dictdata = []
        if res == d.Accepted:
          for each in d.getValues():
              dictdata.append(((each.get('subject'), each.get('protocol')), {'type' : 'Raw T1 MRI', 'mri' : each}) )
        return dictdata

    def get_slices_of_interest(self, data):

        slices = {}
        directions = ['A', 'S', 'C']

        # Unpacking data
        mri = data

        slices_minmax = detect_slices_of_interest(mri, directions)
        voxel_size = mri.header()['voxel_size']

        for d in directions :
            d_minmax = (min(slices_minmax[d][0],
                slices_minmax[d][1]), max(slices_minmax[d][0],
                slices_minmax[d][1]))

            slices_list = [int((d_minmax[0] + d_minmax[1])/2.0)]
            # This converts each slice index into a list applicable to
                # Anatomist camera function
            slices[d] = [(i, self.__get_slice_position__(d, i, voxel_size)) for i in slices_list]

        return slices

    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        mri = aims.read(diskitems['mri'].fileName())
        return mri

    def set_viewer(self, data, w):

        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        mri = data

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


class TabletSnapBase(RawSnapBase):

    def __init__(self, preferences):
        RawSnapBase.__init__(self, preferences)

    def get_slices_of_interest(self, data):

        slices = {}
        directions = ['A']

        # Unpacking data
        mri = data

        slices_minmax = detect_slices_of_interest(mri, directions)
        voxel_size = mri.header()['voxel_size']

        for d in directions :
            d_minmax = (min(slices_minmax[d][0],
                slices_minmax[d][1]), max(slices_minmax[d][0],
                slices_minmax[d][1]))

            slices_list = range(d_minmax[0], d_minmax[1],
                (d_minmax[1]-d_minmax[0])/50.0)[8:15]
            print slices_list
            slices_list = range(d_minmax[0]+30,d_minmax[0]+114,4)
            print slices_list
            # This converts each slice index into a list applicable to
                # Anatomist camera function
            slices[d] = [(i, self.__get_slice_position__(d, i, voxel_size)) for i in slices_list]

        return slices
