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

from brainvisa.processes import *

from brainvisa import shelltools
from brainvisa import anatomist

name = 'Validation Pipeline'
userLevel = 0

def validation():
    anatomist.validation()

signature = Signature(
  'T1mri', ReadDiskItem( "Raw T1 MRI", 'aims readable Volume Formats' ),
#  'validation_total', Choice("Visualise","Lock","Unlock","Delete","Compress","Uncompress","Itemwise"),
  'validation_total', Choice("Visualise","Lock","Unlock","Itemwise"),
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
    'Aims readable volume formats' ),
#  'validation_mri_corrected', Choice("Nothing","Visualise","Lock","Unlock","Delete","Compress","Uncompress"),
  'validation_mri_corrected',
  Choice("Nothing","Visualise","Lock","Unlock"),
  'histo_analysis', ReadDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'validation_histo_analysis',
  Choice("Nothing","Visualise","Lock","Unlock"),
  'brain_mask', ReadDiskItem( 'T1 Brain Mask',
    'Aims readable volume formats' ),
#  'validation_brain_mask', Choice("Nothing","Visualise","Lock","Unlock","Delete","Compress","Uncompress"),
  'validation_brain_mask',
  Choice("Nothing","Visualise","Lock","Unlock"),
  'split_mask', ReadDiskItem( 'Split Brain Mask',
    'Aims readable volume formats' ),
#  'validation_split_mask', Choice("Nothing","Visualise","Lock","Unlock","Delete","Compress","Uncompress"),
  'validation_split_mask',
  Choice("Nothing","Visualise","Lock","Unlock"),
#  'left_hemi_cortex', ReadDiskItem( 'Left CSF+GREY Mask', 'GIS Image' ),
#  'validation_left_hemi_cortex', Choice("Nothing","Visualise","Lock","Unlock","Delete","Compress","Uncompress"),
#  'right_hemi_cortex', ReadDiskItem( 'Right CSF+GREY Mask', 'GIS Image' ),
#  'validation_right_hemi_cortex', Choice("Nothing","Visualise","Lock","Unlock","Delete","Compress","Uncompress"),
  'left_hemi_mesh', ReadDiskItem( 'Left Hemisphere Mesh',
    'Aims mesh formats' ),
  'validation_left_hemi_mesh',
  Choice("Nothing","Visualise","Lock","Unlock"),
  'right_hemi_mesh', ReadDiskItem( 'Right Hemisphere Mesh',
    'Aims mesh formats' ),
  'validation_right_hemi_mesh',
  Choice("Nothing","Visualise","Lock","Unlock"),
  'left_white_mesh', ReadDiskItem( 'Left Hemisphere White Mesh',
    'Aims mesh formats' ),
  'validation_left_white_mesh',
  Choice("Nothing","Visualise","Lock","Unlock"),
  'right_white_mesh', ReadDiskItem( 'Right Hemisphere White Mesh',
    'Aims mesh formats' ),
  'validation_right_white_mesh',
  Choice("Nothing","Visualise","Lock","Unlock"),
  )

def initialization( self ):
  self.validation_total = "Visualise"
  self.validation_mri_corrected="Nothing"
  self.validation_histo_analysis="Nothing"
  self.validation_split_mask="Nothing"
  self.validation_brain_mask="Nothing"
  self.validation_left_hemi_cortex="Nothing"
  self.validation_right_hemi_cortex="Nothing"
  self.validation_left_hemi_mesh="Nothing"
  self.validation_right_hemi_mesh="Nothing"
  self.setOptional('histo_analysis')
  self.setOptional('brain_mask')
  self.setOptional('split_mask')
#  self.setOptional('left_hemi_cortex')
#  self.setOptional('right_hemi_cortex')
  self.setOptional('left_hemi_mesh')
  self.setOptional('right_hemi_mesh')
  self.setOptional('left_white_mesh')
  self.setOptional('right_white_mesh')
  
  self.linkParameters( 'mri_corrected', 'T1mri' )
  self.linkParameters( 'histo_analysis', 'T1mri' )
  self.linkParameters( 'brain_mask', 'T1mri' )
  self.linkParameters( 'split_mask', 'mri_corrected' )
