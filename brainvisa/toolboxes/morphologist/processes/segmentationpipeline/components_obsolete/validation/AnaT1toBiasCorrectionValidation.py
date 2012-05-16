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
import shfjGlobals

name = 'Validation_1 Bias Correction from T1 MRI'
userLevel = 0

signature = Signature(
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
    'Aims readable volume formats' ),
  'T1mri', ReadDiskItem( "Raw T1 MRI", shfjGlobals.vipVolumeFormats ),
#  'validation', Choice("Visualise","Lock","Unlock","Delete","Compress","Uncompress"),
  'validation', Choice("Visualise","Lock","Unlock"),
)

def initialization( self ):
  self.linkParameters( 'T1mri','mri_corrected' )
  self.validation = "Visualise"
  
def execution( self, context ):
    if self.validation == "Visualise":
      return(context.runProcess('AnatomistShowBiasCorrection', mri_corrected=self.mri_corrected,T1mri=self.T1mri))
    elif self.validation == "Lock":
        if os.path.exists(self.mri_corrected.fullName() + '.loc'):
            context.write(self.mri_corrected.fullName(),'has already been locked')
        else:
            shelltools.touch( self.mri_corrected.fullName() + '.loc' )
    elif self.validation == "Unlock":
        if os.path.exists(self.mri_corrected.fullName() + '.loc'):
            os.unlink( self.mri_corrected.fullName() + '.loc' )
        else:
            context.write(self.mri_corrected.fullName(),'has not been locked')
    elif self.validation == "Delete":
        context.write( 'sorry, delete mode is obsolete' )
        #if os.path.exists(self.mri_corrected.fullName() + '.loc'):
            #context.write("Sorry, I can not delete ",self.mri_corrected.fullName(),', which has been locked')
        #elif os.path.exists(self.mri_corrected.fullPath()) or os.path.exists(self.mri_corrected.fullPath() + '.gz'):
            #shelltools.rm( self.mri_corrected.fullName() + '.*' )
        #else:
            #context.write("Sorry ", self.mri_corrected.fullPath(),
            #' does not exist on fdisk')
    elif self.validation == "Compress":
        context.write( 'sorry, compress mode is obsolete' )
        #if os.path.exists(self.mri_corrected.fullPath()):
            #context.system("gzip --force " + self.mri_corrected.fullPath())
            #context.system("gzip --force " + self.mri_corrected.fullName() + '.dim')
        #elif os.path.exists(self.mri_corrected.fullName() + '.ima.gz'):
            #context.write("Sorry ", self.mri_corrected.fullName(),' is already compressed')
        #else:
            #context.write("Sorry ", self.mri_corrected.fullName(),' does not exist on disk')
    elif self.validation == "Uncompress":
        context.write( 'sorry, uncompress mode is obsolete' )
        #if  os.path.exists(self.mri_corrected.fullName() + '.ima.gz'):
            #context.system("gunzip " + self.mri_corrected.fullName() + '.ima')
            #context.system("gunzip " + self.mri_corrected.fullName() + '.dim')
        #elif os.path.exists(self.mri_corrected.fullName() + '.ima'):
            #context.write("Sorry ", self.mri_corrected.fullName(),' is already uncompressed')
        #else:
            #context.write("Sorry ", self.mri_corrected.fullName(),' does not exist on disk')
