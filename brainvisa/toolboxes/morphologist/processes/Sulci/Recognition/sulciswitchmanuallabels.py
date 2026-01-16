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

name = 'Sulci Switch Manual Labels'
userLevel = 1


signature = Signature(
    'input_graph', ReadDiskItem("Data graph", 'Graph',
                                requiredAttributes={'labelled': 'Yes'}),
    'output_graph', WriteDiskItem("Data graph", 'Graph',
                                  requiredAttributes={'labelled': 'Yes'}),
    'source_labeling', Choice(('Auto', 'label'), ('Manual', 'name')),
    'destinaton_labeling', Choice(('Auto', 'label'), ('Manual', 'name')),
    'output_database', Choice(),
    'output_session', String(),
)


def initialization(self):

    def link_output_graph(self, process):
        la = None
        if self.destinaton_labeling == 'label':
            la = 'automatically_labelled'
            nola = 'manually_labelled'
        else:
            la = 'manually_labelled'
            nola = 'automatically_labelled'
        req = {'labelled': 'Yes', la: 'Yes', nola: 'No'}
        if self.output_database is not None:
            req['_database'] = self.output_database
        if self.output_session is not None:
            req['sulci_recognition_session'] = self.output_session
        di = WriteDiskItem("Data graph", 'Graph', requiredAttributes=req)
        return di.findValue(self.input_graph)

    def link_source_labeling(self, process):
        if self.input_graph.get('manually_labelled', None) == 'Yes':
            return 'name'
        else:
            return 'label'

    def link_dest_labeling(self, process):
        if self.output_graph is None:
            return 'name'
        if self.output_graph.get('automatically_labelled', None) == 'Yes':
            return 'label'
        else:
            return 'name'

    # list of possible databases, while respecting the ontology
    # ontology: brainvisa-3.2.0
    databases = [h.name for h in neuroHierarchy.hierarchies()
                 if not h.builtin and (h.fso.name == "brainvisa-3.2.0"
                                       or 'morphologist' in h.fso.name)]
    self.signature["output_database"].setChoices(*databases)
    if len(databases) != 0:
        self.output_database = databases[0]
    else:
        self.signature["output_database"] = OpenChoice()

    self.linkParameters('output_graph',
                        ('input_graph', 'destinaton_labeling',
                         'output_database', 'output_session'),
                        link_output_graph)
    self.linkParameters('source_labeling', 'input_graph', link_source_labeling)
    self.linkParameters('destinaton_labeling', 'output_graph',
                        link_dest_labeling)
    self.setOptional('output_session')


def execution(self, context):
    src = self.source_labeling
    dst = self.destinaton_labeling
    context.system('AimsGraphConvert', '-i', self.input_graph, '-o',
                   self.output_graph, '-c', src, '-d', dst)
    trManager = registration.getTransformationManager()
    trManager.copyReferential(self.input_graph, self.output_graph)
