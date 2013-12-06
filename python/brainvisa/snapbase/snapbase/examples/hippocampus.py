# -*- coding: utf-8 -*-
from brainvisa.snapbase.snapbase import SnapBase
from brainvisa.snapbase.snapbase.interface import Ui_attributes_window

def detect_slices_of_interest(data, slice_directions=['S']):
  '''
  Returns a set of slices of interest : { 'S': [5,10,15,20],
                                          'C': [10,11,12,13] }
  (Only hippocampus selection)
  '''
  
  d = data.arraydata()
  _, n_slices_ax, n_slices_co, n_slices_sa = d.shape
  slices_minmax = {}
  for direction in slice_directions:
      if direction == 'S':
          first_nonempty_slice = 0
          last_nonempty_slice = n_slices_sa - 1
          slices_minmax[direction] = (first_nonempty_slice, last_nonempty_slice)
      elif direction == 'C':
          first_nonempty_slice = 0
          last_nonempty_slice = n_slices_co - 1
          slices_minmax[direction] = (first_nonempty_slice, last_nonempty_slice)
  return slices_minmax


def sacha_recompose(hippo_output_files, raw_output_files):
    from PIL import Image
    # recompose each subject's snapshot
    for h_path, r_path in zip(hippo_output_files, raw_output_files):
        direction = h_path[-5]
        print("direction: ", direction)
        hippo = Image.open(h_path)
        raw = Image.open(r_path)
        w1, h1 = hippo.size
        w2, h2 = raw.size
        tile_w1, tile_h1 = int(hippo.size[0]/{'S':7.0,'C':10.0}[direction]), int(hippo.size[1]/1.0)
        print h1, w1, h2, w2
        views_images = []
        margin = 10
        for j in xrange(1):
            for i in xrange({'S':7,'C':10}[direction]):
                tile_hippo = hippo.crop((i*tile_w1, j*tile_h1, (i+1)*tile_w1, (j+1)*tile_h1))
                tile_raw = raw.crop((i*tile_w1, j*tile_h1, (i+1)*tile_w1, (j+1)*tile_h1))
                both_tiles = Image.new('RGBA', (tile_hippo.size[0] + 2 * margin, tile_hippo.size[1] * 2 + 4 * margin), 'white')
                both_tiles.paste(tile_hippo, (margin, margin))
                both_tiles.paste(tile_raw, (margin, tile_hippo.size[1] + 3 * margin))
                views_images.append(both_tiles)

        # Building the tiled image
        image_size = (max([im.size[0] for im in views_images]), max([im.size[1] for im in views_images]))
        grid_dim = {12 : (4,3), 14 : (14,1), 5 : (5,1), 10:(10,1), 7:(7,1), 1 : (1,1), 3: (3,1), 20 : (4,5)}[len(views_images)]

        tiled_image = Image.new('RGBA', (grid_dim[0] * image_size[0], grid_dim[1] * image_size[1]), 'black')
        positions = [[j*image_size[0], i*image_size[1]] for i in xrange(grid_dim[1]) for j in xrange(grid_dim[0])]
        for i, pos in zip(views_images, positions):
            pos = [pos[j] + (image_size[j] - min(image_size[j], i.size[j]))/2.0 for j in xrange(len(pos))]
            tiled_image.paste(i, (int(pos[0]), int(pos[1])))
        tiled_image.save(r_path, 'PNG')
        import os
        command = ['rm ' + h_path ]
        os.system( *command )



