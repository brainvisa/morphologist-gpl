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


from brainvisa.processes import *
from brainvisa.data.qtgui import neuroDataGUI
from brainvisa import registration
from brainvisa import anatomist


class TalairachPointEditor(neuroDataGUI.PointEditor):
    # define necesssary functions, and especially:
    def selectPressed(self):
        a = anatomist.Anatomist()
        tm = registration.getTransformationManager()

        if self.parameter._Link is not None:
            linked = self.parameter._Link
            self.anatomistObject = a.loadObject(linked)
            w = self.anatomistObject.getWindows()
            if not w:
                self.anatomistView = a.viewObject(linked)
            position = a.linkCursorLastClickedPosition(
                registration.talairachACPCReferentialId)
        else:
            position = a.linkCursorLastClickedPosition()

        if position is None:
            position = [0 for i in xrange(self.parameter.dimension)]

        self.setValue(position)
        self.checkValue()  # to force link mechanism to run


class TalairachPoint3D(Point3D):
    def editor(self, parent, name, context):
        return TalairachPointEditor(self, parent, name)


name = 'Localize Talairach Coordinate'
userLevel = 0

signature = Signature(
    't1mri', ReadDiskItem("Raw T1 MRI", 'aims readable Volume Formats'),
    'talairach_transform', ReadDiskItem('Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
                                        'Transformation matrix'),
    #'hemi_mesh', ReadDiskItem('Hemisphere Mesh', 'MESH mesh' ),
    'localised', WriteDiskItem('3D Volume', 'aims Writable Volume Formats'),
    'point', TalairachPoint3D()
)


def initialization(self):
    self.linkParameters('talairach_transform', 't1mri')
    #self.linkParameters( 'hemi_mesh', 't1mri' )
#  self.signature[ 'point' ].add3DLink( self, 'mesh' )
    self.signature['point'].add3DLink(self, 't1mri')


def execution(self, context):
    from soma import aims
    from soma import aimsalgo

    trans = aims.read(self.talairach_transform.fullPath()
                      )  # read a Motion object
    transInv = trans.inverse()
    coords = transInv.transform(self.point)

    reader = aims.Reader()
    reader.mapType('Volume', 'AimsData')
    data = reader.read(self.t1mri.fullPath())
    dx = data.dimX()
    dy = data.dimY()
    dz = data.dimZ()
    sx = data.sizeX()
    sy = data.sizeY()
    sz = data.sizeZ()

    ima = aims.AimsData_FLOAT(dx, dy, dz, 1)
    ima.setSizeX(sx)
    ima.setSizeY(sy)
    ima.setSizeZ(sz)
    # ima=data.clone()

    context.write('Talairach : ', self.point)
    context.write('Voxel : (', int(
        coords[0]/sx), ',', int(coords[1]/sy), ',', int(coords[2]/sz), ')')

    context.write('Creating functional image of size', dx, 'x', dy, 'x', dz)
    # for z in xrange( dz ):
    # for y in xrange( dy ):
    # for x in xrange( dx ):
    #ima.setValue( 0, x, y, z )
    ima.fill(0.0)
    ima.setValue(100, int(coords[0]/sx), int(coords[1]/sy), int(coords[2]/sz))
    context.write('Smoothing it')
    smooth = aimsalgo.Gaussian3DSmoothing_FLOAT(10.0, 10.0, 10.0)
    func = smooth.doit(ima)

    func.header().update(data.header())

    context.write('Writing it')
    writer = aims.Writer()
    writer.write(func, self.localised.fullPath())
    context.write('OK')
