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
from brainvisa import shelltools

name = 'Validation_4 Split Brain from Brain Mask'
userLevel = 0

signature = Signature(
  'brain_voronoi', ReadDiskItem( 'Voronoi Diagram',
    'Aims readable volume formats' ),
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
    'Aims readable volume formats' ),
  'validation', Choice("Visualise","Lock","Unlock"),
)

def initialization( self ):
  self.linkParameters(  'mri_corrected','brain_voronoi' )
  self.validation = "Visualise"

def execution( self, context ):
    if self.validation == "Visualise":
      return(context.runProcess('AnatomistShowSplitBrain',
        mri_corrected=self.mri_corrected,brain_voronoi=self.brain_voronoi))
    elif self.validation == "Lock":
      if os.path.exists(self.brain_voronoi.fullName() + '.loc'):
        context.write(self.brain_voronoi.fullName(),'has already been locked')
      else:
        shelltools.touch( self.brain_voronoi.fullName() + '.loc' )

    elif self.validation == "Unlock":
      if os.path.exists(self.brain_voronoi.fullName() + '.loc'):
        os.unlink( self.brain_voronoi.fullName() + '.loc' )
      else:
        context.write(self.brain_voronoi.fullName(),'has not been locked')
    #elif self.validation == "Delete":
        #if os.path.exists(self.brain_voronoi.fullName() + '.loc'):
            #context.write("Sorry, I can not delete ",self.brain_voronoi.fullName(),', which has been locked')
        #elif os.path.exists(self.brain_voronoi.fullName() + '.ima') or os.path.exists(self.brain_voronoi.fullName() + '.ima.gz'):
            #shelltools.rm( self.brain_voronoi.fullName() + '.*' )
        #else:
            #context.write("Sorry ", self.brain_voronoi.fullName(),' does not exist on fdisk')
