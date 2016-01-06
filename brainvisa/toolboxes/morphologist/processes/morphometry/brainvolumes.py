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
from soma import aims
import os

name = 'Tissues Volumes'
userLevel = 1

signature = Signature(
    'split_brain', ReadDiskItem('Split brain mask',
                                'Aims readable volume formats' ),
    'left_grey_white', ReadDiskItem('Left Grey White Mask',
                                    'Aims readable volume formats'),
    'right_grey_white', ReadDiskItem('Right Grey White Mask',
                                    'Aims readable volume formats'),
    'left_csf', WriteDiskItem('Left CSF Mask',
                                'Aims writable volume formats'),
    'right_csf', WriteDiskItem('Right CSF Mask',
                                    'Aims writable volume formats'),
    'subject', String(),
    'tissues_volumes_file', WriteDiskItem('CSV file', 'CSV file'),
)


def initialization( self ):
    def linkSubject( self, proc ):
        if self.split_brain is not None:
            subject = self.split_brain.get('subject')
        return subject
    def linkvol( self, proc ):
        if self.subject is not None:
            return os.path.join('/neurospin/cati/Imagen/results/volumes/',
                                'tissues_volumes_' + self.subject + '.csv')
            #return os.path.join( neuroConfig.temporaryDirectory,
                #'volumes_' + self.subject + '.csv' )
        return None
    self.linkParameters( 'left_grey_white', 'split_brain' )
    self.linkParameters( 'right_grey_white', 'split_brain' )
    self.linkParameters( 'left_csf', 'split_brain' )
    self.linkParameters( 'right_csf', 'split_brain' )
    self.linkParameters( 'subject', 'split_brain', linkSubject )
    self.linkParameters( 'tissues_volumes_file', 'subject', linkvol )
    
    self.setOptional( 'tissues_volumes_file', 'subject' )


