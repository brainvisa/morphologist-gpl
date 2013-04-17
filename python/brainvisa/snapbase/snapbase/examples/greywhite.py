# -*- coding: utf-8 -*-
from brainvisa.snapbase.snapbase import detect_slices_of_interest
from brainvisa.snapbase.snapbase import SnapBase

class GreyWhiteSnapBase(SnapBase):

    def __init__(self, preferences):
        SnapBase.__init__(self, preferences)
        self._do_slice_rendering = True

    def get_list_diskitems(self, verbose = True):

        from brainvisa.snapbase.snapbase.diskItemBrowser import SnapBaseItemBrowser

        dictdata = []
        import neuroHierarchy, neuroProcesses

        id_type = 'T1 MRI Bias Corrected'
        d = SnapBaseItemBrowser(neuroHierarchy.databases, required={'_type': id_type})
        res = d.exec_()
        if res == d.Accepted:
            for each in d.getValues():
                left_rdi = neuroHierarchy.ReadDiskItem('Left Grey White Mask', neuroProcesses.getAllFormats())
                right_rdi = neuroHierarchy.ReadDiskItem('Right Grey White Mask', neuroProcesses.getAllFormats())
                left_mask = left_rdi.findValue(each)
                right_mask = right_rdi.findValue(each)
                if left_mask and right_mask:
                    dictdata.append(((each.get('subject'), each.get('protocol')),
                       {'type' : 'Grey White Mask',
                        'mri' : each,
                        'left mask' : left_mask,
                        'right mask': right_mask}) )
        return dictdata


    def get_slices_of_interest(self, data):

        slices = {}
        directions = ['A', 'C']

        # Unpacking data
        left_mask, right_mask, mri = data

        left_slices_minmax = detect_slices_of_interest(left_mask, directions)
        right_slices_minmax = detect_slices_of_interest(right_mask, directions)
        voxel_size = mri.header()['voxel_size']

        slices_nb = {'S': 12, 'A': 16, 'C': 16}
        for d in directions :
            d_minmax = (min(left_slices_minmax[d][0], right_slices_minmax[d][0]),
                        max(left_slices_minmax[d][1], right_slices_minmax[d][1]))
            step = (d_minmax[1]-d_minmax[0])/slices_nb[d]
            remainder = (d_minmax[1]-d_minmax[0]) - step*slices_nb[d]
            first_slice = d_minmax[0] + (step+remainder)/2
            last_slice = d_minmax[1] - (step+remainder)/2 + 1

            slices_list = range(first_slice, last_slice, step)

            # This converts each slice index into a list applicable to
                # Anatomist camera function
            slices[d] = [(i, self.__get_slice_position__(d, i, voxel_size)) for i in slices_list]

        return slices

    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        left_mask = aims.read(diskitems['left mask'].fileName())
        right_mask = aims.read(diskitems['right mask'].fileName())
        mri = aims.read(diskitems['mri'].fileName())
        return left_mask, right_mask, mri

    def set_viewer(self, data, w):

        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        left_mask, right_mask, mri = data

        ana_left_mask = a.toAObject(left_mask)
        ana_right_mask = a.toAObject(right_mask)
        ana_mri = a.toAObject(mri)
        for each in ana_left_mask, ana_right_mask, ana_mri:
            each.releaseAppRef()

        # Fusion of the two masks
        fusion_mask = a.fusionObjects( [ana_left_mask, ana_right_mask], method='Fusion2DMethod' )

        palette = a.getPalette('RAINBOW')
        fusion_mask.setPalette( palette )
        self.aobjects['fusion'] = a.fusionObjects( [ana_mri, fusion_mask], method='Fusion2DMethod' )
        a.execute("Fusion2DParams", object=self.aobjects['fusion'],
            mode='linear', rate = 0.7, reorder_objects = [ ana_mri, fusion_mask ] )

        # Load in Anatomist window
        window = a.AWindow(a, w)
        window.assignReferential( a.centralReferential()  )
        a.addObjects( self.aobjects['fusion'], [window] )

        return window

