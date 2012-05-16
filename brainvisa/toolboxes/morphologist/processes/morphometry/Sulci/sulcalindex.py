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
import os, re

from soma import aims
import sys

name = 'Global Sulcal Index'
userLevel = 1

signature = Signature(
    'graphs', ListOf( ReadDiskItem( 'Cortical folds graph', 'Graph',
                      requiredAttributes = { 'graph_version' : '3.1' } ) ),
    'output_csv_file', WriteDiskItem( 'CSV file', 'CSV file' )
)


def execution( self, context ):
  ng = len( self.graphs )
  n = 0
  f = open( self.output_csv_file.fullPath(), 'w' )
  f.write( 'subject\tside\traw\tnormalized\n' )
  for graph in self.graphs:
    context.progress( n, ng, process=self )
    subject = graph.get('subject')
    side = graph.get('side')

    reader = aims.Reader( options={ 'subobjectsfilter' : 0 } )
    ingraph = reader.read( graph.fullPath() )
    rawfolds = ingraph['folds_area']
    reffolds = ingraph['reffolds_area']
    rawhull = ingraph['brain_hull_area']
    refhull = ingraph['refbrain_hull_area']

    rawSI =  rawfolds / rawhull 
    refSI =  reffolds / refhull 

    f.write( subject + '\t' + side + '\t' + str(rawSI) + '\t' + str(refSI) + '\n' )
    n += 1
  f.close()
  context.progress( ng, ng, process=self )

