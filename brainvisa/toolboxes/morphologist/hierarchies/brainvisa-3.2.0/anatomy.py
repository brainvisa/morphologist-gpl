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

from __future__ import absolute_import
from brainvisa import registration
from brainvisa.morphologist.morpho_hierarchy import *

include('base')
include('registration')
include('raw_data')

insert('{center}/{subject}/t1mri/{acquisition}',
       *(t1mri_acq_content())
       )

#==================================================================================================================================
# SNAPSHOTS
#==================================================================================================================================

# snapshots snapbase morphologist
insert('snapshots/morphologist/{acquisition}',
       *(morpho_snapshots()))

# snapbase qc spm
insert('snapshots/{processing}/{acquisition}',
       "qc_<processing>", SetType('Snapshots Probability Map Quality Scores'),
       )

#==================================================================================================================================
# TABLES
#==================================================================================================================================

insert('tables/{acquisition}',
       *(tables_content()))

#----------------- Registration -------------------------

# insertFirst( '{center}/{subject}/registration',
#'RawT1-<subject>-{acquisition}', SetType( 'Referential of Raw T1 MRI' ),
#'RawT1-<subject>_{acquisition}_TO_Talairach-ACPC', SetType( 'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist' ),
#)

# insertFirst( '{center}/registration',
# idem que pour subject/registration
#'RawT1-{source.subject}-{source.acquisition}_TO_RawT1-{dest.subject}-{dest.acquisition}', SetType( 'Transform Raw T1 MRI to Raw T1 MRI' ),
#)
