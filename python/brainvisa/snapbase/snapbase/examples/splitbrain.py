# -*- coding: utf-8 -*-
from brainvisa.snapbase.snapbase import detect_slices_of_interest, parsefilepath
from brainvisa.snapbase.snapbase import SnapBase
from brainvisa.snapbase.snapbase.interface import Ui_attributes_window

class SplitBrainSnapBase(SnapBase):

    def __init__(self, preferences):
        SnapBase.__init__(self, preferences)
        self._do_slice_rendering = True

#    def get_attributes(self, diskitems):
#        primary_tag = 'mri'
#        return [diskitems[primary_tag].get(each) for each in self.preferences.naming_attributes]

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
        directions = ['C', 'S']

        # Unpacking data
        splitbrain, mri = data
        voxel_size = mri.header()['voxel_size']

        splitbrain_minmax = detect_slices_of_interest(splitbrain, directions, threshold = 0)

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
        directions = ['C', 'S']

        # Unpacking data
        brainmask, mri = data
        voxel_size = mri.header()['voxel_size']

        brainmask_minmax = detect_slices_of_interest(brainmask, directions)

        for d in directions :
            d_minmax = (brainmask_minmax[d][0], brainmask_minmax[d][1])
            step = (d_minmax[1]-d_minmax[0])/12
            remainder = (d_minmax[1]-d_minmax[0]) - step*12
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


class SPMComparisonSnapBase(SplitBrainSnapBase):

    def __init__(self, preferences):
        SplitBrainSnapBase.__init__(self, preferences)

##FIXME
#    def get_list_diskitems(self, db, verbose = True):
#
#        import neuroProcesses
#        from brainvisa.data import neuroHierarchy
#
#        # Checking for ambiguity between diskitems (acquisition, ...)
#        options = {'_type' : 'SPM BrainVisa %s Comparison'%self.preferences['comparison type']}
#        solved_ambiguity = False
#        t1_db = neuroHierarchy.databases.database(self.preferences['T1 db'])
#        options_T1 = {'_type' : 'T1 MRI Bias Corrected' }
#
#        self.db = db
#        self.options = options
#        self.options_T1 = options_T1
#        self.t1_db = t1_db
#
#        solved_ambiguity, att_T1 = self.check_diskitems_ambiguity(t1_db, options_T1)
#        if not solved_ambiguity:
#            return []
#        print 'options : ', att_T1
#
#        return self.get_dictdata(att_T1)

#    def get_dictdata(self, selected_attributes, verbose=True):
#
#        # This function is a bit special since it lets the user get data from two
#        # distinct databases, one for the T1, the other for the segmentations.
#        # This is a bit dodgy because the only link between the two databases is
#        # made by the subject name and protocol, but it has the advantage to keep
#        # external segmentations and difference maps in a separate database, with
#        # no need to import data.
#
#        import neuroProcesses
#        from brainvisa.data import neuroHierarchy
#
#        options = {}
#        options.update(self.options)
#        print 'opt:', options
#        options_T1 = {}
#        options_T1.update(self.options_T1)
#        options_T1.update(selected_attributes)
#        print 'opt_T1:', options_T1
#
#        dictdata = {}
#
#        for key, value in options_T1.items():
#            if value == '*':
#                options_T1.pop(key)
#
#        # List of subjects according to resulting options
#        subjects_id = set([subject for subject in\
#            self.db.findAttributes(('subject', 'protocol'), {}, **options )])
#
#        subjects_id_T1 = set([subject for subject in\
#            self.t1_db.findAttributes(('subject', 'protocol'), {}, **options_T1 )])
#
#        subjects_id = subjects_id.intersection(subjects_id_T1)
#
#        for subject, protocol in subjects_id:
#            # Retrieves MRIs
#            options_T1.update({'_type' : 'T1 MRI Bias Corrected',
#                            'subject' : subject,
#                            'protocol' : protocol})
#            mris = [mri for mri in self.t1_db.findDiskItems(**options_T1)]
#
#            print mris
#            if len(mris) == 1:
#                options_compar = {}
#                options_compar.update(options)
#                options_compar.update({'_type' : 'SPM BrainVisa %s Comparison'%self.preferences['comparison type'],
#                         'subject' : mris[0].get('subject'),
#                         'protocol' : mris[0].get('protocol')})
#                compar_mask = [each for each in self.db.findDiskItems(options_compar)]
#
#                # Here according to given options, ambiguity should be resolved.
#                # If more than one mri, then some attributes are probably misgiven.
#                if len(compar_mask) == 1:
#                    dictdata[(subject, protocol)] = {'type' : self.data_type,
#                        'mri' : mris[0],
#                        'splitbrain' : compar_mask[0]}
#        return dictdata

