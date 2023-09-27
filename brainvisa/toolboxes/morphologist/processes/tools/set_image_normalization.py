# -*- coding: utf-8 -*-

from brainvisa.processes import *
from brainvisa.data.neuroHierarchy import databases


signature = Signature(
    'data_type', Choice('Raw T1 MRI'),
    'input_data', ReadDiskItem('Raw T1 MRI', 'aims readable volume formats'),
    'output_data', WriteDiskItem('Raw T1 MRI',
                                  'aims writable volume formats'),
    'transformation',
    ReadDiskItem('Transform Raw T1 MRI to Talairach-MNI template-SPM',
                 'Transformation matrix'),
    'dest_referential', OpenChoice('Talairach-MNI template-SPM'),
    'insert_first', Boolean(),
)


def dataTypeChanged(self, dataType):
    if dataType:
        formats = list(databases.getTypesFormats(dataType))
        if not formats:
            formats = getAllFormats()
        self.signature['input_data'] = ReadDiskItem(dataType, formats)
        self.signature['output_data'] = WriteDiskItem(dataType, formats)
        self.signatureChangeNotifier.notify(self)


def initialization(self):
    possibleTypes = [t.name for t in getAllDiskItemTypes()]
    self.signature['data_type'].setChoices(*sorted(possibleTypes))
    self.data_type = 'Raw T1 MRI'
    self.linkParameters('output_data', 'input_data')
    self.linkParameters('transformation', 'input_data')
    self.addLink('input_data', 'data_type', self.dataTypeChanged)


def execution(self, context):
    from soma import aims

    vol = aims.read(self.input_data.fullPath())
    tr = aims.read(self.transformation.fullPath())

    refs = list(vol.header().get('referentials', []))
    t0 = vol.header().get('transformations', [])
    trans = list(t0)
    if self.insert_first:
        if self.dest_referential in refs:
            iref = refs.index(self.dest_referential)
            del refs[iref]
            del trans[iref]
        refs.insert(0, self.dest_referential)
        trans.insert(0, tr.toVector())
    else:
        if self.dest_referential in refs:
            iref = refs.index(self.dest_referential)
            trans[iref] = tr.toVector()
        else:
            refs.append(self.dest_referential)
            trans.append(tr.toVector())
    vol.header()['referentials'] = refs
    vol.header()['transformations'] = trans

    aims.write(vol, self.output_data.fullPath())
