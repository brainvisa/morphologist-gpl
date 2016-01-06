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
from soma import aims
import os

name = 'Global Sulcal Index'
userLevel = 1

signature = Signature(
    'graph', ListOf(ReadDiskItem('Cortical folds graph',
                          'Graph',
                          requiredAttributes = {'graph_version': '3.1'})),
    'subject', ListOf(String()),
    'global_sulcal_index_file', WriteDiskItem('CSV file', 'CSV file')
)


def link_subjects(self, proc, dummy):
    subjects = []
    for item in self.graph:
        subjects.append(item.get('subject'))
    return subjects


def initialization( self ):
    self.linkParameters('subject', 'graph',
                        self.link_subjects)


def execution( self, context ):
  ng = len( self.graph )
  n = 0
  f = open( self.global_sulcal_index_file.fullPath(), 'w' )
  f.write( 'subject;side;hemi_hull_area;native_space;talairach_space\n' )
  #itsubject = iter( self.subject )
  #itsides = iter( self.sides )
  for graph, sub in zip(self.graph, self.subject):
    context.progress( n, ng, process=self )
    #subject = itsubject.next()
    side = graph.get('side')

    reader = aims.Reader( options={ 'subobjectsfilter' : 0 } )
    ingraph = reader.read( graph.fullPath() )
    rawfolds = ingraph['folds_area']
    reffolds = ingraph['reffolds_area']
    rawhull = ingraph['brain_hull_area']
    refhull = ingraph['refbrain_hull_area']

    rawSI =  rawfolds / rawhull 
    refSI =  reffolds / refhull 

    f.write( sub + ';' + side + ';' + str(rawhull) + ';' + str(rawSI) + ';' + str(refSI) + '\n' )
    n += 1
  f.close()
  context.progress( ng, ng, process=self )

