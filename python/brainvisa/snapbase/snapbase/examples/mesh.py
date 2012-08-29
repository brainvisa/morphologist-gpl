# -*- coding: utf-8 -*-
from brainvisa.snapbase.snapbase import SnapBase

# -------------------------
# Parent class MeshSnapBase
# -------------------------

class MeshSnapBase(SnapBase):
    def __init__(self, output_path):
        SnapBase.__init__(self, output_path)

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
            # Retrieves Left Hemisphere White Meshes
            options.update({'_type' : self.data_type,
                            'subject' : subject,
                            'protocol' : protocol})
            meshes = [mesh for mesh in self.db.findDiskItems(**options)]

            if len (meshes) == 1 :
                # Retrieves the corresponding transform if existing
                rdi = neuroHierarchy.ReadDiskItem('Transform Raw T1 MRI to Talairach-AC/PC-Anatomist', neuroProcesses.getAllFormats())
                transform = rdi.findValue(meshes[0])

                # Here according to given options, ambiguity should be resolved.
                # If more than one mesh, then some attributes are probably misgiven.
                if transform:
                    dictdata[(subject, protocol)] = {'type' : self.data_type,
                        'mesh' : meshes[0],
                        'transform' : transform}
            else:
                if verbose:
                    print '(subject %s, protocol %s) error in retrieving diskitems'\
                        %(subject, protocol)
        return dictdata

    def get_views_of_interest(self):
        ''' Not implemented '''
        raise NotImplementedError


    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        mesh = aims.read(diskitems['mesh'].fileName())
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
    def __init__(self, output_path):
        SnapBase.__init__(self, output_path)

    def get_dictdata(self, selected_attributes, verbose=True):

        import string
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
            # Retrieves Left Hemisphere White Meshes
            options.update({'_type' : '%s Hemisphere %sMesh'%(string.capitalize(self.preferences['side']), {'hemi' : '', 'white' : 'White '}[self.preferences['mesh']]),
                            'subject' : subject,
                            'protocol' : protocol,
                            'side' : self.preferences['side']})
            meshes = [mesh for mesh in self.db.findDiskItems(**options)]
            print options, meshes

            if len (meshes) == 1 :
                # Retrieves the corresponding transform if existing
                rdi = neuroHierarchy.ReadDiskItem('Transform Raw T1 MRI to Talairach-AC/PC-Anatomist', neuroProcesses.getAllFormats())
                transform = None #rdi.findValue(meshes[0])

                rdi = neuroHierarchy.ReadDiskItem('Cortical thickness', neuroProcesses.getAllFormats(), requiredAttributes={'side':self.preferences['side'], 'mesh': self.preferences['mesh']})
                tex = rdi.findValue(meshes[0])
                print meshes[0], tex

                # Here according to given options, ambiguity should be resolved.
                # If more than one mesh, then some attributes are probably misgiven.
                #if transform and tex:
                if tex:
                    dictdata[(subject, protocol)] = {'type' : self.data_type,
                        'mesh' : meshes[0],
                        'tex' : tex,
                        'transform' : transform}
            else:
                if verbose:
                    print '(subject %s, protocol %s) error in retrieving diskitems'\
                        %(subject, protocol)
        return dictdata

    def get_views_of_interest(self):
        views = {}
        views['3D'] =[self.view_quaternions[view_name]
            for view_name in [self.preferences['side']]] #[{'left':'right', 'right':'left'}[self.preferences['side']]]]
        return views

    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        mesh = aims.read(diskitems['mesh'].fileName())
        tex = aims.read(diskitems['tex'].fileName())

        return mesh, tex, None # diskitems['transform'].fileName()

    def set_viewer(self, data, w):
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        mesh, tex, transform = data
        self.aobjects['mesh'] = a.toAObject(mesh)
        self.aobjects['mesh'].releaseAppRef()
#        self.aobjects['mesh'].assignReferential(self.ref)
        self.aobjects['tex'] = a.toAObject(tex)
        self.aobjects['tex'].releaseAppRef()
