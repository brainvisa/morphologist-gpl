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
from brainvisa import anatomist

name = 'Anatomist Show Bias Correction'
roles = ('viewer',)
userLevel = 0

def validation():
    anatomist.validation()

signature = Signature(
    'mri_corrected', ReadDiskItem('T1 MRI Bias Corrected',
                                  'Anatomist volume formats'),
    't1mri', ReadDiskItem('Raw T1 MRI', 'Anatomist volume formats',
                          exactType = True),
    'histo_analysis', ReadDiskItem('Histo analysis', 'Histo analysis')
)

def initialization(self):
    self.linkParameters('t1mri', 'mri_corrected')
    self.linkParameters('histo_analysis', 'mri_corrected')
    self.setOptional('t1mri', 'histo_analysis')

def execution(self, context):
    selfdestroy = []
    a = anatomist.Anatomist()
    block = None
    if self.t1mri is not None:
        block = a.createWindowsBlock(2)
        selfdestroy.append(block)
        selfdestroy.append(a.viewBias(self.t1mri, forceReload=1,
                                      hanfile=self.histo_analysis,
                                      parent=block))
    selfdestroy.append(a.viewBias(self.mri_corrected,
                                  hanfile=self.histo_analysis, parent=block))
    return selfdestroy
