# -*- coding: utf-8 -*-


from __future__ import absolute_import
class DatabaseChecker(object):
    ''' DatabaseChecker objects are only intended to store as attributes a collection
    of database-related information. '''

    def __init__(self):
        pass


from .diskusage.check import check_disk_usage
from .hierarchies.check import check_hierarchies
from .hierarchies import detect_hierarchies, detect_hierarchy, get_files,  getfilepath, parsefilepath, processregexp, image_extensions, mesh_extensions

from .hierarchies.morphologist import MorphologistCheckbase
from .hierarchies.freesurfer import FreeSurferCheckbase
from .hierarchies.snapshots import SnapshotsCheckbase
from .hierarchies.catishared import CATISharedCheckbase
from .hierarchies.spm import SPMCheckbase
from .hierarchies.checkbase import Checkbase
