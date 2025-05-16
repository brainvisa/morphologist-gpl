
from soma.qt_gui import qt_backend
qt_backend.set_qt_backend(compatible_qt5=True)
from soma.qt_gui.qt_backend import Qt, QtWebEngineWidgets
import threading
from soma.qt_gui import qtThread
from .sulpated_data import SulcalPatternsData, OutdatedError, LockedDataError
from soma import aims
from functools import partial
import weakref
import getpass
import sip
import sys
import os.path as osp
import time


# FIXME: taken from database_qc_table process, should move to soma-base
class RotatedHeaderView(Qt.QHeaderView):

    def __init__(self, orientation, parent=None):
        super(RotatedHeaderView, self).__init__(orientation, parent)
        self.setMinimumSectionSize(20)

    def paintSection(self, painter, rect, logicalIndex):
        import sip
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
        super(RotatedHeaderView, self).paintSection(painter, newrect,
                                                    logicalIndex)
        painter.restore()

    def minimumSizeHint(self):
        size = super(RotatedHeaderView, self).minimumSizeHint()
        size.transpose()
        return size

    def sectionSizeFromContents(self, logicalIndex):
        size = super(RotatedHeaderView, self).sectionSizeFromContents(
            logicalIndex)
        size.transpose()
        return Qt.QSize(size.width(), int(size.height() * 0.9))


#class RightClickTableWidget(Qt.QTableWidget):

    #itemRightClicked = Qt.Signal(Qt.QTableWidgetItem)

    #def contextMenuEvent(self, event):
        #item = self.itemAt(event.pos())
        #if item is not None:
            #self.itemRightClicked.emit(item)


