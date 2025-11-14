
from brainvisa.processes import *
from brainvisa.processing import capsul_process

name = 'Morphologist intersubject QC file'
userLevel = 0

base_class = capsul_process.CapsulProcess
capsul_process = 'morphologist.capsul.morpho_intersubject_status'


signature = Signature(
    'indiv_qc', ListOf(ReadDiskItem('Morphologist JSON report', 'JSON file')),
    'subjects', ListOf(String()),
    'bids', ListOf(String()),
    'intersubject_qc', WriteDiskItem('QC table', 'TSV file'),
    'threads', Integer(),
    'prune', Boolean(),
)


def initialization(self):

    def link_subjects(self, proc):
        if self.indiv_qc is not None:
            subjects = []
            for qc in self.indiv_qc:
                subject = qc.get('subject')
                subjects.append(subject)
            return subjects

    def link_bids(self, proc):
        if self.indiv_qc is not None:
            bidsl = []
            for qc in self.indiv_qc:
                bids = qc.get('bids')
                if bids is None:
                    center = qc.get('center')
                    bids = qc.get('acquisition')
                    if center and bids:
                        bids = f'cnt-{center}_{bids}'
                    elif bids is None:
                        bids = f'cnt-{center}'
                bidsl.append(bids)
            return bidsl

    def link_inter(self, proc):
        if self.indiv_qc:
            return self.signature['intersubject_qc'].findValue(
                self.indiv_qc[0])

    self.linkParameters('subjects', 'indiv_qc', link_subjects)
    self.linkParameters('bids', 'indiv_qc', link_bids)
    self.linkParameters('intersubject_qc', 'indiv_qc', link_inter)
    self.threads = 0
    self.prune = False

