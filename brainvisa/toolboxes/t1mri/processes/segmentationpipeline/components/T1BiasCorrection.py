# -*- coding: utf-8 -*-
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
import shfjGlobals, registration

name = '1 - T1 Bias Correction'
userLevel = 2

signature = Signature(
  'mri', ReadDiskItem( "Raw T1 MRI", shfjGlobals.vipVolumeFormats ),
  'mri_corrected', WriteDiskItem( "T1 MRI Bias Corrected",
      'Aims writable volume formats' ),
  'mode', Choice('write_minimal','write_all','delete_useless'),
  'write_field', Choice('yes','no'),
  'field', WriteDiskItem( "T1 MRI Bias Field",
      shfjGlobals.aimsWriteVolumeFormats ),
  'sampling', Float(),
  'field_rigidity', Float(),
  'zdir_multiply_regul',Float(),
  'ngrid', Integer(),
  'write_hfiltered', Choice('yes','no'),
  'hfiltered', WriteDiskItem( "T1 MRI Filtered For Histo",
      shfjGlobals.aimsWriteVolumeFormats ),
  'write_wridges', Choice('yes','no','read'),
  'white_ridges', WriteDiskItem( "T1 MRI White Matter Ridges",
      shfjGlobals.aimsWriteVolumeFormats ),
  'write_meancurvature', Choice('yes','no'),
  'meancurvature', WriteDiskItem( "T1 MRI Mean Curvature",
      shfjGlobals.aimsWriteVolumeFormats ),
  'variance_fraction',Integer(),
  'write_variance', Choice('yes','no'),
  'variance', WriteDiskItem( "T1 MRI Variance",
      shfjGlobals.aimsWriteVolumeFormats ),
  'edge_mask',Choice('yes','no'),
  'write_edges', Choice('yes','no'),
  'edges', WriteDiskItem( "T1 MRI Edges", shfjGlobals.aimsWriteVolumeFormats ),
  'delete_last_n_slices',Integer()
)

# Default values
def initialization( self ):
  self.linkParameters( 'mri_corrected', 'mri' )
  self.linkParameters( 'field', 'mri_corrected' )
  self.linkParameters( 'hfiltered', 'field' )
  self.linkParameters( 'white_ridges', 'hfiltered' )
  self.linkParameters( 'meancurvature', 'white_ridges' )
  self.linkParameters( 'variance', 'meancurvature' )
  self.linkParameters( 'edges', 'variance' )


  self.mode = 'write_minimal'
  self.write_wridges = 'yes'
  self.write_field = 'no'
  self.write_hfiltered = 'yes'
  self.write_variance = 'yes'
  self.write_meancurvature = 'no'
  self.write_edges = 'yes'
  self.field_rigidity = 20
  self.sampling = 16 
  self.ngrid = 2
  self.zdir_multiply_regul = 0.5
  self.variance_fraction = 75
  self.edge_mask = 'yes'
  self.delete_last_n_slices = '0'

def execution( self, context ):
  if self.mode == 'write_all':
    self.write_wridges = 'yes'
    self.write_field = 'yes'
    self.write_hfiltered = 'yes'
    self.write_variance = 'yes'
    self.write_meancurvature = 'yes'
    self.write_edges = 'yes'
  if self.edge_mask == 'yes':
    edge = '3'
  else:
    edge = 'n'
  if self.mode in ("write_minimal","write_all"):
    if os.path.exists(self.mri_corrected.fullName() + '.loc'):
      context.write(self.mri_corrected.fullName(), ' has been locked')
      context.write('Remove',self.mri_corrected.fullName(),'.loc if you want to trigger a new correction')
    else:
      context.system('VipT1BiasCorrection', '-i', self.mri.fullPath(), '-o', self.mri_corrected.fullPath() , '-Fwrite', self.write_field, '-field', self.field.fullPath(), '-Wwrite', self.write_wridges, '-wridge', self.white_ridges.fullPath(),'-Kregul', self.field_rigidity, '-sampling',  self.sampling, '-Grid', self.ngrid, '-ZregulTuning', self.zdir_multiply_regul, '-vp',self.variance_fraction,'-e',edge, '-eWrite', self.write_edges, '-ename', self.edges.fullPath(), '-vWrite', self.write_variance, '-vname', self.variance.fullPath(), '-mWrite',self.write_meancurvature, '-mname', self.meancurvature.fullPath(), '-hWrite', self.write_hfiltered, '-hname', self.hfiltered.fullPath(), '-Last', self.delete_last_n_slices  )
      tm = registration.getTransformationManager()
      tm.copyReferential(self.mri, self.mri_corrected)
      if self.write_field:
        tm.copyReferential( self.mri, self.field )
      if self.write_hfiltered:
        tm.copyReferential( self.mri, self.hfiltered )
      if self.write_wridges:
        tm.copyReferential( self.mri, self.white_ridges )
      if self.write_variance:
        tm.copyReferential( self.mri, self.variance )
      if self.write_meancurvature:
        tm.copyReferential( self.mri, self.meancurvature )
      if self.write_edges:
        tm.copyReferential( self.mri, self.edges )
  elif  self.mode == 'delete_useless':
    if os.path.exists(self.field.fullName() + '.ima') or os.path.exists(self.field.fullName() + '.ima.gz'):
      shelltools.rm( self.field.fullName() + '.*' )
    if os.path.exists(self.variance.fullName() + '.ima') or os.path.exists(self.variance.fullName() + '.ima.gz'):
      shelltools.rm( self.variance.fullName() + '.*' )
    if os.path.exists(self.edges.fullName() + '.ima') or os.path.exists(self.edges.fullName() + '.ima.gz'):
      shelltools.rm( self.edges.fullName() + '.*' )
    if os.path.exists(self.meancurvature.fullName() + '.ima') or os.path.exists(self.meancurvature.fullName() + '.ima.gz'):
      shelltools.rm( self.meancurvature.fullName() + '.*' )
#  elif  self.mode == 'gzip_wridge_and_hfiltered':
#    if os.path.exists(self.hfiltered.fullName() + '.ima'):
#      context.system("gunzip --force " + self.hfiltered.fullName() + '.ima')
#      context.system("gunzip --force " + self.hfiltered.fullName() + '.dim')
#    if os.path.exists(self.white_ridges.fullName() + '.ima'):
#      context.system("gunzip --force " + self.white_ridges.fullName() + '.ima')
#      context.system("gunzip --force " + self.white_ridges.fullName() + '.dim')
