from capsul.api import Process
import traits.api as traits
from soma.qt_gui.qtThread import MainThreadLife, QtThreadCall
import threading


class MainThreadList:
    def __init__(self, lock, *args, **kwargs):
        self.lock = lock
        self.list = MainThreadLife(list(*args, **kwargs))

    def append(self, item):
        with self.lock:
            self.list.ref().append(item)

    def insert(self, index, item):
        with self.lock:
            self.list.ref().insert(index, item)

    def remove(self, item):
        with self.lock:
            self.list.ref().remove(item)

    def clear(self):
        with self.lock:
            self.list.ref().clear()

    def copy(self):
        copy = MainThreadList(self.lock)
        with self.lock:
            copy.list = MainThreadLife(list(self.list.ref()))

    def extend(self, other):
        with self.lock:
            self.list.ref().extnd(other.list.ref())

    def __getitem__(self, index):
        with self.lock:
            return self.list.ref()[index]

    def __del__(self):
        with self.lock:
            del self.list


class QtViewer(Process):
    roles = ['qc', 'viewer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_trait('main_input', traits.File())

    def _run_process(self):
        result = MainThreadList(threading.RLock())
        QtThreadCall().push(self.exec_mainthread, result)
        return result

    def exec_mainthread(self, result):
        pass  # not implemented in the base class


class AWindowViewer(QtViewer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_trait('view_type', traits.Str())
        self.view_type = 'Axial'

    def exec_mainthread(self, result):
        import anatomist.api as ana

        a = ana.Anatomist()
        obj = a.loadObject(self.main_input)
        w = a.createWindow(self.view_type)
        w.addObjects(obj)

        with result.lock:
            result.list.ref().extend([w, obj])


class AnaT1MRIViewer(AWindowViewer):
    pass


class AnaPialMeshViewer(AWindowViewer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view_type = '3D'


class AnaWhiteMeshViewer(AWindowViewer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view_type = '3D'


class AnaSulciViewer(AWindowViewer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_trait('white_mesh', traits.File(optional=True))
        self.add_trait('pial_mesh', traits.File(optional=True))
        self.add_trait('mri_corrected', traits.File(optional=True))
        self.add_trait('load_mri', traits.Bool())
        self.add_trait('nomenclature_property',
                       traits.Enum(['label', 'name']))
        self.add_trait('mesh_opacity', traits.Float())
        self.add_trait('two_windows', traits.Bool())

        self.view_type = '3D'
        self.load_mri = False
        self.mesh_opacity = 0.9
        self.two_windows = False

    def exec_mainthread(self, result):
        import anatomist.api as ana
        from soma import aims

        a = ana.Anatomist()
        nom_file = aims.carto.Paths.findResourceFile(
            'nomenclature/hierarchy/sulcal_root_colors.hie')
        nomenc = a.loadObject(nom_file)
        result.append(nomenc)
        super().exec_mainthread(result)

        graph = result[-1]
        a.execute('GraphDisplayProperties', objects=[graph],
                  nomenclature_property=self.nomenclature_property)
        if self.load_mri and self.mri_corrected:
            anat = a.loadObject(self.mri_corrected)
            result.append(anat)
        mesh = None
        if self.white_mesh:
            mesh = a.loadObject(self.white_mesh, duplicate=True)
            result.append(mesh)
        elif self.pial_mesh:
            mesh = a.loadObject(self.pial_mesh, duplicate=True)
            result.append(mesh)
        win3 = result[1]
        graphRef = graph.referential
        win3.assignReferential(graphRef)
        if mesh is not None:
            if self.mesh_opacity < 1.:
                mesh.setMaterial(diffuse=[0.8, 0.8, 0.8, self.mesh_opacity])
            win3.addObjects([mesh])
            if self.two_windows:
                win2 = a.createWindow('3D')
                win2.assignReferential(graphRef)
                result.append(win2)
                win2.addObjects([graph])
            else:
                win2 = win3
        else:
            win2 = win3
        if self.load_mri:
            if self.mri_corrected is not None:
                win2.addObjects([anat])
