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
from brainvisa import anatomist

name = 'Anatomist show Commissure coordinates'
roles = ('viewer',)
userLevel = 0

def validation():
    anatomist.validation()

signature = Signature(
    'commissure_coordinates', ReadDiskItem('Commissure coordinates', 
                                           'Commissure coordinates'),
    'show_t1mri', Boolean(), 
    't1mri', ReadDiskItem('Raw T1 MRI', 'Anatomist volume formats', 
                          exactType = True),
    'anatomist_window', anatomist.AWindowChoice(), 
)

def initialization(self):
    self.linkParameters('t1mri' , 'commissure_coordinates')
    self.setOptional('t1mri')
    self.anatomist_window = '<'+_t_('New window (Sagittal)')+'>'

def execution(self, context):
    # read APC file
    acpos, pcpos, ippos = context.runProcess('readAPC',
                                             self.commissure_coordinates,
                                             self.t1mri)
    context.write('AC:', acpos)
    context.write('PC:', pcpos)
    context.write('IP:', ippos)

    context.write('<p>Color code:</p>' \
                  '<table cellspacing="0"><tr bgcolor="#0000ff"><td>' \
                  '<font color="#ffffff">Blue cross is AC: ', acpos,
                  '</font></td></tr>' \
                  '<tr bgcolor="#ffff00"><td>Yellow cross is PC: ', pcpos,
                  '</td></tr>' \
                  '<tr bgcolor="#00ff00"><td>Green cross is IH: ', ippos,
                  '</td></tr></table>')
    # the list selfdestroy will contain all objects that must be stored until the process window is closed. Then these objects will be deleted. 
    selfdestroy = []
    a = anatomist.Anatomist()
    vs = None
    mri = None
    ref = None
    if self.t1mri is not None:
        if self.show_t1mri:
            mri = a.loadObject(self.t1mri)
            selfdestroy.append(mri)
            ref = mri.referential

    sphere = ReadDiskItem('Mesh', 'Aims mesh formats').findValue( \
        {'category': 'standardmeshes', 'filename_variable': 'cross'},
        requiredAttributes = {'category': 'standardmeshes',
                             'filename_variable': 'cross'})
    if sphere:
        sfile = sphere.fullPath()
    else:
        context.write('No pre-built sphere mesh found. Building one...')
        cp = context.temporary('Config file')
        f = open(cp.fullPath(), 'w')
        print >> f, 'attributes = {'
        print >> f, "  'type' : 'cylinder',"
        print >> f, "  'point1' : [ -50, 0, 0 ],"
        print >> f, "  'point2' : [ 50, 0, 0 ],"
        print >> f, "  'radius' : 0.5,"
        print >> f, "  'closed' : 1,"
        print >> f, "  'facets' : 4,"
        print >> f, "  'smooth' : 1,"
        print >> f, "}"
        f.close()
        cf = context.temporary('Mesh mesh')
        context.system('AimsMeshGenerate', '-i', cp.fullPath(), '-o',
                        cf.fullPath())

        f = open(cp.fullPath(), 'w')
        print >> f, 'attributes = {'
        print >> f, "  'type' : 'cylinder',"
        print >> f, "  'point1' : [ 0, -50, 0 ],"
        print >> f, "  'point2' : [ 0, 50, 0 ],"
        print >> f, "  'radius' : 0.5,"
        print >> f, "  'closed' : 1,"
        print >> f, "  'facets' : 4,"
        print >> f, "  'smooth' : 1,"
        print >> f, "}"
        f.close()
        cf2 = context.temporary('Mesh mesh')
        context.system('AimsMeshGenerate', '-i', cp.fullPath(), '-o',
                       cf2.fullPath())

        f = open(cp.fullPath(), 'w')
        print >> f, 'attributes = {'
        print >> f, "  'type' : 'cylinder',"
        print >> f, "  'point1' : [ 0, 0, -50 ],"
        print >> f, "  'point2' : [ 0, 0, 50 ],"
        print >> f, "  'radius' : 0.5,"
        print >> f, "  'closed' : 1,"
        print >> f, "  'facets' : 4,"
        print >> f, "  'smooth' : 1,"
        print >> f, "}"
        f.close()
        cf3 = context.temporary('Mesh mesh')
        context.system('AimsMeshGenerate', '-i', cp.fullPath(), '-o',
                       cf3.fullPath())

        context.system('AimsZCat', '-o', cf.fullPath(), '-i', cf.fullPath(),
                       '-i', cf2.fullPath(), '-i', cf3.fullPath())
        del cf2, cf3

        sfile = cf.fullPath()

    if ref is None:
        ref = a.centralRef
    # the object must be loaded even if it is already loaded in Anatomist. Associated referential will not be loaded event if there is one.
    ac = a.loadObject( sfile, forceReload = True, loadReferential = False )
    ac.setMaterial( a.Material(diffuse = ( 0, 0, 1, 1 )) )
    selfdestroy.append( ac )
    ra = a.createReferential()
    ac.assignReferential(ra)
    ta = a.createTransformation( acpos + [ 1, 0, 0,
                                           0, 1, 0,
                                           0, 0, 1 ], 
                                 ra, ref )

    pc = a.loadObject( sfile, forceReload = True, loadReferential = False )
    pc.setMaterial( a.Material(diffuse = ( 1, 1, 0, 1 )) )
    selfdestroy.append( pc )
    
    rp = a.createReferential()
    pc.assignReferential(rp)
    tp = a.createTransformation( pcpos + [ 1, 0, 0,
                                           0, 1, 0,
                                           0, 0, 1 ], 
                                 rp, ref )

    ip = a.loadObject( sfile, forceReload = True, loadReferential = False )
    ip.setMaterial( a.Material(diffuse = ( 0, 1, 0, 1 )) )
    selfdestroy.append( ip )
    
    ri = a.createReferential()
    ip.assignReferential(ri)
    ti = a.createTransformation( ippos + [ 1, 0, 0,
                                           0, 1, 0,
                                           0, 0, 1 ], 
                                 ri, ref )
    w = self.anatomist_window() # return a window corresponding to the user choice : a new window or an existing window
    w.assignReferential(ref)
    selfdestroy.append( w )
    selfdestroy += [ ta, tp, ti ]

    if mri is not None:
        w.addObjects( [mri] )
    w.addObjects( [ ac, pc, ip ] )
    
    w.moveLinkedCursor( acpos )
    #  set cursor to AC
    #if ref == a.centralRef:
        ## no transformation to Talairach
        #w.moveLinkedCursor( acpos )
    #else:
        ## there is a transformation to Talairach space
        ## in Tal. space, (0,0,0) is AC
        #w.moveLinkedCursor( [ 0, 0, 0 ] )
    a.sync()
    #a.getInfo()

    return selfdestroy
