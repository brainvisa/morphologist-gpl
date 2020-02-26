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


from __future__ import absolute_import
from brainvisa.processes import *

name = 'T1 Bias Correction'
userLevel = 2

signature = Signature(
    'mri', ReadDiskItem("Raw T1 MRI", 'aims readable Volume Formats'),
    'mri_corrected', WriteDiskItem("T1 MRI Bias Corrected",
                                   'aims Writable Volume Formats'),
    'write_hfiltered', Choice('yes', 'no'),
    'hfiltered', WriteDiskItem("T1 MRI Filtered For Histo",
                               'aims Writable Volume Formats'),
    'write_wridges', Choice('yes', 'no', 'read'),
    'white_ridges', WriteDiskItem("T1 MRI White Matter Ridges",
                                  'aims Writable Volume Formats'),
)


def selected(self, subproc):
    if subproc._selected:
        self._executionNode.addLink('BiasCorrection05.write_hfiltered',
                                    'write_hfiltered')
        self._executionNode.addLink('write_hfiltered',
                                    'BiasCorrection05.write_hfiltered')
        self._executionNode.addLink('BiasCorrection05.hfiltered', 'hfiltered')
        self._executionNode.addLink('hfiltered', 'BiasCorrection05.hfiltered')
        self._executionNode.addLink('BiasCorrection05.write_wridges',
                                    'write_wridges')
        self._executionNode.addLink('write_wridges',
                                    'BiasCorrection05.write_wridges')
        self._executionNode.addLink('BiasCorrection05.white_ridges',
                                    'white_ridges')
        self._executionNode.addLink('white_ridges',
                                    'BiasCorrection05.white_ridges')
        self.signature['write_hfiltered'].setChoices('yes', 'no')
        self.signature['write_wridges'].setChoices('yes', 'no', 'read')
        self.write_hfiltered = self._executionNode.BiasCorrection05.write_hfiltered
        self.write_wridges = self._executionNode.BiasCorrection05.write_wridges
        self.hfiltered = self._executionNode.BiasCorrection05.hfiltered
        self.white_ridges = self._executionNode.BiasCorrection05.white_ridges
    else:
        self._executionNode.removeLink('write_hfiltered',
                                       'BiasCorrection05.write_hfiltered')
        self._executionNode.removeLink('BiasCorrection05.write_hfiltered',
                                       'write_hfiltered')
        self._executionNode.removeLink('hfiltered',
                                       'BiasCorrection05.hfiltered')
        self._executionNode.removeLink('BiasCorrection05.hfiltered',
                                       'hfiltered')
        self._executionNode.removeLink('write_wridges',
                                       'BiasCorrection05.write_wridges')
        self._executionNode.removeLink('BiasCorrection05.write_wridges',
                                       'write_wridges')
        self._executionNode.removeLink('white_ridges',
                                       'BiasCorrection05.white_ridges')
        self._executionNode.removeLink('BiasCorrection05.white_ridges',
                                       'white_ridges')
        self.signature['write_hfiltered'].setChoices('no')
        self.signature['write_wridges'].setChoices('no')
        self.write_hfiltered = 'no'
        self.write_wridges = 'no'
        self.hfiltered = None
        self.white_ridges = None


# Default values
def initialization(self):
    self.setOptional('hfiltered')
    self.setOptional('white_ridges')

    eNode = SelectionExecutionNode(self.name, parameterized=self)
    eNode.addChild('BiasCorrection05',
                   ProcessExecutionNode('T1BiasCorrection', selected=1))
    eNode.addChild('BiasCorrection04',
                   ProcessExecutionNode('VipBiasCorrection', selected=0))

    # links for 2005 version

    eNode.addLink('BiasCorrection05.t1mri', 'mri')
    eNode.addLink('mri', 'BiasCorrection05.t1mri')
    eNode.addLink('BiasCorrection05.t1mri_nobias', 'mri_corrected')
    eNode.addLink('mri_corrected', 'BiasCorrection05.t1mri_nobias')
    eNode.addLink('BiasCorrection05.commissure_coordinates',
                  'BiasCorrection05.t1mri_nobias')

    eNode.addLink('BiasCorrection05.write_hfiltered', 'write_hfiltered')
    eNode.addLink('write_hfiltered', 'BiasCorrection05.write_hfiltered')
    eNode.addLink('BiasCorrection05.hfiltered', 'hfiltered')
    eNode.addLink('hfiltered', 'BiasCorrection05.hfiltered')

    eNode.addLink('BiasCorrection05.write_wridges', 'write_wridges')
    eNode.addLink('write_wridges', 'BiasCorrection05.write_wridges')
    eNode.addLink('BiasCorrection05.white_ridges', 'white_ridges')
    eNode.addLink('white_ridges', 'BiasCorrection05.white_ridges')

    # 2004 version

    eNode.addLink('BiasCorrection04.mri', 'mri')
    eNode.addLink('mri', 'BiasCorrection04.mri')
    eNode.addLink('BiasCorrection04.mri_corrected', 'mri_corrected')
    eNode.addLink('mri_corrected', 'BiasCorrection04.mri_corrected')

    eNode.BiasCorrection05._selectionChange.add(self.selected)

    self.setExecutionNode(eNode)
