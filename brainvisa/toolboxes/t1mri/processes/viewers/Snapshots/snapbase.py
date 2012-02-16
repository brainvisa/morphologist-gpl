

from neuroProcesses import *
from neuroConfig import *

name = 'SnapBase : a tool to generate huge snapshots of massive cohorts'
userLevel = 2

if __name__ == '__main__':
    main()

def execution( self, context ):
    import os.path
    import sys
    context.system( 'snapbase' )
