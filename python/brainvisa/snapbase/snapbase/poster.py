# -*- coding: utf-8 -*-

import PIL.Image
import sys

def create_poster( images, output_image, tile=10, padding=0, bgcolor=(0,0,0) ):
    # print 'calculating poster size...'
    rowsizes = []
    n = 0
    for imagename in images:
        image = PIL.Image.open( imagename )
        if n % tile == 0:
            rowsizes.append( ( 0, 0 ) )
        rowsizes[-1] = ( rowsizes[-1][0] + image.size[0] + padding,
            max( rowsizes[-1][1], image.size[1] + padding ) )
        n += 1
    # print 'sizes:', rowsizes
    size = ( max( [ rs[0] for rs in rowsizes ] ) - padding,
        sum( [ rs[1] for rs in rowsizes ] ) - padding )
    # print 'size:', size
    outimage = PIL.Image.new( 'RGB', size, bgcolor )
    # print 'creating image...'
    n = 0
    line = 0
    xpos = 0
    rowsizes.insert( 0, ( 0, 0 ) )
    for imagename in images:
        image = PIL.Image.open( imagename )
        y = rowsizes[line][1] + ( rowsizes[line+1][1] - image.size[1] ) / 2
        bbox = ( xpos, y, xpos+image.size[0], y + image.size[1] )
        outimage.paste( image, bbox )
        xpos = bbox[2] + padding
        n += 1
        if n == tile:
            n = 0
            line += 1
            xpos = 0
    outimage.save( open( output_image, 'w' ) )
    # print 'done.'

if __name__ == '__main__':
    create_poster( sys.argv[1:-1], sys.argv[-1] )
