# -*- coding: utf-8 -*-
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

include( 'builtin' )
include( 'registration' )

Format( 'Commissure coordinates', "f|*.APC" )
Format( 'Histogram', 'f|.his' )
Format( 'Histo Analysis', "f|*.han" )
Format( 'Gyri Model', "f|*.gyr" )

#FileType( 'SPM default parameters', 'XML parameters', 'XML' )

#----------------- Anatomy ------------------------

FileType( 'Registered Raw T1 MRI with fMRI', 'Raw T1 MRI' )
FileType( 'Commissure coordinates', 'Any Type', 'Commissure coordinates')
FileType( 'T1 MRI Bias Corrected', 'T1 MRI' )
FileType( 'T1 MRI Bias Field', 'Rainbow 3D Volume' )
FileType( 'T1 MRI White Matter Ridges', 'Label Volume' )
FileType( 'T1 MRI Mean Curvature', 'Rainbow 3D Volume' )
FileType( 'T1 MRI Filtered For Histo', 'Label Volume' )
FileType( 'T1 MRI Edges', 'Rainbow 3D Volume' )
FileType( 'T1 MRI Variance', 'Rainbow 3D Volume' )
FileType( 'Brain Mask',  'Label Volume')
FileType( 'T1 Brain Mask',  'Brain Mask')
FileType( 'Grey White Mask', 'Label Volume' )
FileType( 'Left Grey White Mask', 'Grey White Mask' )
FileType( 'Right Grey White Mask', 'Grey White Mask' )
FileType( 'CSF+GREY Mask', 'Label Volume' )
FileType( 'Both CSF Mask', 'Label Volume' )
FileType( 'Left CSF Mask', 'Label Volume' )
FileType( 'Right CSF Mask', 'Label Volume' )
FileType( 'Both CSF+GREY Mask', 'CSF+GREY Mask' )
FileType( 'Left CSF+GREY Mask', 'CSF+GREY Mask' )
FileType( 'Right CSF+GREY Mask', 'CSF+GREY Mask' )
FileType( 'Cortex Skeleton', 'Label Volume' )
FileType( 'Left Cortex Skeleton', 'Cortex Skeleton' )
FileType( 'Right Cortex Skeleton', 'Cortex Skeleton' )
FileType( 'Cortex Catchment Bassins', 'Label Volume' )
FileType( 'Left Cortex Catchment Bassins', 'Cortex Catchment Bassins' )
FileType( 'Right Cortex Catchment Bassins', 'Cortex Catchment Bassins' )
FileType( 'Bottom Volume', 'Label Volume' )
#Wait for a solution to the attribute pub in ReadDiskItem
FileType( 'Left Bottom Volume', 'Bottom Volume' )
FileType( 'Right Bottom Volume', 'Bottom Volume' )
FileType( 'Hull Junction Volume', 'Label Volume' )
FileType( 'Left Hull Junction Volume', 'Hull Junction Volume' )
FileType( 'Right Hull Junction Volume', 'Hull Junction Volume' )
FileType( 'Simple Surface Volume', 'Label Volume' )
FileType( 'Left Simple Surface Volume', 'Simple Surface Volume' )
FileType( 'Right Simple Surface Volume', 'Simple Surface Volume' )
FileType( 'Sulci Volume', 'Label Volume' )
FileType( 'Left Sulci Volume', 'Sulci Volume' )
FileType( 'Right Sulci Volume', 'Sulci Volume' )
FileType( 'Hemisphere Mesh', 'Mesh' )
FileType( 'Left Hemisphere Mesh', 'Hemisphere Mesh' )
FileType( 'Right Hemisphere Mesh', 'Hemisphere Mesh' )
FileType( 'Hemisphere White Mesh', 'Mesh' )
FileType( 'Left Hemisphere White Mesh', 'Hemisphere White Mesh' )
FileType( 'Right Hemisphere White Mesh', 'Hemisphere White Mesh' )
FileType( 'Left Hemisphere White Spherical Mesh', 'Left Hemisphere White Mesh' )
FileType( 'Right Hemisphere White Spherical Mesh', 'Right Hemisphere White Mesh' )
FileType( 'Left Fine Hemisphere White Mesh', 'Hemisphere White Mesh' )
FileType( 'Right Fine Hemisphere White Mesh', 'Hemisphere White Mesh' )
FileType( 'Inflated Hemisphere White Mesh', 'Hemisphere White Mesh' )
FileType( 'Median Mesh', 'Hemisphere Mesh' )
FileType( 'Conformal White Mesh', 'Hemisphere White Mesh')
FileType( 'Head Mask', 'Label Volume' )
FileType( 'Head Mesh', 'Mesh' )
FileType( 'Skull Mesh', 'Mesh' )
FileType( 'Brain Mesh', 'Mesh' )
FileType( 'Hemisphere Hull Mesh', 'Mesh' )
FileType( 'Brain Hull Mesh', 'Mesh' )
FileType( 'MNI Cortex Mesh', 'Mesh' )
FileType( 'Histogram', 'Any Type', 'Histogram' )
FileType( 'Histo Analysis', 'Any Type', 'Histo Analysis' )
FileType( 'Moment Vector', 'Any Type', 'Moment Vector' )
FileType( 'Gyri Model', 'Any Type', 'Gyri Model' )
FileType( 'Sulci White Texture', 'Label Texture' )
FileType( 'Sulci White Texture Patch', 'Label Texture' )
FileType( 'Gyri White Texture', 'Label Texture' )
FileType( 'Sulci To White Texture Translation', 'Text File' )
FileType( 'Gyri To White Texture Translation', 'Text File' )
FileType( 'Coordinate Texture', 'Texture' )
FileType( 'Sulci White Volume Patch', '3D Volume' )
FileType( 'Gyri White Volume', '3D Volume' )
FileType( 'Hemispheres Template', '3D Volume' )
FileType( 'Curvature Texture', 'Texture' )
FileType( 'Depth Texture', 'Texture' )
FileType( 'White Curvature Texture', 'Curvature Texture' )
FileType( 'White Depth Texture', 'Depth Texture' )
FileType( 'Blob White Curvature Texture', 'Label Texture' )
FileType( 'Blob White Depth Texture', 'Label Texture' )
FileType( 'Scale Space Texture', 'Texture')
FileType( 'Scale Space White Curvature Texture', 'Scale Space Texture' )
FileType( 'Scale Space White Depth Texture', 'Scale Space Texture' )