class HippocampusSnapBase(SnapBase):

    def __init__(self, preferences):
        preferences['type_database'] = 'SACHA'
        self._do_slice_rendering = True

        SnapBase.__init__(self, preferences)
        
        
    def snap(self):
       self.main_window.setEnabled(False)
       labelsnapbase = HippocampusLabelSnapBase(self.preferences)
       labelsnapbase.snap_base(None, self.qt_app)
       dictdata = labelsnapbase.dictdata
       if len(dictdata) != 0:
           hippo_output_files = self.preferences['output_files']
           rawsnapbase = HippocampusRawSnapBase(self.preferences)
           rawsnapbase.snap_base(None, self.qt_app, dictdata=dictdata)
           raw_output_files = self.preferences['output_files']
           sacha_recompose(hippo_output_files, raw_output_files)
           self.create_png_sacha_report(raw_output_files)
       self.main_window.setEnabled(True)

    def create_png_sacha_report(self, hipporaw_output_files):
        def __render_text(pixmap, text, font, pos=(50, 50), color='black'):
            '''
            Render text on a pixmap using Qt, color may be a string or a tuple of
            3 HSV values
            '''
            from PyQt4 import QtGui, QtCore, Qt
            qp = Qt.QPainter(pixmap)
            qp.setFont(font)
            if isinstance(color, str):
                qcol = QtGui.QColor(color)
            else:
                qcol = QtGui.QColor()
                qcol.setHsl(color[0], color[1], color[2])
            qp.setPen(qcol)
            qp.drawText(pos[0], pos[1], text)
            qp.end()
    
            return pixmap
    
        def qt_to_pil_image(qimg):
            ''' Converting a Qt Image or Pixmap to PIL image '''
    
            from PyQt4 import Qt
            from PIL import Image, ImageChops
            import cStringIO
            buffer = Qt.QBuffer()
            buffer.open(Qt.QIODevice.ReadWrite)
            qimg.save(buffer, 'PNG')
            strio = cStringIO.StringIO()
            strio.write(buffer.data())
            buffer.close()
            strio.seek(0)
            pil_im = Image.open(strio)
            return pil_im
    
    
        from PIL import Image
        all_images = []
        all_images.extend(hipporaw_output_files)
        import string
        subjects = set()
        images_by_subject = {}
        for each, att in zip(hipporaw_output_files, self.preferences['attributes']):
          subject = att[2]
          side = string.split(each, 'hipporaw_')[1][0]
          subjects.add(subject)
          images_by_subject.setdefault(subject, {})
          images_by_subject[subject].setdefault(side, []).append(each)
    
        print subjects
        for subject in subjects:
          for side in images_by_subject[subject]:
            print subject
            print images_by_subject[subject][side]
            if images_by_subject[subject][side][0][-5] == 'C':
                c = images_by_subject[subject][side][0]
                s = images_by_subject[subject][side][1]
            elif images_by_subject[subject][side][0][-5] == 'S':
                c = images_by_subject[subject][side][1]
                s = images_by_subject[subject][side][0]
            else:
                print 'ERROR'
    
            c_im = Image.open(c)
            s_im = Image.open(s)
            w_c, h_c = c_im.size
            w_s, h_s = s_im.size
    
            margin_h = 200
            margin_w = 100
            whole_image  = Image.new('RGB', (max(w_s, w_c) + 2 * margin_w, 2 * max(h_s, h_c) + 3 * margin_h), 'white')
    
            whole_image.paste(s_im, (margin_w, margin_h) )
            whole_image.paste(c_im, (margin_w, h_s + 2 * margin_h) )
    
            from PyQt4 import Qt
    
            font = Qt.QFont('Times', 100)
            data = whole_image.convert('RGBA').tostring('raw', 'BGRA')
            qim  = Qt.QImage(data, whole_image.size[0], whole_image.size[1], Qt.QImage.Format_ARGB32)
            pix  = Qt.QPixmap.fromImage(qim)
            side = {'L': 'left', 'R': 'right'}[side]
            pix  = __render_text(pix, 'subject : %s (%s hemisphere)'%(subject, side), font, (20, 120) )
            whole_image = qt_to_pil_image(pix)
    
            whole_image.save(self.preferences['output_path'] + '/QCSACHA_label_%s_%s.png'%(subject, side), 'PNG')
            side = {'left': 'L', 'right': 'R'}[side]
            import os
            command = ['rm ' + c]
            os.system( *command )
            command = ['rm ' + s]
            os.system( *command )



