# -*- coding: iso-8859-1 -*-
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

###################################################
# Created by A. Moreno - March 2011               #
# using original file "AnatomistShowFoldGraph.py" #
###################################################

from __future__ import print_function
from __future__ import absolute_import
from brainvisa.processes import *
from brainvisa import anatomist
import numpy
import os
from six.moves import range
try:
    from PIL import Image
except:
    pass

name = 'Anatomist Show Fold Graph 4 views - general'
#roles = ('viewer',)
userLevel = 0


def validation():
    anatomist.validation()
    try:
        from PIL import Image
    except:
        raise ValidationError('PIL module not available')


signature = Signature(
    'right_graph', ReadDiskItem('Cortical folds graph', 'Graph and Data',
                                requiredAttributes={'side': 'right'}),
    'left_graph', ReadDiskItem('Cortical folds graph', 'Graph and Data'),
    'nomenclature', ReadDiskItem('Nomenclature', 'Hierarchy'),
    'right_hemi_mesh', ReadDiskItem(
        'Right Hemisphere Mesh', 'Anatomist mesh formats'),
    'left_hemi_mesh', ReadDiskItem(
        'Left Hemisphere Mesh', 'Anatomist mesh formats'),
    'view_quaternionR_V', String(),
    'view_quaternionL_V', String(),
    'view_quaternionR_H', String(),
    'view_quaternionL_H', String(),
    'mesh_transparency', Number(),
    'zoom_V', Number(),
    'zoom_H', Number(),
    'snapshot_size', Integer(),
    'output_image', WriteDiskItem('2D Image', 'Aims image formats'),
    'output_image_1', WriteDiskItem('2D Image', 'Aims image formats'),
    'output_image_2', WriteDiskItem('2D Image', 'Aims image formats'),
    'output_image_3', WriteDiskItem('2D Image', 'Aims image formats'),
    'output_image_4', WriteDiskItem('2D Image', 'Aims image formats'),
)


def initialization(self):
    def linkside(self, proc):
        p = ReadDiskItem('Cortical folds graph', 'Graph and Data')
        x = p.findValue(self.right_graph, requiredAttributes={'side': 'left'})
        return x

    def linkImage0(self, proc):
        if self.right_graph is not None:
            subject = self.right_graph.get('subject')
            return os.path.join(neuroConfig.temporaryDirectory, 'snapshot4views_' + subject + '.png')
        else:
            return os.path.join(neuroConfig.temporaryDirectory, 'snapshot4views.png')

    def linkImage(self, proc, n):
        if self.output_image is not None:
            return self.output_image.fullName() + '_' + n \
                + self.output_image.fullPath()[len(self.output_image.fullName()):]
    self.setOptional('nomenclature')
    #self.setOptional( 'right_graph' )
    self.setOptional('right_hemi_mesh')
    self.setOptional('left_hemi_mesh')
    self.linkParameters('left_graph', 'right_graph', linkside)
    self.linkParameters('right_hemi_mesh', 'right_graph')
    self.linkParameters('left_hemi_mesh', 'left_graph')
    self.nomenclature = self.signature['nomenclature'].findValue({})
    self.view_quaternionR_V = '[0.870882, -0.0316726, -0.429869, -0.236165]'
    self.view_quaternionL_V = '[0.827185, 0.149874, 0.483291, -0.244405]'
    self.view_quaternionR_H = '[0.5, -0.5, -0.5, 0.5]'
    self.view_quaternionL_H = '[0.5, 0.5, 0.5, 0.5]'
    self.mesh_transparency = 1
    self.zoom_V = 1.2
    self.zoom_H = 1
    self.snapshot_size = 400
    self.linkParameters('output_image', 'right_graph', linkImage0)
    self.linkParameters('output_image_1', 'output_image',
                        lambda self, proc: linkImage(self, proc, '1'))
    self.linkParameters('output_image_2', 'output_image',
                        lambda self, proc: linkImage(self, proc, '2'))
    self.linkParameters('output_image_3', 'output_image',
                        lambda self, proc: linkImage(self, proc, '3'))
    self.linkParameters('output_image_4', 'output_image',
                        lambda self, proc: linkImage(self, proc, '4'))


