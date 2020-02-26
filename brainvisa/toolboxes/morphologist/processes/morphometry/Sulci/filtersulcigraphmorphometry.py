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
from brainvisa.processes import Signature
from brainvisa.processes import ReadDiskItem, Boolean, Float, Choice, String
from brainvisa.processes import WriteDiskItem
from brainvisa.processes import ValidationError
import six

# Try to import numpy
try:
    import numpy as np
except:
    pass

# Try to import pandas
try:
    import pandas as pd
except:
    pass


def validation():
    try:
        import numpy as np
    except:
        ValidationError('no module named pandas')
    try:
        import pandas as pd
    except:
        ValidationError('no module named pandas')


name = 'Sulci graph measurements filtering'
userLevel = 0

signature = Signature(
    'sulcal_morpho_measures', ReadDiskItem('Sulcal morphometry measurements',
                                           'CSV File'),
    'separator', String(),
    'filter_sulci', Boolean(),
    'prop_sulci', Float(),
    'filter_subjects', Boolean(),
    'prop_subjects', Float(),
    'replace_missing', Boolean(),
    'replace_method', Choice('median', 'mean'),
    'verbose', Boolean(),
    'filtered_sulcal_morpho_measures', WriteDiskItem(
        'Sulcal morphometry measurements', 'CSV File',
        requiredAttributes={'filtered': True})
)


def initialization(self):
    self.linkParameters('sulcal_morpho_measures',
                        'filtered_sulcal_morpho_measures')
    # Default values
    self.separator = ","
    self.filter_sulci = True
    self.prop_sulci = 0.9
    self.filter_subjects = True
    self.prop_subjects = 0.7
    self.replace_missing = True
    self.replace_method = 'median'
    self.verbose = False

#
# Util functions
#


def index_to_remove(the_df, axis, threshold):
    """
    Remove the line or row index for which the the proportion of non-null
    elements is below a threshold.
    """
    df_is_not_null = ~the_df.isnull()
    prop_non_missing = df_is_not_null.mean(axis=axis)
    mask = prop_non_missing < threshold
    return prop_non_missing.index[mask]


def filter_sulci(df, prop_sulci=0.9, logger=None):
    """
    Remove sulci for which less than prop_sulci percent of the population have
    a correct value.
    """
    # Copy the df
    df = df.copy(deep=True)
    # Sulci filtering
    n, p = df.shape
    if logger:
        logger("Inspecting {p} sulci ({n} subjects)".format(n=n, p=p))
    removed_sulci = index_to_remove(df, 0, prop_sulci)
    if logger:
        m = len(removed_sulci)
        if m:
            logger(m, "sulci to remove:", removed_sulci.values)
        else:
            logger("No sulci to remove")
    df.drop(removed_sulci, axis=1, inplace=True)
    assert(df.shape == (n, p - len(removed_sulci)))
    return df, removed_sulci


def filter_subjects(df, prop_subjects=0.7, logger=None):
    """
    Remove subjects for which less than prop_subjects percent of the sulci have
    a correct value.
    """
    # Copy the df
    df = df.copy(deep=True)
    # Subject filtering
    n, p = df.shape
    if logger:
        logger("Inspecting {n} subjects ({p} sulci)".format(n=n, p=p))
    removed_subjects = index_to_remove(df, 1, prop_subjects)
    if logger:
        m = len(removed_subjects)
        if m:
            logger(m, "subjects to remove:", removed_subjects.values)
        else:
            logger("No subject to remove")
    df.drop(removed_subjects, axis=0, inplace=True)
    assert(df.shape == (n - len(removed_subjects), p))
    return df, removed_subjects


def replace_missing(df, method='median', logger=None):
    """
    Replace missing values in each column by a given statistics of this column.
    """
    # Copy the df
    df = df.copy(deep=True)
    # Replace values
    df_is_null = df.isnull()
    column_mask = df_is_null.any(axis=0)
    changed_cols = df_is_null.columns[column_mask]
    if method == 'median':
        replace_method = df[changed_cols].median
    elif method == 'mean':
        replace_method = df[changed_cols].mean
    else:
        raise ValueError("Unknown method " + str(method))
    col_replace = replace_method(axis=0, skipna=True)
    if logger:
        m = len(changed_cols)
        if m:
            logger(m, "columns to change:", changed_cols.values)
            logger("Replacement values:", col_replace.to_dict())
        else:
            logger("No columns to modify")
    for col in changed_cols:
        S = df[col]
        mask = S.isnull()
        S[mask] = col_replace[col]
    assert(np.all(~df.isnull()))
    return df, changed_cols, col_replace

#
# Main function
#


def execution(self, context):
    # Read input file
    df = pd.io.parsers.read_csv(self.sulcal_morpho_measures.fullPath(),
                                index_col=0,
                                sep=self.separator)
    logger = context.write if self.verbose else None
    # Filter it
    if self.filter_sulci:
        if logger:
            logger("Filtering sulci")
        df, removed_sulci = filter_sulci(df, self.prop_sulci, logger)
    if self.filter_subjects:
        if self.verbose:
            logger("Filtering subjects")
        df, removed_subjects = filter_subjects(df, self.prop_subjects, logger)
    if self.replace_missing:
        if self.verbose:
            logger("Replacing missing values")
        df, changed_cols, replace = replace_missing(df, self.replace_method,
                                                    logger)
    # Write output file
    df.to_csv(self.filtered_sulcal_morpho_measures.fullPath(),
              sep=self.separator)
    # Add parameters to the minf file
    d = {}
    d = {"filtered": True}
    properties = {"filter_sulci": "prop_sulci",
                  "filter_subjects": "prop_subjects",
                  "replace_missing": "replace_method"}
    for condition, threshold in six.iteritems(properties):
        d[condition] = self.__dict__[condition]
        if d[condition]:
            d[threshold] = self.__dict__[threshold]
    self.filtered_sulcal_morpho_measures.updateMinf(d)
