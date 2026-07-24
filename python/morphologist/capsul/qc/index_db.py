from capsul.api import Process
from capsul.attributes import fom_index
import capsul.info as capinfo
import traits.api as traits
import os.path as osp


class IndexDatabase(Process):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_trait('database', traits.Directory(optional=True))
        self.add_trait('database_sqlite', traits.File(output=True,
                                                      optional=True))
        self.add_trait('fom', traits.String(optional=True))
        self.add_trait('main_process', traits.String(optional=True))
        self.main_process = 'morphologist.capsul.morphologist'

    def _run_process(self):
        engine = self.get_study_config().engine
        if not hasattr(engine, '_modules_data') \
                or 'fom' not in engine._modules_data:
            engine.load_modules(['fom', 'axon'])

        with engine.settings as session:
            config = session.config('fom', 'global')
            if self.database in (None, traits.Undefined, ''):
                self.database = config.input_directory
            if self.fom in (None, traits.Undefined, ''):
                self.fom = config.input_fom
            config.input_fom = self.fom
            config.input_directory = self.database
            config.output_directory = self.database

        if self.database_sqlite in (traits.Undefined, None, ''):
            self.database_sqlite = osp.join(
                self.database,
                f'capsul-{capinfo.version_major}.{capinfo.version_minor}.sqlite')

        proc = None
        if self.main_process not in (traits.Undefined, None, ''):
            try:
                proc = engine.get_process_instance(self.main_process)
            except Exception:
                print('process', self.main_process,
                      'could not be used. Indexing without it')
        fom_index.build_fom_sqlite_index(
            engine, self.database_sqlite, directory=self.database,
            main_process=proc, clear_db=True)
