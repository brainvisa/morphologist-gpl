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
from brainvisa.tools import aimsGlobals
import registration

name = 'Segmentation of Corpus Callosum'
userLevel = 2

signature = Signature(
    'left_grey_white', ReadDiskItem("Left Grey White Mask",
        'aims readable volume formats'),
    'right_grey_white', ReadDiskItem("Right Grey White Mask",
        'aims readable volume formats'),
    'corpus_callosum_mask', WriteDiskItem('Corpus Callosum mask',
        'aims writable volume formats'),
    'talairach_transformation', ReadDiskItem( \
        'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
        'Transformation matrix'),
)

def initialization(self):
    self.linkParameters('right_grey_white', 'left_grey_white')
    self.linkParameters('corpus_callosum_mask', 'left_grey_white')
    self.linkParameters('talairach_transformation', 'left_grey_white')
    self.setOptional('talairach_transformation')

def execution(self, context):
    minradius = 15
    maxradius = 50
    minradius *= minradius # square
    maxradius *= maxradius
    tmp1 = context.temporary('NIFTI-1 image')
    # merge both hemispheres segmentations
    context.pythonSystem('cartoLinearComb.py', '-o', tmp1, '-f', 'I1+I2',
                         '-i', self.left_grey_white,
                         '-i', self.right_grey_white)
    # keep white mask
    white = context.temporary('NIFTI-1 image')
    context.system('AimsThreshold', '-i', tmp1, '-o', white, '-t', 200,
                   '-m', 'ge')
    # keep grey mask
    grey = context.temporary('NIFTI-1 image')
    context.system('AimsThreshold', '-i', tmp1, '-o', grey, '-t', 100,
                   '-m', 'eq')
    # close white mask
    context.system('AimsMorphoMath', '-m', 'clo', '-i', white, '-o', tmp1,
                   '-r', 3 )
    #context.system('AimsMorphoMath', '-m', 'clo', '-i', white,
                   #'-o', '/tmp/closed.nii', '-r', 3 ) # FIXME: debug

    # get GM neighbouring in both hemispheres (interhemi cortex)
    tmp2 = context.temporary('NIFTI-1 image')
    tmp3 = context.temporary('NIFTI-1 image')
    context.system('AimsThreshold', '-i', self.left_grey_white,
                   '-o', tmp2, '-t', 100, '-m', 'eq')
    context.system('AimsThreshold', '-i', self.right_grey_white,
                   '-o', tmp3, '-t', 100, '-m', 'eq')
    tmp4 = context.temporary('NIFTI-1 image')
    tmp5 = context.temporary('NIFTI-1 image')
    context.system('AimsMorphoMath', '-m', 'dil', '-i', tmp2, '-o', tmp4,
                   '-r', 2)
    del tmp2
    context.system('AimsMorphoMath', '-m', 'dil', '-i', tmp3, '-o', tmp5,
                   '-r', 2 )
    del tmp3
    ihc = context.temporary('NIFTI-1 image')
    context.system('AimsMask', '-i', tmp4, '-m', tmp5, '-o', ihc)

    # mask dilated white with interhemi cortex
    context.system('AimsMask', '-i', tmp1, '-m', ihc, '-o', tmp4)
    #context.system('AimsMask', '-i', tmp1, '-m', ihc, '-o', '/tmp/mask.nii') # FIXME: debug
    #context.system( 'AimsConnectComp', '-i', tmp4, '-o', tmp5, '-n', 1, '-c',
        #18 )
    del tmp5

    use_talairach = (self.talairach_transformation is not None)
    if use_talairach:
        try:
            from soma import aims, aimsalgo
            import numpy
        except:
            context.write('pyaims not available - not using Talairach info')
            use_talairach = False
    if not use_talairach:
        # no Talairach info
        # close / dilate segmentation
        dilation_size_before_connected_component = 3
        dilmask = context.temporary('NIFTI-1 image')
        context.system('AimsMorphoMath', '-m', 'dil', '-i', tmp4,
                       '-o', dilmask,
                       '-r', dilation_size_before_connected_component)

        # keep biggest connected component
        context.system('AimsConnectComp', '-i', dilmask,
                       '-o', tmp4, '-c', 18, '-n', 1)
        # erode back a little bit (trying to avoid disconnecting the
        # segmentation)
        context.system('AimsMorphoMath', '-m', 'clo', '-i', tmp4, '-o', tmp1,
                       '-r', 2 )
        context.system('AimsErosion', '-m', 'ero', '-i', tmp1,
                       '-o', self.corpus_callosum_mask,
                       '-r', dilation_size_before_connected_component - 2)
    else:
        # use Talairach info
        # keep all connected components, then filter them out
        context.system('AimsConnectComp', '-i', tmp4, '-o', tmp4,
                       '-c', 18, '-s', 50)
        vol = aims.read(tmp4.fullPath())
        tal = aims.read(self.talairach_transformation.fullPath())
        dvol = aims.AimsData( vol ) # still a bug in ref counting
        ar = numpy.asarray(vol)
        roiit = aims.getRoiIterator(dvol)
        todel = []
        comps = []
        #cent = tal.inverse().transform( aims.Point3df( 0, 10, 0 ) )
        cent = aims.Point3df(0, 10, 0)
        while roiit.isValid():
            mit = roiit.maskIterator()
            p = aims.Point3df(0, 0, 0)
            n = 0
            out = 0
            comp = int(roiit.regionName())
            while mit.isValid():
                q = tal.transform(mit.valueMillimeters())
                p += q
                r = (q - cent).norm2()
                if r < minradius or r > maxradius:
                    out += 1
                n += 1
                mit.next()
            p /= n
            #context.write( roiit.regionName(), p, ', out:', out, '/', n )
            if p[2] >= -5 or p[2] <= -40 or p[1] <= -40 or p[1] >= 55 \
                or out > 0.15 * n:
                todel.append(comp)
            else:
                comps.append(comp)
            roiit.next()
        #context.write( 'del:', todel )
        for v in todel:
            ar[ar == v] = 0
        #context.write( 'comps:', comps )
        # distance between connected components
        #fm = aims.FastMarching( '26', True )
        #dist = fm.doit( vol, [ 0 ], comps )
        #lab = fm.midInterfaceLabels()
        #context.write( 'lab:', lab )
        #merge = numpy.zeros( ( max( comps ) + 1, ) )
        #for i, j in lab:
            #mid = fm.midInterfaceVol( i, j )
            #ma = numpy.array( mid, copy=False )
            #ma[ ma == -1 ] = 1e38
            #md = numpy.min( ma )
            #context.write( 'dist', i, j, ':', md )
            #if md < 10:
                #context.write( 'merge', i, j )
                #if merge[j] != 0:
                    #k = j
                    #j = i
                    #i = k
                #merge[j] = i
                #if merge[i] != 0:
                    #context.write( '-  ->', merge[i] )
                    #merge[j] = merge[j]
        #context.write( 'to merge', merge )
        #modif = True
        #while modif:
            #modif = False
            #for i in xrange( merge.shape[0] ):
                #if merge[i] > 0 and merge[merge[i]] > 0:
                    #merge[i] = merge[merge[i]]
                    #modif = True
        #for i in range( merge.shape[0] ):
          #if merge[i] != 0:
            #ar[ ar == i ] = merge[i]
            #comps.remove( i )
        #context.write( 'remaining comps:', comps )
        ## keep only biggest label
        #imax = -1
        #vmax = 0
        #for i in comps:
            #m = numpy.where( ar == i )[0].shape[0]
            #if m > vmax:
                #vmax = m
                #imax = i
        #context.write( 'keep component:', imax, ', size:', vmax )
        #ar[ ar != imax ] = 0
        aims.write( vol, tmp4.fullPath() )
        # close a little bit
        context.system('AimsMorphoMath', '-m', 'clo', '-i', tmp4,
                       '-o', self.corpus_callosum_mask, '-r', 2)

    tm = registration.getTransformationManager()
    tm.copyReferential(self.left_grey_white, self.corpus_callosum_mask)


