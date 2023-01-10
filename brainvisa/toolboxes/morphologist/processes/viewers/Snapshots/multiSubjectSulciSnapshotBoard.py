# -*- coding: utf-8 -*-
#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
#
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.

from __future__ import print_function
from __future__ import absolute_import
from brainvisa.processes import *
from brainvisa import anatomist
import time
import six

name = 'Multi Subject Sulci Snapshot Board'
userLevel = 0


def validation():
    anatomist.validation()
    try:
        import PIL
    except:
        raise ValidationError('module PIL (Python Imaging Library) not present.'
                              ' See http://www.pythonware.com/products/pil')
    try:
        import soma.path
    except:
        raise ValidationError('module soma.path not present.')


from soma.path import find_in_path

signature = Signature(
    'graphs', ListOf(ReadDiskItem('Cortical Folds Graph', 'Graph')),
    'meshes', ListOf(ReadDiskItem('Hemisphere White Mesh',
                                  'anatomist Mesh Formats')),
    'transformations', ListOf(ReadDiskItem('Transform Raw T1 MRI to '
                                           'Talairach-AC/PC-Anatomist', 'Transformation matrix')),
    'nomenclature', ReadDiskItem('Nomenclature', 'Hierarchy'),
    'labels_translation_map',
    ReadDiskItem('Label Translation',
                 ['Label Translation', 'DEF Label translation']),
    'sulci_name', String(),
    'orientation', Choice('left', 'right', 'top', 'bottom'),
    'label_attribute', Choice('name', 'label'),
    'output_image', WriteDiskItem('2D Image',
                                  'aims Image Formats'),
    'pages_number', Integer(),
    'rows', Integer(),
    'columns', Integer(),
    'page_size_ratio', Float(),
    'snapshot_width', Integer(),
    'snapshot_height', Integer(),
)


def initialization(self):
    def linkLabelAttribute(self, process):
        la = None
        if self.graphs and len(self.graphs) > 0:
            la = self.graphs[0].get('manually_labelled', None)
            if la == 'Yes':
                la = 'name'
            else:
                la = 'label'
        else:
            la = 'label'
        return la

    self.setOptional('graphs')
    self.setOptional('meshes')
    self.setOptional('transformations')
    self.setOptional('sulci_name')
    self.setOptional('pages_number')
    self.setOptional('rows')
    self.setOptional('columns')
    self.nomenclature = self.signature['nomenclature'].findValue({})
    self.labels_translation_map = \
        self.signature['labels_translation_map'].findValue(
            {'filename_variable': 'sulci_model_2008'})
    self.orientation = 'left'
    self.pages_number = 1
    self.rows = None
    self.columns = None
    self.page_size_ratio = 4./3
    self.snapshot_width = 0
    self.snapshot_height = 0
    self.linkParameters('meshes', 'graphs')
    self.linkParameters('transformations', 'graphs')
    self.linkParameters('label_attribute', 'graphs', linkLabelAttribute)


def execution(self, context):
    n = max(len(self.graphs), len(self.meshes))
    images = []
    # load a python script into the running BV anatomist
    pyscript = context.temporary('Python Script')
    with open(pyscript.fullPath(), 'w') as pys:
        print('import imp', file=pys)
        print('anasul = imp.find_module( "anaSulciSnapshot", [ "'
              + os.path.dirname(find_in_path('anaSulciSnapshot.py')) + '" ] )',
              file=pys)
        print('anaSulciSnapshot = imp.load_module( "anaSulciSnapshot", '
              'anasul[0], anasul[1], anasul[2] )', file=pys)
        print('anasul[0].close()', file=pys)
    from brainvisa import anatomist
    a = anatomist.Anatomist()
    wins = a.importWindows()
    a.loadObject(pyscript.fullPath())
    #global scripts
    scripts = [pyscript]

    for i in six.moves.xrange(n):
        outim = context.temporary(self.output_image.format)
        # snapshot
        images.append(outim)
        if i < len(self.graphs):
            graph = self.graphs[i]
        else:
            graph = None
        if i < len(self.meshes):
            mesh = self.meshes[i]
        else:
            mesh = None
        cmd = []
        if graph is not None:
            cmd += ['-g', graph.fullPath()]
            cmd += ['--label-mode', self.label_attribute]
        if mesh is not None:
            cmd += ['-m', mesh.fullPath()]
        cmd += ['--orientation', self.orientation, '-o', outim.fullPath(),
                '--hie', self.nomenclature.fullPath(), '--translation',
                self.labels_translation_map.fullPath(), '--size',
                str(self.snapshot_width)+','+str(self.snapshot_height)]
        if i < len(self.transformations):
            tr = self.transformations[i]
            cmd += ['-t', tr.fullPath()]
        if self.sulci_name:
            cmd += ['-s', self.sulci_name]

        #context.system( 'python', find_in_path( 'anaSulciSnapshot.py' ), *cmd )

        # load command into anatomist
        pycom = context.temporary('Python Script')
        with open(pycom.fullPath(), 'w') as pyc:
            print('import anaSulciSnapshot', file=pyc)
            print('res = anaSulciSnapshot.main(', cmd, ')', file=pyc)
        a.loadObject(pycom.fullPath())
        scripts.append(pycom)

        #mainThreadActions().call( anasulci.main, cmd )
        # print('anasulci.main( ' + str( cmd ) + ' )', file=pin)
        # pin.flush()
        #context.write( 'anasulci.main( ' + str( cmd ) + ' )' )
        #context.write( 'sent' )
        a.getObjects()  # sync with anatomist
        # if not objs:
        #objs = a.importObjects()
        # if objs:
        # objs[0].getInfos()
        # else:
        #t = time.time()
        # while not os.path.exists( outim.fullPath() ):
        #time.sleep( 0.05 )
        # if time.time() - t >= 60:
        #context.write( outim, 'still not here' )
        #raise RuntimeError( 'Command failed' )
        # time.sleep( 0.1 ) # let it finish writing

        # crop
        cmd = ['autocrop.py', outim, outim]
        context.system(*cmd)

        # scaling
        height = 500
        if self.snapshot_height != 0:
            height = self.snapshot_height
        cmd = ['convert', '-resize', height, outim, outim]
        context.system(*cmd)

    #pycom = context.temporary( 'Python Script' )
    #pyc = open( pycom.fullPath(), 'w' )
    # print('anasulci.a.close(', cmd, ')', file=pyc)
    # pyc.close()
    #a.loadObject( pycom.fullPath() )

    #anasulci.a.execute( 'Exit' )
    # print('sys.exit(0)', file=pin)
    # pin.close()
    #context.write( pout.read() )
    #context.warning( perr.read() )
    # pout.close()
    #res = perr.close()
    # if res:
        #raise RuntimeError( 'Command failed' )

    # mosaic
    cmd = ['mosaic.py', '-o', self.output_image, '-r', self.page_size_ratio]
    if self.rows and self.columns:
        cmd += ['-s', str(self.rows) + 'x' + str(self.columns)]
    else:
        cmd += ['-n', self.pages_number]
    cmd += images
    context.system(*cmd)

    return scripts
