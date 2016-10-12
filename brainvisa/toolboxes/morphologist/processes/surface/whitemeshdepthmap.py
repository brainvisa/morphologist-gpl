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
import os
from brainvisa import anatomist
from brainvisa import registration

name = 'White Mesh Depth Map'
userLevel = 3

signature = Signature(
    "white_mesh", ReadDiskItem("Hemisphere White Mesh", "Aims mesh formats"),
    "hemi_cortex", ReadDiskItem("CSF+GREY Mask",
        "Aims readable volume formats"),
    "depth_texture", WriteDiskItem("White Depth Texture",
                                   "aims Texture formats"),
    "closing_size", Float(),
)

def initialization(self):
  self.linkParameters("hemi_cortex", "white_mesh")
  self.linkParameters("depth_texture", "white_mesh")
  self.closing_size = 10.

def execution(self, context):
  white = context.temporary('GIS Image')
  # take a white mask image
  context.system('AimsThreshold', self.hemi_cortex, white, '-m', 'eq',
                 '-t', 0, '-b')
  closedwhite = context.temporary('GIS image')
  # severely close it to fill every sulcus and ventricle
  context.system('AimsMorphoMath', '-m', 'clo', '-i', white, '-o', closedwhite,
                 '-r', self.closing_size)
  # erode it so that the white mesh goes out of it
  context.system('AimsMorphoMath', '-m', 'ero', '-i', closedwhite,
                 '-o', closedwhite, '-r', 2.)
  hulltex = context.temporary('Texture')
  registration.getTransformationManager().copyReferential(self.white_mesh,
                                                          closedwhite)
  a = anatomist.Anatomist()
  # mask the white mesh with the eroded mask
  #fusion = context.runProcess( 'fusion3Dmesh', closedwhite, self.hemi_cortex,
  #  hulltex, 0 )
  fusion = context.runProcess('fusion3Dmesh', closedwhite, self.white_mesh,
                              hulltex, 0)
  # wait for synchronous completion from Anatomist
  a.getObjects()
  # change values to get O inside sulci and a positive value outside
  context.pythonSystem('cartoLinearComb.py', '-i', hulltex, '-o', hulltex,
                       '-f', '-I1 + 32767')
  # convert to a label texture (seems to be needed for meshdistance)
  context.system('AimsFileConvert', hulltex, hulltex, '-t', 'S16')
  # get the distance map inside sulci as depth map
  context.system('AimsMeshDistance', '-i', self.white_mesh, '-o',
                 self.depth_texture, '-t', hulltex)

