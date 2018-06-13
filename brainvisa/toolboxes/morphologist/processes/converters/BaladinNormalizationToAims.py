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
from soma import uuid
from brainvisa import registration
import numpy

name = 'Baladin Normalization to AIMS converter'
userLevel = 0


def validation():
    try:
        from soma import aims
    except:
        raise ValidationError('aims module not here')


signature = Signature(
    'read', ReadDiskItem('Baladin Transformation', 'Text file'),
    'source_volume', ReadDiskItem('4D Volume',
                                  'aims readable Volume Formats'),
    'write', WriteDiskItem(
        'Transform Raw T1 MRI to Talairach-MNI template-SPM', 'Transformation matrix'),
    'registered_volume', ReadDiskItem('4D Volume',
                                      'aims readable Volume Formats',
                                      requiredAttributes={'normalized': 'yes'}),
    'set_transformation_in_source_volume', Boolean(),
)


def initialization(self):
    def linkSetTransfo(self, proc):
        return (self.source_volume is not None and
                self.source_volume.isWriteable())

    self.linkParameters('write', 'read')
    self.linkParameters('source_volume', 'read')
    self.linkParameters('write', 'source_volume')
    self.linkParameters('registered_volume', 'read')
    self.setOptional('registered_volume')
    self.linkParameters('set_transformation_in_source_volume',
                        'source_volume', linkSetTransfo)


def execution(self, context):
    fd = open(self.read.fullPath(), 'r')
    lines = fd.readlines()[2:-1]
    lines = [l.strip('\n').split(' ') for l in lines]
    # get translation (4th column)
    T = [float(l[3]) for l in lines][:-1]
    # get rotation (3 first columns and rows)
    R = [[float(x) for x in l[:3]] for l in lines][:3]
    fd.close()

    # fill transformation
    s2atlas = aims.Motion()
    s2atlas.setTranslation(T)
    s2atlasR = s2atlas.rotation()
    # don't know why but R must be transposed
    s2atlasR.volume().arraydata()[0, 0][:] = numpy.array(R).T

    # string of destination referential
    outref = self.write.get("destination_referential", None)
    if outref is None:
        context.warning("unknown destination referential")
        return
    outref = uuid.Uuid(outref)

    if outref == registration.talairachMNIReferentialId:
        stroutref = 'Talairach-MNI template-SPM'
    elif outref == registration.talairachACPCReferentialId:
        stroutref = 'Talairach-AC/PC-Anatomist'
    else:
        raise RuntimeError('output referential is unknown: ' +
                           str(outref))

    # apply remaining transfo of destination
    rvol = aims.read(self.registered_volume.fullPath())
    h = rvol.header()
    atlas2mni = aims.Motion()
    referentials = h['referentials']
    if len(referentials) != 0:
        res = [i for (i, r) in enumerate(referentials) if r == stroutref]
        if len(res) != 0:
            tr = h['transformations'][res[0]]
            tr = numpy.array(tr).reshape(4, 4)
            atlas2mni.fromMatrix(numpy.array(tr).reshape(4, 4))

    s2atlas = atlas2mni * s2atlas
    aims.write(s2atlas, self.write.fullPath())

    # register referentials
    tm = registration.getTransformationManager()
    tm.setNewTransformationInfo(self.write,
                                tm.referential(self.source_volume), outref)

    # write transfo in source volume
    if not self.set_transformation_in_source_volume:
        return
    if not self.source_volume.isWriteable():
        context.warning('source_volume is not writeable: ' +
                        'transformation information will not be set ' +
                        'into its header.')
        return
    context.write('source is writeable: setting its header information')
    self.source_volume.readAndUpdateMinf()
    refs = self.source_volume.get('referentials')
    trans = self.source_volume.get('transformations')

    vec_s2atlas = list(s2atlas.toVector())
    if refs and trans:
        for i, (ref, t) in enumerate(zip(refs, trans)):
            if not (ref in (str(outref), stroutref)):
                continue
            if t != vec_s2atlas:
                context.warning('overriding existing ' +
                                'normalization information!')
                context.write('older one: ' + str(t))
                context.write('new one  : ' + str(vec_s2atlas))

            trans[i] = vec_s2atlas
            break
        else:
            refs.append(stroutref)
            trans.append(vec_s2atlas)
    else:  # no existing refs/trans
        refs = [stroutref]
        trans = [vec_s2atlas]
    self.source_volume.setMinf('referentials', refs)
    self.source_volume.setMinf('transformations', trans)
    self.source_volume.saveMinf()
    # force re-writing image with full native header
    context.system('AimsFileConvert', '-i', self.source_volume, '-o',
                   self.source_volume)
