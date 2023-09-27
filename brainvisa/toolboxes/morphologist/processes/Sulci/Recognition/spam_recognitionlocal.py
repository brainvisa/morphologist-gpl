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
from brainvisa import registration

name = 'SPAM recognition, local registration'
userLevel = 2


signature = Signature(
    'data_graph', ReadDiskItem('Cortical folds graph', 'Graph and data'),
    'output_graph',
    WriteDiskItem('Labelled Cortical folds graph', 'Graph and data',
                  requiredAttributes={'labelled': 'Yes',
                                      'automatically_labelled': 'Yes'}),
    'model', ReadDiskItem('Sulci Segments Model', 'Text Data Table'),
    'posterior_probabilities',
    WriteDiskItem('Sulci Labels Segmentwise Posterior Probabilities',
                  'CSV file'),
    'labels_translation_map',
    ReadDiskItem('Label Translation',
                 ['Label Translation', 'DEF Label translation']),
    'labels_priors', ReadDiskItem('Sulci Labels Priors', 'Text Data Table'),
    'local_referentials', ReadDiskItem('Sulci Local referentials',
                                       'Text Data Table'),
    'direction_priors',
    ReadDiskItem('Sulci Direction Transformation Priors',
                 'Text Data Table'),
    'angle_priors', ReadDiskItem('Sulci Angle Transformation Priors',
                                 'Text Data Table'),
    'translation_priors',
    ReadDiskItem('Sulci Translation Transformation Priors',
                 'Text Data Table'),
    'output_local_transformations',
    WriteDiskItem('Sulci Local SPAM transformations Directory',
                  'Directory'),
    'initial_transformation', ReadDiskItem('Transformation matrix',
                                           'Transformation matrix'),  # FIXME
    'global_transformation',
    ReadDiskItem('Sulci Talairach to Global SPAM transformation',
                 'Transformation matrix'),
)


capsul_param_options = {
    'model': ['dataset="shared"'],
    'labels_translation_map': ['dataset="shared"'],
    'labels_priors': ['dataset="shared"'],
    'local_referentials': ['dataset="shared"'],
    'direction_priors': ['dataset="shared"'],
    'angle_priors': ['dataset="shared"'],
    'translation_priors': ['dataset="shared"'],
    'initial_transformation': ['dataset=None'],
}


def initialization(self):
    def linkModelType(self, proc):
        di = ReadDiskItem('Sulci Segments Model', 'Text Data Table',
                          requiredAttributes={'sulci_segments_model_type':
                                              'locally_from_global_registred_spam'})
        return di.findValue(self.data_graph)
    self.linkParameters('output_graph', 'data_graph')
    self.linkParameters('model', 'data_graph', linkModelType)
    self.linkParameters('posterior_probabilities', 'output_graph')
    self.linkParameters('labels_priors', 'data_graph')
    self.labels_translation_map = \
        self.signature['labels_translation_map'].findValue(
            {'filename_variable': 'sulci_model_2008'})
    self.linkParameters('direction_priors', 'data_graph')
    self.linkParameters('angle_priors', 'data_graph')
    self.linkParameters('translation_priors', 'data_graph')
    self.linkParameters('local_referentials', 'data_graph')
    self.linkParameters('output_local_transformations', 'output_graph')
    self.linkParameters('global_transformation', 'data_graph')
    self.setOptional('initial_transformation')
    self.setOptional('output_local_transformations')
    self.setOptional('global_transformation')


def execution(self, context):
    tmpfile = context.temporary('Text file')
    # find script filename (since it is not in the PATH)
    import brainvisa
    progname = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        brainvisa.__file__))), 'scripts', 'sigraph', 'sulci_registration',
        'independent_tag_with_registration.py')
    cmd = [sys.executable, progname, '-i', self.data_graph, '-o',
           self.output_graph, '-t', self.labels_translation_map, '-d', self.model,
           '-c', self.posterior_probabilities, '-l', tmpfile,
           '-p', self.labels_priors, '--translation-prior',
           self.translation_priors, '--direction-prior', self.direction_priors,
           '--angle-prior', self.angle_priors, '--distrib-gaussians',
           self.local_referentials, '--mode', 'local']
    if self.initial_transformation is not None \
            and self.global_transformation is not None:
        trtmp = context.temporary('Transformation Matrix')
        context.system('AimsComposeTransformation', '-i',
                       self.global_transformation, '-j', self.initial_transformation, '-o',
                       trtmp)
        cmd += ['--input-motion', trtmp, '--no-talairach']
    elif self.initial_transformation is not None:
        cmd += ['--input-motion', self.initial_transformation, '--no-talairach']
    elif self.global_transformation is not None:
        cmd += ['--input-motion', self.global_transformation]
    if self.output_local_transformations is not None:
        cmd += ['--motion', self.output_local_transformations]
    # now run it
    context.system(*cmd)
    trManager = registration.getTransformationManager()
    trManager.copyReferential(self.data_graph, self.output_graph)
