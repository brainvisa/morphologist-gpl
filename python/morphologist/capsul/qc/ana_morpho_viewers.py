from capsul.api import Process
import traits.api as traits
from soma.qt_gui.qtThread import MainThreadLife, QtThreadCall
import threading
import subprocess
import os


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


class QtDataEditor(Process):
    roles = ['qc', 'editor']

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
        if not hasattr(self, 'block'):
            self.block = None

    def exec_mainthread(self, result):
        import anatomist.api as ana

        a = ana.Anatomist()
        obj = a.loadObject(self.main_input)
        w = a.createWindow(self.view_type, block=self.block)
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


class HistoAnalysisViewer(QtViewer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_trait('histo', traits.File())

    def _run_process(self):
        from brainvisa.morphologist.qt4gui import histo_analysis_widget

        self.hdata = histo_analysis_widget.load_histo_data(
            self.main_input, self.histo)
        return super()._run_process()

    def exec_mainthread(self, result):
        from brainvisa.morphologist.qt4gui import histo_analysis_widget
        from soma.qt_gui.qt_backend import QtCore, QtWidgets

        hwid = histo_analysis_widget.HistoAnalysisWidget(None)
        hwid.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        hwid.show_toolbar(True)
        hdata = self.hdata
        del self.hdata
        hwid.set_histo_data(hdata, nbins=100)
        hwid.layout().addWidget(QtWidgets.QLabel(
            '<table><tr><td>Gray peak: </td><td><b>%.1f</b></td>'
            '<td> , std: </td><td><b>%.1f</b></td></tr>'
            '<tr><td>White peak: </td><td><b>%.1f</b></td>'
            '<td> , std: </td><td><b>%.1f</b></td></tr></table>'
            % (hdata.han[0][0], hdata.han[0][1], hdata.han[1][0],
               hdata.han[1][1]),
            hwid))
        hwid.draw_histo()
        hwid.show()
        result.append(hwid)


class HistoAnalysisEditor(QtDataEditor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_trait('histo', traits.File())
        self.add_trait('mri_corrected', traits.File())

    def _run_process(self):
        from brainvisa.morphologist.qt4gui import histo_analysis_widget

        self.hdata = histo_analysis_widget.load_histo_data(
            self.main_input, self.histo)
        return super()._run_process()

    def exec_mainthread(self, result):
        # from brainvisa.morphologist.qt4gui import histo_analysis_editor
        # patch to use brainvisa.anatomist instead of the core anatomist
        # histo_analysis_editor.anatomist = anatomist
        from brainvisa.morphologist.qt4gui.histo_analysis_editor \
            import create_histo_editor

        hdata = self.hdata
        del self.hdata
        hwid = create_histo_editor(hdata, self.mri_corrected)

        hwid.show()
        result.append(hwid)


# code taken from brainvisa.anatomist
def viewBias(fileRef, forceReload=False, wintype="Coronal",
             hanfile=None, parent=None):
    """
    Loads an image, opens it in a new window in the object's
    referential. A
    palette is assigned to the object (Rainbow2) in order to see the
    bias.

    Parameters
    ----------
    fileRef: string or ReadDiskItem
        file name for the bias corrected image
    forceReload: boolean
        if True, the image is reloaded if already in memory.
    wintype: string
        "Axial", "Coronal", "Sagittal", "3D" (or other)
    hanfile: string or ReadDiskItem
        optional file name for histogram analysis file. If present it
        will be used to set palette bounds.
    parent: QWidget or anatomist block
        parent widget or block
    """
    import anatomist.api as ana
    from soma.qt_gui.qt_backend import QtWidgets

    a = ana.Anatomist()
    object = a.loadObject(fileRef, duplicate=True)
    object.setPalette(a.getPalette("Rainbow2"))
    if isinstance(parent, a.AWindowsBlock):
        window = a.createWindow(wintype, block=parent)
    else:
        window = a.createWindow(wintype)
    if isinstance(parent, QtWidgets.QWidget):
        mainThread = QtThreadCall()
        mainThread.push(window.getInternalRep().reparent, parent)
    window.assignReferential(object.referential)

    if hanfile is not None and (hasattr(hanfile, 'fullPath')
                                or os.path.exists(hanfile)):

        def load_histo_analysis(hanfile):
            '''parse histo analysis file (.han) to extract gray and
            white mean/std.
            Returns a tuple in the following shape:
            ( ( gray_mean, gray_stdev ), ( white_mean, white_stdev ) )
            '''
            import re
            r = re.compile(
                '^.*mean:\\s*(-?[0-9]+(\\.[0-9]*)?)\\s*sigma:\\s'
                '(-?[0-9]+(\\.[0-9]*)?)\\s*$')
            gmean, gsigma, wmean, wsigma = None, None, None, None
            with open(hanfile) as f:
                for l in f:
                    l = l.strip()
                    if l.startswith('gray:'):
                        m = r.match(l)
                        if m:
                            gmean = float(m.group(1))
                            gsigma = float(m.group(3))
                    elif l.startswith('white:'):
                        m = r.match(l)
                        if m:
                            wmean = float(m.group(1))
                            wsigma = float(m.group(3))
            return [gmean, gsigma], [wmean, wsigma]

        if hasattr(hanfile, 'fullPath'):
            hanfile = hanfile.fullPath()
        try:
            grey, white = load_histo_analysis(hanfile)
            object.setPalette(minVal=max(grey[0] - grey[1] * 8, 0),
                              maxVal=white[0] + white[1] * 3,
                              absoluteMode=True)
        except Exception:
            print('Warning: histogram could not be read:', hanfile)

    window.addObjects([object])
    return {"object": object, "window": window, "file": fileRef}


class AnaBiasCorrectionViewer(AWindowViewer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_trait('t1mri', traits.File(optional=True))
        self.add_trait('histo_analysis', traits.File(optional=True))

    def _run_process(self):
        import anatomist.api as ana

        a = ana.Anatomist()
        self.block = a.createWindowsBlock()
        return super()._run_process()

    def exec_mainthread(self, result):
        if self.t1mri is not None:
            result.append(
                viewBias(self.t1mri, forceReload=True, wintype="Coronal",
                         hanfile=self.histo_analysis, parent=self.block))
        result.append(
            viewBias(self.main_input, forceReload=True, wintype="Coronal",
                     hanfile=self.histo_analysis, parent=self.block))


class KillablePopen:
    def __init__(self, popen):
        self.popen = popen

    def __del__(self):
        self.popen.terminate()
        self.popen.wait(5)
        self.popen.kill()
        self.popen.communicate()
        self.popen.wait()


class PDFViewer(Process):
    roles = ['qc', 'viewer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_trait('main_input', traits.File())

    def _run_process(self):
        result = MainThreadList(threading.RLock())
        cmd = ['bv_pdf_viewer', self.main_input]
        result.append(KillablePopen(subprocess.Popen(cmd)))
        return result
