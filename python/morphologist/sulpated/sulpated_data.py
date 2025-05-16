
from soma.qt_gui.qt_backend import Qt
from soma.qt_gui import qtThread
import threading
import sys
import os
import os.path as osp
import json
import time
import datetime
import getpass


class OutdatedError(Exception):
    ''' Raised when a file is outdated, which means it has been modified
    externally while its (older) contents are present in memory.
    '''
    pass


class LockedDataError(Exception):
    ''' Raised when a file cannot be re-written because it is locked, either by
    an Axon DiskItem lock, or a :class:`FileLock`.
    '''
    pass


class UpdateAbortError(Exception):
    ''' Raised when a SulcalPatternsData databse update aborts before it is
    finishes, after an interruption request.
    '''
    pass


def sort_items(obj):
    ''' Return a sorted version of the object: sorts dicts and sets in a
    recursive way, in order to get a reproducible items ordering.
    '''
    if isinstance(obj, dict):
        return {k: sort_items(obj[k]) for k in sorted(obj.keys())}
    elif isinstance(obj, set):
        return {sort_items(v) for v in sorted(obj)}
    return obj


class SulcalPattern(object):
    ''' Stores patterns information for a given sulcal graph (subject
        hemisphere).

        All patterns are stored as a dict, with status, lock, modification
        information.
        The sulcal graph file is stored (optionally) as an Axon DiskItem.
    '''
    def __init__(self, filename, sulci_di=None, out_db=None,
                 sulci_db=None, force_sulci_lock=None, out_db_filter={}):
        self.filename = filename
        self.sulci_di = sulci_di
        self.sulci_db = sulci_db
        self.exists = False
        self.patterns = {}
        self.modified = False
        self.status = 'ok'
        self.lock_file = '%s.lock' % self.filename
        self.sulci_status = 'missing'
        self.sulci_locked = False
        self.sulci = None
        self.out_db = out_db
        self.force_sulci_lock = force_sulci_lock
        self.out_db_filter = out_db_filter

        self.load()

    def load(self):
        ''' Loads or reloads, discards unsaved modifications
        '''
        #t0 = time.time()
        backup_file = self.backup_filename()
        patterns = {}

        if osp.exists(backup_file):
            with open(backup_file) as f:
                patterns = json.load(f)
            self.status = 'conflict'

        if self.filename and osp.exists(self.filename):
            self.exists = True
            with open(self.filename) as f:
                in_patterns = json.load(f)
            if self.status == 'conflict':
                if patterns == in_patterns:
                    self.status = 'ok'
                    # no conflict, remove backup
                    os.unlink(backup_file)
            else:
                patterns = in_patterns
                self.status = 'ok'

        self.patterns = patterns
        self.modified = False

        #print('t2:', time.time() - t0)
        if self.sulci_di:
            self.sulci_status = 'ok'
            if self.force_sulci_lock is not None:
                self.sulci_locked = self.force_sulci_lock
            elif self.sulci_di.isLockData():
                self.sulci_locked = True
            #print('t3:', time.time() - t0)
            sulci_backup = self.sulci_backup_filename()
            #print('t4:', time.time() - t0)
            if osp.exists(sulci_backup):
                self.sulci_status = 'conflict'
            #print('t:', time.time() - t0)

    def save(self):
        print('SAVE')
        if self.locked():
            self.save_backup()
            raise LockedDataError(self.filename)
        if not os.path.exists(osp.dirname(self.filename)):
            os.makedirs(osp.dirname(self.filename), exist_ok=True)
        if self.status == 'conflict':
            # try reload and resolve
            self.save_backup()
            if self.status == 'conflict':
                raise OutdatedError(self.filename)

        with open(self.filename, 'w') as f:
            json.dump(self.patterns, f)
        self.exists = True
        self.modified = False
        self.status = 'ok'

    def update_sulci_status(self):
        if not self.sulci_di:
            self.sulci_status = 'missing'
            return None
        filename = self.sulci_di.fullPath()
        if self.sulci:
            if self.sulci_status == 'conflict':
                return None
            if filename != self.sulci.fileName():
                self.sulci_status = 'conflict'
                return None
            mtime = os.stat(filename).st_mtime
            if self.sulci.loadDate <= mtime:
                self.sulci_status = 'conflict'
                return None
                ## if not modified, we should reload.
                #if self.sulci.userModified():
                    #self.sulci_status = 'conflict'
                    #return None
                ## otherwise, outdated but not modified: reload
                #return True
            else:
                # up-to-date: nothing to do.
                return None
        return False

    def load_sulci(self):
        ## currently unused... see set_sulci_graph() instead
        needs_reload = self.update_sulci_status()
        if not needs_reload is None:
            return

        # the following should be called from the GUI thread
        # because it involves threading issues.

        from brainvisa import anatomist as ana

        a = ana.Anatomist()

        backup_filename = self.sulci_backup_filename()
        if osp.exists(backup_filename):
            self.sulci_status = 'conflict'
            filename = backup_filename
        wins = []
        if self.sulci:
            # keep track of views displaying the old graph
            wins = self.sulci.getWindows()
        self.sulci = a.loadObject(filename)
        if self.sulci_di.get('automatically_labelled') == 'Yes':
            # switch to manual labels
            graph = self.sulci.graph()
            for v in graph.vertices():
                label = v.get('label')
                if label is not None:
                    v['name'] = label
            graph['label_property'] = 'name'
            a.execute('GraphDisplayProperties', objects=[self.sulci],
                      nomenclature_property='name')
        self.sulci.addInWindows(wins)
        if self.sulci_status != 'conflict':
            self.sulci_status = 'ok'

    def sulci_load_filename(self):
        if not self.sulci_di:
            return None
        backup_filename = self.sulci_backup_filename()
        print('sulci_load_filename', self.sulci_di, ':', backup_filename)
        if osp.exists(backup_filename):
            print('backup exists')
            self.sulci_status = 'conflict'
            return backup_filename
        return self.sulci_di.fullPath()

    def set_sulci_graph(self, sulci):
        self.sulci = sulci
        if self.sulci_di.get('automatically_labelled') == 'Yes':
            # the following should be called from the GUI thread
            # because it involves threading issues.

            from brainvisa import anatomist as ana

            a = ana.Anatomist()

            # switch to manual labels
            graph = self.sulci.graph()
            for v in graph.vertices():
                label = v.get('label')
                if label is not None:
                    v['name'] = label
            graph['label_property'] = 'name'
            a.execute('GraphDisplayProperties', objects=[self.sulci],
                      nomenclature_property='name')
        if self.sulci_status != 'conflict':
            self.sulci_status = 'ok'
            mtime = os.stat(self.sulci_di.fullPath()).st_mtime
            if self.sulci.loadDate <= mtime:
                self.sulci_status = 'conflict'

    def sulci_modified(self):
        if self.sulci is None:
            return False
        return self.sulci.userModified()

    def release_sulci(self):
        self.sulci = None
        if self.sulci_status == 'conflict' \
                and not osp.exists(self.sulci_backup_filename()):
            self.sulci_status = 'ok'

    def save_sulci(self, modified_only=True):
        graph = self.sulci
        if not graph:
            return False
        if not graph.userModified():
            return False
        graph_di = self.sulci_di

        if self.sulci_db \
                and (graph_di.get('_database') != self.sulci_db
                     or graph_di.get('automatically_labelled') == 'Yes'):
            # was in a read-only database, convert it into the output one
            from brainvisa.data.writediskitem import WriteDiskItem

            sel = dict(graph_di.hierarchyAttributes())
            sel['_database'] = self.sulci_db
            sel['automatically_labelled'] = 'No'
            sel['manually_labelled'] = 'Yes'
            sel.update(self.out_db_filter)
            wdi = WriteDiskItem('Labelled Cortical Folds Graph',
                                'Graph and data')
            di = wdi.findValue(sel)
            if not di:
                print('Could not convert the read-only sulci graph into the '
                      'output sulci database. Using backup')
                print('query:', sel)
                self.sulci_status = 'conflict'
            else:
                print('Switching read-only sulci graph file %s into the '
                      'output sulci database: %s'
                      % (graph_di.fullPath(), di.fullPath()))
                graph_di = di
                self.sulci_di = di
                self.status = 'ok'
                self.sulci_locked = False

        filename = graph_di.fullPath()
        backup_filename = self.sulci_backup_filename()

        if graph_di.isLockData() or (self.force_sulci_lock
                                     and self.sulci_locked):
            filename = backup_filename
            self.sulci_locked = True
            self.sulci_status = 'conflict'
        elif osp.exists(filename):
            mtime = os.stat(filename).st_mtime
            if graph.loadDate <= mtime:
                self.sulci_status = 'conflict'
        if self.sulci_status == 'conflict':
            filename = backup_filename

        if not osp.exists(osp.dirname(filename)):
            os.makedirs(osp.dirname(filename), exist_ok=True)

        graph.save(filename)
        self.is_output_graph = True  # now it has been written in output loc.
        # reset load date to avoid marking it as a conflict
        graph.setLoadDate(int(os.stat(filename).st_mtime) + 1)
        if self.sulci_di == filename:
            from brainvisa.data import neuroHierarchy

            neuroHierarchy.databases.insertDiskItem(self.sulci_di, update=True)
        # print('saved:', filename, ', stat:', os.stat(filename).st_mtime, ', loaddate:', graph.loadDate, ', modified:', graph.userModified())
        return True

    def backup_filename(self):
        return '%s.backup.%s.json' % (self.filename, getpass.getuser())

    def sulci_backup_filename(self):
        if not self.sulci_di:
            return None

        backup = '%s.backup.%s.arg' % (self.sulci_di.fullPath(),
                                       getpass.getuser())
        if self.out_db:
            in_db = self.sulci_di.get('_database')
            backup = osp.join(self.out_db, osp.relpath(backup, in_db))

        return backup

    def save_backup(self):
        backup_file = self.backup_filename()

        # try reload and resolve
        try:
            with open(self.filename) as f:
                patterns = json.load(f)
        except FileNotFoundError:
            # file has been removed in the meantime: just rewrite it
            print('save_backup, orig file', self.filename, 'could not be read. Saving backup:', backup_file)
            os.makedirs(osp.dirname(backup_file), exist_ok=True)
            with open(backup_file, 'w') as f:
                json.dump(self.patterns, f)
            patterns = self.patterns

        if patterns == self.patterns:
            # OK after all
            if osp.exists(backup_file):
                os.unlink(backup_file)
            self.status = 'ok'
            self.modified = False
            self.exists = True
            return

        self.status = 'conflict'
        with open(backup_file, 'w') as f:
            json.dump(self.patterns, f)
        self.modified = False
        self.exists = True

    def locked(self):
        return osp.exists(self.lock_file)

    def lock(self):
        if not osp.exists(osp.dirname(self.lock_file)):
            os.makedirs(osp.dirname(self.lock_file))
        with open(self.lock_file, 'w') as f:
            print(datetime.datetime.now(), file=f)

    def unlock(self):
        if osp.exists(self.lock_file):
            os.unlink(self.lock_file)


