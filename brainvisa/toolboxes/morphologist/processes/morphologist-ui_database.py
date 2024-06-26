from __future__ import print_function
from __future__ import absolute_import
from brainvisa.processes import *


def validation():
    muiexe = findInPath('morphologist')
    if not muiexe:
        raise ValidationError('morphologist program is not found')


name = 'Morphologist UI 2015, run on database'
userLevel = 0

signature = Signature(
    'database', Choice(),
)


def initialization(self):
    databases = [
        (dbs.directory, neuroHierarchy.databases.database(dbs.directory))
        for dbs in neuroConfig.dataPath
        if dbs.expert_settings.ontology
            in ('brainvisa-3.1.0', 'brainvisa-3.2.0', 'morphologist-bids-1.0')]
    self.signature['database'].setChoices(*databases)
    if databases:
        self.database = databases[0][1]
    else:
        self.database = None


def runinthread(self):
    muiexe = os.path.join(findInPath('morphologist'), 'morphologist')
    print(self.database.directory)
    print(type(self.database))
    defaultContext().system(sys.executable, muiexe,
                            '-i', self.database.directory)


def execution(self, context):
    thread = threading.Thread(target=self.runinthread)
    thread.start()
