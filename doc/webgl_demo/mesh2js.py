#!/usr/bin/env python

from __future__ import print_function
import sys
import numpy as np
from soma import aims


def meshlist2js(meshlist, jsname):
    fd = open(jsname, 'w')

    fd.write("function load_objects() {\n")
    fd.write("\n")
    fd.write("var objects = [];\n")
    fd.write("var o;\n\n")
    fd.write("var modelMatrix = mat4.identity();\n")
    fd.write("var modelMatrixIT = mat4.identity();\n")

    # for all meshes
    vertices = []
    for meshname in meshlist:
        fd.write("//*** %s\n\n" % meshname)
        mesh2js(meshname, fd, vertices)
    X = np.vstack(vertices)
    print(X.shape)
    del vertices

    # compute mean dispersion
    mean = X.mean(axis=0)
    X -= mean
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    std = np.sqrt(np.prod(S) ** (1./3))
    s = 1 / (2 * std) # scaling set to 2 standard deviation
    del X

    fd.write("t = vec3.create([%f, %f, %f])\n" % tuple(-mean))
    fd.write("s = vec3.create([%f, %f, %f])\n" % (s, s, s))
    fd.write("m = mat4.identity();\n")
    fd.write("mat4.translate(m, t, m);\n")
    fd.write("mat4.scale(m, s, m);\n")

    fd.write("mat4.set(m, modelMatrix);\n")
    fd.write("mIT = mat4.inverse(mat4.transpose(modelMatrix));\n")
    fd.write("mat4.set(mIT, modelMatrixIT);\n")
    fd.write("\n")


    fd.write("return objects;\n")
    fd.write("}\n")
    fd.close()



def mesh2js(meshname, fd, vertices):
    '''
    convert .mesh file to a javascript file ready to be read by
    a webgl script.
    '''
    m = aims.read(meshname)
    vertices.append(np.array(m.vertex(), copy=True))
    try:
        minf = aims.read(meshname + '.minf')
    except:
        ambient = (0.1, 0.1, 0.1, 1.)
        diffuse = (0.8, 0.8, 0.8, 1.)
        emission = (0., 0., 0., 1.)
        specular = (0.2, 0.2, 0.2, 1.)
    else:
        ambient = tuple(minf['material']['ambient'])
        diffuse = tuple(minf['material']['diffuse'])
        emission = tuple(minf['material']['emission'])
        specular = tuple(minf['material']['specular'])

    # vertices
    fd.write("// vertices\n")
    fd.write("var vbo = gl.createBuffer();\n")
    fd.write("gl.bindBuffer(gl.ARRAY_BUFFER, vbo);\n")
    fd.write("var vertices = new Float32Array([\n")
    for v in m.vertex(): fd.write("\t\t%f, %f, %f,\n" % (v[0], v[1], v[2]))
    fd.write("])\n")
    fd.write("gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);\n")
    fd.write("vbo.size = vertices.length / 3.0;\n")
    fd.write("\n")

    # indices
    fd.write("var ibo = gl.createBuffer();\n")
    fd.write("gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ibo);\n")
    fd.write("var indices = new Uint16Array([\n")
    for p in m.polygon(): fd.write("\t\t%d, %d, %d,\n" % (p[0], p[1], p[2]))
    fd.write("]);\n")
    fd.write("gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, " + \
        "indices, gl.STATIC_DRAW);\n")
    fd.write("ibo.size = indices.length;\n")
    fd.write("\n")

    # normals
    fd.write("//normals\n")
    fd.write("var nbo = gl.createBuffer();\n")
    fd.write("gl.bindBuffer(gl.ARRAY_BUFFER, nbo);\n")
    fd.write("var normals = new Float32Array([\n")
    for n in m.normal(): fd.write("\t\t%f, %f, %f,\n" % (n[0], n[1], n[2]))
    fd.write("]);\n")
    fd.write("gl.bufferData(gl.ARRAY_BUFFER, normals, gl.STATIC_DRAW);\n")
    fd.write("nbo.size = normals.length / 3;\n")
    fd.write("\n")

    # colors
    fd.write("// colors\n")
    fd.write("var cbo = gl.createBuffer();\n")
    fd.write("gl.bindBuffer(gl.ARRAY_BUFFER, cbo);\n")
    fd.write("var colors = new Float32Array([\n")
    for n in m.normal(): fd.write("\t\t%f, %f, %f, %f,\n" % diffuse)
    fd.write("]);\n")
    fd.write("gl.bufferData(gl.ARRAY_BUFFER, colors, gl.STATIC_DRAW);\n")
    fd.write("cbo.size = colors.length / 4.0;\n")
    fd.write("\n")

    fd.write("o = new Object(vbo, ibo, nbo, cbo, " + \
            "modelMatrix, modelMatrixIT);\n")
    fd.write("objects.push(o);\n\n")

def main():
    if len(sys.argv) < 3:
        print("Usage: mesh2js.py file1.mesh "
                      "[file2.mesh ... filen.mesh] output.js")
        sys.exit(1)

    meshlist = sys.argv[1:-1]
    jsname = sys.argv[-1]
    meshlist2js(meshlist, jsname)

if __name__ == '__main__': main()
