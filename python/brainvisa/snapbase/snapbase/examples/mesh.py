# -*- coding: utf-8 -*-
from brainvisa.snapbase.snapbase import SnapBase

# -------------------------
# Parent class MeshSnapBase
# -------------------------

class MeshSnapBase(SnapBase):
    def __init__(self, preferences):
        SnapBase.__init__(self, preferences)

    def get_list_diskitems(self, verbose = True):

        from brainvisa.snapbase.snapbase.diskItemBrowser import SnapBaseItemBrowser

        dictdata = []
        import neuroHierarchy, neuroProcesses

        id_type = 'Hemisphere %sMesh'%({'HemisphereMeshSnapBase': '', 'WhiteMeshSnapBase': 'White '}[self.__class__.__name__])
        d = SnapBaseItemBrowser(neuroHierarchy.databases, required={'_type': id_type})
        res = d.exec_()
        for each in d.getValues():
            rdi = neuroHierarchy.ReadDiskItem('Transform Raw T1 MRI to Talairach-AC/PC-Anatomist', neuroProcesses.getAllFormats())
            transform = rdi.findValue(each)
            dictdata.append(((each.get('subject'), each.get('protocol')),
               {'type' : id_type,
                'mesh' : each,
                'transform' : transform}) )

        return dictdata


    def get_views_of_interest(self):
        ''' Not implemented '''
        raise NotImplementedError


    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        mesh = aims.read(diskitems['mesh'].fileName())
        side = diskitems['mesh'].get('side')
        self.preferences['side'] = side

        return mesh, diskitems['transform'].fileName()

    def set_viewer(self, data, w):
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        mesh, transform = data
        self.aobjects['mesh'] = a.toAObject(mesh)
        self.aobjects['mesh'].releaseAppRef()
        self.aobjects['mesh'].assignReferential(self.ref)
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

    def get_list_diskitems(self, verbose = True):

        from brainvisa.snapbase.snapbase.diskItemBrowser import SnapBaseItemBrowser
        import string
        dictdata = []
        import neuroHierarchy, neuroProcesses

        id_types = ['FreesurferThicknessType', 'ResampledFreesurferThicknessType', 'FreesurferCurvType', 'ResampledFreesurferCurvType', 'Cortical thickness', 'FreesurferGyri', 'ResampledGyri' ]
        d = SnapBaseItemBrowser(neuroHierarchy.databases, required={'_type': id_types})
        res = d.exec_()
        for each in d.getValues():
            id_type = neuroHierarchy.databases.createDiskItemFromFileName(each.fullPath()).type.name
            print id_type[:9]
            #rdi = neuroHierarchy.ReadDiskItem('Hemisphere %sMesh'%({'hemi' : '', 'white' : 'White '}[self.preferences['mesh']]), neuroProcesses.getAllFormats())
            if id_type in ['FreeSurferThicknessType', 'FreesurferCurvType', 'FreesurferGyri']:
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

        return dictdata


    def get_views_of_interest(self):
        views = {}

        views['3D'] =[self.view_quaternions[view_name]
            for view_name in [self.preferences['side']]] #[{'left':'right', 'right':'left'}[self.preferences['side']]]]
#            for view_name in [{'left':'right', 'right':'left'}[self.preferences['side']]]]
        return views

    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        mesh = aims.read(diskitems['mesh'].fileName())
        tex = aims.read(diskitems['tex'].fileName())
        side = diskitems['mesh'].get('side')
        self.preferences['side'] = side
        tex_type = diskitems['tex'].type.name
        self.preferences['tex_type'] = tex_type

        return mesh, tex, None, tex_type # diskitems['transform'].fileName()

    def set_viewer(self, data, w):
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')
        mesh, tex, transform, tex_type = data
        self.aobjects['mesh'] = a.toAObject(mesh)
        self.aobjects['mesh'].releaseAppRef()
        self.aobjects['tex'] = a.toAObject(tex)
        self.aobjects['tex'].releaseAppRef()
        if tex_type in ['FreesurferThicknessType', 'ResampledFreesurferThicknessType', 'Cortical thickness']:
            self.aobjects['tex'].setPalette(a.getPalette('Blue-Red'), minVal = 1.0, maxVal = 5.0, absoluteMode=True)
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


#-----------------------------------------
# Derived classes MeshSnapBase
#-----------------------------------------

class WhiteMeshSnapBase(MeshSnapBase):
    def __init__(self, preferences):
        MeshSnapBase.__init__(self, preferences)

    def get_views_of_interest(self):
        views = {}
        views['3D'] = [self.view_quaternions[view_name]
            for view_name in
                {'left': ['left', 'right', 'back left', 'front left', 'right bottom'],
                'right' : ['right', 'left', 'back right', 'front right', 'left bottom']}[self.preferences['side']]]
        return views


class HemisphereMeshSnapBase(MeshSnapBase):
    def __init__(self, preferences):
        MeshSnapBase.__init__(self, preferences)

    def get_views_of_interest(self):
        views = {}
        views['3D'] =[self.view_quaternions[view_name]
            for view_name in [self.preferences['side']]]
        return views


