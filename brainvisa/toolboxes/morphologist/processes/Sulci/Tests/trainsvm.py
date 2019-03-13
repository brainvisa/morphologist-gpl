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
import six
try:
    from soma import aims
except:
    def validation():
        raise RuntimeError(_t_('module <em>aims</em> not available'))

name = 'Train SVM'
userLevel = 2


signature = Signature(
    'classifier', ReadDiskItem('Classifier', ['SVM classifier']),
    'output_classifier', WriteDiskItem('Classifier', ['SVM classifier']),
    'input_data', ReadDiskItem('2D image', 'aims readable Volume Formats'),
    'svm_mode', Choice('classifier', 'probability', 'regression', 'quality',
                       'decision', 'one_class'),
    'sigma', Float(),
    'C', Float(),
)


def initialization(self):
    self.linkParameters('output_classifier', 'classifier')
    self.sigma = 1.
    self.C = 1.


def execution(self, context):
    r = aims.Reader({})
    im = r.read(self.input_data.fullPath())
    input = context.temporary('Text file')
    f = open(input.fullPath(), 'w')
    for y in six.moves.xrange(im.getSizeY()):
        for x in six.moves.xrange(im.getSizeX()):
            val = im.value(x, y)
            if val:
                f.write('%d\t1:%f\t2:%f\n' %
                        (val-1, float(x)/im.getSizeX(),
                         float(y)/im.getSizeY()))
    f.close()
    if self.svm_mode == 'regression':
        context.system('svm-train', '-p', 0, '-s', 3, '-b', '1', '-c', self.C,
                       '-g', self.sigma,
                       input, self.output_classifier)
    elif self.svm_mode == 'one_class':
        context.system('svm-train', '-s', 2, '-c', self.C,
                       '-g', self.sigma,
                       input, self.output_classifier)
        # TODO
        self.svm_mode = 'classifier'
    else:
        context.system('svm-train', '-b', '1', '-c', self.C, '-g', self.sigma,
                       input, self.output_classifier)
    self.output_classifier.updateMinf({'svm_mode': self.svm_mode})
