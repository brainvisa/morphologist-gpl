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

name = 'BrainVISA Show Histo analysis'
userLevel = 0
roles = ("viewer", )


def validation():
    try:
        import brainvisa.morphologist.qt4gui.histo_analysis_widget
    except:
        # The new viewer does not work: this one will do the job.
        return
    # if it succeeds, then the newer viewer will work, and we invalidate
    # this one
    raise ValidationError(
        'A newer histogram analysis viewer replaces this one')


signature = Signature(
    'histo_analysis', ReadDiskItem('Histo Analysis', 'Histo Analysis'),
    'use_hfiltered', Boolean(),
    'hfiltered', ReadDiskItem("T1 MRI Filtered For Histo",
                              'Aims readable volume formats'),
    'use_wridges', Boolean(),
    'white_ridges', ReadDiskItem(
        "T1 MRI White Matter Ridges",   'Aims readable volume formats')
)


def initialization(self):
    self.linkParameters('hfiltered', 'histo_analysis')
    self.linkParameters('white_ridges', 'histo_analysis')
    self.setOptional('hfiltered')
    self.setOptional('white_ridges')
    self.use_hfiltered = True
    self.use_wridges = True


def execution(self, context):
    renderopt = '--matplotlib'
    try:
        import matplotlib
    except:
        # matplotlib unavailable: use gnuplot (and assume it is here...)
        renderopt = '-g'

    f = open(self.histo_analysis.fullPath(), "r")
    lines = f.readlines()
    undersampling = (lines[10].split())[1]
    f.close()

    option_list = []
    constant_list = ['VipHistoAnalysis', '-i', self.histo_analysis.fullName(),
                     '-S', 'n', '-m', 'a', '-u', undersampling, renderopt, 's']
    if self.use_hfiltered and self.hfiltered is not None:
        option_list += ['-Mask', self.hfiltered.fullPath()]
    if self.use_wridges and self.white_ridges is not None:
        option_list += ['-Ridge', self.white_ridges.fullPath()]
    context.system(*(constant_list + option_list))
