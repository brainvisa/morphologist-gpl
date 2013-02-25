# -*- coding: utf-8 -*-
import os
from brainvisa.checkbase import *
from brainvisa.checkbase.hierarchies.checkbase import Checkbase

patterns = {'sulci' : os.path.join('(?P<database>[\w -/]+)', 'snapshots_sulci_(?P<side>[LR]?)_(?P<mode>\w+)_(?P<group>\w+)_(?P<subject>\w+)_(?P<acquisition>[\w -/]+).png') }
keyitems = []

class SnapshotsCheckbase(Checkbase):
    def __init__(self, directory):
        from brainvisa.checkbase.hierarchies import snapshots as snap
        self.patterns = morpho.patterns
        self.keyitems = morpho.keyitems
        Checkbase.__init__(self, directory)

    def check_database_for_existing_files(self):
        return ({}, {})
