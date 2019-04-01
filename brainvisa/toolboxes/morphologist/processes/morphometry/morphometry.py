# -*- coding: utf-8 -*-
#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
#
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.

from brainvisa.processes import *
from brainvisa.data.labelSelection import LabelSelection
import distutils.spawn
import os

name = 'Morphometry statistics'
userLevel = 2

labelselector = distutils.spawn.find_executable(
    'AimsLabelSelector')
selectionmode = 1


def selectionType():
    global selectionmode
    if selectionmode == 1:
        return LabelSelection()
    else:
        return String()


def changeSelectionMode(mode=1):
    global selectionmode
    if mode < 2:
        global labelselector
        if not labelselector:
            mode = 0
        selectionmode = mode
        signature['region'] = selectionType()
    else:
        selectionmode = mode
        signature['region'] = ReadDiskItem('Labels selection', 'selection')


sign = (
    'data_graphs', ListOf(ReadDiskItem("Data graph", 'Graph')),
    'model', ReadDiskItem('Model graph', 'Graph'),
    'nomenclature', ReadDiskItem('Nomenclature', 'Hierarchy'),
    'region', selectionType(),
    'output_directory', ReadDiskItem('Directory', 'Directory'),
    'output_filename_prefix', String(),
    'region_type', Choice(('Region', 'label'),
                          ('Relations with region', 'label1 label2'),
                          ('All', 'label label1 label2')),
)

if selectionmode == 0:
    sign.append('region_as_regexp', Boolean())

sign += (
    'label_attribute', Choice('auto', 'label', 'name'),
    'run_dataMind', Boolean(),
)

signature = Signature(*sign)


def initialization(self):
    global selectionmode

    def change_region(self, proc):
        if self.model:
            mod = self.model.fullPath()
        else:
            mod = None
        if self.nomenclature:
            nom = self.nomenclature.fullPath()
        else:
            nom = None
        sel = self.region
        if sel is None:
            sel = LabelSelection(mod, nom)
        else:
            sel.value['model'] = mod
            sel.value['nomenclature'] = nom
        return sel

    def linkModel(self, proc):
        if self.data_graphs is not None and len(self.data_graphs) != 0:
            return self.signature['model'].findValue(self.data_graphs[0])
        return None

    self.nomenclature = self.signature['nomenclature'].findValue({})
    self.setOptional('region_type')
    if selectionmode == 0:
        self.region_as_regexp = 0
    self.setOptional('nomenclature')
    self.setOptional('output_filename_prefix')
    self.name_descriptors = 1
    #self.print_subjects = 1
    self.print_labels = 1
    self.run_dataMind = 0
    self.output_directory = os.getcwd()
    self.output_filename_prefix = 'morpho_'
    if selectionmode == 0:
        self.region = 'S.C.'
    elif selectionmode == 1:
        self.linkParameters('region', ('model', 'nomenclature'),
                            change_region)
    self.linkParameters('model', 'data_graphs', linkModel)


def execution(self, context):
    context.write("Morphometry statistics running")
    progname = 'siMorpho'
    tmp = context.temporary('Config file')
    context.write('config : ', tmp.fullPath())
    if len(self.data_graphs) == 0:
        raise Exception(_t_('argument <em>data_graph</em> should not be '
                            'empty'))
    try:
        stream = open(tmp.fullPath(), 'w')
    except IOError as e:
        error(e.strerror, maker.output)
    stream.write('*BEGIN TREE 1.0 siMorpho\n')
    stream.write('modelFile  ' + self.model.fullPath() + "\n")
    stream.write('graphFiles  "' +
                 '" "'.join([x.fullPath() for x in self.data_graphs]) + '"\n')

    if self.region_type is None:
        self.region_type = 'label'
    stream.write('filter_attributes  ' + self.region_type + "\n")
    if selectionmode == 0:
        if self.region_as_regexp:
            region = self.region
        else:
            region = re.sub('(\.|\(|\)|\[|\])', '\\\\\\1', self.region)
            region = re.sub('\*', '.*', region)
        stream.write('filter_pattern  ' + region + "\n")
    elif selectionmode == 1:
        self.region.writeSelection(context)
        sfile = self.region.file
        stream.write('selection ' + sfile.fullPath() + '\n')
    else:
        sfile = self.region
        stream.write('selection ' + sfile.fullPath() + '\n')
    op = self.output_filename_prefix
    if op is None:
        op = ''
    stream.write('output_prefix  ' + os.path.join(
        self.output_directory.fullPath(), op) + "\n")
    if not self.nomenclature is None:
        stream.write('labelsMapFile  ' + self.nomenclature.fullPath()
                     + "\n")
    if self.label_attribute != 'auto':
        stream.write('label_attribute  ' + self.label_attribute + '\n')
    if self.name_descriptors:
        stream.write('name_descriptors 1\n')
    stream.write('descriptor_aliases '
                 'fold_descriptor2 fold_descriptor3\n')
    if self.print_labels:
        stream.write('print_labels 1\n')
# if self.print_subjects:
##    stream.write( 'subject_regex [LR]\\([^/\\]*\\)\\(Base\\|Auto[0-9]*\\)\\.arg\n' )
    subjects = []
    for x in self.data_graphs:
        s = x.get('subject')
        if s:
            s = str(s)
        else:
            s = os.path.basename(x.fullPath())
        subjects.append(s)
    stream.write('subjects ' + string.join(subjects) + "\n")
    stream.write('*END\n')
    stream.close()
    f = open(tmp.fullPath()).read()
    context.log('siMorpho input file', html=f)
    if selectionmode == 2:
        context.write('siMorpho input file:\n<pre>' + f + '</pre>')
    context.system(progname, tmp.fullPath())
    #c = Command( progname + " " + tmp.fullPath() )
    # c.start()
    #sel = self.region.value.get( 'selection' )
    # if not sel:
    #    sel = 'attributes = {}\n'
    #c.stdin.write( sel )
    #result = c.wait()
    # if result:
    #    context.write( '<b>siMorpho failed: result = ' \
    #                   + str( result ) + '</b>' )

    # Run dataMind if needed
    if self.run_dataMind:
        if not distutils.spawn.find_executable('R'):
            context.write('<font color="#c00000">R is not found</font> '
                          'so the data mind module will not be run')
        else:
            def _subj(x):
                y = x.get('subject')
                if y is None:
                    y = os.path.basename(x.fileName())
                    if y[-4:] == '.arg':
                        y = y[:-4]
                    if y[0] == 'L' or y[0] == 'R':
                        y = y[1:]
                return y
            subjects = [_subj(x) for x in self.data_graphs]
            subjectsFile = context.temporary('Config file')
            try:
                f = open(subjectsFile.fullPath(), 'w')
            except IOError as e:
                error(e.strerror, maker.output)
            else:
                f.write('subject\n')
                for subject in subjects:
                    f.write(subject+'\n')
                f.close()
            #context.write( "DataMind running" )
            python_interpretor = sys.executable
            progname = [python_interpretor,
                        os.path.join(os.path.join(mainPath, 'bin'),
                                     'datamind'),
                        subjectsFile.fullPath(),
                        str(self.output_prefix)]
            context.write('Running ', *progname)
            context.system(*progname)


# enable selector
changeSelectionMode(1)
