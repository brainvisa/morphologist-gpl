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

#
# Brain segmentation process declaration
#
name = 'Vip Split Brain'
userLevel = 1

# Argument declaration
signature = Signature(
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
      'Aims readable volume formats' ),
  'Use_template', Boolean(), 
  'voronoi_template', ReadDiskItem( 'Hemispheres Template',
      'Aims readable volume formats' ),
  'brain_mask', ReadDiskItem( "T1 Brain Mask",
      'Aims readable volume formats' ),
  'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'brain_voronoi', WriteDiskItem( "Voronoi Diagram",
      'Aims writable volume formats' ),
  'Commissure_coordinates', ReadDiskItem( 'Commissure coordinates',
      'Commissure coordinates'),
  'white_algo', Choice('r','c','b','t'),
  'mult_factor', Float(),
  'bary_factor', Float(),
  'white_threshold', Integer(),
  'initial_erosion', Float(),
  'cc_min_size', Integer()
)

# Default values
def initialization( self ):
  self.linkParameters( 'histo_analysis', 'mri_corrected' )
  self.linkParameters( 'brain_mask', 'mri_corrected' )
  self.linkParameters( 'brain_voronoi', 'mri_corrected' )
  self.linkParameters( 'Commissure_coordinates', 'mri_corrected' )
  self.voronoi_template = self.signature[ 'voronoi_template' ].findValue( {} )
  self.Use_template = 1
  self.setOptional('voronoi_template')
  self.setOptional('Commissure_coordinates')
  self.setOptional('white_algo')
  self.setOptional('mult_factor')
  self.white_algo = 'r'
  self.bary_factor = 0.75
  self.setOptional('white_threshold')
  self.initial_erosion = 2
  self.cc_min_size = 500
  self.mult_factor = 2.


def execution( self, context ):
  if os.path.exists(self.brain_voronoi.fullName() + '.loc'):
    context.write(self.brain_voronoi.fullName(), ' has been locked')
    context.write('Remove',self.brain_voronoi.fullName(),'.loc if you want to trigger a new segmentation')
  else:
    option_list = []
    if self.Commissure_coordinates is not None:
      option_list += ['-Points', self.Commissure_coordinates.fullPath()]
    if self.white_threshold is not None:
      option_list += ['-wthreshold', self.white_threshold]
      self.white_algo = 't'
    if self.white_algo == 'b' :
      option_list += ['-Bary', self.bary_factor]
    if self.white_algo == 'c' :
      option_list += ['-Coef', self.mult_factor]
    if self.Use_template:
      option_list += ['-template', self.voronoi_template.fullPath(),
                      '-TemplateUse', 'y']
    call_list = ['VipSplitBrain',
                 '-input',  self.mri_corrected.fullPath(),
                 '-brain', self.brain_mask.fullPath(),
                 '-analyse', 'r', '-hname', self.histo_analysis.fullPath(),
                 '-output', self.brain_voronoi.fullPath(),
                 '-erosion', self.initial_erosion,
                 '-ccsize', self.cc_min_size,
                 '-walgo',self.white_algo
                 ]
    apply( context.system, call_list+option_list )