class AnnotationWidget(Qt.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.editor = weakref.proxy(parent)
        self.subject = None
        self.side = None
        self.pattern = None

        layout = Qt.QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(Qt.QLabel('Annotation:'))
        self.edit = Qt.QTextEdit()
        self.edit.setMinimumSize(200, 100)
        self.edit.setSizePolicy(Qt.QSizePolicy.Expanding,
                                Qt.QSizePolicy.Minimum)
        layout.addWidget(self.edit)
        lay2 = Qt.QVBoxLayout()
        layout.addLayout(lay2)
        self.valid = Qt.QPushButton('OK')
        lay2.addWidget(self.valid)
        self.cancel = Qt.QPushButton('Cancel')
        lay2.addWidget(self.cancel)

    def clear(self):
        self.edit.blockSignals(True)
        self.edit.clear()
        self.subject = None
        self.side = None
        self.pattern = None
        self.edit.blockSignals(False)

    def set_pattern(self, subject, side, pattern):
        self.clear()
        self.subject = subject
        self.side = side
        self.pattern = pattern
        annotation = None
        with self.editor.data_model.lock:
            pat = self.editor.get_pattern(subject, side)
            if pat:
                annotation = pat.patterns.get(pattern, {}).get('annotation')
        if annotation:
            self.edit.blockSignals(True)
            self.edit.setPlainText(annotation)
            self.edit.blockSignals(False)


class SulcalPatternsEditor(Qt.QWidget):

    notify_update_started = Qt.Signal()
    notify_update_finished = Qt.Signal()
    CLICK_MINTIME = 0.05  # 20 ms between clicks, at least

    def __init__(self, out_db, region, sulci_db=None, db_filter={},
                 ro_db=None):
        super().__init__()
        self.update_thread = None
        self.updating = False
        self.lock = threading.RLock()

        self.data_model = SulcalPatternsData(out_db, region, sulci_db,
                                             db_filter, ro_db)
        self.pat_status_col = 0
        self.save_pat_col = 1
        self.lock_pat_col = 2
        sulci_status_col = 3
        self.save_sulci_col = 4
        self.lock_sulci_col = 5
        self.pattern_def = {}
        self.disable_conflict_warn = False
        self.displayed_sulci = {}
        self.sulci_window_block = None
        self._last_click = 0.

        # force initialization from main thread
        tc = qtThread.QtThreadCall()

        # init GUI
        layout = Qt.QVBoxLayout()
        self.setLayout(layout)
        self.summary_table = Qt.QTableWidget()
        layout.addWidget(self.summary_table)

        self.annot_widget = AnnotationWidget(self)
        layout.addWidget(self.annot_widget)

        self.data_model.notify_update_started.connect(self.update_started)
        self.data_model.notify_update_finished.connect(self.update_gui)
        self.data_model.notify_backup_saved.connect(
            self.pattern_conflict_detected)
        self.summary_table.itemClicked.connect(self.item_clicked)
        self.summary_table.itemActivated.connect(self.item_clicked)
        self.summary_table.itemChanged.connect(self.item_changed)
        # self.summary_table.itemRightClicked.connect(self.item_right_clicked)
        self.summary_table.currentItemChanged.connect(
            self.current_item_changed)

        self.annot_widget.edit.textChanged.connect(self.annot_edited)
        self.annot_widget.valid.clicked.connect(self.validate_annotation)
        self.annot_widget.cancel.clicked.connect(self.cancel_annotation)

        hlay = Qt.QHBoxLayout()
        layout.addLayout(hlay)
        self.save_btn = Qt.QPushButton('Save all')
        self.show_conflict_btn = Qt.QPushButton('Show conflicts')
        self.export_patterns_btn = Qt.QPushButton('Export patterns')
        self.quit_btn = Qt.QPushButton('Quit')
        hlay.addWidget(self.save_btn)
        hlay.addWidget(self.show_conflict_btn)
        hlay.addWidget(self.export_patterns_btn)
        hlay.addWidget(self.quit_btn)

        hlay.addStretch(1)
        self.help_btn = Qt.QPushButton('Help')
        hlay.addWidget(self.help_btn)

        hlay.addStretch(1)
        vbox = Qt.QGroupBox('Display sulci model:')
        hlay.addWidget(vbox)
        mlay = Qt.QHBoxLayout()
        vbox.setLayout(mlay)
        smodel_l = Qt.QCheckBox('left')
        smodel_r = Qt.QCheckBox('right')
        mlay.addWidget(smodel_l)
        mlay.addWidget(smodel_r)

        self.save_btn.clicked.connect(self.save_all)
        self.show_conflict_btn.clicked.connect(self.show_conflicts)
        self.export_patterns_btn.clicked.connect(
            self.export_patterns_table_gui)
        self.quit_btn.clicked.connect(self.close)
        self.help_btn.clicked.connect(self.show_help)

        smodel_l.stateChanged.connect(self.display_left_model)
        smodel_r.stateChanged.connect(self.display_right_model)

        self.data_model.start_polling_thread(1.)
        self.resize(1100, 800)  # for now...

        self.poll_timer = Qt.QTimer(self)
        self.poll_timer.timeout.connect(self.poll_modified_sulci)
        self.poll_timer.start(1000)

    def __del__(self):
        try:
            self.data_model.notify_update_finished.disconnect()
        except Exception:
            pass  # cannot always disconnect when exiting
        self.data_model.stop_update()

    def update_started(self):
        print('update_started')
        # Qt.QApplication.instance().setOverrideCursor(Qt.Qt.BusyCursor)

    def item_color(self, subject, side, pattern, checked):
        if not self.pattern_def:
            return None
        pd = self.pattern_def.get(pattern)
        if not pd:
            return None
        color = pd.get('color')
        if not color:
            return None
        if not checked:
            gray = [0.7, 0.7, 0.7]
            w = 0.4
            color = [c * w + g * (1. - w)
                      for c, g in zip(color, gray)]
        color = [int(round(c * 255)) for c in color]
        return color

    def update_gui(self, aborted):
        if aborted:
            print('update_gui aborted')
            # Qt.QApplication.instance().restoreOverrideCursor()
            return
        print('update_gui')
        Qt.QApplication.instance().setOverrideCursor(Qt.Qt.BusyCursor)
        self.validate_annotation()
        self.annot_widget.clear()
        with self.lock:
            subjects = self.data_model.subjects
            # graphs = self.data_model.graphs
            patterns = self.data_model.patterns
            pat_def = self.data_model.pattern_def
        # print('subjects:', len(subjects))
        pat_def = pat_def.get(self.data_model.region, {})
        # print('patterns:', patterns)
        table = self.summary_table

        current_item = table.currentItem()
        if current_item:
            cur_sub, cur_side, cur_pat, cur_ctl = self.item_id(current_item)
            current_item = True  # release ref to item
            if cur_pat:
                cur_feature = cur_pat
            else:
                cur_feature = cur_ctl

        table.blockSignals(True)
        self.annot_widget.blockSignals(True)
        #table.clear()
        table.setRowCount(len(subjects))
        base_cols = list(pat_def.keys()) + [
            'status', 'save', 'locked', 'sulci', 'sulci status', 'save sulci',
            'sulci lock']
        pat_status_col = len(base_cols) - 7
        save_pat_col = len(base_cols) - 6
        lock_pat_col = len(base_cols) - 5
        sulci_col = len(base_cols) - 4
        sulci_status_col = len(base_cols) - 3
        save_sulci_col = len(base_cols) - 2
        lock_sulci_col = len(base_cols) - 1
        self.save_pat_col = save_pat_col
        self.lock_pat_col = lock_pat_col
        self.save_sulci_col = save_sulci_col
        self.lock_sulci_col = lock_sulci_col
        self.pattern_def = pat_def

        side_names = []
        for subject, sides in patterns.items():
            for side in sorted(sides):
                if side not in side_names:
                    side_names.append(side)
        sides = len(side_names)

        if sides == 2:
            cols = ['%s L' % x for x in base_cols] \
                + ['%s R' % x for x in base_cols]
        else:
            if len(side_names) == 0:
                side_names = ['left']
            s = {'left': 'L', 'right': 'R'}[side_names[0]]
            cols = ['%s %s' % (x, s) for x in base_cols]
        cols.insert(0, 'subject')
        self.side_names = side_names
        table.setHorizontalHeader(RotatedHeaderView(Qt.Qt.Horizontal, table))

        header = table.horizontalHeader()
        header.show()
        header.setSectionsClickable(True)
        header.setSectionsMovable(True)

        table.setColumnCount(len(cols))
        header.setDefaultSectionSize(32)
        header.setDefaultAlignment(Qt.Qt.AlignLeft)
        table.setHorizontalHeaderLabels(cols)
        table.setSortingEnabled(False)
        table.setEditTriggers(table.NoEditTriggers)

        #table.setVerticalHeaderLabels(sorted(subjects))
        save_icon_f = aims.carto.Paths.findResourceFile('icons/save.png',
                                                        'morphologist')
        self.save_icon = Qt.QIcon(save_icon_f)
        save_d_icon_f = aims.carto.Paths.findResourceFile(
            'icons/save_disabled.png', 'morphologist')
        self.save_dis_icon = Qt.QIcon(save_d_icon_f)

        pat_icon_f = aims.carto.Paths.findResourceFile('icons/pattern.png',
                                                       'morphologist')
        pat_icon = Qt.QImage(pat_icon_f)
        pat_brush = Qt.QBrush(pat_icon)
        self.pattern_brush = pat_brush
        self.pattern_image_file = pat_icon_f

        sul_icon_f = aims.carto.Paths.findResourceFile('icons/sulci.png',
                                                       'morphologist')
        sul_icon = Qt.QImage(sul_icon_f)
        sul_brush = Qt.QBrush(sul_icon)
        sul_w_icon_f = aims.carto.Paths.findResourceFile('icons/sulci_w.png',
                                                         'morphologist')
        sul_w_icon = Qt.QImage(sul_w_icon_f)
        sul_w_brush = Qt.QBrush(sul_w_icon)
        self.sulci_brushes = [sul_brush, sul_w_brush]
        self.sulci_image_files = [sul_icon_f, sul_w_icon_f]

        lock_icon_f = aims.carto.Paths.findResourceFile('icons/lock.png',
                                                        'morphologist')
        lock_icon = Qt.QIcon(lock_icon_f)
        unlock_icon_f = aims.carto.Paths.findResourceFile(
            'icons/lock_open.png', 'morphologist')
        unlock_icon = Qt.QIcon(unlock_icon_f)
        self.lock_icons = [unlock_icon, lock_icon]

        eye_icon_f = aims.carto.Paths.findResourceFile('icons/eye.png',
                                                       'morphologist')
        eye_icon = Qt.QIcon(eye_icon_f)
        eye_c_icon_f = aims.carto.Paths.findResourceFile(
            'icons/eye_closed.png', 'morphologist')
        eye_c_icon = Qt.QIcon(eye_c_icon_f)
        self.visible_icons = [eye_c_icon, eye_icon]

        mod_icon_f = aims.carto.Paths.findResourceFile('icons/modified.png',
                                                       'morphologist')
        self.modified_icon = Qt.QIcon(mod_icon_f)
        confl_icon_f = aims.carto.Paths.findResourceFile('icons/conflict.png',
                                                         'morphologist')
        self.conflict_icon = Qt.QIcon(confl_icon_f)

        self.sul_brush = sul_brush
        self.sul_w_brush = sul_w_brush

        colsizes = [None for c in range(len(cols))]
        null_icon = Qt.QIcon()

        for row, subject in enumerate(subjects):
            table.setItem(row, 0, Qt.QTableWidgetItem(subject))
            for s in range(sides):
                # print(row, subject, s)
                side = side_names[s]
                pats = patterns.get(subject, {}).get(side)
                if pats is None:
                    continue
                for c, (p, pd) in enumerate(pat_def.items()):
                    text = ''
                    checked = Qt.Qt.Unchecked
                    if pats is not None and p in pats.patterns:
                        if pats.patterns[p].get('enabled'):
                            checked = Qt.Qt.Checked
                        confidence = pats.patterns[p].get('confidence')
                        if confidence:
                            text = str(confidence)
                    col = c + s * len(base_cols) + 1
                    colsizes[col] = 65
                    titem = Qt.QTableWidgetItem(text)
                    titem.setCheckState(checked)
                    #titem.setFlags(titem.flags() | Qt.Qt.ItemIsUserCheckable
                                   #| Qt.Qt.ItemNeverHasChildren)
                    table.setItem(row, col, titem)
                    color = self.item_color(subject, side, p, checked)
                    if color:
                        titem.setBackground(Qt.QBrush(Qt.QColor(*color)))
                # status, lock, save patterns button
                pstatus = pats.status
                status_icn = null_icon
                save_icon = self.save_dis_icon
                if pstatus == 'conflict':
                    status_icn = self.conflict_icon
                elif pstatus == 'modified':
                    status_icn = self.modified_icon
                if pats.modified:
                    save_icon = self.save_icon
                sidecol = len(base_cols) * s + 1
                item = Qt.QTableWidgetItem()
                item.setIcon(status_icn)
                item.setBackground(pat_brush)
                table.setItem(row, pat_status_col + sidecol, item)
                item = Qt.QTableWidgetItem(save_icon, None)
                item.setBackground(pat_brush)
                table.setItem(row, save_pat_col + sidecol, item)
                locked_icn = self.lock_icons[int(pats.locked())]
                locked = pats.locked()
                item = Qt.QTableWidgetItem(locked_icn, None)
                item.setData(Qt.Qt.UserRole, locked)
                item.setBackground(pat_brush)
                table.setItem(row, lock_pat_col + sidecol, item)

                visible = side in self.displayed_sulci.get(subject, {})
                visible_icn = self.visible_icons[int(visible)]
                item = Qt.QTableWidgetItem(visible_icn, None)
                item.setData(Qt.Qt.UserRole, visible)
                item.setBackground(sul_brush)
                table.setItem(row, sulci_col + sidecol, item)

                sstatus = pats.sulci_status
                status_icn = null_icon
                save_icon = self.save_dis_icon
                if sstatus == 'conflict':
                    status_icn = self.conflict_icon
                elif pats.sulci_modified():
                    status_icn = self.modified_icon
                if pats.sulci_modified():
                    save_icon = self.save_icon
                item = Qt.QTableWidgetItem()
                item.setIcon(status_icn)
                table.setItem(row, sulci_status_col + sidecol, item)

                if pats.is_output_graph:
                    item.setBackground(sul_w_brush)
                else:
                    item.setBackground(sul_brush)

                item = Qt.QTableWidgetItem(save_icon, None)
                item.setBackground(sul_brush)
                table.setItem(row, save_sulci_col + sidecol, item)
                item = Qt.QTableWidgetItem(None)
                item.setBackground(sul_brush)
                locked_icn = self.lock_icons[int(pats.sulci_locked)]
                if pats.sulci_locked:
                    locked = True
                else:
                    locked = False
                item.setIcon(locked_icn)
                item.setData(Qt.Qt.UserRole, locked)
                table.setItem(row, lock_sulci_col + sidecol, item)

        if len(subjects) != 0:
            header.resizeSection(0, max([len(s) for s in subjects]) * 10)
        for c, s in enumerate(colsizes):
            if s is not None:
                header.resizeSection(c, s)
        table.setSortingEnabled(True)
        table.sortItems(0, Qt.Qt.AscendingOrder)

        table.blockSignals(False)
        self.annot_widget.blockSignals(False)

        # restore current item
        if current_item:
            row, col = self.get_table_item(cur_sub, cur_side, cur_feature)
            if row is not None and col is not None:
                item = table.item(row, col)
                table.setCurrentItem(item)

        for row, subject in enumerate(subjects):
            table.setItem(row, 0, Qt.QTableWidgetItem(subject))
            for side in side_names:
                self.update_sulci_view(subject, side, full=True)

        Qt.QApplication.instance().restoreOverrideCursor()

    def item_id(self, item):
        col = item.column()
        row = item.row()
        subject = self.summary_table.item(row, 0).text()
        col_name = self.summary_table.horizontalHeaderItem(col).text()
        if col_name == 'subject':
            return row, None, None, 'subject'

        side = col_name[-1]
        side = {'L': 'left', 'R': 'right'}[side]
        col_name = col_name[:-2]  # remove side
        with self.data_model.lock:
            pat_def = self.data_model.pattern_def.get(
                self.data_model.region, {})
        if col_name in pat_def:
            pattern = col_name
            control_btn = None
        else:
            pattern = None
            control_btn = col_name
        return subject, side, pattern, control_btn

    def item_clicked(self, item):
        # prevent double call via click and activate callbacks
        if time.time() - self._last_click < self.CLICK_MINTIME:
            return

        # print('CLICK')
        subject, side, pattern, control_btn = self.item_id(item)
        # print('control_btn:', control_btn)
        if control_btn == 'save':
            self.save_pattern_item(item, subject, side)
        elif control_btn == 'save sulci':
            self.save_sulci(subject, side)
        elif control_btn == 'locked':
            self.toggle_lock_pattern(item, subject, side)
        elif control_btn == 'sulci lock':
            self.toggle_lock_sulci(item, subject, side)
        elif control_btn == 'sulci':
            self.toggle_show_sulci(item, subject, side)
        elif pattern is not None:
            self.summary_table.setCurrentItem(item)
            self.summary_table.editItem(item)

        self._last_click = time.time()

    #def item_right_clicked(self, item):
        #print('RIGHT CLICK')
        #subject, side, pattern, control_btn = self.item_id(item)
        #if side:
            #self.edit_patterns_properties(subject, side)

    def item_changed(self, item):
        # print('CHANGED')
        subject, side, pattern, control_btn = self.item_id(item)
        if pattern is not None:
            self.update_pattern(item, subject, side, pattern)
        elif control_btn == 'locked':
            self.lock_pattern(item, subject, side)
        elif control_btn == 'sulci':
            self.show_sulci(item, subject, side)
        elif control_btn == 'sulci lock':
            self.lock_sulci(item, subject, side)

    #def item_double_clicked(self, item):
        #print('DBL CLICK')
        #subject, side, pattern, control_btn = self.item_id(item)
        #if pattern is not None:
            #self.toggle_pattern(item, subject, side, pattern)
        #else:
            #print('button not handled.')

    def current_item_changed(self, item, previous_item):
        # print('CURRENT CHANGED')
        if previous_item:
            subject, side, pattern, control_btn = self.item_id(previous_item)
            if subject and side and pattern:
                self.validate_annotation(subject, side, pattern)
        subject, side, pattern, control_btn = self.item_id(item)
        if subject and side and pattern:
            # edit pattern annotation
            self.annot_widget.set_pattern(subject, side, pattern)
        else:
            # clear annotation
            self.annot_widget.clear()

    def validate_annotation(self, subject=None, side=None, pattern=None):
        # print('validate_annotation', subject, side, pattern)
        if subject is None or side is None or pattern is None:
            subject = self.annot_widget.subject
            side = self.annot_widget.side
            pattern = self.annot_widget.pattern
        if subject is None or side is None or pattern is None:
            return  # not related to a real pattern

        # print('Validate:', subject, side, pattern)
        annotation = self.annot_widget.edit.toPlainText()
        with self.data_model.lock:
            pat = self.get_pattern(subject, side)
            if pat is None or not pat.modified:
                #if pat:
                    #print('NOT MODIFIED')
                return
            if not annotation and pattern not in pat.patterns:
                # not modified, and empty
                return
            p = pat.patterns.setdefault(pattern, {})
            if p.get('annotation') == annotation:
                # not modified
                return
            if not annotation:
                if 'annotation' in p:
                    del p['annotation']
            else:
                p['annotation'] = annotation
        row, col = self.get_table_item(subject, side, pattern)
        item = self.summary_table.item(row, col)
        self.update_pattern(item, subject, side, pattern)

    def cancel_annotation(self, subject=None, side=None, pattern=None):
        if subject is None or side is None or pattern is None:
            subject = self.annot_widget.subject
            side = self.annot_widget.side
            pattern = self.annot_widget.pattern
        # print('Cancel:', subject, side, pattern)
        self.annot_widget.set_pattern(subject, side, pattern)
        row, col = self.get_table_item(subject, side, pattern)
        if row is None or col is None:
            return
        item = self.summary_table.item(row, col)
        self.update_pattern(item, subject, side, pattern)

    def annot_edited(self):
        with self.data_model.lock:
            pat = self.get_pattern(self.annot_widget.subject,
                                   self.annot_widget.side)
            if not pat or pat.modified:
                return
            annotation = self.annot_widget.edit.toPlainText()
            if annotation.strip() == '':
                annotation = None
            if pat.patterns.get(
                    self.annot_widget.pattern, {}).get('annotation') \
                        != annotation:
                pat.modified = True
        row, col = self.get_table_item(self.annot_widget.subject,
                                       self.annot_widget.side,
                                       self.annot_widget.pattern)
        item = self.summary_table.item(row, col)
        self.update_pattern(item, self.annot_widget.subject,
                            self.annot_widget.side, self.annot_widget.pattern)

    def toggle_pattern(self, item, subject, side, pattern):
        if item.checkState() == Qt.Qt.Unchecked:
            item.setCheckState(Qt.Qt.Checked)
        else:
            item.setCheckState(Qt.Qt.Unchecked)
        #self.update_pattern(item, subject, side, pattern)

    def update_pattern(self, item, subject, side, pattern):
        # print('change pattern state')
        if item.checkState() == Qt.Qt.Checked:
            state = True
        else:
            state = False
        color = self.item_color(subject, side, pattern, state)
        if color:
            item.setBackground(Qt.QBrush(Qt.QColor(*color)))
        confidence = None
        if item.text():
            try:
                confidence = float(item.text())
            except ValueError:
                # cancel edition
                with self.data_model.lock:
                    confidence = self.get_pattern(subject, side).patterns.get(
                        pattern, {}).get('confidence')
        if confidence is None:
            conf = ''
        else:
            conf = str(confidence)
        self.summary_table.blockSignals(True)
        item.setText(conf)
        self.summary_table.blockSignals(False)
        remove_keys = []
        with self.data_model.lock:
            pstate = {}
            pat = self.get_pattern(subject, side)
            if pat:
                p = pat.patterns.get(pattern, {})
                pstate.update(p)
            pstate['enabled'] = state
            if confidence is not None:
                pstate['confidence'] = confidence
            elif 'confidence' in pstate:
                remove_keys.append('confidence')

            self.data_model.set_pattern_state(subject, side, pattern, pstate,
                                              remove_keys=remove_keys)
            mod = pat.modified
            status = pat.status
        if mod:
            save_icon = self.save_icon
        else:
            save_icon = self.save_dis_icon
        side_i = self.side_names.index(side)
        status_col \
            = self.pat_status_col + len(self.pattern_def) * (side_i + 1) + 1
        if side_i != 0:
            status_col += 7  # control buttons for side 0
        status_icn = Qt.QIcon()
        if status == 'conflict':
            status_icn = self.conflict_icon
        elif mod:
            status_icn = self.modified_icon
        self.summary_table.item(item.row(), status_col).setIcon(status_icn)
        self.summary_table.item(item.row(), status_col + 1).setIcon(save_icon)
        # update view
        self.update_sulci_view(subject, side)

    def save_pattern_item(self, item, subject, side):
        self.save_pattern(item.row(), subject, side)

    def save_pattern(self, row, subject, side):
        # print('save_pattern', subject, side)
        self.validate_annotation()
        try:
            self.data_model.save_individual_pattern(subject, side)
        except (OutdatedError, LockedDataError):
            pass

        with self.data_model.lock:
            pstatus = self.data_model.patterns[subject][side].status
        status_icn = Qt.QIcon()
        if pstatus == 'conflict':
            status_icn = self.conflict_icon
        side_i = self.side_names.index(side)
        status_col \
            = self.pat_status_col + len(self.pattern_def) * (side_i + 1) + 1
        if side_i != 0:
            status_col += 7  # control buttons for side 0
        self.summary_table.item(row, status_col).setIcon(status_icn)
        self.summary_table.item(row, status_col + 1).setIcon(
            self.save_dis_icon)
        self.update_sulci_view(subject, side)

    def toggle_lock_pattern(self, item, subject, side):
        locked = item.data(Qt.Qt.UserRole)
        # print('toggle locked:', locked)
        self.lock_pattern(item, subject, side, not locked)

    def lock_pattern(self, item, subject, side, state=-1):
        if getattr(self, '_locking_item', None):
            return
        self._locking_item = item
        try:
            if state != -1:
                locked = state
                item.setData(Qt.Qt.UserRole, locked)
            else:
                locked = item.data(Qt.Qt.UserRole)
            # print('lock_pattern:', locked)
            if not locked:
                # confirm unlock
                res = Qt.QMessageBox.question(
                    self, 'Unlock',
                    'Patterns are locked for subject %s, side %s. Do you want '
                    'to unlock them ?' % (subject, side),
                    Qt.QMessageBox.Yes | Qt.QMessageBox.No)
                if res != Qt.QMessageBox.Yes:
                    self.summary_table.blockSignals(True)
                    #item.setCheckState(Qt.Qt.Checked)
                    item.setData(Qt.Qt.UserRole, True)
                    self.summary_table.blockSignals(False)
                    self.update_sulci_view(subject, side)
                    return
            with self.data_model.lock:
                patterns = self.data_model.patterns.get(subject, {}).get(side)
                if not patterns:
                    return  # updated in the meantime
                lock_icn = self.lock_icons[int(locked)]
                if locked:
                    patterns.lock()
                else:
                    patterns.unlock()
                item.setIcon(lock_icn)
                self.data_model.save_version()
            self.update_sulci_view(subject, side)
        finally:
            del self._locking_item

    def update_sulci_view(self, subject, side, full=False):
        view_items = self.displayed_sulci.get(subject, {}).get(side)
        if view_items:
            pat_wid = view_items[-1]
            if full:
                pat_wid.update_gui()
            else:
                pat_wid.update_gui_state()

    def toggle_lock_sulci(self, item, subject, side):
        locked = item.data(Qt.Qt.UserRole)
        # item.setData(Qt.Qt.UserRole, not locked)
        self.lock_sulci(item, subject, side, not locked)

    def lock_sulci(self, item, subject, side, state=-1):
        # locked = item.checkState() == Qt.Qt.Checked
        if getattr(self, '_locking_item', None):
            return
        self._locking_item = item
        try:
            if state != -1:
                locked = state
                item.setData(Qt.Qt.UserRole, locked)
            else:
                locked = item.data(Qt.Qt.UserRole)
            if not locked:
                # confirm unlock
                res = Qt.QMessageBox.question(
                    self, 'Unlock',
                    'Sulci are locked for subject %s, side %s. Do you want to '
                    'unlock them ?' % (subject, side),
                    Qt.QMessageBox.Yes | Qt.QMessageBox.No)
                if res != Qt.QMessageBox.Yes:
                    self.summary_table.blockSignals(True)
                    # item.setCheckState(Qt.Qt.Checked)
                    item.setData(Qt.Qt.UserRole, True)
                    self.summary_table.blockSignals(False)
                    self.update_sulci_view(subject, side)
                    return
            graph = self.data_model.get_sulci_graph_file(subject, side)
            if graph:
                lock_icn = self.lock_icons[int(locked)]
                if locked:
                    graph.lockData()
                else:
                    graph.unlockData()
                self.data_model.save_version()
                item.setIcon(lock_icn)
            self.update_sulci_view(subject, side)
        finally:
            del self._locking_item

    def save_sulci(self, subject, side, silent=False, modified_only=True):
        r = self.data_model.save_sulci(subject, side,
                                       modified_only=modified_only)
        if not r:  # not saved
            print('not modified')
            return
        with self.data_model.lock:
            pat = self.get_pattern(subject, side)
            if not pat:
                return
            status = pat.sulci_status
            locked = pat.sulci_locked
            backup_filename = pat.sulci_backup_filename()

        if status == 'conflict':
            if locked:
                msg = 'Sulci for subject %s, hemisphere %s have been ' \
                    'locked. A backup has been saved at the following ' \
                    'location: %s' % (subject, side, backup_filename)
            else:
                msg = 'Sulci for subject %s, hemisphere %s have been ' \
                        'modified by another user. A backup has been saved ' \
                        'at the following location: %s' \
                        % (subject, side, backup_filename)
            if not silent:
                Qt.QMessageBox.critical(self, 'Conflict', msg)
            status_icon = self.conflict_icon
        else:
            status_icon = Qt.QIcon()
        row, col = self.get_table_item(subject, side, 'sulci status')
        item = self.summary_table.item(row, col)
        item.setIcon(status_icon)
        item.setBackground(self.sul_w_brush)
        item = self.summary_table.item(row, col + 1)
        item.setIcon(self.save_dis_icon)
        self.update_sulci_view(subject, side)

    def get_table_item(self, subject, side=None, pattern_or_button=None):
        row = [i for i in range(self.summary_table.rowCount())
               if self.summary_table.item(i, 0).text() == subject]
        if len(row) != 1:
            return None, None
        row = row[0]
        if side is None or pattern_or_button is None:
            return row, None

        if pattern_or_button == 'subject':
            return row, 0

        hemi = {'left': 'L', 'right': 'R'}[side]
        label = '%s %s' % (pattern_or_button, hemi)
        col = [i for i in range(self.summary_table.columnCount())
                if self.summary_table.horizontalHeaderItem(i).text() == label]
        if len(col) != 1:
            return row, None
        col = col[0]
        return row, col

    def pattern_conflict_detected(self, subject, side, filename):
        if self.disable_conflict_warn:
            return
        Qt.QMessageBox.critical(
            self, 'Conflict',
            'Data for subject %s, hemisphere %s have been locked or modified '
            'by another user. A backup has been saved at the following '
            'location: %s' % (subject, side, filename))
        row, col = self.get_table_item(subject, side, 'status')
        # print('row, col:', row, col)
        item = self.summary_table.item(row, col)
        item.setIcon(self.conflict_icon)

    def unsaved_data(self):
        return self.data_model.unsaved_data()

    def save_all(self):
        # print('save all')
        unsaved = self.unsaved_data()
        self.disable_conflict_warn = True
        for subject, sides in unsaved.items():
            row, _ = self.get_table_item(subject)
            for side, items in sides.items():
                if items.get('patterns'):
                    self.save_pattern(row, subject, side)
                if items.get('sulci'):
                    self.save_sulci(subject, side, silent=True)
        self.disable_conflict_warn = False

    def get_pattern(self, subject, side):
        ''' should be called within the data_model lock
        '''
        return self.data_model.patterns.get(subject, {}).get(side)

    def update_model(self):
        self.data_model.update()

    def closeEvent(self, event):
        # print('CLOSE EVENT')
        unsaved = self.unsaved_data()
        if unsaved:
            res = Qt.QMessageBox.question(
                self, 'Unsaved', 'There are unsaved data. Save all ?',
                Qt.QMessageBox.SaveAll | Qt.QMessageBox.Ignore
                    | Qt.QMessageBox.Cancel)
            if res == Qt.QMessageBox.Cancel:
                event.ignore()
                return
            elif res == Qt.QMessageBox.SaveAll:
                self.save_all()
        event.accept()
        # clear sulci displays, close anatomist
        self.displayed_sulci = {}
        self.data_model.stop_polling()
        if hasattr(self, '_help_widget'):
            del self._help_widget

        from brainvisa import anatomist

        a = anatomist.Anatomist('-b', create=False)
        if a is not None:
            cw = a.getControlWindow()
            if cw:
                cw.close()
        # force exit since the ipython kernel doesn't exit
        sys.exit(0)

    def sulci_window(self):
        if self.sulci_window_block \
                and (self.sulci_window_block.internalWidget is None
                     or not
                     sip.isdeleted(
                        self.sulci_window_block.internalWidget.widget)):
            return self.sulci_window_block

        from brainvisa import anatomist

        a = anatomist.Anatomist()
        block = a.createWindowsBlock()
        #a.setReusableWindowBlock(block, True)
        self.sulci_window_block = block
        return block

    def toggle_show_sulci(self, item, subject, side):
        visible = side in self.displayed_sulci.get(subject, {})
        self.show_sulci(item, subject, side, not visible)

    def show_sulci(self, item, subject, side, state=-1):
        if getattr(self, '_updating_show_sulci', None):
            return
        self._updating_show_sulci = True
        try:
            self._show_sulci(item, subject, side, state)
        finally:
            del self._updating_show_sulci

    def _show_sulci(self, item, subject, side, state=-1):
        if state != -1:
            checked = state
            item.setIcon(self.visible_icons[int(checked)])
        else:
            checked = side in self.displayed_sulci.get(subject, {})
        # print('show sulci', subject, side, checked)
        if checked:
            from brainvisa import anatomist
            from brainvisa import processes

            a = anatomist.Anatomist()
            a.setExitOnQuit(True)

            graph_file = self.data_model.get_sulci_graph_file(subject, side,
                                                              use_backup=True)
            org_graph_file = self.data_model.get_sulci_graph_file(
                subject, side, use_backup=False)
            w = a.createWindow('3D', block=self.sulci_window())
            # remove the save button
            tb = w.findChild(Qt.QToolBar, 'save')
            if tb is not None:
                tb.hide()
            a.setReusableWindow(w, True)
            context = processes.defaultContext()
            viewer = processes.getProcessInstance('AnatomistShowFoldGraph')
            # initialize using database graph in order to have completion
            viewer.graph = org_graph_file
            viewer.mesh_opacity = 0.7
            # then lock all params and set the backup, if any
            if graph_file not in (org_graph_file, org_graph_file.fullPath()):
                for param in viewer.signature:
                    viewer.setDefault(param, False)
                viewer.graph = graph_file
            items = context.runProcess(viewer)
            # remove browser
            del items[1]
            graph = items[1]
            del items[1]  # kept in data model: avoid duplicating
            with self.data_model.lock:
                pat = self.data_model.patterns.get(subject, {}).get(side)
                if pat:
                    pat.set_sulci_graph(graph)
            self.displayed_sulci.setdefault(subject, {})[side] = items
            w.focusView()
            w.setControl('SelectionControl')
            w.setReferential(a.centralReferential())
            pat_wid = self.add_pattern_widget_to_win(items[-1], subject, side)
            items.append(pat_wid)

        else:
            from anatomist import cpp as anacpp

            # check modified
            save = True
            with self.data_model.lock:
                pat = self.data_model.patterns.get(subject, {}).get(side)
                if pat and not pat.sulci_modified():
                    save = False

            if save:
                res = Qt.QMessageBox.question(
                    self, 'Save ?',
                    'You are about to unload sulci data for subject %s, side '
                    '%s. Do you want to save them ?' % (subject, side),
                    Qt.QMessageBox.Yes | Qt.QMessageBox.No
                        | Qt.QMessageBox.Cancel)
                if res == Qt.QMessageBox.Cancel:
                    self.summary_table.blockSignals(True)
                    item.setIcon(self.visible_icons[1])
                    self.summary_table.blockSignals(False)
                    self.update_sulci_view(subject, side)
                    return
                elif res == Qt.QMessageBox.Yes:
                    self.save_sulci(subject, side)

            with self.data_model.lock:
                pat = self.data_model.patterns.get(subject, {}).get(side)
                if pat:
                    pat.release_sulci()

            s = self.displayed_sulci.get(subject)
            if s:
                if side in s:
                    items = s.get(side)
                    if items:
                        items[-1].clear()
                    del s[side]
                    if len(s) == 0:
                        del self.displayed_sulci[subject]

            if hasattr(anacpp.Referential, 'clearUnusedReferentials'):
                anacpp.Referential.clearUnusedReferentials()

            # update status
            row, col = self.get_table_item(subject, side, 'sulci status')
            item = self.summary_table.item(row, col)
            with self.data_model.lock:
                pat = self.data_model.patterns.get(subject, {}).get(side)
                if pat:
                    if pat.sulci_status == 'conflict':
                        status_icon = self.conflict_icon
                    else:
                        status_icon = Qt.QIcon()
                    item.setIcon(status_icon)

    def add_pattern_widget_to_win(self, win, subject, side):
        layout = win.centralWidget().layout()
        if layout.count() > 2:
            pat_wid = layout.itemAt(2).widget()
            pat_wid.clear()
            sip.transferback(pat_wid)
            layout.takeAt(2)
            del pat_wid
        pat_wid = PatternsWidget(self, subject, side)
        layout.addWidget(pat_wid)
        #win.pattern_widget = pat_wid
        return pat_wid

    def poll_modified_sulci(self):
        if not self.displayed_sulci:
            return
        # print('poll_modified_sulci')
        null_icn = Qt.QIcon()
        with self.data_model.lock:
            for subject, sides in self.displayed_sulci.items():
                for side in sides:
                    pat = self.get_pattern(subject, side)
                    if pat:
                        # print(subject, side, pat.sulci_status)
                        if pat.sulci_status == 'missing':
                            continue
                        row, col = self.get_table_item(subject, side,
                                                       'sulci status')
                        item = self.summary_table.item(row, col)
                        if pat.sulci_modified():
                            status_icn = self.modified_icon
                            save_icon = self.save_icon
                        else:
                            status_icn = null_icn
                            save_icon = self.save_dis_icon
                        if pat.sulci_status == 'conflict':
                            status_icn = self.conflict_icon
                        sitem = self.summary_table.item(row, col + 1)
                        update = False
                        if sitem.icon() != save_icon:
                            sitem.setIcon(save_icon)
                            update = True
                        if item.icon() != status_icn:
                            item.setIcon(status_icn)
                        if update:
                            self.update_sulci_view(subject, side)
                        if pat.is_output_graph:
                            brush = self.sul_w_brush
                            # color = [255, 255, 180]
                        else:
                            brush = self.sul_brush
                            # color = [255, 255, 255]
                        # item.setBackground(Qt.QBrush(Qt.QColor(*color)))
                        item.setBackground(brush)

    def display_left_model(self, state):
        self.display_model('left', state == Qt.Qt.Checked)

    def display_right_model(self, state):
        self.display_model('right', state == Qt.Qt.Checked)

    def display_model(self, side, is_on):
        if is_on:
            with self.data_model.bv_lock:
                from brainvisa import processes
                from brainvisa import anatomist
            import time

            a = anatomist.Anatomist()
            w = getattr(self, 'model_window', None)
            if w is not None:
                print('existing model_window:', w)
                #w = w()
            if w is None:
                w = a.createWindow('3D', block=self.sulci_window())
                self.model_window = w
                w.setControl('SelectionControl')
            context = processes.defaultContext()
            try:
                with self.data_model.bv_lock:
                    viewer = processes.getProcessInstance(
                        'AnatomistShowDescriptiveModel')
            except KeyError:
                print('model viewer not found yet.')
                viewer = None
                while viewer is None:
                    time.sleep(1.)
                    try:
                        with self.data_model.bv_lock:
                            viewer = processes.getProcessInstance(
                                'AnatomistShowDescriptiveModel')
                    except KeyError:
                        print('model viewer not found yet.')
                        pass

            di = viewer.signature['read']
            rdi = list(di.findValues({
                'side': side,
                'sulci_seghments_model_type':
                    'locally_from_global_registred_spam'}))[0]
            viewer.read = rdi
            viewer.show_unknown = True
            items = context.runProcess(viewer)
            # obj_items = items[1].objects
            items = [item for item in items if not isinstance(item, a.AWindow)]
            w.addObjects(items)
            moddata = getattr(self, 'sulci_model_data', {})
            moddata[side] = items
            self.sulci_model_data = moddata
        else:  # is_on == False, remove
            moddata = getattr(self, 'sulci_model_data', {})
            if side in moddata:
                del moddata[side]

    def get_conflicts(self):
        return self.data_model.get_conflicts()

    def show_conflicts(self):
        conflicts = self.data_model.get_conflicts()
        print('conflicts:')
        print(conflicts)

    def export_patterns_table_gui(self):
        if self.get_conflicts():
            res = Qt.QMessageBox.question(
                self, 'Conflicts detected',
                'There are unsolved conflicts in the current data model. Do you want to export -your- version now ?',
                Qt.QMessageBox.Yes | Qt.QMessageBox.No)
            if res == Qt.QMessageBox.No:
                return
        filename, _ = Qt.QFileDialog.getSaveFileName(
            self, 'export patterns table', None, '*.json;;*.csv;;*.yaml')
        print('filename:', filename)
        if filename:
            self.data_model.export_patterns(filename)

    def show_help(self):
        if getattr(self, '_help_widget', None) is not None:
            self._help_widget.show()
            return
        self._help_widget = HelpWidget()
        self._help_widget.show()


class PatternsWidget(Qt.QWidget):

    def __init__(self, sulcal_editor, subject, side, parent=None):
        super().__init__(parent)

        self.editor = weakref.proxy(sulcal_editor)
        self.subject = subject
        self.side = side

        layout = Qt.QHBoxLayout()
        self.setLayout(layout)
        #self.setContentsMargins(5, 5, 5, 5)
        self.setContentsMargins(5, 0, 5, 0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.update_gui()

    def update_gui(self):
        self.blockSignals(True)
        layout = self.layout()
        if layout.count() == 0:
            layout.addWidget(Qt.QLabel('%s, %s' % (self.subject, self.side)))
        # clear layout
        while layout.count() > 1:
            item = layout.takeAt(layout.count() - 1)
            w = item.widget()
            w.disconnect()
            sip.transferback(w)
            del w

        for pattern, pd in self.editor.pattern_def.items():
            row, col = self.editor.get_table_item(self.subject, self.side,
                                                  pattern)
            if row is None or col is None:
                continue
            button = Qt.QPushButton(pattern)
            button.setCheckable(True)
            item = self.editor.summary_table.item(row, col)
            checked = item.checkState()
            button.setChecked(checked)
            button.setObjectName('btn-%s-%s' % (self.subject, self.side))
            button.setToolTip(f'Pattern: {pattern} {self.side}')
            active = (checked == Qt.Qt.Checked)
            color = self.editor.item_color(self.subject, self.side, pattern,
                                           True)
            if color:
                button.setStyleSheet(
                    'QPushButton#%s {background-color: rgb(%d, %d, %d); '
                    'margin-left: 0px; margin-right: 0px;}'
                    % (button.objectName(), color[0], color[1], color[2]))
            else:
                button.setStyleSheet(
                    'QPushButton#%s {margin-left: 0px; margin-right: 0px}'
                    % button.objectName())
            layout.addWidget(button)
            button.toggled.connect(partial(self.pattern_changed, pattern))

        pat_wid = Qt.QGroupBox()
        pat_wid.setObjectName('pat_gbx-%s-%s' % (self.subject, self.side))
        pat_wid.setStyleSheet(
            f'QGroupBox#{pat_wid.objectName()} '
            '{padding-top: 7px; padding-bottom: 3px; padding-left: 3px; padding-right: 3px; '
            f'background-image:url({self.editor.pattern_image_file});}}')
        pat_wid.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(pat_wid)
        layout2 = Qt.QHBoxLayout()
        layout2.setContentsMargins(2, 2, 2, 2)
        pat_wid.setLayout(layout2)

        row, col = self.editor.get_table_item(self.subject, self.side,
                                              'status')
        item = self.editor.summary_table.item(row, col)
        state_l = Qt.QLabel()
        state_l.setAutoFillBackground(False)
        icn = item.icon()
        if icn.isNull():
            pix = Qt.QPixmap()
        else:
            pix = icn.pixmap(icn.availableSizes()[0])
        state_l.setPixmap(pix)
        layout2.addWidget(state_l)

        sitem = self.editor.summary_table.item(row, col + 1)
        save_icon = sitem.icon()
        button = Qt.QPushButton(save_icon, None)
        button.setObjectName('savepat-%s-%s' % (self.subject, self.side))
        button.setStyleSheet(
            f'background-image:url({self.editor.pattern_image_file});')
        layout2.addWidget(button)
        button.clicked.connect(self.save_pattern)
        button.setToolTip('Save patterns')

        row, col = self.editor.get_table_item(self.subject, self.side,
                                              'locked')
        item = self.editor.summary_table.item(row, col)
        button = Qt.QToolButton()
        locked = item.data(Qt.Qt.UserRole)
        icon = self.editor.lock_icons[int(locked)]
        button.setIcon(icon)
        button.setStyleSheet(
            f'background-image:url({self.editor.pattern_image_file});')
        button.setCheckable(True)
        checked = Qt.Qt.Checked if locked else Qt.Qt.Unchecked
        button.setChecked(checked)
        layout2.addWidget(button)
        button.toggled.connect(self.lock_pattern)
        button.setToolTip('[un] Lock patterns')

        sul_wid = Qt.QGroupBox()
        sul_wid.setObjectName('sul_gbx-%s-%s' % (self.subject, self.side))
        sul_wid.setStyleSheet(
            f'QGroupBox#{sul_wid.objectName()} '
            '{padding-top: 7px; padding-bottom: 3px; padding-left: 3px; padding-right: 3px; '
            f'background-image:url({self.editor.sulci_image_files[0]});}}')
        sul_wid.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(sul_wid)
        layout2 = Qt.QHBoxLayout()
        layout2.setContentsMargins(2, 2, 2, 2)
        sul_wid.setLayout(layout2)

        row, col = self.editor.get_table_item(self.subject, self.side,
                                              'sulci status')
        item = self.editor.summary_table.item(row, col)
        sstate_l = Qt.QLabel()
        icn = item.icon()
        if icn.isNull():
            pix = Qt.QPixmap()
        else:
            pix = icn.pixmap(icn.availableSizes()[0])
        sstate_l.setPixmap(pix)
        layout2.addWidget(sstate_l)

        sitem = self.editor.summary_table.item(row, col + 1)
        button = Qt.QPushButton(sitem.icon(), None)
        button.setObjectName('savesulci-%s-%s' % (self.subject, self.side))
        #button.setStyleSheet(
            #'QPushButton#%s {margin-left: 1px; margin-right: 2px;'
            #'margin-top: 2px; margin-bottom: 2px; '
            #'background-image:url(%s);};'
            #% (button.objectName(), self.editor.sulci_image_files[0]))
        button.setStyleSheet(
            f'background-image:url({self.editor.sulci_image_files[0]});')
        layout2.addWidget(button)
        button.clicked.connect(self.save_sulci)
        button.setToolTip('Save sulci')

        row, col = self.editor.get_table_item(self.subject, self.side,
                                              'sulci lock')
        item = self.editor.summary_table.item(row, col)
        locked = item.data(Qt.Qt.UserRole)
        checked = Qt.Qt.Checked if locked else Qt.Qt.Unchecked
        button = Qt.QToolButton()
        button.setStyleSheet(
            f'background-image:url({self.editor.sulci_image_files[0]});')
        button.setCheckable(True)
        button.setIcon(self.editor.lock_icons[locked])
        button.setChecked(checked)
        layout2.addWidget(button)
        button.toggled.connect(self.lock_sulci)
        button.setToolTip('[un] Lock sulci')

        self.blockSignals(False)

    def update_gui_state(self):
        self.blockSignals(True)
        num = 1
        layout = self.layout()
        for pattern, pd in self.editor.pattern_def.items():
            button = layout.itemAt(num).widget()
            row, col = self.editor.get_table_item(self.subject, self.side,
                                                  pattern)
            if row is None or col is None:
                return
            item = self.editor.summary_table.item(row, col)
            checked = item.checkState()
            button.setChecked(checked)
            num += 1

        label = layout.itemAt(num).widget().layout().itemAt(0).widget()
        row, col = self.editor.get_table_item(self.subject, self.side,
                                              'status')
        item = self.editor.summary_table.item(row, col)
        icn = item.icon()
        if icn.isNull():
            pix = Qt.QPixmap()
        else:
            pix = icn.pixmap(icn.availableSizes()[0])
        label.setPixmap(pix)

        save_btn = layout.itemAt(num).widget().layout().itemAt(1).widget()
        sitem = self.editor.summary_table.item(row, col + 1)
        save_btn.setIcon(sitem.icon())

        button = layout.itemAt(num).widget().layout().itemAt(2).widget()
        row, col = self.editor.get_table_item(self.subject, self.side,
                                              'locked')
        item = self.editor.summary_table.item(row, col)
        locked = item.data(Qt.Qt.UserRole)
        checked = Qt.Qt.Checked if locked else Qt.Qt.Unchecked
        button.setChecked(checked)
        button.setIcon(self.editor.lock_icons[int(locked)])

        label = layout.itemAt(num + 1).widget().layout().itemAt(0).widget()
        row, col = self.editor.get_table_item(self.subject, self.side,
                                              'sulci status')
        item = self.editor.summary_table.item(row, col)
        icn = item.icon()
        if icn.isNull():
            pix = Qt.QPixmap()
        else:
            pix = icn.pixmap(icn.availableSizes()[0])
        label.setPixmap(pix)

        save_btn = layout.itemAt(num + 1).widget().layout().itemAt(1).widget()
        sitem = self.editor.summary_table.item(row, col + 1)
        save_btn.setIcon(sitem.icon())

        button = layout.itemAt(num + 1).widget().layout().itemAt(2).widget()
        row, col = self.editor.get_table_item(self.subject, self.side,
                                              'sulci lock')
        item = self.editor.summary_table.item(row, col)
        locked = item.data(Qt.Qt.UserRole)
        checked = Qt.Qt.Checked if locked else Qt.Qt.Unchecked
        button.setChecked(checked)
        button.setIcon(self.editor.lock_icons[int(locked)])

        self.blockSignals(False)

    def clear(self):
        layout = self.layout()
        for i in reversed(range(layout.count())):
            w = layout.itemAt(i).widget()
            if w:
                try:
                    # in some rare cases
                    w.disconnect()
                except Exception as e:
                    print('PatternsWidget.clear() error in signals '
                          'disconnection:', file=sys.stderr)
                    print(e, file=sys.stderr)
            sip.transferback(w)
            layout.takeAt(i)
            del w

    def pattern_changed(self, pattern):
        row, col = self.editor.get_table_item(self.subject, self.side,
                                              pattern)
        if row is None or col is None:
            return
        pindex = list(self.editor.pattern_def.keys()).index(pattern) + 1
        button = self.layout().itemAt(pindex).widget()
        checked = Qt.Qt.Checked if button.isChecked() else Qt.Qt.Unchecked
        self.editor.summary_table.item(row, col).setCheckState(checked)

    def save_pattern(self):
        row, col = self.editor.get_table_item(self.subject, self.side, 'save')
        self.editor.save_pattern(row, self.subject, self.side)

    def lock_pattern(self):
        row, col = self.editor.get_table_item(self.subject, self.side,
                                              'locked')
        if row is None or col is None:
            return
        item = self.editor.summary_table.item(row, col)
        pindex = len(self.editor.pattern_def.keys()) + 1
        button \
            = self.layout().itemAt(pindex).widget().layout().itemAt(2).widget()
        self.editor.lock_pattern(item, self.subject, self.side,
                                 button.isChecked())

    def save_sulci(self):
        self.editor.save_sulci(self.subject, self.side)

    def lock_sulci(self):
        row, col = self.editor.get_table_item(self.subject, self.side,
                                              'sulci lock')
        if row is None or col is None:
            return
        item = self.editor.summary_table.item(row, col)
        pindex = len(self.editor.pattern_def.keys()) + 2
        button \
            = self.layout().itemAt(pindex).widget().layout().itemAt(2).widget()
        self.editor.lock_sulci(item, self.subject, self.side,
                               button.isChecked())


class HelpWidget(Qt.QWidget):

    def __init__(self):
        super().__init__()

        layout = Qt.QVBoxLayout()
        self.setLayout(layout)
        hw = QtWebEngineWidgets.QWebEngineView()
        layout.addWidget(hw)
        icn = aims.carto.Paths.findResourceFile('icons/pattern.png',
                                                'morphologist')
        morpho = osp.basename(osp.dirname(osp.dirname(icn)))
        fname = osp.join(osp.dirname(osp.dirname(osp.dirname(icn))), 'doc',
                         morpho, 'user_doc', 'sulpated.html')
        url = Qt.QUrl('file://' + fname)
        # print('URL:', url)
        hw.setUrl(url)
