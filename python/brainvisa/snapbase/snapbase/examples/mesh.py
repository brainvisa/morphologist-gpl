# -*- coding: utf-8 -*-
from brainvisa.snapbase.snapbase import SnapBase

# -------------------------
# Parent class MeshSnapBase
# -------------------------

class MeshSnapBase(SnapBase):
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

        id_types = ['Hemisphere Mesh', 'Hemisphere White Mesh', 'Pial', 'White', 'AimsPial', 'AimsWhite']
        d = SnapBaseItemBrowser(neuroHierarchy.databases, required={'_type': id_types})
        res = d.exec_()
        if res == d.Accepted:
          for each in d.getValues():
              rdi = neuroHierarchy.ReadDiskItem('Transform Raw T1 MRI to Talairach-AC/PC-Anatomist', neuroProcesses.getAllFormats())
              transform = rdi.findValue(each)
              dictdata.append(((each.get('subject'), each.get('protocol')),
                 { 'mesh' : each,
                  'transform' : transform}) )

        return dictdata


    def get_views_of_interest(self):
        views = {}
        side = self.get_current_side()
        current_views = self.views[side]
        prim_key = self.get_primary_key(self.__class__.__name__)
        t = self.current_diskitems[prim_key].type.name
        onto = self.current_diskitems[prim_key].attributes()['_ontology']
        import string
        if t in  ['Pial', 'White']:
           new_views = []
           for each in current_views:
              if each.count('left') > 0:
                 n = string.replace(each, 'left', 'right')
              elif each.count('right') > 0:
                 n = string.replace(each, 'right', 'left')
              new_views.append(n)
           current_views = new_views

        views['3D'] = [self.view_quaternions[view_name]
              for view_name in current_views]
        return views


    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        mesh = aims.read(diskitems['mesh'].fileName())
        side = diskitems['mesh'].get('side')

        if not diskitems['transform'] is None:
           trm_file = diskitems['transform'].fileName()
        else:
           trm_file = None

        return mesh, trm_file #diskitems['transform'].fileName()

    def set_viewer(self, data, w):
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        mesh, transform = data
        self.aobjects['mesh'] = a.toAObject(mesh)
        self.aobjects['mesh'].releaseAppRef()
        self.aobjects['mesh'].assignReferential(self.ref)

        if not transform is None:
           a.loadTransformation(transform, self.ref, a.centralReferential())

        # Load in Anatomist window
        window = a.AWindow(a, w)
        window.assignReferential( a.centralReferential()  )
        a.addObjects( self.aobjects['mesh'], [window] )

        return window

# -------------------------------
# Parent class Cortical Thickness
# -------------------------------

