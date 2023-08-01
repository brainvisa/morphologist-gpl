
# -*- coding: utf-8

from capsul.api import Process
from soma.controller import File, field


class GraphPointCloudLabel(Process):
    ''' Split graph vertices according to sub-vertex label classification
    (from Léonie Borne's automatic labelings).
    '''

    graph: File = field(type_=File, extensions=['.arg'],
                        doc='cortical folds graph')
    voxel_labels: File = field(
        type_=File,
        extensions=['.csv'],
        doc='voxel-wise CSV data. Row should include "point_x", "point_y", '
        '"point_z" for voxels coordinates *in Talairach space* (they are '
        'transformed back into native space during the process), and '
        '"after_cutting" for labels.')
    roots: File = field(
        type_=File,
        extensions=['.nii.gz', '.img', '.hdr', '.v', '.i', '.mnc',
                    '.mnc.gz', '.nii', '.jpg', '.gif', '.png',
                    '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm',
                    '.xpm', '.tiff', '.tif', '.ima', '.dim',
                    '.vimg', '.vinfo', '.vhdr', ''],
        doc='folds skeleton roots regions, from Morphologist pipeline')
    output_graph: File = field(
        type_=File, extensions=['.arg'],
        doc='output split and relabelled sulci graph')

    def execute(self):
        from soma import aims
        from soma.aimsalgo.sulci import graph_pointcloud
        import pandas

        graph = aims.read(self.graph)
        data = pandas.read_csv(self.voxel_labels)
        roots = aims.read(self.roots)
        graph, summary = graph_pointcloud.build_split_graph(graph, data, roots)

        aims.write(graph, self.output_graph)
        print(summary)
