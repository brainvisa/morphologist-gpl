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

include('builtin')
include('registration')
include('structural')

Format('siRelax Fold Energy', "f|*.nrj")
Format('Sigraph Learner', 'f|*.lrn')
Format('SVM classifier', 'f|*.svm')
#Format( 'SVM regressor', 'f|*.svm' )
Format('MLP classifier', 'f|*.net')
Format('SNNS pattern', 'f|*.pat')
#Format( 'Bayesian Model', 'f|*.bmod' ),
Format('Template model', "f|*.mod")
Format('Template model domain', "f|*.dom")

FileType('siRelax Fold Energy', 'Any Type', 'siRelax Fold Energy')
FileType('Left siRelax Fold Energy', 'siRelax Fold Energy')
FileType('Right siRelax Fold Energy', 'siRelax Fold Energy')
FileType('Sigraph Learner', 'Text file', 'Sigraph Learner')
FileType('Classifier', None, ['SVM classifier',  # 'SVM regressor',
                              'MLP classifier'])
FileType('Elevation map', '2D image', 'Aims writable volume formats')
FileType('Sulci Segments Model', 'Any Type', 'Text Data Table')
FileType('Sulci Segments Relations Model', 'Any Type', 'Text Data Table')
FileType('Sulci Labels Segmentwise Posterior Probabilities', 'CSV file',
         'CSV file')
FileType('Sulci Labels Priors', 'Any Type', 'Text Data Table')
FileType('Sulci Direction Transformation Priors',
         'Any Type', 'Text Data Table')
FileType('Sulci Angle Transformation Priors', 'Any Type', 'Text Data Table')
FileType('Sulci Translation Transformation Priors',
         'Any Type', 'Text Data Table')
FileType('Sulci Local referentials', 'Any Type', 'Text Data Table')

FileType('Sulci Global to Local SPAM transformation',
         'Transformation Matrix', 'Transformation Matrix')
FileType('Sulci Talairach to Global SPAM transformation',
         'Transformation Matrix', 'Transformation Matrix')
FileType('Raw T1 to Global SPAM transformation',
         'Transformation Matrix', 'Transformation Matrix')
FileType('Sulci Local SPAM transformations Directory', 'Directory', 'Directory')
FileType('Referential of Labelled Cortical folds graph',
         'Referential', 'Referential')
FileType('White SPAM mesh', 'Hemisphere White Mesh')
FileType('Template model', 'Any Type', 'Template model')
FileType('Template model domain', 'Any Type', 'Template model domain')

#--------------------Morphometry--------------------

FileType('Sulci groups list', 'Any Type', 'JSON file')
FileType('Sulcal morphometry measurements', 'CSV File')