#        self.aobjects['tex'].assignReferential(self.ref)
        self.aobjects['tex'].setPalette(a.getPalette('Blue-Red'), minVal = 1.0, maxVal = 5.0, absoluteMode=True)
#        a.loadTransformation(transform, self.ref, a.centralReferential())

        # Load in Anatomist window
        window = a.AWindow(a, w)
#        window.assignReferential( a.centralReferential()  )

        self.aobjects['fusion'] = a.fusionObjects([self.aobjects['mesh'], self.aobjects['tex']], method='FusionTexSurfMethod')
#        self.aobjects['fusion'].assignReferential(self.ref)
        a.addObjects(self.aobjects['fusion'], [window])

        return window

#-------------------------------------
# Derived classes Cortical Thickness
#-------------------------------------

class LeftHemiThicknessSnapBase(ThicknessSnapBase):
    def __init__(self, output_path):
        ThicknessSnapBase.__init__(self, output_path)
        self.preferences['side'] = 'left'
        self.preferences['mesh'] = 'hemi'
        self.data_type = 'Cortical Thickness'


class RightHemiThicknessSnapBase(ThicknessSnapBase):
    def __init__(self, output_path):
        ThicknessSnapBase.__init__(self, output_path)
        self.preferences['side'] = 'right'
        self.preferences['mesh'] = 'hemi'
        self.data_type = 'Cortical Thickness'


class LeftWhiteThicknessSnapBase(ThicknessSnapBase):
    def __init__(self, output_path):
        ThicknessSnapBase.__init__(self, output_path)
        self.preferences['side'] = 'left'
        self.preferences['mesh'] = 'white'
        self.data_type = 'Cortical Thickness'


class RightWhiteThicknessSnapBase(ThicknessSnapBase):
    def __init__(self, output_path):
        ThicknessSnapBase.__init__(self, output_path)
        self.preferences['side'] = 'right'
        self.preferences['mesh'] = 'white'
        self.data_type = 'Cortical Thickness'

#-----------------------------------------
# Derived classes MeshSnapBase
#-----------------------------------------

class WhiteMeshSnapBase(MeshSnapBase):
    def __init__(self, output_path):
        MeshSnapBase.__init__(self, output_path)


class HemisphereMeshSnapBase(MeshSnapBase):
    def __init__(self, output_path):
        MeshSnapBase.__init__(self, output_path)

    def get_views_of_interest(self):
        views = {}
        views['3D'] =[self.view_quaternions[view_name]
            for view_name in [self.preferences['side']]]
        return views


class LeftWhiteMeshSnapBase(WhiteMeshSnapBase):
    def __init__(self, output_path):
        WhiteMeshSnapBase.__init__(self, output_path)
        self.preferences['side'] = 'left'
        self.data_type = 'Left Hemisphere White Mesh'

    def get_views_of_interest(self):
        views = {}
        views['3D'] = [self.view_quaternions[view_name]
            for view_name in ['left', 'right', 'back left', 'front left',
                'right bottom']]
        return views


class RightWhiteMeshSnapBase(WhiteMeshSnapBase):
    def __init__(self, output_path):
        WhiteMeshSnapBase.__init__(self, output_path)
        self.preferences['side'] = 'right'
        self.data_type = 'Right Hemisphere White Mesh'

    def get_views_of_interest(self):
        views = {}
        views['3D'] = [self.view_quaternions[view_name]
            for view_name in ['right', 'left', 'back right', 'front right',
                'left bottom']]
        return views


class LeftHemisphereMeshSnapBase(HemisphereMeshSnapBase):
    def __init__(self, output_path):
        HemisphereMeshSnapBase.__init__(self, output_path)
        self.data_type = 'Left Hemisphere Mesh'


class RightHemisphereMeshSnapBase(HemisphereMeshSnapBase):
    def __init__(self, output_path):
        HemisphereMeshSnapBase.__init__(self, output_path)
        self.data_type = 'Right Hemisphere Mesh'