class FileLock(object):
    ''' File locking mechanism, working as a filesystem-only lock

    Currently implemented as a directory. Based on the atomicity of mkdir(),
    which throws an error if the direcrory has already been created. The
    implementation might change in the future, provided all users use the same
    implementation on the same database.

    Recursive lock is handled.

    A timeout can be passed to exit the lock after a given time. Raises a
    LockedDataError in such a case.

    Usage: same as a thread RLock, using the "with" statement::

        with FileLock(filename, timeout=10):
            # do something

    Can also be operated "manually"::

        lock = FileLock(filename)
        if not lock.wait(10, raise_error=False):
            print('Lock wait has timed out')
            return
        lock.lock()
        # do something
        lock.unlock()
    '''
    def __init__(self, filename, timeout=None):
        self.filename = filename
        self.lock_name = '%s.lock' % filename
        self.lock_level = 0
        self.timeout = timeout

    def __enter__(self):
        self.lock()

    def __exit__(self ,type, value, traceback):
        self.unlock()

    def lock(self):
        if self.lock_level != 0:
            self.lock_level += 1
            return

        done = False
        while not done:
            self.wait(self.timeout, raise_error=True)
            try:
                os.mkdir(self.lock_name)
                done = True  # success
            except FileExistsError:
                # someone else has locked in the meantime
                pass
        # handle recursive lock
        self.lock_level += 1

    def unlock(self):
        self.lock_level -= 1
        if self.lock_level == 0:
            os.rmdir(self.lock_name)

    def wait(self, timeout=None, raise_error=False):
        if self.lock_level > 0:
            # already locked by myself
            return True
        t0 = time.time()
        freed = False
        while not freed and (timeout is None or time.time() - t0 < timeout):
            if not osp.exists(self.lock_name):
                freed = True
            time.sleep(0.1)
        if not freed and raise_error:
            raise LockedDataError('lock file %s is locked too long.'
                                  % self.lock_name)
        return freed


