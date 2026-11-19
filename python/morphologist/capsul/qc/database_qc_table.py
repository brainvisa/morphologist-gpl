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

from capsul.api import Process
from capsul.attributes.completion_engine import ProcessCompletionEngine
from soma.wip.application.api import findIconFile
from soma.qt_gui.qtThread import MainThreadLife, QtThreadCall
from soma.qt_gui.qt_backend import Qt
from morphologist.capsul.qc import find_viewer
from capsul.datasel.data_selector import get_data_selector, DataSelector
import traits.api as traits
import subprocess
import shutil
import os
import os.path as osp
import tempfile
import time
import datetime


wkhtmltopdf = shutil.which('wkhtmltopdf')


class QSortingItem(Qt.QStandardItem):
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


class CustomSortProxyModel(Qt.QSortFilterProxyModel):
    def lessThan(self, left_index, right_index):
        while not isinstance(left_index.model(), Qt.QStandardItemModel):
            proxy = left_index.model()
            if proxy is None:
                break
            left_index = proxy.mapToSource(left_index)
        left_item = left_index.model().itemFromIndex(left_index)
        while not isinstance(right_index.model(), Qt.QStandardItemModel):
            proxy = right_index.model()
            if proxy is None:
                break
            right_index = proxy.mapToSource(right_index)
        right_item = right_index.model().itemFromIndex(right_index)

        if left_item is None:
            return True
        if right_item is None:
            return False

        try:
            return left_item < right_item
        except TypeError:
            # Sécurité si les types ne sont pas comparables
            return super().lessThan(left_index, right_index)

    def filterAcceptsRow(self, sourceRow, sourceParent):
        if self.filterRegularExpression() is None:
            return True
        col = self.filterKeyColumn()
        if col != -1:
            index = self.sourceModel().index(sourceRow, col, sourceParent)
            item = self.sourceModel().itemFromIndex(index)
            if item is None or not hasattr(item, 'sort_data'):
                return super().filterAcceptsRow(sourceRow, sourceParent)
            stat_str = DataSelector.status_str[item.sort_data]
            return self.filterRegularExpression().match(stat_str).hasMatch()
        res = False
        for col in range(self.sourceModel().columnCount()):
            index = self.sourceModel().index(sourceRow, col, sourceParent)
            item = self.sourceModel().itemFromIndex(index)
            if item is None or not hasattr(item, 'sort_data'):
                res |= super().filterAcceptsRow(sourceRow, sourceParent)
                if res:
                    break
            else:
                stat_str = DataSelector.status_str[item.sort_data]
                res |= \
                    self.filterRegularExpression().match(stat_str).hasMatch()
                if res:
                    break
        return res


status_for_type = {}