class ThicknessSnapBase(SnapBase):
    def __init__(self, preferences):
        SnapBase.__init__(self, preferences)

    def snap(self):
       from PyQt4 import Qt
       choice, ok_choice = Qt.QInputDialog.getItem(None,
           'hemi or white ?', 'hemi/white',
           ['hemi', 'white'], 0, False)
       if ok_choice:
          if choice == 'hemi':
              snap = HemiThicknessSnapBase(self.preferences)
          elif choice == 'white':
              snap = WhiteThicknessSnapBase(self.preferences)
          c, ok_c = Qt.QInputDialog.getItem(None,
              'single or multi view ?', 'single/multi',
              ['single', 'multi'], 0, False)
          if ok_c:
              if c == 'single':
                 snap.views = {'left': ['left'], 'right': ['right']}
              elif c == 'multi':
                 snap.views = {'left': ['left', 'right', 'back left', 'front left', 'left top', 'right bottom'],
                   'right' : ['right', 'left', 'back right', 'front right', 'right top', 'left bottom']}
              snap.snap_base(None, qt_app = self.qt_app)

    def get_list_diskitems(self, verbose = True):

        from brainvisa.snapbase.snapbase.diskItemBrowser import SnapBaseItemBrowser
        import string
        dictdata = []
        import neuroHierarchy, neuroProcesses

        id_types = ['FreesurferThicknessType', 'ResampledFreesurferThicknessType', 'FreesurferCurvType', 'ResampledFreesurferCurvType', 'Cortical thickness', 'FreesurferGyri', 'ResampledGyri' ]
        d = SnapBaseItemBrowser(neuroHierarchy.databases, required={'_type': id_types})
        res = d.exec_()
        if res == d.Accepted:
          for each in d.getValues():
              id_type = neuroHierarchy.databases.createDiskItemFromFileName(each.fullPath()).type.name

              print id_type[:9]
              if id_type in ['FreesurferThicknessType', 'FreesurferCurvType', 'FreesurferGyri']:
                rdi = neuroHierarchy.ReadDiskItem('%s'%({'hemi' : 'Pial', 'white' : 'White'}[self.preferences['mesh']]), neuroProcesses.getAllFormats())
              elif id_type[:9] == 'Resampled':
                rdi = neuroHierarchy.ReadDiskItem('%s'%({'hemi' : 'AimsPial', 'white' : 'AimsWhite'}[self.preferences['mesh']]), neuroProcesses.getAllFormats())
              elif id_type in ['Cortical thickness']:
                rdi = neuroHierarchy.ReadDiskItem('Hemisphere %sMesh'%({'hemi' : '', 'white' : 'White '}[self.preferences['mesh']]), neuroProcesses.getAllFormats())


              mesh = rdi.findValue(each)
              dictdata.append(((each.get('subject'), each.get('protocol')),
                 {'type' : each.get('_type'),
                  'mesh' : mesh,
                  'tex' : each}) )

        self.preferences.pop('mesh')

        return dictdata


    def get_views_of_interest(self):
        views = {}
        side = self.get_current_side()
        current_views = self.views[side]

        views['3D'] =[self.view_quaternions[view_name]
            for view_name in current_views]
        return views

    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        mesh = aims.read(diskitems['mesh'].fileName())
        tex = aims.read(diskitems['tex'].fileName())
        side = diskitems['mesh'].get('side')

        return mesh, tex

    def set_viewer(self, data, w):
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')
        mesh, tex = data
        tex_type = self.current_diskitems['tex'].type.name
        self.aobjects['mesh'] = a.toAObject(mesh)
        self.aobjects['mesh'].releaseAppRef()
        self.aobjects['tex'] = a.toAObject(tex)
        self.aobjects['tex'].releaseAppRef()
        if tex_type in ['FreesurferThicknessType', 'ResampledFreesurferThicknessType', 'Cortical thickness']:
            self.aobjects['tex'].setPalette(a.getPalette('Blue-Red-fusion'), minVal = 0.0, maxVal = 5.0, absoluteMode=True)
        elif tex_type in ['FreesurferCurvType', 'ResampledFreesurferCurvType', 'Curvature Texture', 'White Curvature Texture']:
            self.aobjects['tex'].setPalette(a.getPalette('Blue-Red'), minVal = -1.0, maxVal = 1.0, absoluteMode=True)
        elif tex_type in ['FreesurferGyri', 'ResampledGyri']:
            self.aobjects['tex'].setPalette(a.getPalette('Blue-Red'), minVal = 0.0, maxVal = 35.0, absoluteMode=True)

        # Load in Anatomist window
        window = a.AWindow(a, w)

        self.aobjects['fusion'] = a.fusionObjects([self.aobjects['mesh'], self.aobjects['tex']], method='FusionTexSurfMethod')
        a.addObjects(self.aobjects['fusion'], [window])

        return window

#-------------------------------------
# Derived classes Cortical Thickness
#-------------------------------------

class HemiThicknessSnapBase(ThicknessSnapBase):
    def __init__(self, preferences):
        ThicknessSnapBase.__init__(self, preferences)
        self.preferences['mesh'] = 'hemi'