def execution( self, context ):
    #def massCenter( context, image ):
        ## cmd = [ 'AimsMassCenter', image, '-b' ]
        ## cmd = context._buildCommand( cmd ) # doesn't work for popen() on windows
        #if type( image ) is types.StringType:
          #cmd = 'AimsMassCenter "' + image + '" -b'
        #else:
          #cmd = 'AimsMassCenter "' + image.fullPath() + '" -b'
        #f = os.popen( cmd )
        #output = f.read()
        #res = f.close()
        #if res is not None and res != 0:
          #raise RuntimeError ( 'failure in execution of command ' + cmd )
        #r = re.compile( '^General:.*Vol: (.*)$', re.M )
        #o = r.search( output )
        #return float( o.group(1) )

    #im1 = context.temporary( 'NIFTI-1 image' )
    #lres = {}
    #rres = {}
    #white = im1.fullPath()

    #subject = self.subject


    ## white
    #context.system( 'AimsThreshold', '-i', self.LGW_interface.fullPath(),
                    #'-o', white, '-m', 'eq', '-t', '200' )
    #lres[ 'white' ] = massCenter( context, white )
    #context.write( 'Left hemisphere white matter volume: ',
                   #lres[ 'white' ], '\n' )

    #context.system( 'AimsThreshold', '-i', self.RGW_interface.fullPath(),
                    #'-o', white, '-m', 'eq', '-t', '200' )
    #rres[ 'white' ] = massCenter( context, white )
    #context.write( 'Right hemisphere white matter volume: ',
                   #rres[ 'white' ], '\n' )

    ## grey
    #grey = white
    #context.system( 'AimsThreshold', '-i', self.LGW_interface.fullPath(),
                    #'-o', grey, '-m', 'eq', '-t', '100' )
    #lres[ 'grey' ] = massCenter( context, grey )
    #context.write( 'Left hemisphere grey matter volume: ',
                   #lres[ 'grey' ], '\n' )

    #context.system( 'AimsThreshold', '-i', self.RGW_interface.fullPath(),
                    #'-o', grey, '-m', 'eq', '-t', '100' )
    #rres[ 'grey' ] = massCenter( context, grey )
    #context.write( 'Right hemisphere grey matter volume: ', rres[ 'grey' ], '\n' )

    #brain = grey 

    #Fermeture morphologisque du cerveau pour optenir le volume de csf contenu dans le creu des sillons et ainsi calculer un TIV (ICV) approximatif.
    brain_closed = context.temporary('NIFTI-1 Image')
    #brain_closed = '/tmp/brain_closed.nii'
    #brain_closed = '/tmp/brain_closed_' + self.subject + '.nii'
    context.system('AimsThreshold',
                   '-i', self.split_brain.fullPath(),
                   '-o', brain_closed,
                   '-m', 'di', '-t', '0', '-b')
    context.system('AimsMorphoMath',
                   '-i', brain_closed,
                   '-o', brain_closed,
                   '-m', 'clo', '-r', '20')
    #On s'assure qu'il n'y a pas de trou surtout au niveau des ventricules.
    context.system('AimsThreshold',
                   '-i', brain_closed,
                   '-o', brain_closed,
                   '-m', 'eq', '-t', '0', '-b')
    context.system('AimsConnectComp',
                   '-i', brain_closed,
                   '-o', brain_closed,
                   '-c', '6', '-n', '1', '-b')
    context.system('AimsThreshold',
                   '-i', brain_closed,
                   '-o', brain_closed,
                   '-m', 'eq', '-t', '0', '-b')

    context.write('Extracting left and right CSF inside sulci.\n')
    context.runProcess('AnaComputeLCRClassif',
                       left_grey_white=self.left_grey_white,
                       right_grey_white=self.right_grey_white,
                       left_csf=self.left_csf,
                       right_csf=self.right_csf,
                       split_mask=self.split_brain)

    #lres[ 'LCR' ] = massCenter( context, self.LCSF_interface )
    #context.write( 'Left CSF volume: ', lres[ 'LCR' ], '\n' )
    
    #rres[ 'LCR' ] = massCenter( context, self.RCSF_interface )
    #context.write( 'Right CSF volume: ', rres[ 'LCR' ], '\n' )
    
    #Calcul des volumes des tissues
    if os.path.exists(self.split_brain.fullPath()) and \
    os.path.exists(self.left_grey_white.fullPath()) and \
    os.path.exists(self.right_grey_white.fullPath()) and \
    os.path.exists(self.left_csf.fullPath()) and \
    os.path.exists(self.right_csf.fullPath()):
        split_img = aims.read(self.split_brain.fullPath())
        lgw_img = aims.read(self.left_grey_white.fullPath())
        rgw_img = aims.read(self.right_grey_white.fullPath())
        lcsf_img = aims.read(self.left_csf.fullPath())
        rcsf_img = aims.read(self.right_csf.fullPath())
        eTIV_img = aims.read(brain_closed.fullPath())
        
        vox_sizes = split_img.header()['voxel_size']
        vox_vol = vox_sizes[0]*vox_sizes[1]*vox_sizes[2]
        
        split_arr = split_img.arraydata()
        lgw_arr = lgw_img.arraydata()
        rgw_arr = rgw_img.arraydata()
        lcsf_arr = lcsf_img.arraydata()
        rcsf_arr = rcsf_img.arraydata()
        eTIV_arr = eTIV_img.arraydata()
        
        #Classify
        lgm_vox = (lgw_arr == 100)
        lwm_vox = (lgw_arr == 200)
        rgm_vox = (rgw_arr == 100)
        rwm_vox = (rgw_arr == 200)
        lcsf_vox = (lcsf_arr == 32767)
        rcsf_vox = (rcsf_arr == 32767)
        cerebellum_vox = (split_arr == 3)
        
        rh_vox = rgm_vox + rwm_vox
        lh_vox = lgm_vox + lwm_vox
        rh_closed_vox = rh_vox + rcsf_vox
        lh_closed_vox = lh_vox + lcsf_vox
        hemi_closed_vox = rh_closed_vox + lh_closed_vox
        
        brain_vox = (split_arr == 1) | (split_arr == 2) | (split_arr == 3)
        eTIV_vox = (eTIV_arr == 32767)
        
        #Calculation of the volumes
        lgm_vol = lgm_vox.sum()*vox_vol/1000.
        lwm_vol = lwm_vox.sum()*vox_vol/1000.
        rgm_vol = rgm_vox.sum()*vox_vol/1000.
        rwm_vol = rwm_vox.sum()*vox_vol/1000.
        rh_vol = rh_vox.sum()*vox_vol/1000.
        lh_vol = lh_vox.sum()*vox_vol/1000.
        cerebellum_vol = cerebellum_vox.sum()*vox_vol/1000.
        brain_vol = brain_vox.sum()*vox_vol/1000.
        rh_closed_vol = rh_closed_vox.sum()*vox_vol/1000.
        lh_closed_vol = lh_closed_vox.sum()*vox_vol/1000.
        hemi_closed_vol = hemi_closed_vox.sum()*vox_vol/1000.
        eTIV = eTIV_vox.sum()*vox_vol/1000.
    else:
        lgm_vol = 0.
        lwm_vol = 0.
        rgm_vol = 0.
        rwm_vol = 0.
        rh_vol = 0.
        lh_vol = 0.
        cerebellum_vol = 0.
        brain_vol = 0.
        rh_closed_vol = 0.
        lh_closed_vol = 0.
        hemi_closed_vol = 0.
        eTIV = 0.

    if self.tissues_volumes_file is not None:
        f = open(self.tissues_volumes_file.fullPath(), 'w')
        #res = { 'left' : lres, 'right' : rres }
        f.write('subject;left_wm;right_wm;left_gm;right_gm;lh;rh;brain;hemi_closed;eTIV\n' )
        f.write(self.subject+';'+str(round(lwm_vol,3))+';'+
                str(round(rwm_vol,3))+';'+str(round(lgm_vol,3))+';'+
                str(round(rgm_vol,3))+';'+str(round(lh_vol,3))+';'+
                str(round(rh_vol,3))+';'+str(round(brain_vol,3))+';'+
                str(round(hemi_closed_vol))+';'+str(round(eTIV,3)))
        #rk = res.keys()
        #rk.sort()
        #for side in rk:
            #sres = res[ side ]
            #k = sres.keys()
            #k.sort()
            #for i in k:
                #f.write( subject + '\t' + side + '\t' + i + '\t' + str( sres[i] ) + '\n' )
        f.close()
    

