# Copyright CEA and IFR 49 (2000-2005)
#
#  This software and supporting documentation were developed by
#      CEA/DSV/SHFJ and IFR 49
#      4 place du General Leclerc
#      91401 Orsay cedex
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

#
# VipBiasCorrection
#
from neuroProcesses import *
import shfjGlobals, registration

name = 'Vip Bias Correction'
userLevel = 1

signature = Signature(
  'mri', ReadDiskItem( "T1 MRI", shfjGlobals.vipVolumeFormats ),
  'mri_corrected', WriteDiskItem( "T1 MRI Bias Corrected",
      shfjGlobals.aimsWriteVolumeFormats ),
  #'coil',Choice('volumic','surface'),
  'field_rigidity', Float(),
  'write_field', Choice('Yes','No'),
  'dim_rigidity', Choice('2D','3D'),
  'sampling', Float(),
  'ngrid', Integer(),
  'geometric', Float(),
  'nIncrement', Choice('1','2','3','4','5'),
  'init_temperature', Float(),
  'increment',Float(),
  'init_amplitude',Float(),
  'zdir_multiply_regul',Float()
)

# Default values
def initialization( self ):

  def setFieldRigidity( self, proc ):
    if self.dim_rigidity == '2D':
      return 0.5
    else:
      return 10
    

  def setGeo( self, proc ):
    if self.dim_rigidity == '2D':
      return 0.97
    else:
      return 0.97

  def setSampling( self, proc ):
    if self.dim_rigidity == '2D':
      return 64.0
    else:
      return 16.0
   
  def setNinc( self, proc ):
    if self.dim_rigidity == '2D':
      return 5
    else:
      return 2
    
  def setNgrid( self, proc ):
    if self.dim_rigidity == '2D':
      return 5
    else:
      return 2

  def setInitTemp( self, proc ):
    if self.dim_rigidity == '2D':
      return 10
    else:
      return 10

  
  self.linkParameters( 'mri_corrected', 'mri' )
  self.write_field = 'No'
  self.dim_rigidity = '3D'
  #self.sampling = 16 
  self.increment = 1.03
  self.init_amplitude = 1.1
  self.zdir_multiply_regul = 1
  self.ngrid = 2
  
  self.linkParameters('field_rigidity','dim_rigidity',setFieldRigidity)
  self.linkParameters('sampling','dim_rigidity',setSampling)
  self.linkParameters('ngrid','dim_rigidity',setNgrid)
 
  self.linkParameters('geometric','dim_rigidity',setGeo)
  self.linkParameters('nIncrement','dim_rigidity',setNinc)
  self.linkParameters('init_temperature','dim_rigidity',setInitTemp)


def execution( self, context ):
    if os.path.exists(self.mri_corrected.fullName() + '.loc'):
      context.write(self.mri_corrected.fullName(), ' has been locked')
      context.write('Remove',self.mri_corrected.fullName(),'.loc if you want to trigger a new correction')
    else:
      if self.dim_rigidity == '2D':
        dim = 2
      else:
        dim = 3
      if self.write_field == 'No':
        write = 'n'
        context.system('VipBiasCorrection', '-input', self.mri.fullPath(), '-o', self.mri_corrected.fullPath() , '-Fwrite', write, '-Kregul', self.field_rigidity, '-Dimfield', dim, '-sampling',  self.sampling, '-Grid', self.ngrid, '-geometric', self.geometric, '-nIncrement',  self.nIncrement, '-Increment',self.increment, '-Temperature', self.init_temperature, '-amplitude', self.init_amplitude, '-ZregulTuning', self.zdir_multiply_regul)
      else:
        write = 'y'
        fieldname = self.mri_corrected.fullName() + 'Field '
        context.system('VipBiasCorrection', '-i', self.mri.fullPath(), '-o', self.mri_corrected.fullPath() , '-Fwrite', write, '-field',fieldname, '-Kregul', self.field_rigidity, '-Dimfield', dim, '-sampling',  self.sampling, '-Grid', self.ngrid, '-geometric', self.geometric, '-nIncrement',  self.nIncrement, '-Increment',self.increment, '-T', self.init_temperature, '-a', self.init_amplitude, '-Z', self.zdir_multiply_regul)
      # copy referential of mri
      tm = registration.getTransformationManager()
      tm.copyReferential(self.mri, self.mri_corrected)

