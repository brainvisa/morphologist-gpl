from brainvisa.snapbase.snapbase import SnapBase

class MeshSnapBase(SnapBase):
    def __init__(self, output_path):
        SnapBase.__init__(self, output_path)

    def get_list_diskitems(self, db, general_options = {}, verbose=True):

        import neuroProcesses
        import neuroHierarchy

        dictdata = {}

        # Checking for ambiguity between diskitems (acquisition, ...)
        options = {'_type' : 'T1 MRI Bias Corrected',
                   'subject' : '*'} #,
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
            # Retrieves Left Hemisphere White Meshes
            options.update({'_type' : self.data_type,
                            'subject' : subject,
                            'protocol' : protocol})
            meshes = [mesh for mesh in db.findDiskItems(**options)]

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


class WhiteMeshSnapBase(MeshSnapBase):
    def __init__(self, output_path):
        MeshSnapBase.__init__(self, output_path)



class HemisphereMeshSnapBase(MeshSnapBase):
    def __init__(self, output_path):
        MeshSnapBase.__init__(self, output_path)

class LeftWhiteMeshSnapBase(WhiteMeshSnapBase):
    def __init__(self, output_path):
        WhiteMeshSnapBase.__init__(self, output_path)
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

    def get_views_of_interest(self):
        views = {}
        views['3D'] =[self.view_quaternions[view_name]
            for view_name in ['left']]
        return views


class RightHemisphereMeshSnapBase(HemisphereMeshSnapBase):
    def __init__(self, output_path):
        HemisphereMeshSnapBase.__init__(self, output_path)
        self.data_type = 'Right Hemisphere Mesh'

    def get_views_of_interest(self):
        views = {}
        views['3D'] =[self.view_quaternions[view_name]
            for view_name in ['right']]
        return views

