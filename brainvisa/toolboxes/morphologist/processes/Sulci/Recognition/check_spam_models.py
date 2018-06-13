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
from soma.wip.application.api import Application
from brainvisa.configuration import neuroConfig
from brainvisa.data.neuroHierarchy import databases

name = 'Check SPAM models installation'
userLevel = 2

signature = Signature(
    'auto_install', Boolean(),
)


def initialization(self):
    self.auto_install = False


def execution(self, context):
    ap = Application()
    if not ap.configuration.sulci.check_spam_models:
        return None  # don't check, do nothing.

    models = list(ReadDiskItem(
        'Sulci Segments Model',
        'Text Data Table')._findValues({}, None, False))
    if len(models) == 0:
        # try upating the shared databases and retry
        for directory, db in databases._databases.items():
            if db.fso.name == 'shared':
                try:
                    db.clear()
                    db.update()
                except:
                    pass  # could not update
        models = list(ReadDiskItem(
            'Sulci Segments Model',
            'Text Data Table')._findValues({}, None, False))
    context.write('models:', len(models))
    if len(models) == 0:
        context.warning(_t_('SPAM models have not be installed yet.'))
        gui = neuroConfig.gui
        if self.auto_install:
            context.runProcess('spam_install_models')
        elif gui:
            inst = context.ask(_t_('Do you want to download and install '
                                   'the SPAM models for sulci '
                                   'identification ?'),
                               _t_('Yes'), _t_('No'), _t_('Don\'t ask again'))
            if inst == 0:
                mainThreadActions().call(showProcess, 'spam_install_models')
                context.warning(_t_('You should stop and re-open the '
                                    'current pipeline (if any) after '
                                    'installing models, to take '
                                    'modifications into account.'))
            elif inst == 2:
                ap.configuration.sulci.check_spam_models = False
                ap.configuration.save(neuroConfig.userOptionFile)

        return False
    else:
        context.write(_t_('SPAM models are present.'))
        return True
