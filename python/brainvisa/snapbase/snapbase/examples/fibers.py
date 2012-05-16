# -*- coding: utf-8 -*-
from brainvisa.snapbase.snapbase import SnapBase

class FibersSnapBase(SnapBase):

    def __init__(self, output_path):
        SnapBase.__init__(self, output_path)
        self.data_type = 'Labelled Fiber Bundles'


    def get_list_diskitems(self, db, general_options = {}, verbose = True):

        import os

        # This module is particular since it retrieves data out from a proper BV db
        # i.e. it rebuilds filepaths from the db root directory.
        dictdata = {}

        print db.directory

        subjects = [each for each in os.listdir(db.directory) \
            if os.path.isdir(os.path.join(db.directory, each)) and \
            'Bundle-labelling' in os.listdir(os.path.join(db.directory, each))]

        for subject in subjects:
            subject_dir = os.path.join(db.directory, subject)
            trm_dir = os.path.join(subject_dir, 'TRM')
            trm_path = os.path.join(trm_dir, 'RawT1-%s_raw_TO_Talairach-ACPC.trm'%subject)
            #trm_path = '' #os.path.join(trm_dir, 'dw_to_t1.trm')
            #assert(os.path.exists(trm_path))
            bundles_dir = os.path.join(subject_dir, 'Bundle-labelling')
            assert(len(os.listdir(bundles_dir)) == 1 and os.listdir(bundles_dir)[0] == subject)
            bundles_dir = os.path.join(bundles_dir, subject)
            bundles_list = []
            for bundle in [os.path.join(bundles_dir, each) for each in os.listdir(bundles_dir) \
                if os.path.splitext(each)[1] == '.bundles']:
                g = {}
                l = {}
                execfile(bundle, g, l)
                assert(l.has_key('attributes') and l['attributes'].has_key('curves_count'))
                curves_count = l['attributes']['curves_count']
                if curves_count > 0:
                    bundles_list.append(bundle)
            print bundles_list

            protocol = subject[8:11]

            print trm_path
            if len(bundles_list) != 0:
                dictdata[(subject, protocol)] = {'type' : self.data_type,
                    'bundles' : bundles_list,
                    'transform': trm_path}
            else:
                if verbose:
                    print '(subject %s, protocol %s) error in retrieving diskitems'\
                        %(subject, protocol)
        return dictdata

    def read_data(self, diskitems):

#        from soma import aims
#        import anatomist.direct.api as ana
#        a = ana.Anatomist('-b')

        bundles = diskitems['bundles']
        transform = diskitems['transform']
#        mesh = aims.read(diskitems['mesh'].fileName())
        return bundles, transform

    def get_views_of_interest(self):
        views = {}
        views['3D'] =[self.view_quaternions[view_name]
            for view_name in ['left']]
        return views

    def set_viewer(self, data, w):

        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        bundles, transform = data
        ana_bundles = [a.loadObject(each) for each in bundles]
#        for ana_bundle in ana_bundles:
#            ana_bundle.releaseAppRef()
        a.execute( 'GraphDisplayProperties', objects=ana_bundles,
          nomenclature_property='name' )
        a.setGraphParams(label_attribute='label', show_tooltips=1, use_nomenclature=1)
        for ana_bundle in ana_bundles:
            ana_bundle.setMaterial( a.Material(diffuse = [0.8, 0.8, 0.8, 0.2]) )

        self.aobjects['bundles'] = ana_bundles

        for ana_bundle in self.aobjects['bundles']:
            ana_bundle.assignReferential(self.ref)
        a.loadTransformation(transform, self.ref, a.centralReferential())

        # Load in Anatomist window
        window = a.AWindow(a, w)

#        window.assignReferential( a.centralReferential()  )
        a.addObjects( ana_bundles, [window],  add_graph_nodes = True)
        obs_pos = window.getInfos()['observer_position']
#        obs_pos[2] = obs_pos[2] - 100.0
#        a.execute ('Camera', observer_position = obs_pos, windows=[window])
#            boundingbox_max = [ 102.579, 91.6496, 53.2049 ],
#            boundingbox_min = [ -106.464, -79.7929, -36.3754 ], windows=[window] )

        return window
