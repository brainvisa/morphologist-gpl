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
import os, re

name = 'Brain volumes'
userLevel = 0

signature = Signature(
#  'left_grey_white', ReadDiskItem( 'Left Grey White Mask', 'GIS Image' ),
#  'right_grey_white', ReadDiskItem( 'Right Grey White Mask', 'GIS Image' ),
#  'left_csf', WriteDiskItem( 'Left CSF Mask', 'GIS Image' ),
#  'right_csf', WriteDiskItem( 'Right CSF Mask', 'GIS Image' ),
   'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
       'AIMS readable volume formats'),
   'LGW_interface', ReadDiskItem( 'Left Grey White Mask',
       'AIMS readable volume formats' ),
   'RGW_interface', ReadDiskItem( 'Right Grey White Mask',
       'AIMS readable volume formats' ),
   'LCSF_interface', WriteDiskItem( 'Left CSF Mask',
       'AIMS writable volume formats' ),
   'RCSF_interface', WriteDiskItem( 'Right CSF Mask',
       'AIMS writable volume formats' ),
   'split_mask', ReadDiskItem( 'Split brain mask',
      'AIMS readable volume formats' ),
   'subject_name', String(),
   'volumes', WriteDiskItem( 'Data Table', 'Text Data Table' ),
)

def initialization( self ):
  def linkSubject( self, proc ):
    if self.mri_corrected is not None:
      subject = self.mri_corrected.get('subject')
      return subject
  def linkvol( self, proc ):
    if self.subject_name is not None:
      return os.path.join( neuroConfig.temporaryDirectory,
        'volumes_' + self.subject_name + '.dat' )
    return None
  self.linkParameters( 'LGW_interface', 'mri_corrected' )
  self.linkParameters( 'RGW_interface', 'mri_corrected' )
  self.linkParameters( 'LCSF_interface', 'mri_corrected' )
  self.linkParameters( 'RCSF_interface', 'mri_corrected' )
  self.linkParameters( 'subject_name', 'mri_corrected', linkSubject )
  self.linkParameters( 'split_mask', 'mri_corrected' )
  self.linkParameters( 'volumes', 'subject_name', linkvol )
  self.setOptional( 'volumes', 'subject_name' )


def execution( self, context ):
    def massCenter( context, image ):
        # cmd = [ 'AimsMassCenter', image, '-b' ]
        # cmd = context._buildCommand( cmd ) # doesn't work for popen() on windows
        if type( image ) is types.StringType:
          cmd = 'AimsMassCenter "' + image + '" -b'
        else:
          cmd = 'AimsMassCenter "' + image.fullPath() + '" -b'
        f = os.popen( cmd )
        output = f.read()
        res = f.close()
        if res is not None and res != 0:
          raise RuntimeError ( 'failure in execution of command ' + cmd )
        r = re.compile( '^General:.*Vol: (.*)$', re.M )
        o = r.search( output )
        return float( o.group(1) )

    im1 = context.temporary( 'NIFTI-1 image' )
    lres = {}
    rres = {}
    white = im1.fullPath()

    subject = self.subject_name


    # white
    context.system( 'AimsThreshold', '-i', self.LGW_interface.fullPath(),
                    '-o', white, '-m', 'eq', '-t', '200' )
    lres[ 'white' ] = massCenter( context, white )
    context.write( 'Left hemisphere white matter volume: ',
                   lres[ 'white' ], '\n' )

    context.system( 'AimsThreshold', '-i', self.RGW_interface.fullPath(),
                    '-o', white, '-m', 'eq', '-t', '200' )
    rres[ 'white' ] = massCenter( context, white )
    context.write( 'Right hemisphere white matter volume: ',
                   rres[ 'white' ], '\n' )

    # grey
    grey = white
    context.system( 'AimsThreshold', '-i', self.LGW_interface.fullPath(),
                    '-o', grey, '-m', 'eq', '-t', '100' )
    lres[ 'grey' ] = massCenter( context, grey )
    context.write( 'Left hemisphere grey matter volume: ',
                   lres[ 'grey' ], '\n' )

    context.system( 'AimsThreshold', '-i', self.RGW_interface.fullPath(),
                    '-o', grey, '-m', 'eq', '-t', '100' )
    rres[ 'grey' ] = massCenter( context, grey )
    context.write( 'Right hemisphere grey matter volume: ', rres[ 'grey' ], '\n' )

    brain = grey 

    # csf

    if  os.path.exists(self.LCSF_interface.fullPath() )  and os.path.exists(self.RCSF_interface.fullPath() ) :    
        context.write('Left and right CSF masks already extracted \n')
    else:
        context.write('Extracting left and right CSF masks \n')
        context.runProcess('AnaComputeLCRClassif',
                           left_grey_white = self.LGW_interface,
                           right_grey_white = self.RGW_interface,
                           left_csf = self.LCSF_interface,
                           right_csf = self.RCSF_interface,
                           split_mask = self.split_mask)
    
    lres[ 'LCR' ] = massCenter( context, self.LCSF_interface )
    context.write( 'Left CSF volume: ', lres[ 'LCR' ], '\n' )
    
    rres[ 'LCR' ] = massCenter( context, self.RCSF_interface )
    context.write( 'Right CSF volume: ', rres[ 'LCR' ], '\n' )

    if self.volumes is not None:
        f = open( self.volumes.fullPath(), 'w' )
        res = { 'left' : lres, 'right' : rres }
        f.write( 'subject\tside\tmatter\tvolume\n' )
        rk = res.keys()
        rk.sort()
        for side in rk:
            sres = res[ side ]
            k = sres.keys()
            k.sort()
            for i in k:
                f.write( subject + '\t' + side + '\t' + i + '\t' + str( sres[i] ) + '\n' )
        f.close()

