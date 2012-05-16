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
import registration

name = 'Sulci Switch Manual Labels'
userLevel = 1


signature = Signature(
  'input_graph', ReadDiskItem( "Data graph", 'Graph',
        requiredAttributes = { 'labelled' : 'Yes' } ),
  'output_graph', WriteDiskItem( "Data graph", 'Graph',
        requiredAttributes = { 'labelled' : 'Yes' } ),
  #'conversion_direction', Choice( 'Auto -> Manual', 'Manual -> Auto' ),
)


def initialization( self ):
  def linkLabelAttribute( self, process ):
    la = None
    if self.input_graph:
      la = self.input_graph.get( 'manually_labelled', None )
      if la == 'Yes':
        la = 'automatically_labelled'
        nola = 'manually_labelled'
      else:
        la = self.input_graph.get( 'automatically_labelled', None )
        if la == 'Yes':
          la = 'manually_labelled'
          nola = 'automatically_labelled'
        else:
          la = None
    if la:
      di = WriteDiskItem( "Data graph", 'Graph',
        requiredAttributes = { 'labelled' : 'Yes', la : 'Yes', nola : 'No' } )
    else:
      di = WriteDiskItem( "Data graph", 'Graph',
        requiredAttributes = { 'labelled' : 'Yes' } )
    #print 'link:', di.findValue( self.input_graph )
    return di.findValue( self.input_graph )
  self.linkParameters( 'output_graph', 'input_graph', linkLabelAttribute )

def execution( self, context ):
  la = self.input_graph.get( 'manually_labelled', None )
  if la == 'Yes':
    src = 'name'
  else:
    src = 'label'
  la = self.output_graph.get( 'manually_labelled', None )
  if la == 'Yes':
    dst = 'name'
  else:
    dst = 'label'
  context.system( 'AimsGraphConvert', '-i', self.input_graph, '-o',
    self.output_graph, '-c', src, '-d', dst )
  trManager = registration.getTransformationManager()
  trManager.copyReferential( self.input_graph, self.output_graph )
