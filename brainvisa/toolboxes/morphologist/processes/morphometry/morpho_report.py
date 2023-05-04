
from brainvisa.processes import *
try:
    import reportlab
    from reportlab.pdfgen import canvas
    from brainvisa import anatomist
    from anatomist import cpp as anacpp
    import csv
    import PIL
    from PIL import ImageDraw
except ImportError:
    pass

def validation():
    import reportlab
    from reportlab import pdfgen, platypus
    from brainvisa import anatomist
    import csv


userLevel = 0

signature = Signature(
    't1mri', ReadDiskItem('Raw T1 MRI', 'aims readable volume formats'),
    'left_grey_white', ReadDiskItem('Left Grey White Mask',
                                    'aims readable volume formats'),
    'right_grey_white', ReadDiskItem('Right Grey White Mask',
                                     'aims readable volume formats'),
    'left_gm_mesh', ReadDiskItem('Hemisphere mesh', 'aims mesh formats',
                                 requiredAttributes={'side': 'left'}),
    'right_gm_mesh', ReadDiskItem('Hemisphere mesh', 'aims mesh formats',
                                 requiredAttributes={'side': 'right'}),
    'left_wm_mesh', ReadDiskItem('Hemisphere white mesh', 'aims mesh formats',
                                 requiredAttributes={'side': 'left'}),
    'right_wm_mesh', ReadDiskItem('Hemisphere white mesh', 'aims mesh formats',
                                 requiredAttributes={'side': 'right'}),
    'left_labelled_graph', ReadDiskItem(
        'labelled Cortical Folds Graph', 'Graph and data',
        requiredAttributes={'side': 'left'}),
    'right_labelled_graph', ReadDiskItem(
        'labelled Cortical Folds Graph', 'Graph and data',
        requiredAttributes={'side': 'right'}),
    'brain_volumes_file', ReadDiskItem(
        'Brain volumetry measurements', 'CSV file'),
    'report', WriteDiskItem('Morphologist report', 'PDF file'),
    'subject', String(),
)


def initialization(self):
    def linkSubject(self, proc):
        if self.t1mri is not None:
            subject = self.t1mri.get('subject')
        return subject

    self.setOptional('left_grey_white', 'right_grey_white',
                     'left_gm_mesh', 'right_gm_mesh',
                     'left_wm_mesh', 'right_wm_mesh',
                     'left_labelled_graph', 'right_labelled_graph',
                     'brain_volumes_file')
    self.linkParameters('subject', 't1mri', linkSubject)
    self.linkParameters('left_grey_white', 't1mri')
    self.linkParameters('right_grey_white', 't1mri')
    self.linkParameters('left_gm_mesh', 't1mri')
    self.linkParameters('right_gm_mesh', 't1mri')
    self.linkParameters('left_wm_mesh', 't1mri')
    self.linkParameters('right_wm_mesh', 't1mri')
    self.linkParameters('left_labelled_graph', 't1mri')
    self.linkParameters('right_labelled_graph', 't1mri')
    self.linkParameters('brain_volumes_file', 't1mri')
    self.linkParameters('report', 't1mri')