#  self.linkParameters( 'left_hemi_cortex', 'mri_corrected' )
#  self.linkParameters( 'right_hemi_cortex', 'mri_corrected' )
  self.linkParameters( 'left_hemi_mesh', 'mri_corrected' )
  self.linkParameters( 'right_hemi_mesh', 'mri_corrected' )
  self.linkParameters( 'left_white_mesh', 'mri_corrected' )
  self.linkParameters( 'right_white_mesh', 'mri_corrected' )

def execution( self, context ):
  result = []

  if self.validation_total != "Itemwise":
     result.append(context.runProcess( 'AnaT1toBiasCorrectionValidation',
                                      T1mri=self.T1mri,
                                      mri_corrected=self.mri_corrected,
                                      validation=self.validation_total))
  elif self.validation_mri_corrected != "Nothing" :
     result.append(context.runProcess( 'AnaT1toBiasCorrectionValidation',
                                       T1mri=self.T1mri,
                                       mri_corrected=self.mri_corrected,
                                       validation=self.validation_mri_corrected))
				 
  if self.validation_total != "Itemwise":
    result.append(context.runProcess( 'AnaHistoAnalysisValidation',
    				      histo_analysis=self.histo_analysis,
				      mri_corrected=self.mri_corrected,
                                      validation=self.validation_total))
  elif self.validation_histo_analysis!="Nothing":
    result.append(context.runProcess( 'AnaHistoAnalysisValidation',
        		              histo_analysis=self.histo_analysis,
                                      mri_corrected=self.mri_corrected,
                                      validation=self.validation_histo_analysis))

  if self.validation_total != "Itemwise":
    result.append(context.runProcess( 'AnaT1toBrainMaskValidation',
                                      mri_corrected=self.mri_corrected,
                                      brain_mask=self.brain_mask,
                                      validation=self.validation_total))
  elif self.validation_brain_mask!="Nothing":
    result.append(context.runProcess( 'AnaT1toBrainMaskValidation',
                                      mri_corrected=self.mri_corrected,
                                      brain_mask=self.brain_mask,
                                      validation=self.validation_brain_mask))

  if self.validation_total != "Itemwise":
    result.append(context.runProcess( 'AnaSplitBrainfromBrainMaskValidation',
                                      mri_corrected=self.mri_corrected,
                                      split_mask=self.split_mask,
                                      validation=self.validation_total))   
  elif self.validation_split_mask!="Nothing":
    result.append(context.runProcess( 'AnaSplitBrainfromBrainMaskValidation',
                                      mri_corrected=self.mri_corrected,
                                      split_mask=self.split_mask,
                                      validation=self.validation_split_mask))


  if self.validation_total == "Visualise" or (self.validation_total == "Itemwise" and self.validation_left_hemi_mesh=="Visualise"):
    a=anatomist.Anatomist()
    # load the mesh and add it in a new 3D window. The method returns the loaded object and the new window. Theses objects are added in the results list in order to be stored after process execution's end.
    result.append(a.viewMesh(self.left_hemi_mesh))
    
  if self.validation_total == "Visualise" or (self.validation_total == "Itemwise" and self.validation_right_hemi_mesh=="Visualise"):
    # Anatomist is a singleton in anatomist module, so calling the constructor will not create a new instance if it exists already one.
    a=anatomist.Anatomist()
    result.append(a.viewMesh(self.right_hemi_mesh))
    
  if self.validation_total == "Visualise" or (self.validation_total == "Itemwise" and self.validation_left_hemi_mesh=="Visualise"):
    a=anatomist.Anatomist()
    result.append(a.viewMesh(self.left_white_mesh))
    
  if self.validation_total == "Visualise" or (self.validation_total == "Itemwise" and self.validation_right_hemi_mesh=="Visualise"):
    a=anatomist.Anatomist()
    result.append(a.viewMesh(self.right_white_mesh))
  # the results returned by the process are stored while the window process exists, so objects persists in anatomist application after the process execution's end.
  return result
