
from brainvisa.processes import *
import os.path as osp
try:
    import reportlab
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from brainvisa import anatomist
    from anatomist import cpp as anacpp
    import csv
    import PIL
    from PIL import ImageDraw
    import numpy as np
except ImportError:
    pass

def validation():
    import reportlab
    from reportlab import pdfgen, platypus
    from brainvisa import anatomist
    import csv


userLevel = 0
needs_opengl = True

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
    'talairach_transform', ReadDiskItem(
        'Transform Raw T1 MRI to Talairach-AC/PC-Anatomist',
        'Transformation matrix'),
    'brain_volumes_file', ReadDiskItem(
        'Brain volumetry measurements', 'CSV file'),
    'normative_brain_stats', ReadDiskItem('Normative brain volumes stats',
                                          'JSON file'),
    'report', WriteDiskItem('Morphologist report', 'PDF file'),
    'report_json', WriteDiskItem('Morphologist JSON report', 'JSON file'),
    'subject', String(),
)


capsul_param_options = {
    'subject': ['dataset="output"'],
    'normative_brain_stats': ['dataset=None'],
}


def initialization(self):
    def linkSubject(self, proc):
        if self.t1mri is not None:
            subject = self.t1mri.get('subject')
            return subject

    self.setOptional('left_grey_white', 'right_grey_white',
                     'left_gm_mesh', 'right_gm_mesh',
                     'left_wm_mesh', 'right_wm_mesh',
                     'left_labelled_graph', 'right_labelled_graph',
                     'brain_volumes_file', 'normative_brain_stats',
                     'talairach_transform', 'report_json')
    self.linkParameters('subject', 't1mri', linkSubject)
    self.linkParameters('left_grey_white', 't1mri')
    self.linkParameters('right_grey_white', 't1mri')
    self.linkParameters('left_gm_mesh', 't1mri')
    self.linkParameters('right_gm_mesh', 't1mri')
    self.linkParameters('left_wm_mesh', 't1mri')
    self.linkParameters('right_wm_mesh', 't1mri')
    self.linkParameters('left_labelled_graph', 't1mri')
    self.linkParameters('right_labelled_graph', 't1mri')
    self.linkParameters('talairach_transform', 't1mri')
    self.linkParameters('brain_volumes_file', 't1mri')
    self.linkParameters('report', 't1mri')
    self.linkParameters('report_json', 't1mri')
    # self.linkParameters('normative_brain_stats', 't1mri')


