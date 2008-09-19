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
from neuroProcesses import *
import shfjGlobals     

name = 'nlfit_smr'
#Non linear registration with a model
userLevel = 1

signature = Signature(
  'source', ReadDiskItem( 'MINC image', 'MINC image' ),   
  'model', ReadDiskItem( 'MINC image', 'MINC image' ),   
  'transformed_source', WriteDiskItem( 'MINC image', 'MINC image' ),   
  'output_transfile', WriteDiskItem( 'MINC transformation matrix', 'MINC transformation matrix' ),
  )


def initialization( self ):
  
  
  self.setOptional('transformed_source')

def execution( self, context ):

  weight = 1
  stiffness = 1
  similarity_cost_ratio = 0.3

  source8 = context.temporary('MINC image')
  source4 = context.temporary('MINC image')
  model8 = context.temporary('MINC image')
  model4 = context.temporary('MINC image')
  out8 = context.temporary('MINC transformation matrix')
  out16 = context.temporary('MINC transformation matrix')  
  
  # blur the target files 
  context.system('mincblur', '-fwhm', 8,self.source.fullPath(),source8.fullName())
  context.system('mincblur', '-fwhm', 4,self.source.fullPath(),source4.fullName())
 
  # blur the model files 
  context.system('mincblur', '-fwhm', 8,self.model.fullPath(),model8.fullName())
  context.system('mincblur', '-fwhm', 4,self.model.fullPath(),model4.fullName())
  
  # level 16 registration
  context.system('minctracc','-nonlinear', 'corrcoeff',
       '-debug', '-weight', weight,
       '-stiffness', stiffness,
       '-similarity', similarity_cost_ratio,
       '-iterations', 30,
       '-step', 8, 8, 8,
       '-sub_lattice', 6,
       '-lattice_diam', 24, 24, 24,
       '-ident',
       source8.fullName() + '_blur.mnc', 
       model8.fullName() + '_blur.mnc' , 
       out16.fullPath() )
  
  # level 8 registration
  context.system('minctracc','-nonlinear', 'corrcoeff',
       '-debug', '-weight', weight,
       '-stiffness', stiffness,
       '-similarity', similarity_cost_ratio,
       '-iterations', 30,
       '-step', 4, 4, 4,
       '-sub_lattice', 6,
       '-lattice_diam', 12, 12, 12,
       '-transformation', out16.fullPath(), 
       source8.fullName() + '_blur.mnc', 
       model8.fullName() + '_blur.mnc' ,
       out8.fullPath() )
       
  # level 4 registration
  context.system('minctracc','-nonlinear', 'corrcoeff',
       '-debug', '-weight', weight,
       '-stiffness', stiffness,
       '-similarity', similarity_cost_ratio,
       '-iterations', 10,
       '-step', 2, 2, 2,
       '-sub_lattice', 6,
       '-lattice_diam', 6, 6, 6,
       '-transformation',out8.fullPath(),
       source4.fullName() + '_blur.mnc', 
       model4.fullName() + '_blur.mnc' ,
       self.output_transfile.fullPath() )
       
  

  
