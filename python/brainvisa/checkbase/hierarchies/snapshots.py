# -*- coding: utf-8 -*-
import os

patterns = {'sulci' : os.path.join('(?P<database>[\w -/]+)', 'snapshots_sulci_(?P<side>[LR]?)_(?P<mode>\w+)_(?P<group>\w+)_(?P<subject>\w+)_(?P<acquisition>[\w -/]+).png') }
keyitems = []
