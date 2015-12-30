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
name = 'Recognition Error'
userLevel = 1

# FIXME : un nouveau type et format ont ete crees pour l'occasion pour les
# fichier de traduction de sillons. Ce type est assez similaire a celui utilise 
# pour les fichier de traduction des gyris. Il faudrait
# 1) mettre un format commun pour les 2
# 2) changer l'extension def en trl pour les sillons et prevoir des modifs
#    dans sigraph et renommer quelques fichiers
# 3) enlever les ambiguites possibles dans la hierarchie (grace a un .minf sur
#    le fichier de traduction par exemple)
signature = Signature(
     'model', ReadDiskItem( 'Model graph', 'Graph' ),
     'labels_translation', ReadDiskItem('Label translation',
     [ 'Label translation', 'DEF Label translation' ] ),
     'base_graph', ReadDiskItem('Labelled Cortical folds graph','Graph', 
          requiredAttributes = { 'labelled' :'Yes' }),
     'labeled_graph', ReadDiskItem('Labelled Cortical folds graph','Graph', 
          requiredAttributes = { 'labelled' :'Yes','automatically_labelled' : 'Yes' }),
     'error_file', WriteDiskItem( 'Text File', 'Text File' ),
     )

# FIXME : l'ideal serait que la commande siError ait le fichier de traduction
# comme parametre optionnel car elle connait le chemin shared de sigraph.
def get_sigraph_path():
     p = os.popen('siError --info')
     lines = p.readlines()
     r = [l for l in lines if l.startswith('sigraph base path')][0]
     path = r[r.find('/'):-1]
     return path
     

def initialization(self):
     self.linkParameters('labeled_graph', 'base_graph')
     self.labels_translation = \
          self.signature[ 'labels_translation' ].findValue(
               { 'filename_variable' : 'sulci_model_noroots' } )
     self.signature['labels_translation'].userLevel = 2
     self.parent = {}
     self.parent['manage_tasks'] = False
     self.setOptional( 'error_file' )

def execution(self, context):
     import os
     context.write('...')
     if self.parent['manage_tasks']:
          package = self.parent['self'].package
          if package == 'default':
               progname = distutils.spawn.find_executable(
                         'siErrorLightWrapper.py')
          else:
               progname = os.path.join(self.parent['package_dir'],
                          package,'bin', 'siErrorLightWrapper.py')
          graphname = self.labeled_graph.get('subject')
          args = [progname, '-m', self.model.fullPath(),
               '-l', self.labeled_graph.fullPath(),
               '-t', self.labels_translation.fullPath(),
               '-b', self.base_graph.fullPath(), 
               '-c', self.parent['self'].Output.fullPath(),
               '-n', graphname]
          cmd = ' '.join(args)
          self.parent['tasks'].append(cmd)
     else:
          import sigraph.error as sierror
          # reload( sierror )
          import sigraph.nrj as sinrj
          error_rate = str(sierror.computeErrorRates(
                    self.base_graph.fullPath(),
                    self.labeled_graph.fullPath(),
                    self.labels_translation.fullPath()
                    ))
          nrj = str(sinrj.computeNrj(self.model.fullPath(),
                    self.labeled_graph.fullPath(),
                    self.labels_translation.fullPath()))
          self.parent['error_rate'] = error_rate
          self.parent['nrj'] = nrj
          context.write('Error rate = ' + error_rate + '%')
          context.write('Energy = ' + nrj)
          if self.error_file is not None:
               f = open( self.error_file.fullPath(), 'w' )
               print >> f, 'error_rate =', error_rate
               print >> f, 'energy =', nrj
               f.close()

