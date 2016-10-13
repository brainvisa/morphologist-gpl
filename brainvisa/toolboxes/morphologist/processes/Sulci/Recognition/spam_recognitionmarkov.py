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
from brainvisa import registration

name = 'SPAM recognition, Markovian model'
userLevel = 2


signature = Signature(
    'data_graph', ReadDiskItem( 'Cortical folds graph', 'Graph and data' ),
    'output_graph',
      WriteDiskItem( 'Labelled Cortical folds graph', 'Graph and data',
                    requiredAttributes = { 'labelled' : 'Yes',
                                            'automatically_labelled' \
                                            : 'Yes' } ),
    'model', ReadDiskItem( 'Sulci Segments Model', 'Text Data Table',
        requiredAttributes={ 'sulci_segments_model_type' : \
            'global_registered_spam' } ),
    'posterior_probabilities',
        WriteDiskItem( 'Sulci Labels Segmentwise Posterior Probabilities',
            'CSV file' ),
    'labels_translation_map',
      ReadDiskItem( 'Label Translation',
                    [ 'Label Translation', 'DEF Label translation' ] ),
    'labels_priors', ReadDiskItem( 'Sulci Labels Priors', 'Text Data Table' ),
    'segments_relations_model',
        ReadDiskItem( 'Sulci Segments Relations Model', 'Text Data Table' ),
    'initial_transformation', ReadDiskItem( 'Transformation matrix',
      'Transformation matrix' ), # FIXME
    'global_transformation',
        ReadDiskItem( 'Sulci Talairach to Global SPAM transformation',
            'Transformation matrix' ),
    #'output_energy', WriteDiskItem( 'siRelax Fold Energy',
        #'siRelax Fold Energy' ),
    'fix_random_seed', Boolean(),
)

def initialization( self ):
    self.linkParameters( 'output_graph', 'data_graph' )
    self.linkParameters( 'model', 'data_graph' )
    self.linkParameters( 'posterior_probabilities', 'output_graph' )
    self.linkParameters( 'labels_priors', 'data_graph' )
    self.labels_translation_map = \
        self.signature[ 'labels_translation_map' ].findValue(
            { 'filename_variable' : 'sulci_model_2008' } )
    self.linkParameters( 'global_transformation', 'data_graph' )
    self.linkParameters( 'segments_relations_model', 'data_graph' )
    # self.setOptional( 'segments_relations_model' )
    self.setOptional( 'initial_transformation' )
    self.setOptional( 'global_transformation' )
    self.signature['fix_random_seed'].userLevel = 3
    self.fix_random_seed = False

def execution( self, context ):
    tmpfile = context.temporary( 'Text file' )
    # find script filename (since it is not in the PATH)
    import brainvisa
    progname = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname( \
        brainvisa.__file__))), 'scripts', 'sigraph', 'sulci_registration',
        'annealing_tag.py')
    cmd = [ sys.executable, progname, '-i', self.data_graph, '-o',
        self.output_graph, '-t', self.labels_translation_map, '-d', self.model,
        '-c', self.posterior_probabilities, '-p', self.labels_priors,
        '--distrib_relations', self.segments_relations_model, '--nrj', tmpfile,
        '--mode', 'sa', '--init-mode', 'segments_potentials',
        '--select-mode', 'threshold', '--init-temperature', 50,
        '--temperature-rate', 0.995, '--stop-rate', 0.02, '--tmax', 10000,
        '--weighting-mode', 'number', '--normalize-weights', '--init-prior',
        self.labels_priors ]
    if self.global_transformation is not None:
        cmd += [ '--motion', self.global_transformation ]
    if self.initial_transformation is not None:
        context.warning( 'initial_transformation is set but is not working yet: it will not be used in the Markovian recognition, and thus might produce inexpected results' )
    if self.fix_random_seed:
        cmd += ['--seed', 10]
    # now run it
    context.system( *cmd )
    trManager = registration.getTransformationManager()
    trManager.copyReferential( self.data_graph, self.output_graph )

