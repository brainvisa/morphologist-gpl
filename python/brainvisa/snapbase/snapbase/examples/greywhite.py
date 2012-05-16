# -*- coding: utf-8 -*-
from brainvisa.snapbase.snapbase import detect_slices_of_interest
from brainvisa.snapbase.snapbase import SnapBase

class GreyWhiteSnapBase(SnapBase):

    def __init__(self, output_path):
        SnapBase.__init__(self, output_path)
        self.data_type = 'Grey White Mask'

    def get_dictdata(self, selected_attributes, verbose=True):

        import neuroProcesses
        from brianvisa.data import neuroHierarchy

        options = {}
        options.update(self.options)
        options.update(selected_attributes)
        print 'opt:', options

        dictdata = {}

        for key, value in options.items():
            if value == '*':
                options.pop(key)

        # List of subjects according to resulting options
        subjects_id = set([subject for subject in\
            self.db.findAttributes(('subject', 'protocol'), {}, **options )])

        for subject, protocol in subjects_id:
            # Retrieves MRIs
            options.update({'_type' : 'T1 MRI Bias Corrected',
                            'subject' : subject,
                            'protocol' : protocol})
            mris = [mri for mri in self.db.findDiskItems(**options)]

            if len(mris) == 1:
                left_rdi = neuroHierarchy.ReadDiskItem('Left %s'%self.data_type, neuroProcesses.getAllFormats())
                right_rdi = neuroHierarchy.ReadDiskItem('Right %s'%self.data_type, neuroProcesses.getAllFormats())
                left_mask = left_rdi.findValue(mris[0])
                right_mask = right_rdi.findValue(mris[0])

                # Here according to given options, ambiguity should be resolved.
                # If more than one mri, then some attributes are probably misgiven.
                if left_mask and right_mask:
                    dictdata[(subject, protocol)] = {'type' : self.data_type,
                        'mri' : mris[0],
                        'left mask' : left_mask,
                        'right mask' : right_mask}
            else:
                if verbose:
                    print '(subject %s, protocol %s) error in retrieving diskitems'\
                        %(subject, protocol)
        return dictdata

    def get_slices_of_interest(self, data):

        slices = {}
        directions = ['A', 'S']

        # Unpacking data
        left_mask, right_mask, mri = data

        left_slices_minmax = detect_slices_of_interest(left_mask, directions)
        right_slices_minmax = detect_slices_of_interest(right_mask, directions)
        voxel_size = mri.header()['voxel_size']

        for d in directions :
            d_minmax = (min(left_slices_minmax[d][0],
                right_slices_minmax[d][0]), max(left_slices_minmax[d][1],
                right_slices_minmax[d][1]))

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

