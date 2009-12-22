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

from neuroProcesses import *
from soma.path import find_in_path
import shfjGlobals

name = 'Cortical Fold Graph Thickness and Volumes'
userLevel = 2


signature = Signature(
  'graph', ReadDiskItem( 'Cortical folds graph', 'Graph'),
  'hemi_cortex', ReadDiskItem( 'CSF+GREY Mask',
      'Aims readable volume formats' ),
  'GW_interface', ReadDiskItem( 'Grey White Mask',
      'Aims readable volume formats' ),
  'white_mesh', ReadDiskItem( 'Hemisphere White Mesh', 'Aims mesh formats' ),
  'hemi_mesh', ReadDiskItem( 'Hemisphere Mesh', 'Aims mesh formats'),
  'output_graph', WriteDiskItem ( 'Cortical folds graph', 'Graph'),
  'write_mid_interface', Boolean(),
  'output_mid_interface', WriteDiskItem ( 'Grey White Mid-Interface Volume',
      'Aims writable volume formats' ),
)

def initialization( self ):
  self.linkParameters( 'hemi_cortex', 'graph' )
  self.linkParameters( 'GW_interface', 'hemi_cortex' )
  self.linkParameters( 'white_mesh', 'hemi_cortex' )
  self.linkParameters( 'hemi_mesh', 'white_mesh' )
  self.linkParameters( 'output_graph', 'graph' )
  self.linkParameters( 'output_mid_interface', 'hemi_cortex' )
  self.setOptional( 'output_mid_interface' )
  self.write_mid_interface = False


def execution( self, context ):
  context.system( 'python', find_in_path( 'AimsFoldsGraphThickness.py' ),
    '-i', self.graph, '-c', self.hemi_cortex, '-g', self.GW_interface,
    '-w', self.white_mesh, '-l', self.hemi_mesh, '-o', self.output_graph ,'-m', self.output_mid_interface )
