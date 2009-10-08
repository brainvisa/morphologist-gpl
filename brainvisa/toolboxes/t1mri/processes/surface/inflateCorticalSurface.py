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

#
# AimsInflate process declaration
#

from neuroProcesses import *

name = 'Inflate Cortical Surface'
userLevel = 0

# Argument declaration
signature = Signature(
	'input_mesh',ReadDiskItem( 'Hemisphere White Mesh' , ['TRI mesh', 'MESH mesh']),
	'output_mesh',WriteDiskItem( 'Inflated Hemisphere White Mesh', 'MESH mesh'),
	'curvature_texture',WriteDiskItem( 'White Curvature Texture', 'Texture'),
	'iterations', Integer(),
	'normal_force', Float(),
	'spring_force', Float(),
	'smoothing_force', Float(),
	'save_sequence', Boolean(),
	)


# Default values
def initialization( self ):
	self.linkParameters( 'output_mesh', 'input_mesh' )
	self.linkParameters( 'curvature_texture', 'input_mesh' )
	self.iterations = 500
	self.normal_force = 0.01
	self.spring_force = 0.01
	self.smoothing_force = 0.5
	self.save_sequence = 0

# AimsInflate process
#

def execution( self, context ):
	if os.path.exists(self.output_mesh.fullName() + '.loc'):
		context.write( "Inflated cortical surface locked")
	else:
		if self.save_sequence:
			context.system( 'AimsInflate', '-i',  self.input_mesh.fullName(), '-o', self.output_mesh.fullName(), '-t', self.iterations, '-Kn', self.normal_force, '-Ksp', self.spring_force, '-Ksm', self.smoothing_force, '-c', self.curvature_texture.fullName(), '-S')
		else:
			context.system( 'AimsInflate', '-i',  self.input_mesh.fullName(), '-o', self.output_mesh.fullName(), '-t', self.iterations, '-Kn', self.normal_force, '-Ksp', self.spring_force, '-Ksm', self.smoothing_force,'-c', self.curvature_texture.fullName())
