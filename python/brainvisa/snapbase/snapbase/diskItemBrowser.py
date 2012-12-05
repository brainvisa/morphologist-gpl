
from brainvisa.data.qtgui import diskItemBrowser as dib

class SnapBaseItemBrowser(dib.DiskItemBrowser):
    def __init__(self, database, parent=None, multiple=True,
                    selection={}, required={}, enableConversion=False, exactType=False ):
        dib.DiskItemBrowser.__init__(self, database, parent, False, multiple, selection, required,
            enableConversion, exactType)
