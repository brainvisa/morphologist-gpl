# -*- coding: utf-8 -*-
from brainvisa.snapbase.snapbase import SnapBase

class SulciSnapBase(SnapBase):

    def __init__(self, preferences):
        SnapBase.__init__(self, preferences)

    def snap(self):
       from PyQt4 import Qt
       choice, ok_choice = Qt.QInputDialog.getItem(None,
           'single or multi view ?', 'single/multi',
           ['single', 'multi'], 0, False)
       if ok_choice:
           if choice == 'single':
              self.views = {'left': ['left'], 'right': ['right']}
           elif choice == 'multi':
              self.views = {'left': ['left', 'right', 'back left', 'front left', 'left top', 'right bottom'],
                'right' : ['right', 'left', 'back right', 'front right', 'right top', 'left bottom']}
           self.snap_base(None, qt_app = self.qt_app)

    def get_list_diskitems(self, verbose = True):

        from brainvisa.snapbase.snapbase.diskItemBrowser import SnapBaseItemBrowser

        dictdata = []
        import neuroHierarchy, neuroProcesses

        id_type = 'Cortical folds graph' #Hemisphere White Mesh'
        d = SnapBaseItemBrowser(neuroHierarchy.databases, required={'_type': id_type})
        res = d.exec_()
        if res == d.Accepted:
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


    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        folds_graph = aims.read(diskitems['folds graph'].fileName())
        mesh = aims.read(diskitems['mesh'].fileName())
        side = diskitems['mesh'].get('side')
        #self.preferences['side'] = side
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

    def get_views_of_interest(self):
        views = {}
        side = self.get_current_side()
        current_views = self.views[side]
        views['3D'] = [self.view_quaternions[view_name]
              for view_name in current_views]
        return views

#
#class SulciSingleViewSnapBase(SulciSnapBase):
#
#    def __init__(self, preferences):
#        SulciSnapBase.__init__(self, preferences)
#
#
#
#class SulciMultiViewSnapBase(SulciSnapBase):
#
#    def __init__(self, preferences):
#        SulciSnapBase.__init__(self, preferences)
#
#    def get_views_of_interest(self):
#        views = {}
#        side = self.get_current_side()
#        views['3D'] =[self.view_quaternions[view_name]
#            for view_name in {'left':['right bottom', 'back left', 'front top left'],
#                               'right': ['left bottom', 'back right', 'front top right']}[side]] #self.preferences['side']]]
#        return views
#