class SPMGreySnapBase(SplitBrainSnapBase):

    def __init__(self, preferences):
        SplitBrainSnapBase.__init__(self, preferences)

    def get_acquisition(self, diskitems):
        from brainvisa.snapbase.snapbase import parsefilepath
        datatype, attributes = parsefilepath(diskitems['mri'])
        import re
        datatype, _ = parsefilepath(diskitems['splitbrain'])
        spmtype = {'spm_greymap':'grey', 'spm_whitemap':'white', 'spm_brainmask':'brain'}[datatype]

        return '%s_%s'%(attributes['acquisition'], spmtype)

    def get_outfile_path(self, attributes):
        import os

        output_dir = self.preferences['output_path']
        filename_root = self.preferences['filename_root']

        assert(os.path.exists(output_dir))

        id_type = 'SPM'

        output_filename = '%s%s'%(filename_root, id_type)

        for att in attributes:
            output_filename = '%s_%s'%(output_filename, att)

        output_filename = '%s.png'%output_filename

        outfile_path = os.path.join(output_dir, output_filename)

        return outfile_path


    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        brainmask = aims.read(diskitems['splitbrain'])
        mri = aims.read(diskitems['mri'])
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


    def get_list_diskitems(self, verbose=True):

        # Checking for ambiguity between diskitems (acquisition, ...)
        db_dir = self.preferences['db']

        dictdata = []
        ui_att_win = Ui_attributes_window()

        import os
        from glob import glob
        import neuroHierarchy

        items = [('subject', [os.path.split(each)[1] for each in glob(os.path.join(db_dir,'*','*')) if os.path.isdir(each) and each not in ['sacha_log_files', '.', '..']] ),
                 ('type', ['grey mask', 'white mask', 'brain mask'])]

        from PyQt4 import QtGui, Qt
        window = QtGui.QDialog()
        ui_att_win.setupUi(window, items)
        ui_att_win.connect_signals(self)
        res = ui_att_win.window.exec_()

        if res == Qt.QDialog.Accepted:

            att = ui_att_win.get_attributes()
            spmtype = {'grey mask':'grey', 'white mask':'white', '*':'*'}[att['type']]

            if att['subject'] != '*':
              center = os.path.split(os.path.split(glob(os.path.join(db_dir,'*',att['subject']))[0])[0])[1]
            else:
              center = '*'

            hippos_1 = glob(os.path.join(db_dir, center, att['subject'], '*', '*', 'whasa_*', 'spm_preproc', 'unified_segmentation', '%s_%s_probamap.nii.gz'%(att['subject'], spmtype)))
            hippos = []
            mris = []
            for each in hippos_1:
              m = parsefilepath(each)
              if m:
                datatype, attributes = m
                hippos.append(each)
                mris.append(os.path.join(attributes['database'], attributes['group'], attributes['subject'], attributes['modality'], attributes['acquisition'], 'whasa_%s'%attributes['whasa_analysis'], 'spm_preproc', 'nobias_%s.nii.gz'%attributes['subject']))

            for hippo, mri in zip(hippos, mris):
                datatype, attributes = parsefilepath(hippo)
                subject = attributes['subject']
                center = attributes['group']
                dictdata.append(((subject, center),
                    {'splitbrain' : hippo,
                     'mri': mri}))

        return dictdata

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
