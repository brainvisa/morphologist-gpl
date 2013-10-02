# -*- coding: utf-8 -*-
from brainvisa.snapbase.snapbase import detect_slices_of_interest, parsefilepath
from brainvisa.snapbase.snapbase import SnapBase
from brainvisa.snapbase.snapbase.interface import Ui_attributes_window

class SplitBrainSnapBase(SnapBase):

    def __init__(self, preferences):
        SnapBase.__init__(self, preferences)
        self._do_slice_rendering = True

    def get_list_diskitems(self, verbose = True):

        from brainvisa.snapbase.snapbase.diskItemBrowser import SnapBaseItemBrowser

        dictdata = []
        import neuroHierarchy, neuroProcesses

        id_type = 'Split Brain Mask'
        d = SnapBaseItemBrowser(neuroHierarchy.databases, required={'_type': id_type})
        res = d.exec_()
        if res == d.Accepted:
          for each in d.getValues():
              rdi = neuroHierarchy.ReadDiskItem('T1 MRI Bias Corrected', neuroProcesses.getAllFormats())
              mri = rdi.findValue(each)
              dictdata.append(((each.get('subject'), each.get('protocol')),
                 {'type' : 'Split Brain',
                  'mri' : mri,
                  'splitbrain' : each}) )
        return dictdata

    def get_slices_of_interest(self, data):

        slices = {}
        directions = ['S', 'C']

        # Unpacking data
        splitbrain, mri = data
        voxel_size = mri.header()['voxel_size']

        splitbrain_minmax = detect_slices_of_interest(splitbrain, directions, threshold = 0)

        slices_nb = {'S': 12, 'C': 16}
        for d in directions :
            d_minmax = (splitbrain_minmax[d][0], splitbrain_minmax[d][1])
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

        splitbrain = aims.read(diskitems['splitbrain'].fileName())
        mri = aims.read(diskitems['mri'].fileName())
        return splitbrain, mri

    def set_viewer(self, data, w):

        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        splitbrain, mri = data

        ana_splitbrain = a.toAObject(splitbrain)
        ana_mri = a.toAObject(mri)
        for each in ana_splitbrain, ana_mri:
            each.releaseAppRef()

        # Fusion of the two masks
        palette = a.getPalette('RAINBOW')
        ana_splitbrain.setPalette( palette )
        self.aobjects['split'] = a.fusionObjects( [ana_mri, ana_splitbrain], method='Fusion2DMethod' )
        a.execute("Fusion2DParams", object=self.aobjects['split'], mode='linear', rate = 0.7,
                      reorder_objects = [ ana_mri, ana_splitbrain] )

        # Load in Anatomist window
        window = a.AWindow(a, w)
        window.assignReferential( a.centralReferential()  )
        a.addObjects( self.aobjects['split'], [window] )

        return window


class BrainMaskSnapBase(SnapBase):

    def __init__(self, preferences):
        SnapBase.__init__(self, preferences)
        self._do_slice_rendering = True


    def get_list_diskitems(self, verbose = True):

        from brainvisa.snapbase.snapbase.diskItemBrowser import SnapBaseItemBrowser

        dictdata = []
        import neuroHierarchy, neuroProcesses

        id_type = 'T1 Brain Mask'
        d = SnapBaseItemBrowser(neuroHierarchy.databases, required={'_type': id_type})
        res = d.exec_()
        if res == d.Accepted:
          for each in d.getValues():
              rdi = neuroHierarchy.ReadDiskItem('T1 MRI Bias Corrected', neuroProcesses.getAllFormats())
              mri = rdi.findValue(each)
              dictdata.append(((each.get('subject'), each.get('protocol')),
                 {'type' : 'T1 Brain Mask',
                  'mri' : mri,
                  'brainmask' : each}) )
        return dictdata

    def get_slices_of_interest(self, data):

        slices = {}
        directions = ['S', 'C']

        # Unpacking data
        brainmask, mri = data
        voxel_size = mri.header()['voxel_size']

        brainmask_minmax = detect_slices_of_interest(brainmask, directions)

        slices_nb = {'S': 12, 'C': 16}
        for d in directions :
            d_minmax = (brainmask_minmax[d][0], brainmask_minmax[d][1])
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

        brainmask = aims.read(diskitems['brainmask'].fileName())
        mri = aims.read(diskitems['mri'].fileName())
        return brainmask, mri

    def set_viewer(self, data, w):

        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        brainmask, mri = data

        ana_brainmask = a.toAObject(brainmask)
        ana_mri = a.toAObject(mri)
        for each in ana_brainmask, ana_mri:
            each.releaseAppRef()

        # Fusion of the two masks
        palette = a.getPalette('GREEN-ufusion')
        ana_brainmask.setPalette( palette )
        self.aobjects['brainmask'] = a.fusionObjects( [ana_mri, ana_brainmask], method='Fusion2DMethod' )
        a.execute("Fusion2DParams", object=self.aobjects['brainmask'], mode='linear_on_defined', rate = 0.7,
                      reorder_objects = [ ana_mri, ana_brainmask] )

        # Load in Anatomist window
        window = a.AWindow(a, w)
        window.assignReferential( a.centralReferential()  )
        a.addObjects( self.aobjects['brainmask'], [window] )

        return window