class WhiteThicknessSnapBase(ThicknessSnapBase):
    def __init__(self, preferences):
        ThicknessSnapBase.__init__(self, preferences)
        self.preferences['mesh'] = 'white'


#-------------------------------------
# Mesh Cut
#-------------------------------------

class MeshCutSnapBase(SnapBase):
    def __init__(self, preferences):
      SnapBase.__init__(self, preferences)
      self._do_slice_rendering = True

    def get_list_diskitems(self, verbose = True):

        from brainvisa.snapbase.snapbase.diskItemBrowser import SnapBaseItemBrowser

        dictdata = []
        import neuroHierarchy, neuroProcesses

        id_types = ['Hemisphere Mesh'] #, 'Hemisphere White Mesh', 'Pial', 'White', 'AimsPial', 'AimsWhite']
        d = SnapBaseItemBrowser(neuroHierarchy.databases, required={'_type': id_types, 'side' : 'left'})
        res = d.exec_()
        if res == d.Accepted:
          for each in d.getValues():
              rdi = neuroHierarchy.ReadDiskItem('Transform Raw T1 MRI to Talairach-AC/PC-Anatomist', neuroProcesses.getAllFormats())
              transform = rdi.findValue(each)
              rdi = neuroHierarchy.ReadDiskItem('T1 MRI Bias Corrected', neuroProcesses.getAllFormats())
              mri = rdi.findValue(each)
              rdi = neuroHierarchy.ReadDiskItem('Split Brain Mask', neuroProcesses.getAllFormats())
              split = rdi.findValue(each)
              rdi = neuroHierarchy.ReadDiskItem('Hemisphere Mesh', neuroProcesses.getAllFormats(), requiredAttributes = {'side': 'right'})
              right_hemi = rdi.findValue(each)
              rdi = neuroHierarchy.ReadDiskItem('Hemisphere White Mesh', neuroProcesses.getAllFormats(), requiredAttributes = {'side': 'left'})
              left_white = rdi.findValue(each)
              rdi = neuroHierarchy.ReadDiskItem('Hemisphere White Mesh', neuroProcesses.getAllFormats(), requiredAttributes = {'side': 'right'})
              right_white = rdi.findValue(each)
              rdi = neuroHierarchy.ReadDiskItem('Left Grey White Mask', neuroProcesses.getAllFormats())
              left_gw = rdi.findValue(each)
              rdi = neuroHierarchy.ReadDiskItem('Right Grey White Mask', neuroProcesses.getAllFormats())
              right_gw = rdi.findValue(each)
              dictdata.append(((each.get('subject'), each.get('protocol')),
                 {'mri' : mri,
                  'split' : split,
                  'left hemi' : each,
                  'right hemi' : right_hemi,
                  'left white' : left_white,
                  'right white' : right_white,
                  'left mask' : left_gw,
                  'right mask': right_gw,
                  'transform' : transform}) )

        return dictdata

    def get_slices_of_interest(self, data):

        from brainvisa.snapbase.snapbase import detect_slices_of_interest
        slices = {}
        directions = ['C', 'A']

        # Unpacking data
        left_hemi, right_hemi, left_white, right_white, left_mask, right_mask, mri, trm_file = data

        left_slices_minmax = detect_slices_of_interest(left_mask, directions)
        right_slices_minmax = detect_slices_of_interest(right_mask, directions)
        voxel_size = mri.header()['voxel_size']
        print voxel_size, left_mask.header()['voxel_size']

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

        left_hemi = aims.read(diskitems['left hemi'].fileName())
        right_hemi = aims.read(diskitems['right hemi'].fileName())
        left_white = aims.read(diskitems['left white'].fileName())
        right_white = aims.read(diskitems['right white'].fileName())
        mri = aims.read(diskitems['mri'].fileName())
        left_mask = aims.read(diskitems['left mask'].fileName())
        right_mask = aims.read(diskitems['right mask'].fileName())

        if not diskitems['transform'] is None:
           trm_file = diskitems['transform'].fileName()
        else:
           trm_file = None

        return left_hemi, right_hemi, left_white, right_white, left_mask, right_mask, mri, trm_file

    def set_viewer(self, data, w):
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        left_hemi, right_hemi, left_white, right_white, left_mask, right_mask, mri, transform = data
        self.aobjects['left hemi'] = a.toAObject(left_hemi)
        self.aobjects['left hemi'].releaseAppRef()
        self.aobjects['left hemi'].assignReferential(a.centralReferential())
        self.aobjects['right hemi'] = a.toAObject(right_hemi)
        self.aobjects['right hemi'].releaseAppRef()
        self.aobjects['right hemi'].assignReferential(a.centralReferential())
        self.aobjects['left white'] = a.toAObject(left_white)
        self.aobjects['left white'].releaseAppRef()
        self.aobjects['left white'].assignReferential(a.centralReferential())
        self.aobjects['right white'] = a.toAObject(right_white)
        self.aobjects['right white'].releaseAppRef()
        self.aobjects['right white'].assignReferential(a.centralReferential())
        self.aobjects['mri'] = a.toAObject(mri)
        self.aobjects['mri'].releaseAppRef()
        self.aobjects['mri'].assignReferential(a.centralReferential())

        ana_left_mask = a.toAObject(left_mask)
        ana_right_mask = a.toAObject(right_mask)
        for each in ana_left_mask, ana_right_mask:
            each.releaseAppRef()

        # Fusion of the two masks
        fusion_mask = a.fusionObjects( [ana_left_mask, ana_right_mask], method='Fusion2DMethod' )

        palette = a.getPalette('RAINBOW')
        fusion_mask.setPalette( palette )
        self.aobjects['fusion'] = a.fusionObjects( [self.aobjects['mri'], fusion_mask], method='Fusion2DMethod' )
        a.execute("Fusion2DParams", object=self.aobjects['fusion'],
            mode='linear', rate = 0.7, reorder_objects = [ self.aobjects['mri'], fusion_mask ] )

        if not transform is None:
           a.loadTransformation(transform, self.ref, a.centralReferential())

        self.aobjects['left hemi cut'] = a.fusionObjects( [self.aobjects['left hemi']], method='Fusion2DMeshMethod' )
        self.aobjects['left hemi cut'].setMaterial(diffuse = [1, 1, 0.1, 0.7])
        self.aobjects['left hemi cut'].assignReferential(a.centralReferential())
        self.aobjects['right hemi cut'] = a.fusionObjects( [self.aobjects['right hemi']], method='Fusion2DMeshMethod' )
        self.aobjects['right hemi cut'].setMaterial(diffuse = [1, 1, 0.1, 0.7])
        self.aobjects['right hemi cut'].assignReferential(a.centralReferential())
        self.aobjects['left white cut'] = a.fusionObjects( [self.aobjects['left white']], method='Fusion2DMeshMethod' )
        self.aobjects['left white cut'].setMaterial(diffuse = [0.1, 1.0, 1.0, 0.7])
        self.aobjects['left white cut'].assignReferential(a.centralReferential())
        self.aobjects['right white cut'] = a.fusionObjects( [self.aobjects['right white']], method='Fusion2DMeshMethod' )
        self.aobjects['right white cut'].setMaterial(diffuse = [0.1, 1.0, 1.0, 0.7])
        self.aobjects['right white cut'].assignReferential(a.centralReferential())

        # Load in Anatomist window
        window = a.AWindow(a, w)
        window.assignReferential( a.centralReferential()  )
        a.addObjects( self.aobjects['left hemi cut'], [window] )
        a.addObjects( self.aobjects['right hemi cut'], [window] )
        a.addObjects( self.aobjects['left white cut'], [window] )
        a.addObjects( self.aobjects['right white cut'], [window] )
        a.addObjects( self.aobjects['fusion'], [window] )
        a.addObjects( self.aobjects['mri'], [window] )

        return window
