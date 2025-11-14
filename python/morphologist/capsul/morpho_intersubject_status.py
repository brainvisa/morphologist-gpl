
from capsul.api import Process
from traits.api import File, Int, Bool, List, Str


class MorphoInterSubjectStatus(Process):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_trait('indiv_qc', List(File(allowed_extensions=['.json']),
                       output=False))
        self.add_trait('subjects', List(Str()))
        self.add_trait('bids', List(Str()))
        self.add_trait('intersubject_qc', File(allowed_extensions=['.tsv'],
                       output=True))
        self.add_trait('threads', Int(0)),
        self.add_trait('prune', Bool(False))

    def _run_process(self):
        from morphologist.qc import global_qc_table

        subjects_def = [{'subject': s, 'bids': b}
                        for s, b in zip(self.subjects, self.bids)]

        global_qc_table.qc_table_from_indiv(
            self.indiv_qc, subjects_def,
            qc_file=self.intersubject_qc,
            prune=self.prune, threads=self.threads)