class DatabaseQcTable(Process):

    roles = ['qc']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_trait('database', traits.Directory(optional=True))
        self.add_trait('fom', traits.Str(optional=True))
        self.add_trait('database_sqlite', traits.File(optional=True))
        self.add_trait('data_types', traits.ListStr())
        self.add_trait('data_filters', traits.Str(optional=True))
        self.add_trait('keys', traits.ListStr())
        self.add_trait('type_labels', traits.ListStr())
        self.add_trait('output_file',
                       traits.File(allowed_extensions=['HTML', 'PDF file',
                                                       'CSV file'],
                                   output=True, optional=True))
        self.add_trait('index_status', traits.Enum(('False', 'Force', 'Use',
                                                    'Set_if_absent')))

        self.status_for_type = status_for_type
        self.statuses = DataSelector.statuses
        self.index_status = 'Set_if_absent'
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

        # find data
        t0 = time.time()
        self.t0 = t0

        self.data_selector = get_data_selector(
            self.database,
            engine=self.get_study_config().engine,
            fom=self.fom,
            database_sqlite=self.database_sqlite,
            data_types=self.data_types,
            data_filters=self.data_filters,
            type_labels=self.type_labels,
            index_status=self.index_status,
            status_for_type=self.status_for_type)
        data = list(self.data_selector.get_data())
        t1 = time.time()

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

        # print('filter status:', self.data_selector.need_status, self.status_filters)
        if self.data_selector.need_status:
            # filter out by status
            todel = []
            for row, items in enumerate(elements):
                # print(items)
                for c, sfilt in enumerate(self.status_filters):
                    if not sfilt:
                        continue
                    if not items[c]:
                        if sfilt != 'absent':
                            # print('not present', row)
                            todel.append(row)
                            break
                    if sfilt == 'absent' and items[c]:
                        # print('remove absent row:', row, items[c])
                        todel.append(row)
                        break
                    citems = items[c]
                    citems = citems if isinstance(citems, list) else (
                        [] if citems is None else [citems])
                    fitems = []
                    dtype = self.data_types[c]
                    for item in citems:
                        status = DataSelector.status_str[
                            self.file_status(item['path'], dtype)]
                        if status == sfilt:
                            fitems.append(item)
                    if len(fitems) == 0 and sfilt != 'absent':
                        # print('del fitems', row, ':', fitems)
                        todel.append(row)
                        break

            # print('to del:', todel)
            delid = []
            for row in reversed(todel):
                del elements[row]
                for row_id, r in row_ids.items():
                    if r == row:
                        delid.append(row_id)
                    elif r >= row:
                        row_ids[row_id] = r - 1
            for row_id in delid:
                del row_ids[row_id]
            max_row -= len(todel)

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

    def exec_mainthread(self):
        t1 = time.time()

        mw = Qt.QMainWindow()
        wid = Qt.QWidget()
        mw.setCentralWidget(wid)
        lay = Qt.QVBoxLayout()
        wid.setLayout(lay)
        tablew = Qt.QTableView()
        lay.addWidget(tablew)

        eye = Qt.QIcon(findIconFile('eye.png'))
        pen = Qt.QIcon(findIconFile('pencil.png'))

        vlay = Qt.QVBoxLayout()
        lay.addLayout(vlay)
        slay = Qt.QHBoxLayout()
        vlay.addLayout(slay)
        slay.addWidget(Qt.QLabel('Selected item:'))
        slay.addStretch()
        count_label = Qt.QLabel()
        self.count_label = count_label
        slay.addWidget(count_label)
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

        count_label.setText(f'Items count: {nrows}')

        model = Qt.QStandardItemModel(nrows, ncols + nkeys)
        self.model = model

        tablew.setHorizontalHeader(RotatedHeaderView(Qt.Qt.Horizontal, tablew))

        header = tablew.horizontalHeader()
        header.setSectionsClickable(True)
        header.setSectionsMovable(True)

        header.setDefaultSectionSize(32)
        header.setDefaultAlignment(Qt.Qt.AlignLeft)
        labels = self.keys + self.type_labels \
            + self.data_types[len(self.type_labels):]
        model.setHorizontalHeaderLabels(labels)
        tablew.setSortingEnabled(True)
        tablew.setEditTriggers(tablew.NoEditTriggers)

        undefined_icon = Qt.QIcon(findIconFile('absent.png'))
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
            self.statuses.UNDEFINED: undefined_icon,
            self.statuses.OK: ok_icon,
            self.statuses.PRESENT: present_icon,
            self.statuses.WARNING: warn_icon,
            self.statuses.SUSPICIOUS: susp_icon,
            self.statuses.BAD: bad_icon,
            self.statuses.ABSENT: no_icon,

            self.statuses.VALID_OK: valid_ok_icon,
            self.statuses.VALID_PRESENT: valid_present_icon,
            self.statuses.VALID_WARNING: valid_warn_icon,
            self.statuses.VALID_SUSPICIOUS: valid_susp_icon,
            self.statuses.VALID_BAD: valid_bad_icon,
            self.statuses.VALID_ABSENT: valid_no_icon,

            self.statuses.INVALID_OK: invalid_ok_icon,
            self.statuses.INVALID_PRESENT: invalid_present_icon,
            self.statuses.INVALID_WARNING: invalid_warn_icon,
            self.statuses.INVALID_SUSPICIOUS: invalid_susp_icon,
            self.statuses.INVALID_BAD: invalid_bad_icon,
            self.statuses.INVALID_ABSENT: invalid_no_icon,
        }

        row_ids = self.row_ids

        for row_id, row in row_ids.items():
            for c, key in enumerate(row_id):
                if key is not None:
                    model.setItem(row, c, Qt.QStandardItem(key))

        for col in range(ncols):
            for row in range(nrows):
                elem = self.elements[row][col]
                if elem is None:
                    titem = QSortingItem(no_icon, '')
                    titem.sort_data = self.statuses.ABSENT
                elif isinstance(elem, list):
                    titem = QSortingItem(mult_icon, '')
                    titem.sort_data = -1
                    titem.position = (row, col)
                else:
                    status = self.data_selector.file_status(
                        elem['path'], self.data_types[col])
                    icon = status_icons[status]
                    titem = QSortingItem(icon, '')
                    titem.sort_data = status
                    # titem.setData(15, status + 10)
                    titem.position = (row, col)
                model.setItem(row, col + nkeys, titem)

        if self.db and getattr(self, '_commit', False):
            self.db.execute('COMMIT')

        proxy = CustomSortProxyModel()
        proxy.setSourceModel(model)
        tablew.setModel(proxy)
        tablew.clicked.connect(self.item_clicked)
        tablew.doubleClicked.connect(self.item_double_clicked)

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
        action.setShortcut(Qt.QKeySequence(Qt.Qt.CTRL + Qt.Qt.Key_S))
        action.triggered.connect(self.save_gui)
        action = fmenu.addAction('Quit')
        action.setShortcut(Qt.QKeySequence(Qt.Qt.CTRL + Qt.Qt.Key_Q))
        action.triggered.connect(Qt.QApplication.instance().quit)
        emenu = menu.addMenu('Edit')
        action = emenu.addAction('Find / filter...')
        action.setShortcut(Qt.QKeySequence(Qt.Qt.CTRL + Qt.Qt.Key_F))
        action.triggered.connect(self.find_data_gui)
        mw.setMenuBar(menu)

        mw.resize(800, 800)
        mw.show()

        self.table = tablew

        t2 = time.time()
        print('GUI build time:', datetime.timedelta(seconds=t2 - t1))
        print('total:', datetime.timedelta(seconds=t2 - self.t0))

        return MainThreadLife(mw)

    def item_clicked(self, index):
        while index.model() is not self.model:
            proxy = index.model()
            if proxy is None:
                break
            index = proxy.mapToSource(index)
        item = self.model.itemFromIndex(index)

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
            self.current_item = (element, self.data_types[col], row, col)
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

    def item_double_clicked(self, index):
        while index.model() is not self.model:
            proxy = index.model()
            if proxy is None:
                break
            index = proxy.mapToSource(index)
        item = self.model.itemFromIndex(index)

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
            self.current_item = (element, self.data_types[col], row, col)
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
                        viewer.protect_parameter('main_input')
                        pc = ProcessCompletionEngine.get_completion_engine(
                            viewer)
                        if pc is not None:
                            att = pc.get_attribute_values()
                            self._set_compl_attribs(
                                att, element['attributes'], row, col)
                            pc.complete_parameters()
                        res = viewer()
                        viewer_res[num] = res
                        item.setBackground(Qt.QBrush(Qt.QColor(210, 210, 230)))
                        break
                    except Exception:
                        pass

    def _set_compl_attribs(self, atts, val_dict, row, col):
        done = set()
        for k, v in val_dict.items():
            if atts.trait(k) is not None:
                setattr(atts, k, v)
                done.add(k)

        if len(done) != len(atts.user_traits()):
            # some attributes are missing in the main input: look for
            # them in other elements of the same table row
            missing = set(atts.user_traits()).difference(done)
            row_elements = self.elements[row]
            for c in range(len(row_elements)):
                if c == col:
                    continue
                elements = row_elements[c]
                if elements is None:
                    continue
                if not isinstance(elements, list):
                    elements = [elements]
                for element in elements:
                    eatts = element['attributes']
                    for k in missing:
                        if k in eatts:
                            setattr(atts, k, eatts[k])
                            missing.remove(k)
                            if len(missing) == 0:
                                break
                    if len(missing) == 0:
                        break

    def viewer_clicked(self, checked):
        if checked:
            element_d = self.current_item
            if element_d is None:
                return
            element, data_type, row, col = element_d
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
                        self._set_compl_attribs(att, element['attributes'],
                                                row, col)
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
            element, data_type, row, col = element_d
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
                        self._set_compl_attribs(att, element['attributes'],
                                                row, col)
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
        element, data_type, _, _ = element_d
        viewers = self.get_viewers(element, process=self,
                                   data_type=data_type, check_values=True)
        self.show_interactive_viewers(element, data_type, viewers)

    def editor_right_clicked(self, pos):
        element_d = self.current_item
        if element_d is None:
            return
        element, data_type, _, _ = element_d
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
                        row, col = self.current_item[2:4]
                        self._set_compl_attribs(att, element['attributes'],
                                                row, col)
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

    def find_data_gui(self):
        if hasattr(self, 'find_dialog'):
            dialog = self.find_dialog
        else:
            # self.current_search = None
            self.current_search_col = 0
            # self.current_filter = None
            dialog = Qt.QDialog()
            dialog.setWindowTitle('Find elements')
            lay = Qt.QVBoxLayout(dialog)
            lay.addWidget(Qt.QLabel('Find elements'))
            grid = Qt.QGridLayout()
            lay.addLayout(grid)
            text = Qt.QLineEdit()
            grid.addWidget(Qt.QLabel('What'), 0, 0)
            grid.addWidget(Qt.QLabel('Where'), 0, 1)
            grid.addWidget(text, 1, 0)
            combo = Qt.QComboBox()
            grid.addWidget(combo, 1, 1)
            combo.addItem('Current column')
            combo.addItem('Whole table')

            bl = Qt.QHBoxLayout()
            lay.addLayout(bl)
            ok = Qt.QPushButton('OK')
            ok.setSizePolicy(Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Fixed)
            bl.addWidget(ok)
            ok.pressed.connect(dialog.accept)
            filt = Qt.QToolButton()
            filt.setCheckable(True)
            filt.setText('Filter')
            bl.addWidget(filt)
            filt.hide()
            filt.setChecked(True)
            self.find_dialog = dialog
            self.find_text = text
            self.find_mode_combo = combo
            self.find_filter_btn = filt
            text.textChanged.connect(self.update_find_gui)
            filt.toggled.connect(self.update_find_gui)
            combo.textActivated.connect(self.update_find_gui)

        index = self.table.currentIndex()
        if index:
            while index.model() is not self.model:
                proxy = index.model()
                if proxy is None:
                    break
                index = proxy.mapToSource(index)
            item = self.model.itemFromIndex(index)
            ctext = ''
            if item is not None:
                ctext = item.text()
                if not ctext and hasattr(item, 'sort_data'):
                    ctext = DataSelector.status_str[item.sort_data]
            self.find_text.setText(ctext)

        dialog.show()

    def update_find_gui(self, _=None):
        text = self.find_text.text()
        filt = self.find_filter_btn.isChecked()
        col_mode = self.find_mode_combo.currentText()
        index = self.table.currentIndex()
        # item = None
        col = self.current_search_col
        if index:
            while index.model() is not self.model:
                proxy = index.model()
                if proxy is None:
                    break
                index = proxy.mapToSource(index)
            # item = self.model.itemFromIndex(index)
            col = index.column()
            if col >= 0:
                self.current_search_col = col
        # print('search:', text, filt, col_mode, index, item)
        if col_mode == 'Whole table':
            col = -1
        elif col < 0:
            col = self.current_search_col
        if filt:
            proxy = self.table.model()
            proxy.setFilterKeyColumn(col)
            regexp = Qt.QRegularExpression(
                text, Qt.QRegularExpression.NoPatternOption)
            proxy.setFilterRegularExpression(regexp)
        else:
            proxy.setFilterRegularExpression(None)
        nrows = proxy.rowCount()
        self.count_label.setText(f'Items count: {nrows}')


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

    action_triggered = Qt.Signal(Qt.QStandardItem, int)
    viewer_triggered = Qt.Signal(Qt.QStandardItem, int)

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
    proc.data_filters = "{'*': {'center': 'subjects'}}"
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