def execution(self, context):

    subject = self.right_graph.get('subject')
    self.output = self.output_image.fullPath()
    context.write('Output file :', self.output)
    snapshot1 = self.output_image_1.fullPath()
    snapshot2 = self.output_image_2.fullPath()
    snapshot3 = self.output_image_3.fullPath()
    snapshot4 = self.output_image_4.fullPath()

    a = anatomist.Anatomist()

    # view an object in a 4 views block
    block = a.createWindowsBlock(2)  # 2 columns
    w1 = a.createWindow("3D", block=block, no_decoration=True)
    w2 = a.createWindow("3D", block=block, no_decoration=True)
    w3 = a.createWindow("3D", block=block, no_decoration=True)
    w4 = a.createWindow("3D", block=block, no_decoration=True)

    selfdestroy = []
    if self.nomenclature is not None:
        (hie, br) = context.runProcess('AnatomistShowNomenclature',
                                       read=self.nomenclature)
        selfdestroy += (hie, br)
    r = self.right_graph.get('automatically_labelled')
    l = self.left_graph.get('automatically_labelled')
    context.write('right automatically_labelled:', r)
    context.write('left automatically_labelled:', l)
    nomenclatureprop = 'default'
    if (r and r) and (l and l) == 'Yes':
        nomenclatureprop = 'label'
        #a.setGraphParams( label_attribute='label', use_nomenclature=1 )
    else:
        r = self.right_graph.get('manually_labelled')
        l = self.left_graph.get('manually_labelled')
        context.write('right manually_labelled:', r)
        context.write('left manually_labelled:', l)
        if (r and r) and (l and l) == 'Yes':
            nomenclatureprop = 'name'
            #a.setGraphParams( label_attribute='name', use_nomenclature=1 )
    right_graph = a.loadObject(self.right_graph)
    left_graph = a.loadObject(self.left_graph)
    context.write('nomenclature_property:', nomenclatureprop)
    a.execute('GraphDisplayProperties', objects=[right_graph],
              nomenclature_property=nomenclatureprop)
    a.execute('GraphDisplayProperties', objects=[left_graph],
              nomenclature_property=nomenclatureprop)
    selfdestroy.append(right_graph)
    selfdestroy.append(left_graph)

    # Apply built-in referential to right and left graphs
    right_graph.applyBuiltinReferential()
    left_graph.applyBuiltinReferential()

    cr = a.centralRef

    if self.right_hemi_mesh is not None:
        right_mesh = a.loadObject(self.right_hemi_mesh, duplicate=True)
        selfdestroy.append(right_mesh)
        right_mesh.setMaterial(a.Material(
            diffuse=[0.8, 0.8, 0.8, self.mesh_transparency]))
        # Apply built-in referential to right mesh
        right_mesh.applyBuiltinReferential()
    if self.left_hemi_mesh is not None:
        left_mesh = a.loadObject(self.left_hemi_mesh, duplicate=True)
        selfdestroy.append(left_mesh)
        left_mesh.setMaterial(a.Material(
            diffuse=[0.8, 0.8, 0.8, self.mesh_transparency]))
        # Apply built-in referential to left mesh
        left_mesh.applyBuiltinReferential()

    w1.assignReferential(cr)
    w2.assignReferential(cr)
    w3.assignReferential(cr)
    w4.assignReferential(cr)
    selfdestroy.append(w1)
    selfdestroy.append(w2)
    selfdestroy.append(w3)
    selfdestroy.append(w4)
    w1.addObjects([right_graph], add_graph_nodes=True)
    w2.addObjects([left_graph], add_graph_nodes=True)
    w3.addObjects([right_graph], add_graph_nodes=True)
    w4.addObjects([left_graph], add_graph_nodes=True)

    if self.right_hemi_mesh is not None:
        w1.addObjects([right_mesh])
        w3.addObjects([right_mesh])
    if self.left_hemi_mesh is not None:
        w2.addObjects([left_mesh])
        w4.addObjects([left_mesh])

    # hide toolbar/menu
    w1.showToolbox(0)
    w2.showToolbox(0)
    w3.showToolbox(0)
    w4.showToolbox(0)

    view_quaternionR_V = eval(self.view_quaternionR_V)
    view_quaternionL_V = eval(self.view_quaternionL_V)
    view_quaternionR_H = eval(self.view_quaternionR_H)
    view_quaternionL_H = eval(self.view_quaternionL_H)
    applied_zoomR_V = self.zoom_V
    applied_zoomL_V = applied_zoomR_V
    applied_zoomR_H = self.zoom_H
    applied_zoomL_H = applied_zoomR_H

    a.camera([w1], view_quaternion=view_quaternionR_V)  # Right hemisphere
    a.camera([w2], view_quaternion=view_quaternionL_V)  # Left hemisphere
    a.camera([w3], view_quaternion=view_quaternionR_H)  # Right hemisphere
    a.camera([w4], view_quaternion=view_quaternionL_H)  # Left hemisphere
    # Help about quaternions:
    # http://brainvisa.info/doc/anatomist/ana_training/en/html/ch08s03.html
    # http://fr.wikipedia.org/wiki/Quaternion
    # http://code.google.com/p/coloradocollegegame/wiki/Quaternions
    # Important:
    # view_quaternion=[w, x, y, z]
    # Values found with the help of command "getInfos":
    # quat=w1.getInfos()['view_quaternion']
    #'ObjectInfo'
    #{ 0 : { 'boundingbox_max' : [ 1, 1, 1 ],
    # 'boundingbox_min' : [ 0, 0, 0 ],
    # 'geometry' : [ 1248, 0, 424, 459 ],
    # 'group' : 0,
    # 'observer_position' : [ 0, 0, 0 ],
    # 'position' : [ 0, 0, 0, 0 ],
    # 'referential' : 1,
    # 'slice_quaternion' : [ 0, 0, 0, 1 ],
    # 'type' : 'AWindow',
    # 'view_quaternion' : [ 0.707107, 0, 0, 0.707107 ],
    # 'view_size' : [ 384, 384 ],
    # 'windowType' : '3D',
    # 'zoom' : 1 } }

    a.execute("WindowConfig", windows=[w1, w2, w3, w4], cursor_visibility=0)

    # making snapshots of the images
    # Problem with "raise" (recognized as a python command)
    # Solution: we pass all the parameters of "WindowConfig" as a dictionary

    # RIGHT HEMISPHERE
    # w1
    w_tempR = a.createWindow("3D", no_decoration=True, geometry=[
                             0, 0, self.snapshot_size, self.snapshot_size], allowreuse=False)  # [positionX, positionY, sizeX, sizeY]
    w_tempR.showToolbox(0)
    w_tempR.assignReferential(cr)
    w_tempR.addObjects([right_graph], add_graph_nodes=True)
    if self.right_hemi_mesh is not None:
        w_tempR.addObjects([right_mesh])
    a.camera([w_tempR], view_quaternion=view_quaternionR_V,
             zoom=applied_zoomR_V)  # Right hemisphere
    a.execute("WindowConfig", **
              {'windows': [w_tempR], 'cursor_visibility': 0, 'raise': 0, 'snapshot': snapshot1})
    my_objects = w_tempR.objects
    w_tempR.removeObjects(my_objects)
    #
    # w3
    w_tempR.addObjects([right_graph], add_graph_nodes=True)
    if self.right_hemi_mesh is not None:
        w_tempR.addObjects([right_mesh])
    a.camera([w_tempR], view_quaternion=view_quaternionR_H,
             zoom=applied_zoomR_H)  # Right hemisphere
    a.execute("WindowConfig", **
              {'windows': [w_tempR], 'cursor_visibility': 0, 'raise': 0, 'snapshot': snapshot3})
    #
    a.closeWindows(w_tempR)

    # LEFT HEMISPHERE
    # w2
    w_tempL = a.createWindow("3D", no_decoration=True, geometry=[
                             0, 0, self.snapshot_size, self.snapshot_size], allowreuse=False)  # [positionX, positionY, sizeX, sizeY]
    w_tempL.showToolbox(0)
    w_tempL.assignReferential(cr)
    w_tempL.addObjects([left_graph], add_graph_nodes=True)
    if self.left_hemi_mesh is not None:
        w_tempL.addObjects([left_mesh])
    a.camera([w_tempL], view_quaternion=view_quaternionL_V,
             zoom=applied_zoomL_V)  # Left hemisphere
    a.execute("WindowConfig", **
              {'windows': [w_tempL], 'cursor_visibility': 0, 'raise': 0, 'snapshot': snapshot2})
    my_objects = w_tempL.objects
    w_tempL.removeObjects(my_objects)
    #
    # w4
    w_tempL.addObjects([left_graph], add_graph_nodes=True)
    if self.left_hemi_mesh is not None:
        w_tempL.addObjects([left_mesh])
    a.camera([w_tempL], view_quaternion=view_quaternionL_H,
             zoom=applied_zoomL_H)  # Left hemisphere
    a.execute("WindowConfig", **
              {'windows': [w_tempL], 'cursor_visibility': 0, 'raise': 0, 'snapshot': snapshot4})
    #
    a.closeWindows(w_tempL)

    # Creation of the mosaic image
    time.sleep(1)  # wait 1 sec
    mosaic([snapshot1, snapshot3, snapshot2, snapshot4], self.output)

    self._dontdestroy = [block, w1, w2, w3, w4]

    return selfdestroy