def execution(self, context):
    # status:
    # 0: OK
    # 1: Warning (stat out of 1-99% bounds)
    # 2: Suspicious (stat out of bounds)
    # 3: Bad (stat over limit, or missing data)
    status = 0
    comments = []

    context.write('<h1>Morphologist report</h1>')
    pdf = canvas.Canvas(self.report.fullPath())
    pdf.setStrokeColorRGB(0.5, 0.53, 0.6)
    pdf.setFillColorRGB(0.78, 0.82, 0.93)
    pdf.roundRect(10, 750, 575, 70, 5, stroke=1, fill=1)
    pdf.setStrokeColorRGB(0., 0., 0.)
    pdf.setFillColorRGB(0., 0., 0.)
    pdf.setFont('Helvetica', 10)
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

    bbox = (80, 120, 90)
    bbmin = (-80, -100, -120)
    obs_pos = tuple((x+y)/2 for x, y in zip(bbox, bbmin))

    a = anatomist.Anatomist()
    t1mri = a.loadObject(self.t1mri)
    new_ref = None
    if t1mri.getReferential().uuid() \
                == anacpp.Referential.acPcReferential().uuid() \
            and self.talairach_transform is not None \
            and osp.exists(self.talairach_transform.fullPath()):
        # if we are running without databasing, this is not done automatically
        # by brainvisa.anatomist. Do it manually.
        new_ref = a.createReferential()
        tr = a.loadTransformation(self.talairach_transform.fullPath(), new_ref,
                                  anacpp.Referential.acPcReferential())
        t1mri.assignReferential(new_ref)
    w = a.createWindow('Axial')
    w.addObjects(t1mri)
    w.setReferential(anacpp.Referential.acPcReferential())
    a.execute('WindowConfig', windows=[w], cursor_visibility=0)
    w.focusView()
    w.camera(boundingbox_min=bbmin, boundingbox_max=bbox,
             cursor_position=(0, 0, 0), zoom=1, observer_position=obs_pos)
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
    if self.left_grey_white is not None \
            and osp.exists(self.left_grey_white.fullPath()):
        lgw = a.loadObject(self.left_grey_white)
        if new_ref:
            lgw.assignReferential(new_ref)
        lgw.setPalette('RAINBOW')
        fusiono.append(lgw)
    if self.right_grey_white is not None \
            and osp.exists(self.right_grey_white.fullPath()):
        rgw = a.loadObject(self.right_grey_white)
        if new_ref:
            rgw.assignReferential(new_ref)
        rgw.setPalette('RAINBOW')
        fusiono.append(rgw)
    if fusiono:
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
                 cursor_position=(0, 0, 0), zoom=1, observer_position=obs_pos)
        tmpimage2 = context.temporary('JPEG image')
        w.snapshot(tmpimage2.fullPath(), 192, 256)
        pdf.drawImage(tmpimage2.fullPath(), 130, 580, width=96, height=128)
        w.removeObjects(gwfusion)
    else:
        pdf.drawString(160, 650, 'MISSING')
        status = 3
        comments.append('Missing segmentation file')

    objs = []
    wmeshes = []
    w.mute3D()
    if self.left_wm_mesh is not None \
            and osp.exists(self.left_wm_mesh.fullPath()):
        lwm = a.loadObject(self.left_wm_mesh)
        if new_ref:
            lwm.assignReferential(new_ref)
        w.addObjects(lwm)
        objs.append(lwm)
    if self.right_wm_mesh is not None \
            and osp.exists(self.right_wm_mesh.fullPath()):
        rwm = a.loadObject(self.right_wm_mesh)
        if new_ref:
            rwm.assignReferential(new_ref)
        w.addObjects(rwm)
        objs.append(rwm)
    if objs:
        w.addObjects(objs)
        w.focusView()
        w.camera(boundingbox_min=bbmin, boundingbox_max=bbox,
                 cursor_position=(0, 0, 0), view_quaternion=[0, 0, 1, 0],
                 zoom=1, observer_position=obs_pos)
        tmpimage3 = context.temporary('JPEG image')
        w.snapshot(tmpimage3.fullPath(), 192, 256)
        pdf.drawImage(tmpimage3.fullPath(), 230, 580, width=96, height=128)
        w.removeObjects(objs)
        wmeshes = objs
    else:
        pdf.drawString(260, 650, 'MISSING')
        status = 3
        comments.append('Missing G/W mesh file')


    objs = []
    if self.left_gm_mesh is not None \
            and osp.exists(self.left_gm_mesh.fullPath()):
        lgm = a.loadObject(self.left_gm_mesh)
        if new_ref:
            lgm.assignReferential(new_ref)
        w.addObjects(lgm)
        objs.append(lgm)
    if self.right_gm_mesh is not None \
            and osp.exists(self.right_gm_mesh.fullPath()):
        rgm = a.loadObject(self.right_gm_mesh)
        if new_ref:
            rgm.assignReferential(new_ref)
        w.addObjects(rgm)
        objs.append(rgm)
    if objs:
        w.focusView()
        w.camera(boundingbox_min=bbmin, boundingbox_max=bbox,
                 cursor_position=(0, 0, 0), view_quaternion=[0, 0, 1, 0],
                 zoom=1, observer_position=obs_pos)
        tmpimage4 = context.temporary('JPEG image')
        w.snapshot(tmpimage4.fullPath(), 192, 256)
        pdf.drawImage(tmpimage4.fullPath(), 330, 580, width=96, height=128)
        w.removeObjects(objs)
    else:
        pdf.drawString(360, 650, 'MISSING')
        status = 3
        comments.append('Missing pial mesh file')


    objs = []
    hie_file = aims.carto.Paths.findResourceFile(
        'nomenclature/hierarchy/sulcal_root_colors.hie')
    hie = a.loadObject(hie_file)
    if self.left_labelled_graph is not None \
            and osp.exists(self.left_labelled_graph.fullPath()):
        lg = a.loadObject(self.left_labelled_graph)
        if new_ref:
            lg.assignReferential(new_ref)
        lg.setLabelProperty('label')
        objs.append(lg)
    if self.right_labelled_graph is not None \
            and osp.exists(self.right_labelled_graph.fullPath()):
        rg = a.loadObject(self.right_labelled_graph)
        if new_ref:
            rg.assignReferential(new_ref)
        rg.setLabelProperty('label')
        objs.append(rg)
    if objs:
        objs = wmeshes + objs
        w.addObjects(objs)
        w.focusView()
        w.camera(boundingbox_min=bbmin, boundingbox_max=bbox,
                 cursor_position=(0, 0, 0), view_quaternion=[0, 0, 1, 0],
                 zoom=1, observer_position=obs_pos)
        tmpimage5 = context.temporary('JPEG image')
        w.snapshot(tmpimage5.fullPath(), 192, 256)
        pdf.drawImage(tmpimage5.fullPath(), 430, 580, width=96, height=128)
        w.removeObjects(objs)
    else:
        pdf.drawString(460, 650, 'MISSING')
        status = 3
        comments.append('Missing sulci graph file')


    pdf.setFillColorRGB(0., 0., 0.)

    hdr = []
    morph = []
    morph_z = []
    norm_stat = {}
    n_quant = None
    if self.brain_volumes_file is not None \
            and osp.exists(self.brain_volumes_file.fullPath()):
        with open(self.brain_volumes_file.fullPath()) as f:
            csv_reader = csv.reader(f, csv.Sniffer().sniff(f.read(2048)))
            f.seek(0)
            morph_hdr = next(iter(csv_reader))
            for row in csv_reader:
                row = [row[0]] + [float(x) for x in row[1:]]
                morph.append(row)
        if self.normative_brain_stats is not None:
            with open(self.normative_brain_stats.fullPath()) as f:
                norm_stat = json.load(f)
            ncols = {c: i for i, c in enumerate(norm_stat.get('columns', []))}
            morph_z = [None] * len(morph[0])
            avg = norm_stat.get('averages')
            std = norm_stat.get('std')
            quantiles = norm_stat.get('quantiles')
            if avg and std:
                # print('avg:', len(avg), ', quantiles:', len(quantiles))
                for i, mv in enumerate(morph[0]):
                    c = ncols.get(morph_hdr[i])
                    if c is not None:
                        z0 = avg[c]
                        zs = std[c]
                        if z0 is not None and zs != 0:
                            z = (mv - z0) / zs
                            morph_z[i] = z
            if quantiles:
                n_quant = np.array([(np.array(q) - avg) / std
                                    for q in quantiles])
            # morph and morph_z have the subject column,
            # whereas n_quand, std, avg have not.
        #else:
            #morph_z = [None] * len(morph[0])

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
        'both.skel_points': 'skel. pts',
        'log_ratio.skel_points': 'skel. log. ratio',
    }
    units = {
        'both.brain_volume': 'mm3',
        'both.GM': 'mm3',
        'both.WM': 'mm3',
        'both.eTIV': 'mm3',
        'both.GM_area': 'mm2',
        'both.WM_area': 'mm2',
        'both.fold_length': 'mm',
        'both.mean_depth': 'mm',
        'both.mean_thickness': 'mm',
        'both.mean_opening': 'mm',
        'both.skel_points': 'vox',
    }

    skel_asym_low = [-0.097663, -0.169090]
    skel_asym_high = [0.073922, 0.116971]

    zvals = [None] * len(keymap)
    quants = [None] * len(keymap)
    #if n_quant is not None:
        #print('n_quant:', n_quant.shape)
    #if morph_z:
        #print('morph_z:', len(morph_z))
    for i, (k, tk) in enumerate(keymap.items()):
        missing = False
        z = None
        unit = None
        try:
            j = morph_hdr.index(k)
            val = morph[0][j]
            v = str(round(val, 2))
            unit = units.get(k)
            if morph_z:
                z = morph_z[j]
                zvals[i] = z
                if n_quant is not None:
                    q = n_quant[:, j - 1]  # -1 to skip subject col
                    # print(q)
                    # add 3 values at each extrema
                    # and remove extrema (0, 100% qantiles)
                    q = np.hstack((np.zeros((3, )), q[1: -1], np.zeros((3, ))))
                    qv1 = quantiles[1][j - 1]
                    qv99 = quantiles[-2][j - 1]
                    if k == 'log_ratio.skel_points' and (val <= qv1 * 1.6
                                                         or val >= qv99 * 1.6):
                        # problem detection from the skel log ratio:
                        # use hard-coded empirical values
                        # origin: if value exceeds quantile(1%)) * 1.6
                        # qv1_6 = qv1 * 1.6
                        # qv99_6 = qv99 * 1.6
                        qv1_susp = skel_asym_low[0]
                        qv99_susp = skel_asym_high[0]
                        qv1_bad = skel_asym_low[1]
                        qv99_bad = skel_asym_high[1]
                        q[2] = (qv1_susp - avg[j - 1]) / std[j - 1]
                        q[-3] = (qv99_susp - avg[j - 1]) / std[j - 1]
                        q[1] = (qv1_bad - avg[j - 1]) / std[j - 1]
                        q[-2] = (qv99_bad - avg[j - 1]) / std[j - 1]
                        if val <= qv1:
                            q[0] = z
                        else:
                            q[-1] = z
                        if val <= qv1_bad or val >= qv99_bad:
                            # segmentation problem almost certain
                            status = np.max((3, status))
                            comments += [
                                'Probable segmentation problem or important '
                                'anomaly:',
                                '      large asymmetry in folds sizes.']
                        else:
                            # suspected segmentation problem
                            status = np.max((2, status))
                            comments += [
                                'Possible segmentation problem or important '
                                'anomaly:',
                                '      large asymmetry in folds sizes.']
                    elif val <= qv1 or val >= qv99:
                        if val <= qv1:
                            q[2] = z
                        else:
                            q[-3] = z
                        status = np.max((1, status))
                        comments.append(
                            f'Possible problem: {tk} out of 1-99% percentile.')
                    quants[i] = q
            else:  # no normative stats
                if k == 'log_ratio.skel_points' \
                        and (val <= skel_asym_low[0]
                             or val >= skel_asym_high[0]):
                    if val <= skel_asym_low[1] or val >= skel_asym_high[1]:
                        # segmentation problem almost certain
                        status = np.max((3, status))
                        comments += [
                            'Probable segmentation problem or important '
                            'anomaly:',
                            '      large asymmetry in folds sizes.']
                    else:
                        # suspected segmentation problem
                        status = np.max((2, status))
                        comments += [
                            'Possible segmentation problem or important '
                            'anomaly:',
                            '      large asymmetry in folds sizes.']
        except Exception:
            #context.write(e)
            #raise
            v = '<MISSING>'
            status = 3
            comments.append('missing stat')
            unit = None
            missing = True
        h = 530 - i * 12
        pdf.drawString(30, h, '%s:' % tk)
        if missing:
            pdf.setFillColorRGB(0.6, 0., 0.)
        elif z is not None:
            pdf.drawRightString(270, h, '%+1.2f σ' % z)
        pdf.drawRightString(200, h, v)
        if unit is not None:
            pdf.setFontSize(8)
            pdf.drawString(210, h, unit)
            pdf.setFontSize(10)
        if missing:
            pdf.setFillColorRGB(0., 0., 0.)

    if morph_z:
        import matplotlib
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.31, top=1., left=0.05)
        ax.add_patch(plt.Rectangle((-0.5, -1), len(keymap), 2.,
                                   facecolor='#d0f0d0', fill=True,
                                   edgecolor='#d0f0d0'))
        if quantiles:
            nq = 0
            for q in quants:
                if q is not None:
                    nq = len(q)
                    break
            for i, q in enumerate(quants):
                if q is None:
                    quants[i] = np.zeros(nq)
            quants = np.array(quants).T
            quant_colors = [
                '#c04040ff',
                '#ff7070ff',
                '#f0d080ff',
                '#e0ff90ff',
                '#a0ffa0ff',
                '#c0ffc0ff',
                '#e0ffe0ff',
                '#c0ffc0ff',
                '#a0ffa0ff',
                '#e0ff90ff',
                '#f0d080ff',
                '#ff7070ff',
                '#c04040ff',
            ]
            while len(quant_colors) > len(quants):
                quant_colors = quant_colors[1:-1]
            # reorder quantiles 0->0.5 then 1->0.5 for good plot overlapping
            quant_colors = quant_colors[:len(quants) // 2] \
                + quant_colors[len(quants) - 1:len(quants) // 2 - 1:-1]
            quants = np.vstack(
                (quants[:len(quants) // 2],
                 quants[len(quants) - 1:len(quants) // 2 - 1:-1]))
            for i, q in enumerate(quants):
                c = quant_colors[i]
                ax.bar(np.arange(len(q)), q, width=0.5, color=c)
        plt.xticks(rotation=60)
        ax.set_xticks(range(len(keymap)))
        ax.set_xticklabels(keymap.values())
        #ax.plot([-0.7, len(keymap) + 0.7], [0, 0], '-', color='black')
        ax.stem(range(len(zvals)), zvals, 'o')
        tmpimage6 = context.temporary('PNG image')
        fig.savefig(tmpimage6.fullPath())

        pdf.drawImage(tmpimage6.fullPath(), 290, 290, width=310, height=250)
        pdf.drawString(400, 275, 'Z scores')

    # status
    statuses = ['OK', 'Warning', 'Suspicious', 'Bad']
    status_colors = [(0., 0., 0.), (0.7, 0.7, 0.), (0.8, 0.5, 0.),
                        (0.6, 0., 0.)]

    pdf.drawString(30, 350, 'QC status:')
    pdf.setFont('Helvetica-Bold', 10)
    pdf.setFillColorRGB(*status_colors[status])
    pdf.drawString(100, 350, statuses[status])
    pdf.setFillColorRGB(0., 0., 0.)
    pdf.setFont('Helvetica', 10)
    if comments:
        for i, c in enumerate(comments):
            pdf.drawString(30, 330 - 12 * i, c)

    pdf.save()

