#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from brainvisa.processes import *
from brainvisa import anatomist as ana
from soma import aims

name = 'Clean database - side error'
userLevel = 0

signature = Signature(
    'graphs', ListOf(ReadDiskItem(
        'labelled cortical folds graph', 'graph and data')),
)


def execution(self, context):

    for graph_filename in self.graphs:
        subject = graph_filename.get('subject')
        side = graph_filename.get('side')
        context.write('Processing', subject, side, '...')

        graph = aims.read(graph_filename.fullPath())

        error = False
        for vertex in graph.vertices():
            if 'name' in vertex:
                name = vertex['name']
                if name != 'unknown':
                    if name[-4:] != side[-4:]:
                        context.write('LABELISATION ERROR:',
                                      name, 'for', subject, side)
                        error = True
                        vertex['name'] = name[:name.find('_')] + '_' + side
                        context.write('new name:', vertex['name'])

        if error == True:
            context.write('Saving the graph...')
            aims.write(graph, graph_filename.fullPath())
        context.write('------------')
