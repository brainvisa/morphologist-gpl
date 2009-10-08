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

from neuroProcesses import *
import shfjGlobals

name = 'Read and complete AC-PC files'
userLevel = 2

signature = Signature(
    'Commissure_coordinates',
    ReadDiskItem( 'Commissure coordinates','Commissure coordinates'),
    'T1mri', ReadDiskItem( "Raw T1 MRI", shfjGlobals.vipVolumeFormats ), 
)


def initialization( self ):
    self.linkParameters( 'T1mri', 'Commissure_coordinates' )
    self.setOptional( 'T1mri' )


def execution( self, context ):
    f = open( self.Commissure_coordinates.fullPath() )
    lines = f.readlines()
    f.close()
    ac = []
    pc = []
    ip = []
    acm = []
    pcm = []
    ipm = []
    la = None
    lp = None
    li = None
    for l in lines:
        if l[:3] == 'AC:':
            ac = map( lambda x: int(x), l.split()[1:4] )
        elif l[:3] == 'PC:':
            pc = map( lambda x: int(x), l.split()[1:4] )
        elif l[:3] == 'IH:':
            ip = map( lambda x: int(x), l.split()[1:4] )
        elif l[:5] == 'ACmm:':
            acm = map( lambda x: float(x), l.split()[1:4] )
            la = l
        elif l[:5] == 'PCmm:':
            pcm = map( lambda x: float(x), l.split()[1:4] )
            lp = l
        elif l[:5] == 'IHmm:':
            ipm = map( lambda x: float(x), l.split()[1:4] )
            li = l

    if len( acm ) == 3 and len( pcm ) == 3 and len( ipm ) == 3:
        return ( acm, pcm, ipm )
    if self.T1mri is None:
        raise 'AC/PC positions in mm are not recorded. You must specify a ' \
              'T1 MRI for voxel sizes'

    vs = shfjGlobals.aimsVolumeAttributes( self.T1mri )[ 'voxel_size' ]
    wa = 0
    wp = 0
    wi = 0
    if len( acm ) != 3:
        acm = [ ac[0] * vs[0], ac[1] * vs[1], ac[2] * vs[2] ]
        wa = 1
    if len( pcm ) != 3:
        pcm = [ pc[0] * vs[0], pc[1] * vs[1], pc[2] * vs[2] ]
        wp = 1
    if len( ipm ) != 3:
        ipm = [ ip[0] * vs[0], ip[1] * vs[1], ip[2] * vs[2] ]
        wi = 1
    try:
        f = open( self.Commissure_coordinates.fullPath(), 'w' )
        for l in lines:
            if l == la and wa:
                f.write( 'ACmm: ' + \
                         string.join( map( lambda x:str(x), acm ) ) + '\n' )
                wa = 0
            elif l == lp and wp:
                f.write( 'PCmm: ' + \
                         string.join( map( lambda x:str(x), pcm ) ) + '\n' )
                wp = 0
            elif l == li and wi:
                f.write( 'IHmm: ' + \
                         string.join( map( lambda x:str(x), ipm ) ) + '\n' )
                wi = 0
            else:
                f.write( l )
        if wa:
            f.write( '# The previous coordinates, used by the system, are ' \
                     'defined in voxels\n' )
            f.write( '# They stem from the following coordinates in ' \
                     'millimeters:\n' )
            f.write( 'ACmm: ' + \
                     string.join( map( lambda x:str(x), acm ) ) + '\n' )
        if wp:
            f.write( 'PCmm: ' + \
                     string.join( map( lambda x:str(x), pcm ) ) + '\n' )
        if wi:
            f.write( 'IHmm: ' + \
                     string.join( map( lambda x:str(x), ipm ) ) + '\n' )
        f.close()
    except:
        # could not write modifications
        pass

    return ( acm, pcm, ipm )