class HippocampusLabelSnapBase(SnapBase):

    def __init__(self, preferences):
        SnapBase.__init__(self, preferences)
        self._do_slice_rendering = True

    def get_list_diskitems(self, verbose=True):

        if self.preferences['type_database'] == 'SACHA':
            from brainvisa.snapbase.snapbase.diskItemBrowser import SnapBaseItemBrowser

            dictdata = []
            import neuroHierarchy, neuroProcesses
    
            id_types = ['Left automatic HA label subvolume', 'Right automatic HA label subvolume']
            d = SnapBaseItemBrowser(neuroHierarchy.databases, required={'_type': id_types})
            res = d.exec_()
            if res == d.Accepted:
              for each in d.getValues():
                  rdi = neuroHierarchy.ReadDiskItem('T1 MRI', neuroProcesses.getAllFormats())
                  mri = rdi.findValue(each)
                  dictdata.append(((each.get('subject'), each.get('protocol')),
                     {'type' : 'Label Hippocampus',
                      'mri' : mri,
                      'hippo' : each}) )
            print dictdata
            return dictdata
            
        elif self.preferences['type_database'] == 'SACHA_old':
          raise NotImplementedError()
        
        
    
    def get_slices_of_interest(self, data):

        slices = {}
        directions = ['C', 'S']

        # Unpacking data
        hippo, mri = data
        voxel_size = mri.header()['voxel_size']
        header = mri.header()

        hippo_minmax = detect_slices_of_interest(hippo, directions)

        count_pas1 = 0
        count_pas2 = 0
        for d in directions :
            d_minmax = (hippo_minmax[d][0], hippo_minmax[d][1])
            slices_list = []
            nb_of_slices = {'S': 7, 'C':10}[d]
            nb_coupes = d_minmax[1]-d_minmax[0]
            for i in xrange(nb_of_slices):
              if d == "C":
                offset = round((8.0*nb_coupes)/50.0)
                pas1 = (3.0*nb_coupes)/50.0
                pas2 = (8.0*nb_coupes)/50.0
                if (count_pas1 < 5):
                  slices_list.append(round(d_minmax[0] + offset + count_pas1*pas1))
                  count_pas1 = count_pas1 + 1;
                else:
                  if (count_pas1 < 8):
                    count_pas2 = count_pas2 + 1
                    slices_list.append(round(d_minmax[0] + offset + (count_pas1-count_pas2)*pas1 + count_pas2*pas2))
                    count_pas1 = count_pas1 + 1
                  else:
                    if (count_pas1 < 9):
                      slices_list.append(round(d_minmax[0] + offset + (count_pas1-count_pas2)*pas1 + count_pas2*pas2))
                      count_pas1 = count_pas1 + 1
                    else:
                      count_pas1 = count_pas1 + 1
                      slices_list.append(d_minmax[1])
              else:
                offset = (8*nb_coupes)/26
                if self.preferences['side'] == "right":
                  slices_list.append(d_minmax[0] + i*(d_minmax[1]-offset)/6)
                else:
                  slices_list.append(d_minmax[0] + offset + i*(d_minmax[1]-offset)/6)
            print("slices list : ", slices_list)
            # This converts each slice index into a list applicable to
                # Anatomist camera function
            slices[d] = [(i, self.__get_slice_position__(d, i, voxel_size)) for i in slices_list]

        return slices


    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')
        self.preferences['side'] = diskitems['hippo'].get('hemisphere')
        hippo = aims.read(diskitems['hippo'].fileName())
        mri = aims.read(diskitems['mri'].fileName())
        return hippo, mri


    def set_viewer(self, data, w):

        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        hippo, mri = data

        ana_hippo = a.toAObject(hippo)
        ana_mri = a.toAObject(mri)
        for each in ana_hippo, ana_mri:
            each.releaseAppRef()

        # Fusion of the two masks
        palette = a.getPalette('RAINBOW')
        ana_hippo.setPalette( palette )
        self.aobjects['hippo'] = a.fusionObjects( [ana_mri, ana_hippo], method='Fusion2DMethod' )
        a.execute("Fusion2DParams", object=self.aobjects['hippo'], mode='linear', rate = 0.7,
                      reorder_objects = [ ana_mri, ana_hippo] )

        # Load in Anatomist window
        window = a.AWindow(a, w)
        window.assignReferential( a.centralReferential()  )
        a.addObjects( self.aobjects['hippo'], [window] )

        return window



class HippocampusRawSnapBase(HippocampusLabelSnapBase):

    def __init__(self, output_path):
        HippocampusLabelSnapBase.__init__(self, output_path)
        self._do_slice_rendering = False

    def set_viewer(self, data, w):

        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        hippo, mri = data

        ana_mri = a.toAObject(mri)
        for each in [ana_mri]:
            each.releaseAppRef()

        # Fusion of the two masks
        palette = a.getPalette('B-W LINEAR')
        ana_mri.setPalette( palette )
        self.aobjects['mri'] = ana_mri

        # Load in Anatomist window
        window = a.AWindow(a, w)
        window.assignReferential( a.centralReferential()  )
        a.addObjects( self.aobjects['mri'], [window] )

        return window