########################################################################################


def create_cmd(images, size, sizes, bbox):
    nx, ny = size
    bbx, bby = bbox
    args = ''
    px = 0
    ind = 0
    for i in range(nx):
        py = 0
        for j in range(ny):
            sx, sy = sizes[ind]
            ox = (bbx - sx) / 2.
            oy = (bby - sy) / 2.
            args += "-page %dx%d+%d+%d %s " % \
                (sx, sy, px + ox, py + oy, images[ind])
            py += bby
            ind += 1
            if ind >= len(images):
                break
        px += bbx

    return args


def compute_bb(images):
    sizes = []
    bbx, bby = 0, 0
    for filename in images:
        img = Image.open(filename)
        sx, sy = img.size
        sizes.append((sx, sy))
        if sx > bbx:
            bbx = sx
        if sy > bby:
            bby = sy
        del img
    return sizes, (bbx, bby)


def shape_ratio(n, bb, ratio):
    bbx, bby = bb
    wratio = ratio * float(bby) / float(bbx)
    h = int(numpy.ceil(numpy.sqrt(float(n) / wratio) - 0.5))
    emin, hmin, wmin = numpy.inf, h, int(n / h)
    while 1:
        w = int(n / h)
        if w * h < n:
            w += 1
        e = (wratio - w / h) ** 2
        if e < emin:
            emin, hmin, wmin = e, h, w
        else:
            break
        h += 1
    w, h = wmin, hmin
    print("size = ", bbx * w, bby * h)
    print("ratio = ", float(bbx * w) / float(bby * h))
    return w, h


def mosaic(images, output):
    '''
    mosaic output images
    '''
    number = 1  # number of pages
    ratio = 1  # ratio of the size page (4./3, for example)

    # shape
    global_n = len(images)
    page_n = (global_n / number)
    if page_n * number < global_n:
        page_n += 1
    offset = 0
    for i, page in enumerate(range(number)):
        print("**** page ****")
        offset_high = min(global_n + 1, offset + page_n)
        page_images = images[offset:offset_high]
        print(page_images, offset, offset_high, page_n)
        sizes, bb = compute_bb(page_images)
        nx, ny = shape_ratio(offset_high - offset, bb, float(ratio))
        print("bb = ", bb)
        print("mosaic shape : ", (nx, ny))

        args = create_cmd(page_images, (nx, ny), sizes, bb)
        # plop.ext -> plop_N.ext
        if number != 1:
            ind = output.rfind('.')
            output = output[:ind] + ('_%d' % i) + output[ind:]
        cmd = "convert " + args + " -mosaic %s" % output
        print("cmd = ", cmd)
        os.system(cmd)
        offset += page_n