class SPMSnapBase(SplitBrainSnapBase):

    def __init__(self, preferences):
        SplitBrainSnapBase.__init__(self, preferences)

    def get_list_diskitems(self, verbose = True):

        from brainvisa.snapbase.snapbase.diskItemBrowser import SnapBaseItemBrowser

        dictdata = []
        import neuroHierarchy, neuroProcesses

        id_type = ['T1 MRI Nat GreyProba', 'T1 MRI Nat WhiteProba', 'T1 MRI Nat CSFProba']
        d = SnapBaseItemBrowser(neuroHierarchy.databases, required={'_type': id_type})
        res = d.exec_()
        if res == d.Accepted:
          for each in d.getValues():
              rdi = neuroHierarchy.ReadDiskItem('T1 MRI Bias Corrected', neuroProcesses.getAllFormats())
              mri = rdi.findValue(each)
              dictdata.append(((each.get('subject'), each.get('protocol')),
                 {'type' : 'T1 Brain Mask',
                  'mri' : mri,
                  'greymap' : each}) )
        return dictdata



    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        brainmask = aims.read(diskitems['greymap'].fileName())
        mri = aims.read(diskitems['mri'].fileName())
        return brainmask, mri

    def get_slices_of_interest(self, data):

        slices = {}
        directions = ['C', 'S']

        # Unpacking data
        splitbrain, mri = data
        voxel_size = mri.header()['voxel_size']

        mini = splitbrain.arraydata().min()
        maxi = splitbrain.arraydata().max()
        
        splitbrain_minmax = detect_slices_of_interest(splitbrain, directions, threshold = (mini + maxi) / 2.0)
        
        for d in directions :
            d_minmax = (splitbrain_minmax[d][0], splitbrain_minmax[d][1])
            step = (d_minmax[1]-d_minmax[0])/12
            remainder = (d_minmax[1]-d_minmax[0]) - step*12
            first_slice = d_minmax[0] + (step+remainder)/2
            last_slice = d_minmax[1] - (step+remainder)/2 + 1

            slices_list = range(first_slice, last_slice, step)

            # This converts each slice index into a list applicable to
                # Anatomist camera function
            slices[d] = [(i, self.__get_slice_position__(d, i, voxel_size)) for i in slices_list]

        return slices


    def set_viewer(self, data, w):

        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        splitbrain, mri = data

        ana_splitbrain = a.toAObject(splitbrain)
        ana_mri = a.toAObject(mri)
        for each in ana_splitbrain, ana_mri:
            each.releaseAppRef()

        # Fusion of the two masks
        palette = a.getPalette('Blue-Green-Red-Yellow')
        ana_splitbrain.setPalette( palette )
        self.aobjects['split'] = a.fusionObjects( [ana_mri, ana_splitbrain], method='Fusion2DMethod' )
        a.execute("Fusion2DParams", object=self.aobjects['split'], mode='linear', rate = 0.7,
                      reorder_objects = [ ana_mri, ana_splitbrain] )

        # Load in Anatomist window
        window = a.AWindow(a, w)
        window.assignReferential( a.centralReferential()  )
        a.addObjects( self.aobjects['split'], [window] )

        return window

class SPMComparisonSnapBase(SPMSnapBase):

    def __init__(self, preferences):
        SplitBrainSnapBase.__init__(self, preferences)

    def get_list_diskitems(self, verbose = True):

        from brainvisa.snapbase.snapbase.diskItemBrowser import SnapBaseItemBrowser

        dictdata = []
        import neuroHierarchy, neuroProcesses

        id_type = ['T1 MRI Nat GreyProba', 'T1 MRI Nat WhiteProba']
        d = SnapBaseItemBrowser(neuroHierarchy.databases, required={'_type': id_type})
        res = d.exec_()
        if res == d.Accepted:
          for each in d.getValues():
              rdi = neuroHierarchy.ReadDiskItem('T1 MRI Bias Corrected', neuroProcesses.getAllFormats())

              left_rdi = neuroHierarchy.ReadDiskItem('Left Grey White Mask', neuroProcesses.getAllFormats())
              right_rdi = neuroHierarchy.ReadDiskItem('Right Grey White Mask', neuroProcesses.getAllFormats())
              left_mask = left_rdi.findValue(each)
              right_mask = right_rdi.findValue(each)

              if left_mask and right_mask:
               mri = rdi.findValue(each)
               dictdata.append(((each.get('subject'), each.get('protocol')),
                 {'type' : 'T1 Brain Mask',
                  'mri' : mri,
                  'left mask' : left_mask,
                  'right mask': right_mask,
                  'greymap' : each}) )
        return dictdata


    def get_slices_of_interest(self, data):

        slices = {}
        directions = ['C', 'A']

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
        spmgreymap = aims.read(diskitems['greymap'].fileName())

        # fusion des masks et spmgreymap avec attribution couleurs spécifiques a intersection

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

