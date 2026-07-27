# This is the generic version of a QC table process.
# See morphologist_qc_table (in Morphologist) for instance for an example
# of concrete use of it.
#
# By default, each data file is displayed using a "present/absent" status icon.
# It is possible to specialize the status on a type-by-type basis.
# To do so, the specialized process must register a status function in
# the status_for_type table. Typically:
#
# def get_qc_status(proc, di):
#     with open(di[1]) as f:
#         report = json.load(f)
#     stat = {
#         'OK': proc.statuses.OK,
#         'Warning': proc.statuses.WARNING,
#         'Suspicious': proc.statuses.SUSPICIOUS,
#         'Bad': proc.statuses.BAD,
#     }
#     status = report.get('status', 'Bad')
#     return stat[status]
#
# def execution(self, context):
#     self.proc = get_process_instance(
#         'morphologist.capsul.qc.database_qc_table')
#     self.proc.status_for_type[
#         'morphologist.capsul.morphologist.Morphologist.report_json'] \
#             = get_qc_status
#
#     return context.runProcess(self.proc, database=self.database, ...)
#

from capsul.api import Process, Pipeline
from capsul.attributes.completion_engine import ProcessCompletionEngine
from soma.wip.application.api import findIconFile
from soma.qt_gui.qtThread import MainThreadLife, QtThreadCall
from soma.qt_gui.qt_backend.Qt import QTableWidgetItem
from soma.qt_gui.qt_backend import Qt
from morphologist.capsul.qc import find_viewer
import traits.api as traits
import subprocess
import shutil
import numpy as np
import os
import os.path as osp
import tempfile
import glob
import sqlite3
import time
import datetime


wkhtmltopdf = shutil.which('wkhtmltopdf')


class statuses:
    OK = 0
    PRESENT = 1
    WARNING = 2
    SUSPICIOUS = 3
    BAD = 4
    ABSENT = 5
    # VALID_* for manually validated (marked OK)
    VALID_OK = 8
    VALID_PRESENT = 9
    VALID_WARNING = 10
    VALID_SUSPICIOUS = 11
    VALID_BAD = 12
    VALID_ABSENT = 13
    # INVALID_* for manually invalidated (marked bad)
    INVALID_OK = 16
    INVALID_PRESENT = 17
    INVALID_WARNING = 18
    INVALID_SUSPICIOUS = 19
    INVALID_BAD = 20
    INVALID_ABSENT = 21