def execution(self, context):
    context.write('<h1>Morphologist report</h1>')
    pdf = canvas.Canvas(self.report.fullPath())
    pdf.setStrokeColorRGB(0.5, 0.53, 0.6)
    pdf.setFillColorRGB(0.78, 0.82, 0.93)
    pdf.roundRect(10, 750, 570, 70, 5, stroke=1, fill=1)
    pdf.setStrokeColorRGB(0., 0., 0.)
    pdf.setFillColorRGB(0., 0., 0.)
    logo = os.path.join(neuroConfig.iconPath, 'brainvisa.png')
    # add circular transparency to logo
    logo_im = PIL.Image.open(logo)
    logo_im.load()
    pim3 = PIL.Image.new('RGBA', (170, 170), (255, 255, 255, 255))
    pim3.paste(logo_im, (11, 10))
    mask = PIL.Image.new('L', pim3.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, 169, 169), fill=255)
    pim3.putalpha(mask)
    tlogo = context.temporary('PNG image')
    pim3.save(tlogo.fullPath())
    pdf.drawImage(tlogo.fullPath(), 20, 760, width=50, height=50,
                  mask='auto')

    pdf.setFontSize(20)
    pdf.drawString(200, 780, 'Morphologist report')
    pdf.setFontSize(16)
    pdf.drawString(30, 720, 'Subject ID:')
    pdf.drawString(250, 720, self.subject)

    bbox = (78, 100, 100)
    bbmin = tuple(-b for b in bbox)

    a = anatomist.Anatomist()
    t1mri = a.loadObject(self.t1mri)
    w = a.createWindow('Axial')
    w.addObjects(t1mri)
    w.setReferential(anacpp.Referential.acPcReferential())
    a.execute('WindowConfig', windows=[w], cursor_visibility=0)
    w.focusView()
    w.camera(boundingbox_min=bbmin, boundingbox_max=bbox,
             cursor_position=(0, 0, 0), zoom=1)
    tmpimage = context.temporary('JPEG image')
    w.snapshot(tmpimage.fullPath(), 192, 256)
    w.removeObjects(t1mri)

    pdf.drawImage(tmpimage.fullPath(), 30, 580, width=96, height=128)

    pdf.setFontSize(10)
    pdf.drawString(60, 570, 'raw T1')
    pdf.drawString(135, 570, 'G/W segmentation')
    pdf.drawString(255, 570, 'G/W mesh')
    pdf.drawString(360, 570, 'pial mesh')
    pdf.drawString(470, 570, 'sulci')

    pdf.setFillColorRGB(0.6, 0., 0.)

    fusiono = []
    gwfusion = None
    if self.left_grey_white is not None:
        lgw = a.loadObject(self.left_grey_white)
        lgw.setPalette('RAINBOW')
        fusiono.append(lgw)
    if self.right_grey_white is not None:
        rgw = a.loadObject(self.right_grey_white)
        rgw.setPalette('RAINBOW')
        fusiono.append(rgw)
    if self.left_grey_white is not None or self.right_grey_white is not None:
        a.execute('TexturingParams', objects=fusiono, value_interpolation=0)
        fusiono.insert(0, t1mri)
        gwfusion = a.fusionObjects(fusiono, method='Fusion2DMethod')
        rate = 0.6
        a.execute('TexturingParams', objects=[gwfusion], mode='linear',
                  texture_index=1, rate=rate)
        w.addObjects(gwfusion)
        w.setReferential(anacpp.Referential.acPcReferential())
        w.focusView()
        w.camera(boundingbox_min=bbmin, boundingbox_max=bbox,
                 cursor_position=(0, 0, 0), zoom=1)
        tmpimage2 = context.temporary('JPEG image')
        w.snapshot(tmpimage2.fullPath(), 192, 256)
        pdf.drawImage(tmpimage2.fullPath(), 130, 580, width=96, height=128)
        w.removeObjects(gwfusion)
    else:
        pdf.drawString(160, 650, 'MISSING')

    objs = []
    wmeshes = []
    w.mute3D()
    if self.left_wm_mesh is not None:
        lwm = a.loadObject(self.left_wm_mesh)
        w.addObjects(lwm)
        objs.append(lwm)
    if self.right_wm_mesh is not None:
        rwm = a.loadObject(self.right_wm_mesh)
        w.addObjects(rwm)
        objs.append(rwm)
    if self.left_wm_mesh is not None or self.right_wm_mesh is not None:
        w.addObjects(objs)
        w.focusView()
        w.camera(boundingbox_min=bbmin, boundingbox_max=bbox,
                 cursor_position=(0, 0, 0), view_quaternion=[0, 0, 1, 0],
                 zoom=1)
        tmpimage3 = context.temporary('JPEG image')
        w.snapshot(tmpimage3.fullPath(), 192, 256)
        pdf.drawImage(tmpimage3.fullPath(), 230, 580, width=96, height=128)
        w.removeObjects(objs)
        wmeshes = objs
    else:
        pdf.drawString(260, 650, 'MISSING')


    objs = []
    if self.left_gm_mesh is not None:
        lgm = a.loadObject(self.left_gm_mesh)
        w.addObjects(lgm)
        objs.append(lgm)
    if self.right_gm_mesh is not None:
        rgm = a.loadObject(self.right_gm_mesh)
        w.addObjects(rgm)
        objs.append(rgm)
    if self.left_gm_mesh is not None or self.right_gm_mesh is not None:
        w.focusView()
        w.camera(boundingbox_min=bbmin, boundingbox_max=bbox,
                 cursor_position=(0, 0, 0), view_quaternion=[0, 0, 1, 0],
                 zoom=1)
        tmpimage4 = context.temporary('JPEG image')
        w.snapshot(tmpimage4.fullPath(), 192, 256)
        pdf.drawImage(tmpimage4.fullPath(), 330, 580, width=96, height=128)
        w.removeObjects(objs)
    else:
        pdf.drawString(360, 650, 'MISSING')


    objs = []
    hie_file = aims.carto.Paths.findResourceFile(
        'nomenclature/hierarchy/sulcal_root_colors.hie')
    hie = a.loadObject(hie_file)
    if self.left_labelled_graph is not None:
        lg = a.loadObject(self.left_labelled_graph)
        objs.append(lg)
    if self.right_labelled_graph is not None:
        rg = a.loadObject(self.right_labelled_graph)
        objs.append(rg)
    if self.left_labelled_graph is not None \
            or self.right_labelled_graph is not None:
        objs = wmeshes + objs
        w.addObjects(objs)
        w.focusView()
        w.camera(boundingbox_min=bbmin, boundingbox_max=bbox,
                 cursor_position=(0, 0, 0), view_quaternion=[0, 0, 1, 0],
                 zoom=1)
        tmpimage5 = context.temporary('JPEG image')
        w.snapshot(tmpimage5.fullPath(), 192, 256)
        pdf.drawImage(tmpimage5.fullPath(), 430, 580, width=96, height=128)
        w.removeObjects(objs)
    else:
        pdf.drawString(460, 650, 'MISSING')


    pdf.setFillColorRGB(0., 0., 0.)

    if self.brain_volumes_file is not None:
        morph = []
        with open(self.brain_volumes_file.fullPath()) as f:
            csv_reader = csv.reader(f, csv.Sniffer().sniff(f.read(1024)))
            f.seek(0)
            morph_hdr = next(iter(csv_reader))
            for row in csv_reader:
                row = [row[0]] + [float(x) for x in row[1:]]
                morph.append(row)

        keymap = {
            'both.brain_volume': 'brain volume',
            'both.GM': 'GM volume',
            'both.WM': 'WM volume',
            'both.eTIV': 'eTIV',
            'both.GM_area': 'GM area',
            'both.WM_area': 'WM area',
            'left.gi_native_space': 'gyration index',
            'both.fold_length': 'total folds length',
            'both.mean_depth': 'avg. folds depth',
            'both.mean_thickness': 'avg. cortical thickness',
            'both.mean_opening': 'avg. folds opening',
        }

        for i, (k, tk) in enumerate(keymap.items()):
            try:
                j = morph_hdr.index(k)
                v = morph[0][j]
                v = str(round(v, 2))
            except Exception as e:
                v = '<MISSING>'
            h = 530 - i * 12
            pdf.drawString(30, h, '%s:' % tk)
            pdf.drawRightString(200, h, v)

    pdf.save()

