from brainvisa.snapbase.snapbase import detect_slices_of_interest
from brainvisa.snapbase.snapbase import SnapBase

class SplitBrainSnapBase(SnapBase):

    def __init__(self, output_path):
        SnapBase.__init__(self, output_path)
        self.data_type = 'Split Brain'

    def get_list_diskitems(self, db, general_options = {}, verbose = True):

        import neuroProcesses
        import neuroHierarchy

        dictdata = {}

        # Checking for ambiguity between diskitems (acquisition, ...)
        options = {'_type' : 'T1 MRI Bias Corrected'} #,
                   #'subject' : '*'} #,
                   #'protocol' : '*'}
        options.update(general_options)
        solved_ambiguity = False
        while not solved_ambiguity:
            solved_ambiguity, options = self.check_diskitems_ambiguity(db, options)
            print 'options : ', options

        for key, value in options.items():
            if value == '*':
                options.pop(key)

        # List of subjects according to resulting options
        subjects_id = set([subject for subject in\
            db.findAttributes(('subject', 'protocol'), {}, **options )])

        for subject, protocol in subjects_id:
            # Retrieves MRIs
            options.update({'_type' : 'T1 MRI Bias Corrected',
                            'subject' : subject,
                            'protocol' : protocol})
            mris = [mri for mri in db.findDiskItems(**options)]

            if len(mris) == 1:
                rdi = neuroHierarchy.ReadDiskItem('Voronoi Diagram', neuroProcesses.getAllFormats())
                splitbrain = rdi.findValue(mris[0])

                # Here according to given options, ambiguity should be resolved.
                # If more than one mri, then some attributes are probably misgiven.
                if splitbrain:
                    dictdata[(subject, protocol)] = {'type' : self.data_type,
                        'mri' : mris[0],
                        'splitbrain' : splitbrain}
            else:
                if verbose:
                    print '(subject %s, protocol %s) error in retrieving diskitems'\
                        %(subject, protocol)

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

