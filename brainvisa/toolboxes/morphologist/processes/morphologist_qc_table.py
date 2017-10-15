 
from brainvisa.processes import *

name = 'Morphologist QC table'
userLevel = 0

signature = Signature(
    'database', Choice(),
    'keys', ListOf(String()),
    'acquisition', String(),
    'analysis', String(),
    'graph_version', String(),
    'data_filters', ListOf(String()),
)


def initialization(self):
    # list of possible databases, while respecting the ontology
    # ontology: brainvisa-3.2.0
    databases = [h.name for h in neuroHierarchy.hierarchies()]
    self.signature["database"].setChoices(*databases)
    if len(databases) >= 2:
        self.database = databases[1]
    else:
        self.signature["database"] = OpenChoice()

    self.setOptional('data_filters', 'acquisition', 'analysis',
                     'graph_version')
    self.keys = ['subject']


def execution(self, context):
    dtypes = ['Raw T1 MRI', 'T1 MRI Bias Corrected', 'Histo Analysis',
              'T1 Brain Mask', 'Split Brain Mask', 'Head Mesh',
              'Left Grey White Mask', 'Right Grey White Mask',
              'Left CSF+GREY Mask', 'Right CSF+GREY Mask',
              'Left Hemisphere White Mesh', 'Right Hemisphere White Mesh',
              'Left Cortex Skeleton', 'Right Cortex Skeleton',
              'Left Hemisphere Mesh', 'Right Hemisphere Mesh',
              'Left Cortical folds graph', 'Right Cortical folds graph',
              'Labelled Cortical folds graph', 'Labelled Cortical folds graph',
              'Sulcal morphometry measurements']

    tlabels = ['Raw T1 MRI', 'Bias Corrected', 'Histo Analysis',
              'Brain Mask', 'Hemispheres Split', 'Head Mesh',
              'Left Grey White Mask', 'Right Grey White Mask',
              'Left CSF+GREY Mask', 'Right CSF+GREY Mask',
              'Left Hemisphere White Mesh', 'Right Hemisphere White Mesh',
              'Left Cortex Skeleton', 'Right Cortex Skeleton',
              'Left Hemisphere Mesh', 'Right Hemisphere Mesh',
              'Left Cortical Sulci', 'Right Cortical Sulci',
              'Left Labelled Sulci', 'Right Labelled Cortical Sulci',
              'Sulcal morphometry measurements']

    custom_filt = [eval(filt) for filt in self.data_filters]
    if len(custom_filt) == 1:
        custom_filt = custom_filt * len(dtypes)
    if len(custom_filt) < len(dtypes):
        custom_filt = custom_filt + [{}] * (len(dtypes) - len(custom_filt))

    filter1 = {}
    if self.acquisition:
        filter1.update({'acquisition': self.acquisition})
    filter2 = dict(filter1)
    filter1['normalized'] = 'no'
    if self.analysis:
        filter2.update({'analysis': self.analysis})
    filter3_l = dict(filter2)
    filter3_l.update({'side': 'left'})
    filter3_r = dict(filter2)
    filter3_r.update({'side': 'right'})
    filter4_l = dict(filter3_l)
    if self.graph_version:
        filter4_l.update({'graph_version': self.graph_version})
    filter4_r = dict(filter3_r)
    if self.graph_version:
        filter4_r.update({'graph_version': self.graph_version})
    filter5 = dict(filter2)
    if self.graph_version:
        filter2.update({'graph_version': self.graph_version})

    filters = [filter1, filter2, filter2, filter2, filter2, filter2,
               filter3_l, filter3_r, filter3_l, filter3_r, filter3_l,
               filter3_r, filter3_l, filter3_r, filter3_l, filter3_r,
               filter4_l, filter4_r, filter4_l, filter4_r, filter5]
    for filt, custfilt in zip(filters, custom_filt):
        filt.update(custfilt)
    filters = [repr(filt) for filt in filters]

    self.proc = getProcessInstance('database_qc_table')
    return context.runProcess(self.proc, database=self.database,
                              data_types=dtypes,
                              data_filters=filters,
                              keys=self.keys,
                              type_labels=tlabels)

