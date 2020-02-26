
# -*- coding: utf-8

from __future__ import absolute_import
from __future__ import print_function
from capsul.api import Process
import traits.api as traits


class GraphPointCloudLabel(Process):
    ''' Split graph vertices according to sub-vertex label classification
    (from Léonie Borne's automatic labelings).
    '''

    graph = traits.File(output=False, allowed_extensions=['.arg'],
                        desc='cortical folds graph')
    voxel_labels = traits.File(
        output=False, allowed_extensions=['.csv'],
        desc='voxel-wise CSV data. Row should include "point_x", "point_y", '
        '"point_z" for voxels coordinates *in Talairach space* (they are '
        'transformed back into native space during the process), and '
        '"after_cutting" for labels.')
    roots = traits.File(
        output=False,
        allowed_extensions=['.nii.gz', '.img', '.hdr', '.v', '.i', '.mnc',
                            '.mnc.gz', '.nii', '.jpg', '.gif', '.png',
                            '.mng', '.bmp', '.pbm', '.pgm', '.ppm', '.xbm',
                            '.xpm', '.tiff', '.tif', '.ima', '.dim',
                            '.vimg', '.vinfo', '.vhdr', ''],
        desc='folds skeleton roots regions, from Morphologist pipeline')
    output_graph = traits.File(
        output=True, allowed_extensions=['.arg'],
        desc='output split and relabelled sulci graph')

    def _run_process(self):
        from soma import aims
        from soma.aimsalgo.sulci import graph_pointcloud
        import pandas

        graph = aims.read(self.graph)
        data = pandas.read_csv(self.voxel_labels)
        roots = aims.read(self.roots)
        graph, summary = graph_pointcloud.build_split_graph(graph, data, roots)

        aims.write(graph, self.output_graph)
        print(summary)