class SulcalPatternsData(Qt.QObject):
    '''
    Sulcal patterns data storage, for a full database, and for a given region.

    Implemented as a Qt QObject, emits signals when some events happen, like
    update started / finished.

    A polling thread monitors external changes by other users so that the data
    state is updated when needed.

    The modification criterion is the update of a "version" file: a single file
    for the whole database. The file is modified each time a file is written in
    the database. Thus sync is ensured by assuming all users will modify data
    using the same version file (or at least they will "touch" the version file
    after modifying any other file).

    Atomicity of modifications (version file, plus all other files) is ensured
    using a :class:`FileLock`, so all external accesses by other users (both
    for reading and writing) are supposed to be done through the same lock
    mechanism.
    '''

    notify_update_started = Qt.Signal()
    notify_update_finished = Qt.Signal(bool)
    notify_backup_saved = Qt.Signal(str, str, str)

    def __init__(self, out_db, region, sulci_db=None, db_filter={},
                 ro_db=None):
        super().__init__()

        if out_db is None:
            out_db = os.getcwd()
        if sulci_db is None:
            sulci_db = out_db
        if sulci_db:
            sulci_db = osp.realpath(sulci_db)
        if ro_db:
            ro_db = osp.realpath(ro_db)
        self.sulci_database = sulci_db
        self.out_database = out_db
        self.ro_database = ro_db
        self.region = region
        self.db_filter = db_filter
        self.out_db_filter = {}

        self.lock = threading.RLock()
        self.bv_lock = threading.RLock()
        self.updating = False
        self.update_thread = None
        self.bv_started = False

        self.pattern_def = {}
        self.subjects = []
        # self.graphs = []
        self.patterns = {}
        self.version_file = osp.join(out_db, 'data_versions.json')
        self.last_poll = None
        self.last_poll_started = None
        self.database_lock = FileLock(self.version_file)
        self.polling_thread = None
        self.polling_inuse = False
        self.polling_interval = 1.

    def __del__(self):
        self.stop_polling()

    def update(self):
        ''' may be called from any thread (like a polling thread)

        Starts update asynchronously: returns now, update takes place in a
        thread. Use notification signals notify_update_started and
        notify_update_finished to perform actions when it's done.
        '''
        with self.lock:
            last_poll = self.last_poll
        if last_poll is not None:
            if not osp.exists(self.version_file):
                return
            s = os.stat(self.version_file)
            if self.last_poll == s.st_mtime:
                return  # things are up to date

        with self.lock:
            # abort previous ongoing update
            if self.updating:
                if not osp.exists(self.version_file):
                    return
                s = os.stat(self.version_file)
                if self.last_poll_started == s.st_mtime:
                    # print('dont reupdate')
                    return
                # updte has started for this timestamp of the version file
                self.last_poll_started = s.st_mtime
                self.updating = False
                # print('starting real update')
        qtThread.QtThreadCall().push(self.notify_update_started.emit)
        if self.update_thread:
            self.update_thread.join()
        self.update_thread = threading.Thread(target=self._update)
        with self.lock:
            self.updating = True
        self.update_thread.start()

    def _update(self):
        # runs in a separate thread, started from update()
        print('data model updating...')

        try:
            # start brainvisa
            with self.bv_lock:
                if not self.bv_started:
                    from brainvisa.axon import processes
                    processes.initializeProcesses()
                    self.bv_started = True
                    with self.lock:
                        if not self.updating:
                            return

            from brainvisa.configuration import neuroConfig
            from brainvisa.data import neuroHierarchy
            from brainvisa.data.readdiskitem import ReadDiskItem

            # collect available graphs and subjects

            rdi = ReadDiskItem('Labelled Cortical Folds Graph',
                               'Graph and data')
            db_def = {}

            with self.database_lock:

                # collect patterns names
                pnfile = osp.join(self.out_database, 'patterns_def.json')
                print('patterns config:', pnfile)
                pat_def = {}
                bd_def = {}
                if osp.exists(pnfile):
                    with open(pnfile) as f:
                        pat_conf = json.load(f)
                    db_def = pat_conf.get('database_definition', {})
                    pat_def = pat_conf.get('patterns_definition', {})
                    print('db_def:', db_def)

            self.db_def = db_def
            if not self.db_filter:
                self.db_filter = db_def.get('database_filter', {})
            if not self.out_db_filter:
                self.out_db_filter = db_def.get('output_database_filter', {})
            if 'sulci_database' in db_def:
                self.sulci_database \
                    = osp.realpath(db_def['sulci_database'])
            if 'ro_database' in db_def:
                self.ro_database = osp.realpath(db_def['ro_database'])
            if not self.region:
                self.region = db_def.get('region', '')
            force_sulci_locks_state = db_def.get('force_sulci_locks_state')

            db_settings = [ds for ds in neuroConfig.dataPath
                           if osp.realpath(ds.directory)
                              == self.sulci_database]
            if not db_settings:
                print('Database %s not found.' % self.sulci_database,
                      file=sys.stderr)

                if not osp.exists(self.version_file):
                    self.save_version()
                s = os.stat(self.version_file)
                last_poll = s.st_mtime

                with self.lock:
                    self.last_poll = last_poll
                # we can make this error fatal
                raise ValueError(
                    'Database %s not found. Maybe it is not declared, or not '
                    'enabled in BrainVISA, or not declared with the same path '
                    '/ mount point. Please check there.'
                    % self.sulci_database)
            db_settings = db_settings[0]
            self.sulci_database = db_settings.directory

            db_settings_ro = None
            graphs_ro = []
            if self.ro_database:
                print('ro_database:', self.ro_database)
                db_settings_ro = [ds for ds in neuroConfig.dataPath
                                  if osp.realpath(ds.directory)
                                      == self.ro_database]
                if db_settings_ro:
                    db_settings_ro = db_settings_ro[0]
                    self.ro_database = db_settings_ro.directory
                    print('found ro:', self.ro_database)

            sel = {'_database': self.sulci_database}
            sel.update(self.db_filter)
            if self.out_db_filter:
                sel_bak = dict(sel)
                sel.update(self.out_db_filter)
            print('sel filter:', sel)
            graphs = list(rdi.findValues({}, requiredAttributes=sel))
            print('1st query done.:', len(graphs))
            out_graphs = set(graphs)
            self._check_abort()
            if self.out_db_filter:
                # look for input graphs
                sel = sel_bak
                print('now try filter;', sel)
                ingraphs = list(rdi.findValues({}, requiredAttributes=sel))
                ingraphs = [g for g in ingraphs if g not in graphs]
                print('2nd query done:', len(ingraphs))
                # TODO: eliminate duplicates differing only on
                # self.out_db_filter attributes
                graphs += ingraphs

            if db_settings_ro:
                sel['_database'] = db_settings_ro.directory
                print('sel filter RO:', sel)
                graphs_ro = list(rdi.findValues({}, requiredAttributes=sel))
                print('RO query done.:', len(graphs_ro))
                graphs += graphs_ro
                del graphs_ro
                self._check_abort()

            subjects = {di.get('subject') for di in graphs}
            print('subjects:', len(subjects))

            # filter graphs and check we have one matching for each subject
            done = {}
            new_graphs = []

            for graph in graphs:
                sub = graph.get('subject')
                side = graph.get('side')
                man_label = (graph.get('manually_labelled') == 'Yes')

                readonly = graph.get('_database') == self.ro_database

                old = done.get((sub, side))
                if old is not None:
                    old_ro, old_man = old[:2]
                    # if old is read-only,
                    # or old is not manually labelled and new is:
                    # replace it
                    if old_ro and not readonly:
                        replace = True
                    elif not old_ro and readonly:
                        replace = False
                    elif old_man and not man_label:
                        replace = False
                    elif not old_man and man_label:
                        replace = True
                    else:
                        print('conflicting sulci:')
                        print(old_ro, old_man, old[2].fullPath())
                        print(readonly, man_label, graph.fullPath())
                        raise ValueError(
                            'Several sulci graphs for subject %s and side '
                            '%s: you should focus your query for input '
                            'sulci data' % (sub, side))
                    if not replace:
                        continue  # ignore RO graphs already in outputs

                done[(sub, side)] = (readonly, man_label, graph)
                new_graphs.append(graph)

            # keep unique final ones
            graphs = [graph for graph in new_graphs
                      if done[(graph.get('subject'), graph.get('side'))][2]
                          is graph]
            del done, new_graphs
            print('filtered graphs:', len(graphs))

            # now build the data model
            with self.database_lock:

                self._check_abort()

                # collect patterns names
                pnfile = osp.join(self.out_database, 'patterns_def.json')
                print('patterns config:', pnfile)
                pat_def = {}
                bd_def = {}
                if osp.exists(pnfile):
                    with open(pnfile) as f:
                        pat_conf = json.load(f)
                    db_def = pat_conf.get('database_definition', {})
                    pat_def = pat_conf.get('patterns_definition', {})
                self.db_def = db_def

                # collect patterns
                patterns = {}
                ns = len(graphs)

                for n, graph in enumerate(graphs):
                    self._check_abort()
                    sub = graph.get('subject')
                    side = graph.get('side')
                    print('\r%d / %d (%d%%)' % (n+1, ns, int(n * 100 / ns)),
                          end='')

                    # print(sub, side)
                    pat_file = osp.join(
                        self.out_database, 'sub-%s' % sub, 'patterns',
                        self.region, side, 'patterns.json')
                    old_pat = self.patterns.get(sub, {}).get(side)

                    if old_pat and (not osp.exists(pat_file)
                                    or (self.last_poll
                                        and os.stat(pat_file).st_mtime
                                            < self.last_poll)):
                        # the file has not been modified since we have read it
                        pat = old_pat
                    else:
                        pat = SulcalPattern(
                            pat_file, graph, self.out_database,
                            db_settings.directory,
                            force_sulci_lock=force_sulci_locks_state,
                            out_db_filter=self.out_db_filter)
                        if old_pat:
                            if old_pat.sulci and not old_pat.modified:
                                pat.set_sulci_graph(old_pat.sulci)
                                pat.update_sulci_status()
                            elif old_pat.modified:
                                # print('keep old pat', sub, side,
                                #       old_pat.modified)
                                patterns.setdefault(sub, {})[side] = old_pat
                                old_pat.out_db = self.out_database
                                if old_pat.modified \
                                        and old_pat.patterns != pat.patterns:
                                    old_pat.status = 'conflict'
                                else:
                                    old_pat.status = 'ok'
                                    old_pat.modified = False
                                old_pat.sulci_locked = pat.sulci_locked
                                if old_pat.sulci:
                                    old_pat.update_sulci_status()
                                pat = old_pat

                    pat.is_output_graph = (graph in out_graphs)

                    patterns.setdefault(sub, {})[side] = pat

                print('\r%d / %d (100%%)' % (ns, ns))
                if not osp.exists(self.version_file):
                    self.save_version()
                s = os.stat(self.version_file)
                last_poll = s.st_mtime

            with self.lock:
                self.subjects = sorted(subjects)
                # self.graphs = graphs
                self.patterns = patterns
                self.pattern_def = pat_def
                self.last_poll = last_poll

        finally:
            print('data update done.')
            with self.lock:
                qtThread.QtThreadCall().push(self.notify_update_finished.emit,
                                             not self.updating)
                self.updating = False

    def _check_abort(self):
        with self.lock:
            if not self.updating:
                  raise UpdateAbortError('abort update')

    def stop_update(self):
        with self.lock:
            self.update = False
        if self.update_thread:
            self.update_thread.join()

    def _new_pattern(self, subject, side, graph):
        pat_file = osp.join(
            self.out_database, 'sub-%s' % subject, 'patterns',
            self.region, side, 'patterns.json')
        force_sulci_locks_state = self.db_def.get('force_sulci_locks_state')
        pat = SulcalPattern(pat_file, graph, self.out_database,
                            self.sulci_database,
                            force_sulci_lock=force_sulci_locks_state,
                            out_db_filter=self.out_db_filter)
        return pat

    def set_pattern_state(self, subject, side, pattern, state_dict,
                          remove_keys=None):
        # print('set_pattern_state', subject, side, pattern, state_dict)
        with self.lock:
            pat = self.patterns.get(subject, {}).get(side)
            if pat is None:
                print('NO PATTERN.')
                # updated in the meantime
                return
            p = pat.patterns.get(pattern)
            # init default optional values to avoid differing on their absence
            pd = {'enabled': False}
            if p is not None:
                pd.update(p)
            sd = dict(pd)
            sd.update(state_dict)
            if remove_keys:
                for key in remove_keys:
                    del sd[key]
            if sd != pd:
                print('MODIF:', subject, side, pattern, pd, sd)
                pat.modified = True
                pat.patterns[pattern] = sd
                # import traceback
                # traceback.print_stack()
            else: print('no change:', sd, pd)

    def check_updated(self):
        if not osp.exists(self.version_file):
            return
        s = os.stat(self.version_file)
        if self.last_poll != s.st_mtime:
            # not up-to-date
            raise OutdatedError()

    def save_version(self):
        with self.database_lock:
            self.check_updated()

            with open(self.version_file, 'w') as f:
                print(datetime.datetime.now(), file=f)
            self.last_poll = os.stat(self.version_file).st_mtime

    def save_individual_pattern(self, subject, side):
        with self.database_lock:
            with self.lock:
                pattern = self.patterns[subject][side]

                try:
                    self.check_updated()
                except OutdatedError:
                    # print('OUTDATED')
                    pattern.save_backup()
                    if pattern.status == 'conflict':
                        backup_filename = pattern.backup_filename()
                        self.notify_backup_saved.emit(subject, side,
                                                      backup_filename)
                    return

                try:
                    pattern.save()
                    self.save_version()
                except (LockedDataError, OutdatedError):
                    backup_filename = pattern.backup_filename()
                    self.notify_backup_saved.emit(subject, side,
                                                  backup_filename)

    def save_sulci(self, subject, side, modified_only=True):
        with self.database_lock:
            with self.lock:
                pattern = self.patterns[subject][side]

                saved = pattern.save_sulci(modified_only=modified_only)

                if saved:
                    self.save_version()
        return saved

    def unsaved_data(self):
        unsaved = {}
        with self.lock:
            for subject, mitems in self.patterns.items():
                for side, patterns in mitems.items():
                    if patterns.modified:
                        unsaved.setdefault(subject, {})[side] \
                            = {'patterns': True}
                    if patterns.sulci_modified():
                        unsaved.setdefault(subject, {}).setdefault(
                            side, {})['sulci'] = True
        return unsaved

    def save_all(self):
        # print('save all')
        unsaved = self.unsaved_data()
        for subject, sides in unsaved.items():
            for side, items in sides.items():
                if items.get('patterns'):
                    self.save_individual_pattern(subject, side)
                if items.get('sulci'):
                    self.save_sulci(subject, side)

    def get_sulci_graph_file(self, subject, side, use_backup=False):
        with self.lock:
            pattern = self.patterns.get(subject, {}).get(side)
            if not pattern:
                return None
            if use_backup:
                return pattern.sulci_load_filename()
            else:
                return pattern.sulci_di

    def set_sulci_graph(self, subject, side, graph):
        with self.lock:
            pattern = self.patterns.get(subject, {}).get(side)
            pattern.set_sulci_graph(graph)

    def start_polling_thread(self, polling_interval=1.):
        with self.lock:
            self.polling_interval = polling_interval
            if self.polling_thread is None:
                self.polling_thread \
                    = threading.Thread(target=self._polling_thread)
        if not self.polling_inuse:
            self.polling_inuse = True
            self.polling_thread.start()

    def stop_polling(self):
        polling_thread = None
        with self.lock:
            self.polling_inuse = False
            polling_thread = self.polling_thread
        if polling_thread and polling_thread.is_alive():
            polling_thread.join()

    def _polling_thread(self):
        while True:
            with self.lock:
                if not self.polling_inuse:
                    return

            with self.lock:
                do_update = not self.updating

            self.update()

            time.sleep(self.polling_interval)

    def get_conflicts(self):
        conflicts = {}
        with self.lock:
            for subject, sides in self.patterns.items():
                for side, pat in sides.items():
                    if pat.status == 'conflict':
                        conflicts.setdefault(subject, {}).setdefault(
                            side, {})['patterns'] \
                            = {'orig': pat.filename,
                               'backup': pat.backup_filename()}
                    if pat.sulci_status == 'conflict':
                        conflicts.setdefault(subject, {}).setdefault(
                            side, {})['sulci'] \
                            = {'orig': pat.sulci_di.fullPath(),
                               'backup': pat.sulci_backup_filename()}
        return conflicts

    def patterns_as_dict(self):
        #return sort_items(self.patterns)
        pdict = {}
        patterns = list(self.pattern_def.get(self.region, {}).keys())
        with self.lock:
            for subject in sorted(self.patterns.keys()):
                sides = self.patterns[subject]
                for side in sorted(sides.keys()):
                    pat = sides[side]
                    #pl = [n for n in patterns
                          #if pat.patterns.get(n, {}).get('enabled')]
                    pl = sort_items(pat.patterns)
                    p = pdict.setdefault(subject, {})[side] = pl
        return pdict

    def export_patterns(self, filename):
        ext = osp.splitext(filename)[1]
        if not ext:
            ext = '.json'
            filename = filename + ext
        if ext == '.json':
            return self.export_patterns_json(filename)
        elif ext == '.yaml':
            return self.export_patterns_yaml(filename)
        elif ext == '.csv':
            return self.export_patterns_csv(filename)

    def export_patterns_json(self, filename):
        pdict = self.patterns_as_dict()
        ptable = {
            "region": self.region,
            "patterns": list(self.pattern_def.get(self.region, {}).keys()),
            "data": pdict
        }

        with open(filename, 'w') as f:
            json.dump(ptable, f)
        return True

    def export_patterns_yaml(self, filename):
        import yaml

        pdict = self.patterns_as_dict()
        ptable = {
            "region": self.region,
            "patterns": list(self.pattern_def.get(self.region, {}).keys()),
            "data": pdict
        }

        with open(filename, 'w') as f:
            yaml.dump(ptable, f)
        return True

    def export_patterns_csv(self, filename):
        import csv

        pdict = self.patterns_as_dict()
        patterns = sorted(self.pattern_def.get(self.region, {}).keys())
        pat_cols = sum([[p, '%s.conf' % p, '%s.annot' % p]
                        for p in patterns], [])
        sidel = []
        notdone = True

        with open(filename, 'w') as f:
            writer = csv.writer(f)  # , dialect='csv')
            writer.writerow(['subject', 'side', 'region'] + pat_cols)
            while notdone:
                cur_side = None
                notdone = False
                for subject, sides in pdict.items():
                    for side, pat, in sides.items():
                        if cur_side is None and side not in sidel:
                            cur_side = side
                            sidel.append(side)
                        if side == cur_side:
                            row = [subject, side, self.region]
                            for p in patterns:
                                pitem = pat.get(p)
                                if pitem is None:
                                    row += [0, None, '']
                                else:
                                    row.append(1 if pitem.get('enabled')
                                               else 0)
                                    row.append(pitem.get('confidence'))
                                    row.append(pitem.get('annotation', ''))
                            writer.writerow(row)
                        elif side in sidel:
                            # done
                            continue
                        else:
                            notdone = True

        return True


