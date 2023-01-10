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

from __future__ import absolute_import
from brainvisa.processes import *
name = 'Morphometry model and stats'
userLevel = 3

signature = Signature(
    'data_graphs', ListOf(ReadDiskItem("Data graph", 'Graph')),
    'nomenclature', ReadDiskItem('Nomenclature', 'Hierarchy'),
    'template_region_model', ReadDiskItem('Template model',
                                          'Template model'),
    'template_domain_model', ReadDiskItem('Template model domain',
                                          'Template model domain'),
    'template_relation_model', ReadDiskItem('Template model',
                                            'Template model'),
    #    'region', OpenChoice( ( 'S.C._right', 'S\.C\._right' ) ),
    'region', String(),
    'output_prefix', String(),
    'region_type', Choice(('Region', 'label'),
                          ('Relation', 'label1 label2')),
)


def initialization(self):
    self.nomenclature = self.signature['nomenclature'].findValue({})
    self.region = 'S.C._right'
    self.template_region_model = \
        self.signature['template_region_model'].findValue(
            {'model_type': 'vertex', 'inputs': 27})
    self.template_domain_model = \
        self.signature['template_domain_model'].findValue(
            {'domain_type': 'inertial_box'})
    self.template_relation_model = \
        self.signature['template_relation_model'].findValue(
            {'model_type': 'edge', 'inputs': 23})
    self.setOptional('template_relation_model')
    self.setOptional('region_type')
    self.setOptional('output_prefix')
    #    self.linkParameters( 'region', 'nomenclature', change_region )

    self.name_descriptors = 1


def execution(self, context):
    context.write("Morphometry statistics with model running")
    tmpdir = context.temporary('Directory')
    #model = context.temporary( 'Graph' )
    model = tmpdir.fullPath() + '/model.arg'
    os.makedirs(tmpdir.fullPath() + '/model.data/adap/nnets')
    os.makedirs(tmpdir.fullPath() + '/model.data/domain')
    os.makedirs(tmpdir.fullPath() + '/model.data/edges/nnets')
    context.write('model : ', model)
    #labels = self.nomenclature.fullPath()
    labels = context.temporary('Config file')
    lid = open(labels.fullPath(), 'w')
    if self.region_type == 'label':
        rgn = re.sub('_right', '', self.region)
        rgn = re.sub('_left', '', rgn)
        lid.write('%' + rgn + '  ' + rgn + '\n')
    else:
        context.write('Relation mode not supported yet !')
        raise ValueError('Relation mode not supported yet !')
    lid.close()
    f = open(labels.fullPath())
    context.log('siMakeModel labels file', html=f.read())
    f.close()
    cmd = ['siMakeModel', model, labels.fullPath(),
           self.template_region_model.fullPath(),
           self.template_domain_model.fullPath()]
    if self.region_type == 'label1 label2':
        if self.template_relation_model is None:
            context.write('template_relation_model is needed for '
                          'region_type=Relation')
            raise ValueError(_t_('template_relation_model is needed for '
                                 'region_type=Relation'))
        cmd += ['-', self.template_relation_model.fullPath()]

#    if self.template_default_model is not None:
#       cmd += ' ' + self.template_default_model.fullPath()
#    if self.template_default_rel_model is not None:
#       if self.template_default_model is None:
#           cmd += ' -'
#       cmd += ' ' + self.template_default_rel_model.fullPath()

    context.system(*cmd)

    tmp = context.temporary('Config file')
    context.write('config : ', tmp.fullPath())
    try:
        stream = open(tmp.fullPath(), 'w')
    except IOError as e:
        error(e.strerror, maker.output)
    else:
        stream.write('*BEGIN TREE 1.0 siMorpho\n')
        stream.write('modelFile  ' + model + "\n")
        stream.write('graphFiles  ' +
                     ' '.join([x.fullPath() for x in self.data_graphs]) + "\n")
        if self.region_type is None:
            self.region_type = 'label'
        stream.write('filter_attributes  ' + self.region_type + "\n")
        stream.write('filter_pattern  ' + self.region + "\n")
        if not self.output_prefix is None:
            stream.write('output_prefix  ' + self.output_prefix + "\n")
        if not self.nomenclature is None:
            stream.write('labelsMapFile  ' + self.nomenclature.fullPath()
                         + "\n")

        if self.name_descriptors:
            stream.write('name_descriptors 1\n')

        subjects = [str(x.get('subject')) for x in self.data_graphs]
        stream.write('subjects ' + ' '.join(subjects) + "\n")

        stream.write('*END\n')
        stream.close()
        f = open(tmp.fullPath())
        context.log('siMorpho input file', html=f.read())
        f.close()
        progname = 'siMorpho'
#        context.write( 'Running ', progname + " " + tmp.fullPath() )
#       raw_input()
        context.system(progname, tmp.fullPath())