class QSortingTabeWidgetItem(Qt.QTableWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sort_data = None

    def __lt__(self, other):
        if self.sort_data is not None \
                and getattr(other, 'sort_data', None) is not None:
            return (self.sort_data < other.sort_data)
        return super().__lt__(other)

    def __gt__(self, other):
        if self.sort_data is not None \
                and getattr(other, 'sort_data', None) is not None:
            return (self.sort_data > other.sort_data)
        return super().__gt__(other)


status_for_type = {}


class DatabaseQcTable(Process):

    roles = ['qc']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_trait('database', traits.Directory(optional=True))
        self.add_trait('fom', traits.Str(optional=True))
        self.add_trait('database_sqlite', traits.File(optional=True))
        self.add_trait('data_types', traits.ListStr())
        self.add_trait('data_filters', traits.ListStr())
        self.add_trait('keys', traits.ListStr())
        self.add_trait('type_labels', traits.ListStr())
        self.add_trait('output_file',
                       traits.File(allowed_extensions=['HTML', 'PDF file',
                                                       'CSV file'],
                                   output=True, optional=True))
        self.add_trait('index_status', traits.Enum(('False', 'Force', 'Use')))

        self.status_for_type = status_for_type
        self.statuses = statuses
        self.index_status = 'Use'
        # self.fom = 'morphologist-bids-2.0'

        # possibleTypes = [t.name for t in getAllDiskItemTypes()]

        self.keys = ['subject']
        sc = getattr(self, 'study_config', None)
        if sc is not None:
            self.database = sc.input_directory
            self.fom = sc.input_fom

    def _run_process(self):
        self.row_ids = {}
        self.elements = None
        self.db = None

        if self.database in (None, traits.Undefined, ''):
            sc = self.get_study_config()
            self.database = sc.input_directory
        if self.database_sqlite:
            self.db = sqlite3.connect(self.database_sqlite)
        if self.fom in (None, traits.Undefined, '') and self.db is not None:
            self.fom = list(self.db.execute('SELECT fom_name FROM fom'))[0][0]
        if self.fom in (None, traits.Undefined, ''):
            sc = self.get_study_config()
            self.fom = sc.input_fom
        # find data
        t0 = time.time()
        self.t0 = t0
        data = self.find_data()
        t1 = time.time()
        print('query/parse time:', datetime.timedelta(seconds=t1 - t0))

        if len(data) == 0:
            nrows = 0
        else:
            nrows = max([len(values[1]) for values in data])
        ncols = len(self.data_types)
        elements = [[None] * ncols]

        keys = self.keys
        row_ids = {}
        # [key_i]: {value: set(rows)}
        row_sets = [{} for s in range(len(keys))]
        row_ids_sets = [row_ids, row_sets, []]
        max_row = 0

        for elem_col, (dtype, items) in enumerate(data):
            # print('dtype:', dtype, ', items:', len(items))
            for item_d in items:
                # print('item_d:', item_d)
                item = item_d['attributes']
                key_vals = [item.get(att) for att in keys]
                row, row_id, changed_id = self.get_row(key_vals, row_ids_sets)
                # print('item', key_vals, ':', row, row_id, changed_id)
                if changed_id:
                    if row >= len(elements):
                        old_nrow = len(elements)
                        elements += [[None] * ncols
                                     for row in range(old_nrow, row + 1)]
                    max_row = max((max_row, row))
                element = elements[row][elem_col]
                if isinstance(element, list):
                    elements[row][elem_col].append(item_d)
                elif element is None:
                    elements[row][elem_col] = item_d
                else:
                    elements[row][elem_col] = [element, item_d]

        t2 = time.time()
        print('table building time:', datetime.timedelta(seconds=t2 - t1))

        nrows = max_row + 1
        old_nrow = len(elements)
        elements += [[None] * ncols for row in range(len(elements), nrows)]
        self.elements = elements
        self.row_ids = row_ids
        result = None

        if self.output_file:
            self.save()
        else:
            result = QtThreadCall().call(self.exec_mainthread)

        del self.db
        return result

    def find_items(self, dtype, dfilt):
        profile = False
        if profile:
            t0 = time.time()

        data = []
        engine = self.get_study_config().engine
        if not hasattr(engine, '_modules_data') \
                or 'fom' not in engine._modules_data:
            engine.load_modules(['fom', 'axon'])
        with engine.settings as session:
            config = session.config('fom', 'global')
            config.input_fom = self.fom
            config.output_fom = self.fom
            if self.database is not None:
                config.input_directory = self.database
                config.output_directory = self.database

        procname, param = dtype.rsplit('.', 1)

        # use a cached process with its completion to speed up
        # repeated parameters scan on the same process
        if not hasattr(self, '_cached_procs'):
            self._cached_procs = {}
        if procname in self._cached_procs:
            proc, cached_atts = self._cached_procs[procname]
        else:
            proc = engine.get_process_instance(procname)
            self._cached_procs[procname] = [proc, dfilt]
            cached_atts = None
        if cached_atts != dfilt:
            pc = ProcessCompletionEngine.get_completion_engine(proc)
            att = pc.get_attribute_values()
            for k, v in att.user_traits().items():
                val = '*'
                if k in dfilt:
                    val = dfilt[k]
                setattr(att, k, val)
            # print('completion values:', att.export_to_dict())
            pc.complete_parameters()
            self._cached_procs[procname][1] = dfilt

        if self.db is not None:
            return self.find_items_sqlite(proc, procname, param, dfilt)

        path_pat = getattr(proc, param)
        # print('path_pat:', path_pat)
        if profile: t1 = time.time(); print('    t1 (compl):', t1 - t0); t0 = t1
        paths = glob.glob(path_pat)
        if profile: t1 = time.time(); print('    t2 (glob) :', t1 - t0); t0 = t1
        for p in paths:
            for fom_type in ('input', 'output'):
                pta = engine._modules_data['fom']['fom_pta'][fom_type]
                attl = list(pta.parse_path(osp.relpath(p, self.database)))
                atts = None
                if len(attl) == 1:
                    atts = attl[0]
                else:
                    attl_filt = [item for item in attl
                                 if item[2]['fom_process'] == procname
                                 and item[2]['fom_parameter'] == param]
                    if len(attl_filt) != 0:
                        atts = attl_filt[0]
                    elif len(attl) != 0:
                        atts = attl[0]
                if atts is not None:
                    data.append({'attributes': atts[2], 'path': p})
                    break
        if profile: t1 = time.time(); print('    t3 (fom)  :', t1 - t0); t0 = t1

        return data

    def proc_param_names(self, proc, proname, param):
        names = []
        fallbacks = []
        fom = self.get_study_config().engine._modules_data[
            'fom']['all_foms'][self.fom]
        todo = []
        if isinstance(proc, Pipeline):
            node = proc.pipeline_node
        else:
            node = proc
        todo.append((node, proc.name, param, {}))
        while todo:
            node, procname, param, attr = todo.pop(0)
            # check for FOM-imposed attributes on the process
            fom_patterns = fom.patterns.get(procname)
            if fom_patterns is not None:
                pa = fom_patterns.get('.process_attributes', {})
                attr.update(pa)
            names.append((procname, param, attr))
            if isinstance(node, Process):
                break
            if hasattr(node, 'process'):
                fb = (node.process.name, param, attr)
                if fb not in fallbacks:
                    fallbacks.append(fb)
            plug = node.plugs[param]
            links = [plug.links_to, plug.links_from][int(plug.output)]
            for link in links:
                todo.append((link[2], f'{procname}.{link[0]}', link[1], attr))

        return names + [fb for fb in fallbacks if fb not in names]

    def find_items_sqlite(self, proc, procname, param, dfilt):
        data = []
        cols = [x[1] for x in self.db.execute('PRAGMA table_info(files)')]
        keys = ', '.join(cols)
        names = self.proc_param_names(proc, procname, param)
        for procname, param, att in names:
            dfilt2 = dict(dfilt)
            incompatible = False
            for k, v in att.items():
                if k in dfilt2 and dfilt2[k] != v:
                    incompatible = True
                    break
                dfilt2[k] = v
            if incompatible:
                continue
            where = ' AND '.join(f'({k} == "{v}" OR {k} IS NULL)'
                                 for k, v in dfilt2.items())
            where2 = [f'fom_process = "{procname}"',
                      f'fom_parameter = "{param}"']
            if where != '':
                where2.insert(0, where)
            sql = f'SELECT {keys} FROM files WHERE ' + ' AND '.join(where2)
            items = list(self.db.execute(sql))
            if len(items) == 0:
                continue  # look for next name
            for item in items:
                atts = {k: v for k, v in zip(cols, item) if v is not None}
                path = osp.join(self.database, atts['filename'])
                del atts['filename']
                data.append({'attributes': atts, 'path': path})
            break  # procname found, don't continue search

        return data

    def find_data(self):
        data = []
        profile = False
        if profile:
            import time
            print('find_data')
            t0 = time.time()

        for i, dtype in enumerate(self.data_types):
            if len(self.data_filters) > i or len(self.data_filters) == 1:
                ifilt = i
                if len(self.data_filters) == 1:
                    # broadcast filter
                    ifilt = 0
                filt = self.data_filters[ifilt]
                if filt == '':
                    dfilt = {}
                else:
                    dfilt = eval(filt)
            else:
                dfilt = {}
            items = self.find_items(dtype, dfilt)
            data.append((dtype, items))
            # print(dtype, ':', len(items), 'items')
            if profile: print('time:', time.time() - t0)

        return data

    def get_row(self, key_vals, row_ids_sets):
        # print('get_row for:', key_vals)
        row_id = tuple(key_vals)
        row_ids, row_sets, rows = row_ids_sets
        # print('row_id:', row_id)
        row = row_ids.get(row_id)
        if row is not None:
            changed_id = False
            # print('existing id:', row_id)
        else:
            # print('changed id:', row_id)
            changed_id = True
            row = None
            matching = set()
            first = True
            for i, v in enumerate(key_vals):
                if v is not None:
                    m = row_sets[i].get(v, set()).union(
                        row_sets[i].get(None, []))
                    # print(i, ':', m)
                    if first:
                        matching = set(m)
                        first = False
                    else:
                        matching = matching.intersection(m)
            if len(matching) != 0:
                # print('matching:', matching)
                # print(rows)
                # print(row_sets)
                row = next(iter(matching))
                old_id = rows[row]
                # print('found old row:', row, 'for id:', row_id, ':', old_id)
                nkey = list(old_id)
                for i, v in enumerate(key_vals):
                    if v is not None:
                        nkey[i] = v
                        # register new key for row
                        olds = row_sets[i].get(None)
                        if olds is not None:
                            olds.discard(row)
                        row_sets[i].setdefault(v, set()).add(row)
                row_id = tuple(nkey)
                # print('new id:', row_id)
                if old_id != row_id:
                    rows[row] = row_id
                    # delete key with None values to avoid ambiguities with
                    # other different key values which may come later
                    del row_ids[old_id]
                    row_ids[row_id] = row
            if row is None:
                if len(row_ids) == 0:
                    row = 0
                else:
                    row = len(rows)
                # print('new row:', row, row_id)
                if len(rows) <= row:
                    rows.append(row_id)
                row_ids[row_id] = row
                for i, v in enumerate(row_id):
                    row_sets[i].setdefault(v, set()).add(row)

        return row, row_id, changed_id

    def file_status(self, filename, data_type):
        if filename is None:
            return statuses.ABSENT
        stat_func = self.status_for_type.get(data_type)
        if stat_func is not None:
            if self.status_db_col is not None and self.index_status == 'Use':
                rfname = osp.relpath(filename, self.database)
                if not hasattr(self, 'file_statuses'):
                    # cache all statuses in a single request
                    statusl = self.db.execute(f'SELECT DISTINCT filename, {self.status_db_col} FROM files WHERE {self.status_db_col} IS NOT NULL')
                    self.file_statuses = {
                        status[0]: status[1] for status in statusl}
                return self.file_statuses.get(rfname, statuses.PRESENT)
            status = stat_func(self, filename)
            if self.status_db_col is not None \
                    and self.index_status == 'Force':
                rfname = osp.relpath(filename, self.database)
                self.db.execute(
                    f'UPDATE files SET {self.status_db_col}="{status}" WHERE filename="{rfname}"')
                self._commit = True
            return status
        return statuses.PRESENT

    def prepare_status_column(self):
        # check / add status cols in SQLite database
        self.status_db_col = None
        if self.index_status in ('Use', 'Force') and self.db is not None:
            cname = 'database_qc_status'
            # # reopen DB in this thread
            # if self.database_sqlite:
            #     self.db = sqlite3.connect(self.database_sqlite)
            cols = [c[1] for c in
                    self.db.execute('PRAGMA table_info(files)')]
            self.db_cols = cols
            if cname in cols:
                self.status_db_col = cname
                return  # OK
            if self.index_status == 'Force':
                for col in range(len(self.data_types)):
                    data_type = self.data_types[col]
                    stat_func = self.status_for_type.get(data_type)
                    if stat_func is not None:
                        # create missing column
                        self.db.execute(
                            f'ALTER TABLE files ADD {cname} INTEGER')
                        self.status_db_col = cname
                        cols = [c[1] for c in
                                self.db.execute('PRAGMA table_info(files)')]
                        self.db_cols = cols
                        return

    def exec_mainthread(self):
        t1 = time.time()

        self.prepare_status_column()

        mw = Qt.QMainWindow()
        wid = Qt.QWidget()
        mw.setCentralWidget(wid)
        lay = Qt.QVBoxLayout()
        wid.setLayout(lay)
        tablew = Qt.QTableWidget()
        lay.addWidget(tablew)

        eye = Qt.QIcon(findIconFile('eye.png'))
        pen = Qt.QIcon(findIconFile('pencil.png'))

        vlay = Qt.QVBoxLayout()
        lay.addLayout(vlay)
        vlay.addWidget(Qt.QLabel('Selected item:'))
        hlay = Qt.QHBoxLayout()
        vlay.addLayout(hlay)
        self.view_btn = RightClickablePushButton()
        self.view_btn.setIcon(eye)
        self.view_btn.setCheckable(True)
        hlay.addWidget(self.view_btn)
        self.edit_btn = RightClickablePushButton()
        self.edit_btn.setIcon(pen)
        self.edit_btn.setCheckable(True)
        hlay.addWidget(self.edit_btn)
        item_view = Qt.QLineEdit()
        hlay.addWidget(item_view)
        self.item_view = item_view
        item_view.setReadOnly(True)
        self.view_btn.setEnabled(False)
        self.edit_btn.setEnabled(False)
        self.current_item = None
        self._viewer = None
        self._editor = None

        nrows, ncols = len(self.elements), len(self.data_types)
        nkeys = len(self.keys)

        tablew.setHorizontalHeader(RotatedHeaderView(Qt.Qt.Horizontal, tablew))

        header = tablew.horizontalHeader()
        header.setSectionsClickable(True)
        header.setSectionsMovable(True)

        tablew.setColumnCount(ncols + nkeys)
        header.setDefaultSectionSize(32)
        header.setDefaultAlignment(Qt.Qt.AlignLeft)
        labels = self.keys + self.type_labels \
            + self.data_types[len(self.type_labels):]
        tablew.setHorizontalHeaderLabels(labels)
        tablew.setSortingEnabled(True)
        tablew.setEditTriggers(tablew.NoEditTriggers)

        tablew.setRowCount(nrows)

        no_icon = Qt.QIcon(findIconFile('absent.png'))
        present_icon = Qt.QIcon(findIconFile('ok.png'))
        ok_icon = Qt.QIcon(findIconFile('code_ok.png'))
        warn_icon = Qt.QIcon(findIconFile('code_warning.png'))
        susp_icon = Qt.QIcon(findIconFile('code_suspicious.png'))
        bad_icon = Qt.QIcon(findIconFile('code_bad.png'))
        mult_icon = Qt.QIcon(findIconFile('multiple.png'))
        valid_no_icon = Qt.QIcon(findIconFile('absent.png'))
        valid_present_icon = Qt.QIcon(findIconFile('code_valid_ok.png'))
        valid_ok_icon = Qt.QIcon(findIconFile('code_valid_ok.png'))
        valid_warn_icon = Qt.QIcon(findIconFile('code_valid_warning.png'))
        valid_susp_icon = Qt.QIcon(findIconFile('code_valid_suspicious.png'))
        valid_bad_icon = Qt.QIcon(findIconFile('code_valid_bad.png'))
        invalid_no_icon = Qt.QIcon(findIconFile('absent.png'))
        invalid_present_icon = Qt.QIcon(findIconFile('code_invalid_ok.png'))
        invalid_ok_icon = Qt.QIcon(findIconFile('code_invalid_ok.png'))
        invalid_warn_icon = Qt.QIcon(findIconFile('code_invalid_warning.png'))
        invalid_susp_icon = Qt.QIcon(findIconFile(
            'code_invalid_suspicious.png'))
        invalid_bad_icon = Qt.QIcon(findIconFile('code_invalid_bad.png'))

        status_icons = {
            statuses.OK: ok_icon,
            statuses.PRESENT: present_icon,
            statuses.WARNING: warn_icon,
            statuses.SUSPICIOUS: susp_icon,
            statuses.BAD: bad_icon,
            statuses.ABSENT: no_icon,

            statuses.VALID_OK: valid_ok_icon,
            statuses.VALID_PRESENT: valid_present_icon,
            statuses.VALID_WARNING: valid_warn_icon,
            statuses.VALID_SUSPICIOUS: valid_susp_icon,
            statuses.VALID_BAD: valid_bad_icon,
            statuses.VALID_ABSENT: valid_no_icon,

            statuses.INVALID_OK: invalid_ok_icon,
            statuses.INVALID_PRESENT: invalid_present_icon,
            statuses.INVALID_WARNING: invalid_warn_icon,
            statuses.INVALID_SUSPICIOUS: invalid_susp_icon,
            statuses.INVALID_BAD: invalid_bad_icon,
            statuses.INVALID_ABSENT: invalid_no_icon,
        }

        row_ids = self.row_ids

        for row_id, row in row_ids.items():
            for c, key in enumerate(row_id):
                if key is not None:
                    tablew.setItem(row, c, QSortingTabeWidgetItem(key))

        for col in range(ncols):
            for row in range(nrows):
                elem = self.elements[row][col]
                if elem is None:
                    titem = QSortingTabeWidgetItem(no_icon, '')
                    titem.sort_data = statuses.ABSENT
                elif isinstance(elem, list):
                    titem = QSortingTabeWidgetItem(mult_icon, '')
                    titem.sort_data = -1
                    titem.position = (row, col)
                else:
                    status = self.file_status(elem['path'],
                                              self.data_types[col])
                    icon = status_icons[status]
                    titem = QSortingTabeWidgetItem(icon, '')
                    titem.sort_data = status
                    titem.setData(15, status)
                    titem.position = (row, col)
                tablew.setItem(row, col + nkeys, titem)

        if self.db and getattr(self, '_commit', False):
            self.db.execute('COMMIT')

        tablew.itemClicked.connect(self.item_clicked)
        tablew.itemDoubleClicked.connect(self.item_double_clicked)

        tablew.sortByColumn(0, Qt.Qt.AscendingOrder)
        for col in range(nkeys):
            tablew.resizeColumnToContents(col)

        self.view_btn.toggled.connect(self.viewer_clicked)
        self.edit_btn.toggled.connect(self.editor_clicked)
        self.view_btn.rightPressed.connect(self.viewer_right_clicked)
        self.edit_btn.rightPressed.connect(self.editor_right_clicked)

        menu = Qt.QMenuBar()
        fmenu = menu.addMenu('File')
        action = fmenu.addAction('Save HTML or PDF...')
        action.triggered.connect(self.save_gui)
        mw.setMenuBar(menu)

        mw.resize(800, 800)
        mw.show()

        t2 = time.time()
        print('GUI build time:', datetime.timedelta(seconds=t2 - t1))
        print('total:', datetime.timedelta(seconds=t2 - self.t0))


        return MainThreadLife(mw)

    def item_clicked(self, item):
        if not self._viewer:
            self.view_btn.setEnabled(False)
        if not self._editor:
            self.edit_btn.setEnabled(False)

        if not hasattr(item, 'position'):
            # no data under this item
            self.item_view.setText('')
            self.current_item = None
            return
        row, col = item.position
        elements = self.elements[row][col]
        # print('item_clicked:', row, col, elements)
        element = None
        if isinstance(elements, list):
            menu = Qt.QMenu()
            try:
                # eye = Qt.QIcon(findIconFile('eye.png'))
                for i, element in enumerate(elements):
                    # action = menu.addAction(element['path'])
                    # action.setCheckable(True)
                    has_view = hasattr(item, 'viewer_res') \
                        and item.viewer_res[i] is not None
                    # action.number = i
                    # action = menu.addAction(eye, element['path'])
                    # action.number = -i - 1
                    action = QActionWithViewer(element['path'], has_view,
                                               item, i, menu)
                    # action.number = i
                    menu.addAction(action)
                    action.action_triggered.connect(self.display_item)
                    action.viewer_triggered.connect(self.run_element_viewer)
                    action.triggered.connect(menu.close)
                element = None
                # chosen_action = menu.exec(Qt.QCursor.pos())
                menu.exec(Qt.QCursor.pos())
            except Exception:
                import traceback
                traceback.print_exc()
                return
            # if chosen_action is not None:
                # if chosen_action.number < 0:
                    # use viewer
                    # self.run_element_viewer(item, -chosen_action.number - 1)
                    # element = elements[-chosen_action.number - 1]
                # else:
                    # element = elements[chosen_action.number]
        else:
            element = elements
        # print('element:', element)

        if element is not None:
            self.item_view.setText(element['path'])
            self.current_item = (element, self.data_types[col])
            viewers = self.get_viewers(element, process=self,
                                       data_type=self.data_types[col],
                                       check_values=True)
            if viewers:
                self.view_btn.setEnabled(True)
            editors = self.get_data_editors(element, process=self,
                                            data_type=self.data_types[col],
                                            check_values=True)
            if editors:
                self.edit_btn.setEnabled(True)

    def get_viewers(self, element, process, data_type, check_values):
        viewers = find_viewer.find_viewers(self.get_study_config().engine,
                                           element['path'])
        # print('get viewers for:', element['path'], ':')
        # print(viewers)
        return viewers

    def get_data_editors(self, element, process, data_type, check_values):
        editors = find_viewer.find_data_editors(
            self.get_study_config().engine, element['path'])
        return editors

    def item_double_clicked(self, item):
        if not hasattr(item, 'position'):
            # no data under this item
            return
        row, col = item.position
        elements = self.elements[row][col]
        element = None
        if isinstance(elements, list):
            element = elements[0]
        else:
            element = elements

        if element is not None:
            self.run_element_viewer(item)

    def display_item(self, item, num):
        if not self._viewer:
            self.view_btn.setEnabled(False)
        if not self._editor:
            self.edit_btn.setEnabled(False)
        if not hasattr(item, 'position'):
            # no data under this item
            return
        row, col = item.position
        elements = self.elements[row][col]
        element = None
        if isinstance(elements, list):
            element = elements[num]

        if element is not None:
            self.item_view.setText(element['path'])
            self.current_item = (element, self.data_types[col])
            viewers = self.get_viewers(element, process=self,
                                       data_type=self.data_types[col],
                                       check_values=True)
            if viewers:
                self.view_btn.setEnabled(True)
            editors = self.get_data_editors(element, process=self,
                                            data_type=self.data_types[col],
                                            check_values=True)
            if editors:
                self.edit_btn.setEnabled(True)

    def run_element_viewer(self, item, num=0):
        if not hasattr(item, 'position'):
            # no data under this item
            return
        row, col = item.position
        elements = self.elements[row][col]
        element = None
        if isinstance(elements, list):
            element = elements[num]
            if not hasattr(item, 'viewer_res'):
                item.viewer_res = [None] * len(elements)
            viewer_res = item.viewer_res
        else:
            element = elements
            if not hasattr(item, 'viewer_res'):
                item.viewer_res = [None]
            viewer_res = item.viewer_res
            num = 0
        if element is not None:
            if viewer_res[num] is not None:
                viewer_res[num] = None
                if not any(viewer_res):
                    item.setBackground(Qt.QBrush(Qt.QColor(255, 255, 255)))
            else:
                viewers = self.get_viewers(element, process=self,
                                           data_type=self.data_types[col],
                                           check_values=True)
                for viewer in viewers:
                    try:
                        viewer.reference_process = self
                        viewer.main_input = element['path']
                        pc = ProcessCompletionEngine.get_completion_engine(
                            viewer)
                        if pc is not None:
                            att = pc.get_attribute_values()
                            self._set_compl_attribs(att, element['attributes'])
                            pc.complete_parameters()
                        res = viewer()
                        viewer_res[num] = res
                        item.setBackground(Qt.QBrush(Qt.QColor(210, 210, 230)))
                        break
                    except Exception:
                        pass

    def _set_compl_attribs(self, atts, val_dict):
        for k, v in val_dict.items():
            if atts.trait(k) is not None:
                setattr(atts, k, v)

    def viewer_clicked(self, checked):
        if checked:
            element_d = self.current_item
            if element_d is None:
                return
            element, data_type = element_d
            viewers = self.get_viewers(element, process=self,
                                       data_type=data_type, check_values=True)
            # print('viewers:', viewers)

            for viewer in viewers:
                try:
                    viewer.reference_process = self
                    viewer.main_input = element['path']
                    pc = ProcessCompletionEngine.get_completion_engine(viewer)
                    if pc is not None:
                        att = pc.get_attribute_values()
                        self._set_compl_attribs(att, element['attributes'])
                        pc.complete_parameters()
                    res = viewer()
                    self._viewer = res
                    break
                except Exception as e:
                    print('EXC:', e)
                    import traceback
                    traceback.print_exc()
                    pass
        else:
            self._viewer = None
            if self.current_item is None:
                self.view_btn.setEnabled(False)

    def editor_clicked(self, checked):
        if checked:
            element_d = self.current_item
            if element_d is None:
                return
            element, data_type = element_d
            editors = self.get_data_editors(element, process=self,
                                            data_type=data_type,
                                            check_values=True)
            for editor in editors:
                try:
                    editor.reference_process = self
                    editor.main_input = element['path']
                    pc = ProcessCompletionEngine.get_completion_engine(editor)
                    if pc is not None:
                        att = pc.get_attribute_values()
                        self._set_compl_attribs(att, element['attributes'])
                        pc.complete_parameters()
                    res = editor()
                    self._editor = res
                    break
                except Exception:
                    pass
        else:
            self._editor = None
            if self.current_item is None:
                self.edit_btn.setEnabled(False)

    def viewer_right_clicked(self, pos):
        element_d = self.current_item
        if element_d is None:
            return
        element, data_type = element_d
        viewers = self.get_viewers(element, process=self,
                                   data_type=data_type, check_values=True)
        self.show_interactive_viewers(element, data_type, viewers)

    def editor_right_clicked(self, pos):
        element_d = self.current_item
        if element_d is None:
            return
        element, data_type = element_d
        viewers = self.get_data_editors(element, process=self,
                                        data_type=data_type, check_values=True)
        self.show_interactive_viewers(element, data_type, viewers)

    def show_interactive_viewers(self, element, data_type, viewers):
        if len(viewers) != 0:
            menu = Qt.QMenu()
            for i, viewer in enumerate(viewers):
                action = Qt.QAction(viewer.name, menu)
                action.viewer = viewer
                menu.addAction(action)
                # action.triggered.connect(self.run_interactive_viewer)
            chosen_action = menu.exec(Qt.QCursor.pos())
            del menu
            if chosen_action is not None:
                viewer = chosen_action.viewer
                engine = self.get_study_config().engine
                try:
                    viewer = engine.get_process_instance(viewer)
                    viewer.reference_process = self
                    viewer.main_input = element['path']
                    pc = ProcessCompletionEngine.get_completion_engine(viewer)
                    if pc is not None:
                        att = pc.get_attribute_values()
                        self._set_compl_attribs(att, element['attributes'])
                        pc.complete_parameters()
                    self.show_process(viewer)
                except Exception:
                    import traceback
                    traceback.print_exc()

    def show_process(self, viewer):
        # TODO NotImplemented
        pass

    def save_gui(self):
        from soma.qt_gui import qt_backend
        if wkhtmltopdf is None:
            filters = 'Supported files (*.html);; HTML files (*.html)'
        else:
            filters = 'Supported files (*.html *.pdf);; ' \
                'HTML files (*.html);; PDF files (*.pdf)'
        filename = qt_backend.getSaveFileName(
            None, 'Save QC table', '', filters)
        if filename is not None and filename != '':
            try:
                self.save_file(filename)
            except Exception:
                import traceback
                traceback.print_exc()

    def save(self):
        self.save_file(self.output_file)

    def save_file(self, filename):
        if filename.endswith('.html'):
            self.save_html(filename)
        elif filename.endswith('.pdf'):
            self.save_pdf(filename)
        elif filename.endswith('.csv'):
            self.save_csv(filename)
        else:
            raise ValueError('Unrecognized output format')

    def save_html(self, filename):

        with open(filename, 'w') as f:
            f.write('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <style type="text/css">
    div.ok { width: 16px; height: 14px;
             background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAOCAYAAAAmL5yKAAAACXBIWXMAAAsOAAALDgFAvuFBAAAAB3RJTUUH0gEQFyIZJOsyvgAAAAZiS0dEAP8A/wD/oL2nkwAAAOxJREFUKM9jYBggwATFJAPGR3/3/V/xV+8/kC0OxJxkaW57wvA/YhoDyBB1Yp2GoVnHD2yAN4qCjX/9kJ3GiCpnha65AG4ASMHmv3b/J/xlAisCCmkAMTcQM8M0195D0VwMxKFgdSAB2yKG//nHGP5P/Mv2f8pfHrBioKQWSPOivzr/a54x/A/ow9CsCbWEgUFan+G/dR7D/6wjDGADJv5l+Q/T3PWG4b9vC07NMG8y6MMMAbmk8x8D2Nkgm4nRDAK8IAlkQ0DewONsRoxogkqADbEvwxpgODVjNQSquZBYzeiGgKLRB4o18GkGAPXUpkdmxKgBAAAAAElFTkSuQmCC");
           }
    div.no { width: 15px; height: 16px;
             background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAQAgMAAAC0OM2XAAAADFBMVEVlLWeAgIDAAAD/AADpI7RpAAAAAXRSTlMAQObYZgAAAAFiS0dEAIgFHUgAAAAJcEhZcwAACxMAAAsTAQCanBgAAAAHdElNRQfhChEICCvZr2gsAAAASklEQVQI12NggABmBgZ+BrsGBr4PryYwWK1bFcDAtmqpAwND1hSgpNUFIPFqA1DV0jVAYoomAwNfABeQcGByYOB1YAASIDMYgRgAgEcOCf2eaP8AAAAASUVORK5CYII=");
           }
    div.ml { width: 22px; height: 22px;
             background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsOAAALDgFAvuFBAAAAB3RJTUUH4QoRCBERhKMYhgAAAjpJREFUOMvtk8tLlFEYh59vLs5oaSPpJIWTxoBZYBBEuAzKdkJQ/0MoaEbLWfgXtJSgiBZBLVzo6MJLfbTJRWAwjmaOZ4bm4mViupjOaPNdTgu/Yr7JgUyX/uBszuE873nOeQ8c5YBxWOPQohhClcbDDgmcAqoPFZrpQQ51IYG2SjaOf1RUDKGahO+xJuYIC5hIABDco7ABNDpsk8+6DaDRUlRs0MmQDRoWDFQqPNTFugPAEKrJ9CAsjpPpYR04C9QATl2oppwMkYzOlEIfACtAvJKN0h1EBuvhdhtcba4CZxXJ3BbnHnFRF+qCMtpHNjHPy0V4k4KxOCEpWQaiQNoQ6iaTIdYWbIUHXGGB0uFH6iaYskhnaxUBnwtdTC0oo318S87zNArvVsHr9eCv5/TXH8VpTZcreuz1JpbNRMJu4wTI5hnZMbib18DnLhKoNSG3TDY2y+O5XWhDrQfd6eF6QLkS+WK+2IpOf1TG+snGZhleglef/kBTwLzLuvxE5DMXgA9Yr9a0McNIbBe6+tOL2+vgZJ2LzjM6oaFxVRnrt9mUQoGU0wJrQCGb5/mOQa9uQm579xRTKceTJl/1ZZ+7yK2WPDeaNTwbCZtNORQoOEtaRv8N39LozRUgLLgvJaKmzv1+O69d03STxhowvqcZXoK3mb2hgFTKP4LVZs0lzR+vPe7aKBaNhvM+GbnZCi0nbA/1F3Rf3xk4BrRf8iO7g0hgALgDtFtrSvmG/cDLbQSQ/p+THuXg+QUn/kKA+EqPswAAAABJRU5ErkJggg==");
           }
    .vert div {
        transform: rotate(-90deg);
        text-align: center;
        vertical-align: middle;
        white-space: nowrap;
        margin-bottom: -50px;
        #padding-left: 100px;
        #padding-bottom: -50px;
        #margin-right: 0px;
        #margin-left: 100px;
        position: relative;
        left: 143px;
        bottom: -80px;
        height: 300px;
        width: 24px;
    }
    table {
        border: 1px solid #99b;
        border-spacing: 0px;
        padding: 2px;
    }
    tr {
        border: none;
    }
    tbody tr:nth-child(4n) {
        background-color: #ddd;
    }
    tbody tr:nth-child(4n+3) {
        background-color: #ddd;
    }
    td {
        border-collapse: collapse;
        border: none;
        padding: 1px;
        margin: 0px;
        vertical-align: middle;
        position:relative;

        a {
            height: 100%;
            display: block;
            position: absolute;
            top:0;
            bottom:0;
            right:0;
            left:0;
          }

        .item-container {
            padding: 0px;
            margin: 0px;
            border: none;
        }
    }
    thead tr {
        background-color: #ddf;
        font-weight: bold;
    }
    .key_col:nth-child(even) {
        background-color: #f0f0f8;
    }

    .key_cell {
        padding-left: 5px;
        padding-right: 5px;
    }
  </style>
  <!-- script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
  <script>
    $(document).ready(function() {
  $('.vert').css('height', $('.vert').width());
});
  </script -->
</head>
<body>
  <table>
    <colgroup>
''')

            nrows, ncols = len(self.elements), len(self.data_types)

            labels = self.keys + self.type_labels \
                + self.data_types[len(self.type_labels):]
            for label in self.keys:
                f.write('      <col class="key_col" />\n')
            for label in self.type_labels:
                f.write('      <col />\n')
            f.write('''    </colgroup>
    <thead>
      <tr>
''')
            for label in labels:
                f.write('        <td class="vert"><div>%s</div></td>\n'
                        % label)
            f.write('''      </tr>
    </thead>
    <tbody>
''')

            row_ids = self.row_ids

            # eliminate duplicate rows by keeping most complete id for each
            rev_row_ids = {}
            for row_id, row in row_ids.items():
                rev_row_ids.setdefault(row, []).append(row_id)
            rev_row_ids = dict([(row, max(row_id))
                                for row, row_id in rev_row_ids.items()])

            # sort items
            rows_order = list(zip(*sorted(zip(rev_row_ids.values(),
                                              range(nrows)))))[1]

            for row in rows_order:
                row_id = max([rid for rid in row_ids if row_ids[rid] == row])
                f.write('      <tr>\n')
                for key in row_id:
                    if key is None:
                        key = ''
                    f.write('        <td class="key_cell">%s</td>\n' % key)

                for elem in self.elements[row]:
                    if elem is None:
                        f.write('        <td><div class="no" /></td>\n')
                    elif isinstance(elem, list):
                        f.write('        <td><div class="ml" /></td>\n')
                    else:
                        f.write('        <td><a href="file://%s"><div class="item-container"><div class="ok" /></div></a></td>\n' % elem)

            f.write('''    </tbody>
  </table>
</body>
</html>
''')

    def save_pdf(self, filename):
        temp = tempfile.mkstemp(prefix='bv_', suffix='.html')
        os.close(temp[0])
        temp_file = temp[1]
        self.save_html(temp_file)
        subprocess.check_call(['wkhtmltopdf', temp_file, filename])

    def save_csv(self, filename):
        f = open(filename, 'w')

        nrows, ncols = len(self.elements), len(self.data_types)

        labels = self.keys + self.type_labels \
            + self.data_types[len(self.type_labels):]
        f.write('\t'.join(labels))
        f.write('\n')

        row_ids = self.row_ids

        # eliminate duplicate rows by keeping most complete id for each
        rev_row_ids = {}
        for row_id, row in row_ids.items():
            rev_row_ids.setdefault(row, []).append(row_id)
        rev_row_ids = dict([(row, max(row_id))
                            for row, row_id in rev_row_ids.items()])
        # sort items
        rows_order = list(zip(*sorted(zip(rev_row_ids.values(),
                                          range(nrows)))))[1]

        for row in rows_order:
            row_id = max([rid for rid in row_ids if row_ids[rid] == row])
            for key in row_id:
                if key is None:
                    key = ''
                f.write('%s\t' % key)

            for elem in self.elements[row]:
                if elem is None:
                    f.write('0\t')
                elif isinstance(elem, list):
                    f.write('2\t')
                else:
                    f.write('1\t')
            f.write('\n')


class RotatedHeaderView(Qt.QHeaderView):

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setMinimumSectionSize(20)

    def paintSection(self, painter, rect, logicalIndex):
        from soma.qt_gui.qt_backend import sip
        if sip.isdeleted(self):
            return
        painter.save()
        # translate the painter such that rotate will rotate around the
        # correct point
        # painter.translate(rect.x()+rect.width(), rect.y())
        # painter.rotate(90)
        painter.translate(rect.x(), rect.y()+rect.height())
        painter.rotate(270)
        # and have parent code paint at this location
        newrect = Qt.QRect(0, 0, rect.height(), rect.width())
        super().paintSection(painter, newrect, logicalIndex)
        painter.restore()

    def minimumSizeHint(self):
        size = super().minimumSizeHint()
        size.transpose()
        return size

    def sectionSizeFromContents(self, logicalIndex):
        size = super().sectionSizeFromContents(
            logicalIndex)
        size.transpose()
        return Qt.QSize(size.width(), int(size.height() * 0.9))


class QActionWithViewer(Qt.QWidgetAction):

    action_triggered = Qt.Signal(QTableWidgetItem, int)
    viewer_triggered = Qt.Signal(QTableWidgetItem, int)

    def __init__(self, text, checked, item, num, parent):
        super().__init__(parent)
        self._widget = None
        self._view_button = None
        self.text = text
        self._checked = checked
        self._item = item
        self.number = num

    def createWidget(self, parent):
        if self._widget is not None:
            return self._widget

        eye = Qt.QPixmap(findIconFile('eye.png')).scaledToHeight(
            20, Qt.Qt.SmoothTransformation)
        eye = Qt.QIcon(eye)
        w = Qt.QWidget(parent)
        l = Qt.QHBoxLayout()
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(5)
        w.setLayout(l)
        b = Qt.QToolButton(parent)
        b.setCheckable(True)
        b.setChecked(self._checked)
        l.addWidget(b)
        b.setIcon(eye)
        b.setSizePolicy(Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Fixed)
        label = Qt.QToolButton(parent)
        label.setText(self.text)
        # label.setTextAlignment(Qt.Qt.LeftAlignment)
        l.addWidget(label)
        l.addStretch(1)
        self._view_button = b
        self._widget = w
        label.clicked.connect(self._action_triggered)
        label.clicked.connect(self.triggered)
        b.toggled.connect(self._viewer_triggered)
        return w

    def _action_triggered(self):
        self.action_triggered.emit(self._item, self.number)

    def _viewer_triggered(self, state):
        self.viewer_triggered.emit(self._item, self.number)

    def requestWidget(self, parent):
        return self._widget


class RightClickablePushButton(Qt.QPushButton):

    rightPressed = Qt.Signal(Qt.QPoint)

    def mousePressEvent(self, e):
        if e.button() == Qt.Qt.RightButton:
            self.rightPressed.emit(self.mapToGlobal(e.pos()))
        else:
            Qt.QPushButton.mousePressEvent(self, e)


if __name__ == '__main__':
    from capsul.api import capsul_engine
    import json

    def get_qc_status(proc, path):
        if not osp.exists(path):
            return proc.statuses.BAD
        with open(path) as f:
            report = json.load(f)
        stat = {
            'OK': proc.statuses.OK,
            'Warning': proc.statuses.WARNING,
            'Suspicious': proc.statuses.SUSPICIOUS,
            'Bad': proc.statuses.BAD,
        }
        status = report.get('status', 'Bad')
        return stat[status]

    engine = capsul_engine()
    proc = DatabaseQcTable()
    proc.status_for_type[
        'morphologist.capsul.morphologist.Morphologist.Report_report_json'] \
            = get_qc_status
    proc.set_study_config(engine.study_config)
    proc.database = '/home/dr144257/data/baseessai'
    proc.fom = 'morphologist-auto-1.0'
    # proc.database = '/home/dr144257/data/morpho_bids/derivatives/morphologist-6.0'
    # proc.fom = 'morphologist-bids-2.0'
    proc.data_types = [
        'morphologist.capsul.morphologist.Morphologist.t1mri',
        'morphologist.capsul.morphologist.Morphologist.t1mri_nobias',
        'morphologist.capsul.morphologist.Morphologist.histo_analysis',

        'morphologist.capsul.morphologist.Morphologist.GreyWhiteMesh_white_mesh',
        'morphologist.capsul.morphologist.Morphologist.GreyWhiteMesh_1_white_mesh',

        'morphologist.capsul.morphologist.Morphologist.PialMesh_pial_mesh',
        'morphologist.capsul.morphologist.Morphologist.PialMesh_1_pial_mesh',
        'morphologist.capsul.morphologist.Morphologist.left_graph',
        'morphologist.capsul.morphologist.Morphologist.right_graph',
        'morphologist.capsul.morphologist.Morphologist.left_labelled_graph',
        'morphologist.capsul.morphologist.Morphologist.right_labelled_graph',

        'morphologist.capsul.morphologist.Morphologist.Report_report',
        'morphologist.capsul.morphologist.Morphologist.Report_report_json']
    proc.data_filters = ["{'center': 'subjects'}"]
    proc.keys = ['subject', 'acquisition', 'bids', 'sulci_recognition_session']
    proc.type_labels = [
        'Raw T1 MRI', 'Bias Corrected', 'Histo Analysis',
        # 'Brain Mask', 'Hemispheres Split', 'Head Mesh',
        # 'Left Grey White Mask', 'Right Grey White Mask',
        # 'Left CSF+GREY Mask', 'Right CSF+GREY Mask',
        'Left Hemisphere White Mesh', 'Right Hemisphere White Mesh',
        # 'Left Cortex Skeleton', 'Right Cortex Skeleton',
        'Left Hemisphere Mesh', 'Right Hemisphere Mesh',
        'Left Cortical Sulci', 'Right Cortical Sulci',
        'Left Labelled Sulci', 'Right Labelled Sulci',
        # 'Sulcal morphometry measurements', 'Brain volumes',
        'Report', 'QC']
    # proc.output_file = '/tmp/qc_report.pdf'

    qapp = Qt.QApplication([])
    keep = proc()
    qapp.exec()
    del keep