FileType( 'MRI Ext Edge Image',    '3D Volume' )
FileType( 'Central Nuclei Template', '4D Volume' )
FileType( 'Deep Nuclei Mask',  'Label Volume' )
#SPM 2 segmentation
FileType( 'Probability Map', '3D Volume' )
FileType( 'CSF Probability Map', 'Probability Map' )
FileType( 'White matter Probability Map', 'Probability Map' )
FileType( 'Grey matter Probability Map', 'Probability Map' )
FileType( 'Grey White Mid-Interface Volume', '3D Volume' )

#SPM 2 segmentation and bias correction
FileType( 'SPM2 parameters', 'XML parameters', ['XML' , 'Matlab file', 'bz2 Matlab file' ])
FileType( 'SPM bias parameters', 'SPM2 parameters', 'XML' )
FileType( 'SPM bias correction', 'Any Type', 'Matlab file' )
FileType( 'SPM segmentation parameters', 'SPM2 parameters', 'XML' )

#SPM 5 transformation parameters
# defined in axon/registration
#FileType( 'SPM Transformation Parameters', 'Any Type', 'Matlab file' )

FileType( 'Lesion Mask', 'Label Volume' )
FileType( 'Lesion distance map', '3D Volume' )
FileType( 'Sulci Voronoi', 'Label Volume' )

#----------------- Graphs -------------------------

FileType( 'Cortical folds graph', 'Data graph' )
FileType( 'Nucleus graph', 'Data graph' )
FileType( 'Deep Nuclei Graph', 'Graph' )
FileType( 'Right Cortical folds graph', 'Cortical folds graph' )
FileType( 'Left Cortical folds graph', 'Cortical folds graph' )
FileType( 'Labelled Cortical folds graph', 'Cortical folds graph' )
FileType( 'Parallel Labelled Cortical folds graph', 'Cortical folds graph' )
FileType( 'Base Cortical folds graph', 'Labelled Cortical folds graph' )
FileType( 'AutoLabelled Cortical folds graph',
          'Labelled Cortical folds graph' )
FileType( 'Left Base Cortical folds graph', 'Base Cortical folds graph' )
FileType( 'Right Base Cortical folds graph', 'Base Cortical folds graph' )
FileType( 'Primal Sketch', 'Data graph' )
FileType( 'Curvature Map Primal Sketch', 'Primal Sketch' )
FileType( 'Depth Map Primal Sketch', 'Primal Sketch' )

FileType( 'Grey Level Blob Graph', 'Data graph' )
FileType( 'Gyri Graph', 'Data graph' )
FileType( 'Sulcal Patch Graph', 'Data graph' )

FileType( 'Bounding Box Points', 'ROI' )

#----------------- Registration -------------------------

FileType( 'Referential of Raw T1 MRI', 'Referential' )
FileType( 'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist', 'Transformation matrix' )
FileType( 'Transform Raw T1 MRI to Talairach-MNI template-SPM', 'Transformation matrix' )
FileType( 'Transform Raw T1 MRI to Raw T1 MRI', 'Transformation matrix' )

#--------------- Templates ------------------------
FileType( 'anatomical Template', '3D Volume')
FileType( 'anatomical Mask Template', '3D Volume')

#----------- Obsololete registration ----------------------

FileType( 'MINC transformation matrix', 'Any Type', 'MINC transformation matrix' )
