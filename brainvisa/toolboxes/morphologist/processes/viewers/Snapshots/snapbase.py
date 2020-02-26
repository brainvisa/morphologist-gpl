# -*- coding: utf-8 -*-


from __future__ import absolute_import
from brainvisa.processes import *

name = 'SnapBase : a tool to generate huge snapshots of massive cohorts'
userLevel = 2

if __name__ == '__main__':
    main()


def execution(self, context):
    context.system('snapbase')
