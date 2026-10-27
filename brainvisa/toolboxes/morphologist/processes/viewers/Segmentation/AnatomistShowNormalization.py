from brainvisa.processes import (
    Signature, ReadDiskItem, String, Float,
)
from brainvisa import anatomist
from soma.qt_gui.qtThread import QtThreadCall, MainThreadLife

name = 'Anatomist Show Normalization'
roles = ('viewer',)
userLevel = 0


def validation():
    anatomist.validation()


signature = Signature(
    'normalization_transformation',
    ReadDiskItem('Transform Raw T1 MRI to Talairach-MNI template-SPM',
                 'Transformation matrix'),
    't1mri_nobias', ReadDiskItem('T1 MRI Bias Corrected',
                                 'Anatomist volume formats'),
    'referential', ReadDiskItem('Referential of raw T1 MRI', 'Referential'),
    'mni_template', ReadDiskItem('anatomical Template',
                                 'Anatomist volume formats'),
    'split_brain', ReadDiskItem('Split Brain Mask',
                                'Anatomist volume formats'),
    'palette', String(),
    'fmode', String(),
    'rate', Float(),
)


def initialization(self):
    self.linkParameters('t1mri_nobias', 'normalization_transformation')
    self.linkParameters('referential', 't1mri_nobias')
    self.linkParameters('split_brain', 't1mri_nobias')
    self.setOptional('split_brain')

    self.mni_template = self.signature['mni_template'].findValue(
        {'skull_stripped': 'yes', 'Size': '1 mm'})
    self.palette = 'RED-lfusion'
    self.fmode = 'linear_A_if_B_black'
    self.rate = 0.7


def execution(self, context):
    return QtThreadCall().call(self.exec_mainthread, context)


class AutoDel:
    def __init__(self, element):
        self.element = element

    def __del__(self):
        import anatomist.api as ana
        a = ana.Anatomist()
        a.deleteElements(self.element)


def exec_mainthread(self, context):
    from anatomist import cpp as cppapi

    result = []
    a = anatomist.Anatomist()
    block = a.createWindowsBlock(2)

    mri = a.loadObject(self.t1mri_nobias)
    ref_file = self.referential
    if ref_file is None:
        ref_file = ''
    mref = a.createReferential(ref_file)
    mri.assignReferential(mref)
    a.loadTransformation(
        self.normalization_transformation.fullPath(), mref,
        cppapi.Referential.mniTemplateReferential())
    tpl = a.loadObject(self.mni_template)
    a.execute('TexturingParams', objects=[tpl], value_interpolation=0)
    tpl.applyBuiltinReferential()

    tpl.setPalette(self.palette)
    fus_obj = [mri, tpl]
    if self.split_brain:
        split = a.loadObject(self.split_brain)
        split.assignReferential(mref)
        pal = a.getPalette('split_in_norm')
        if pal is None:
            pal = a.createPalette('split_in_norm')
            pal.setColors([0, 0, 0,  0, 0, 255,  0, 255, 0,  255, 255, 0])
        split.setPalette(pal, minVal=0, maxVal=3, absoluteMode=1)
        a.execute('TexturingParams', objects=[split],
                  value_interpolation=0)
        fus_obj.append(split)
    fusion = a.fusionObjects(fus_obj, method='Fusion2DMethod')
    a.execute('TexturingParams', objects=[fusion], mode=self.fmode,
              texture_index=1, rate=self.rate)
    a.execute("Fusion2DParams", object=fusion, reorder_objects=fus_obj)
    if self.split_brain:
        a.execute('TexturingParams', objects=[fusion],
                  texture_index=1, rate=0.57)
        a.execute('TexturingParams', objects=[fusion],
                  texture_index=2, rate=0.5)
    window1 = a.createWindow('Coronal', block=block)
    window1.assignReferential(mri.referential)
    window1.addObjects([fusion])
    window2 = a.createWindow('Sagittal', block=block)
    window2.assignReferential(mri.referential)
    window2.addObjects([fusion])
    window3 = a.createWindow('Axial', block=block)
    window3.assignReferential(mri.referential)
    window3.addObjects([fusion])

    sz = [block.internalWidget.widget.width(),
          block.internalWidget.widget.height()]
    if sz[0] < 800:
        sz[0] = 800
    if sz[1] < 800:
        sz[1] = 800
    block.internalWidget.widget.resize(*sz)

    refdel = [AutoDel(mref),
              AutoDel(tpl.referential)]
    if a.config().get('userLevel', 0) > 1:
        # find disk ref of template
        for t in a.getTransformations():
            if t.destination().internalRep is tpl.referential.internalRep \
                    and not t.isGenerated() \
                    and t.destination() is not \
                    cppapi.Referential.mniTemplateReferential():
                refdel.append(AutoDel(t.source()))

    result.extend([fusion, window1, window2, window3] + refdel)

    return result
