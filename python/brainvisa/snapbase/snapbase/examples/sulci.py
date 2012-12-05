# -*- coding: utf-8 -*-
from brainvisa.snapbase.snapbase import SnapBase

class SulciSnapBase(SnapBase):

    def __init__(self, preferences):
        SnapBase.__init__(self, preferences)

    def get_list_diskitems(self, verbose = True):

        from brainvisa.snapbase.snapbase.diskItemBrowser import SnapBaseItemBrowser

        dictdata = []
        import neuroHierarchy, neuroProcesses

        id_type = 'Cortical folds graph' #Hemisphere White Mesh'
        req_att = {'_type' : id_type,
                'labelled' : 'Yes',
                'graph_version' : '3.1',
                'manually_labelled' : 'No'}
        d = SnapBaseItemBrowser(self.db, multiple=True, selection={'_database': self.db.directory}, required={'_type': id_type})
        res = d.exec_()
        for each in d.getValues():
            rdi = neuroHierarchy.ReadDiskItem('Transform Raw T1 MRI to Talairach-AC/PC-Anatomist', neuroProcesses.getAllFormats())
            transform = rdi.findValue(each)
            rdi = neuroHierarchy.ReadDiskItem('Hemisphere White Mesh', neuroProcesses.getAllFormats())
            mesh = rdi.findValue(each)
            rdi = neuroHierarchy.ReadDiskItem('Raw T1 MRI', neuroProcesses.getAllFormats())
            mri = rdi.findValue(each)
            if mesh and transform and mri:
              dictdata.append(((each.get('subject'), each.get('protocol')),
                 {'type' : 'Hemisphere White Mesh',
                  'mesh' : mesh,
                  'mri' : mri,
                  'folds graph' : each,
                  'transform' : transform}) )
        return dictdata

    def get_dictdata(self, selected_attributes, verbose=True):

        import neuroProcesses
        from brainvisa.data import neuroHierarchy

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
            # Retrieves T1 MRI Bias Corrected
            options.update({'_type' : 'T1 MRI Bias Corrected',
                            'subject' : subject,
                            'protocol' : protocol})
            mris = [mri for mri in self.db.findDiskItems(**options)]

            if len(mris) == 1:
                # Retrieves the corresponding transform, mesh, and sulci if existing
                rdi = neuroHierarchy.ReadDiskItem('Transform Raw T1 MRI to Talairach-AC/PC-Anatomist', neuroProcesses.getAllFormats())
                transform = rdi.findValue(mris[0])
                rdi = neuroHierarchy.ReadDiskItem('Hemisphere White Mesh', neuroProcesses.getAllFormats(), requiredAttributes={'side' : self.preferences['side']})
                mesh = rdi.findValue(mris[0])
                req_att = {'subject' : options['subject'],
                           'protocol' : options['protocol'],
                           'side' : self.preferences['side'],
                           'labelled' : 'Yes',
                           'graph_version' : '3.1',
                           'manually_labelled' : 'No',
                           'automatically_labelled' : 'Yes'}
                rdi = neuroHierarchy.ReadDiskItem('Labelled Cortical folds graph', neuroProcesses.getAllFormats(), requiredAttributes=req_att )
                folds_graph = rdi.findValue(mris[0])

                # Here according to given options, ambiguity should be resolved.
                # If more than one mesh, then some attributes are probably misgiven.
                if mesh and folds_graph and transform:
                    dictdata[(subject, protocol)] = {'type' : self.data_type,
                        'mesh' : mesh,
                        'transform' : transform,
                        'mri' : mris[0],
                        'folds graph' : folds_graph}

            else:
                if verbose:
                    print '(subject %s, protocol %s) error in retrieving diskitems'\
                        %(subject, protocol)
        return dictdata

    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        folds_graph = aims.read(diskitems['folds graph'].fileName())
        mesh = aims.read(diskitems['mesh'].fileName())
        side = diskitems['mesh'].get('side')
        self.preferences['side'] = side
        return folds_graph, mesh, diskitems['transform'].fileName()


    def set_viewer(self, data, w):

        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        folds_graph, mesh, transform = data
        ana_graph = a.toAObject(folds_graph)
        ana_mesh = a.toAObject(mesh)
        ana_graph.releaseAppRef()
        ana_mesh.releaseAppRef()
        a.execute( 'GraphDisplayProperties', objects=[ana_graph],
          nomenclature_property='label' )
        a.setGraphParams(label_attribute='label', show_tooltips=1, use_nomenclature=1)
        ana_mesh.setMaterial( a.Material(diffuse = [0.8, 0.8, 0.8, 1.0]) )

        self.aobjects['folds graph'] = ana_graph
        self.aobjects['mesh'] = ana_mesh

        self.aobjects['folds graph'].assignReferential(self.ref)
        self.aobjects['mesh'].assignReferential(self.ref)
        a.loadTransformation(transform, self.ref, a.centralReferential())

        # Load in Anatomist window
        window = a.AWindow(a, w)

        window.assignReferential( a.centralReferential()  )
        a.addObjects( ana_mesh, [window] )
        a.addObjects( ana_graph, [window],  add_graph_nodes = True)

        return window


class SulciSingleViewSnapBase(SulciSnapBase):

    def __init__(self, preferences):
        SulciSnapBase.__init__(self, preferences)
        self.preferences['singlemulti'] = 'single'
        self.data_type = 'Left Cortical folds graph'

    def get_views_of_interest(self):
        views = {}
        views['3D'] =[self.view_quaternions[view_name]
            for view_name in [self.preferences['side']]]
        return views


class SulciMultiViewSnapBase(SulciSnapBase):

    def __init__(self, preferences):
        SulciSnapBase.__init__(self, preferences)
        self.preferences['singlemulti'] = 'multi'
        self.data_type = 'Left Cortical folds graph'

    def get_views_of_interest(self):
        views = {}
        views['3D'] =[self.view_quaternions[view_name]
            for view_name in {'left':['right bottom', 'back left', 'front top left'],
                               'right': ['left bottom', 'back right', 'front top right']}[self.preferences['side']]]
        return views

