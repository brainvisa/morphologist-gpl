# -*- coding: utf-8 -*-
from brainvisa.snapbase.snapbase import SnapBase
from brainvisa.snapbase.snapbase.interface import Ui_attributes_window

def detect_slices_of_interest(data, slice_directions=['A']):
    '''
    Returns a set of slices of interest : { 'S': [5,10,15,20],
                                            'C': [10,11,12,13] }
    (Only whasa selection)
    '''

    d = data.arraydata()
    _, n_slices_ax, n_slices_co, n_slices_sa = d.shape
    slices_minmax = {}
    for direction in slice_directions:
        if direction == 'A':
          # On vire les deux premières et dernières car elles sont parfois "coupées"
          first_nonempty_slice = 2
          last_nonempty_slice = n_slices_ax - 3
          slices_minmax[direction] = (first_nonempty_slice, last_nonempty_slice)
    return slices_minmax






class WhasaSnapBase(SnapBase):

    def __init__(self, output_path):
        SnapBase.__init__(self, output_path)

    def snap(self):
       self.main_window.setEnabled(False)
       labelsnapbase = WhasaLabelSnapBase(self.preferences)
       labelsnapbase.snap_base(None, self.qt_app)
       dictdata = labelsnapbase.dictdata
       if len(dictdata) != 0:
         whasa_output_files = self.preferences['output_files']
         rawsnapbase = WhasaRawSnapBase(self.preferences)
         rawsnapbase.snap_base(None, self.qt_app, dictdata=dictdata)
         raw_output_files = self.preferences['output_files']
         res = self.whasa_recompose(whasa_output_files, raw_output_files)
         self.create_png_whasa_report(res)
       self.main_window.setEnabled(True)
       
    def whasa_recompose(self, whasa_output_files, raw_output_files):
      from PIL import Image
      import os, string
      # recompose each subject's snapshot
      tiled_images_outpath = {}
      for w_path, r_path, att in zip(whasa_output_files, raw_output_files, self.preferences['attributes']):
          direction = w_path[-6:-4]
          print("direction: ", direction)
          whasa = Image.open(w_path)
          raw   = Image.open(r_path)
          w1, h1 = whasa.size
          w2, h2 = raw.size
          tile_w1, tile_h1 = int(whasa.size[0]/7.0), int(whasa.size[1]/1.0)
          print h1, w1, h2, w2
          views_images = []
          margin = 10
          for j in xrange(1):
              for i in xrange(7):
                  tile_whasa = whasa.crop((i*tile_w1, j*tile_h1, (i+1)*tile_w1, (j+1)*tile_h1))
                  tile_raw = raw.crop((i*tile_w1, j*tile_h1, (i+1)*tile_w1, (j+1)*tile_h1))
                  both_tiles = Image.new('RGBA', (tile_whasa.size[0] + 2 * margin, tile_whasa.size[1] * 2 + 4 * margin), 'white')
                  both_tiles.paste(tile_whasa, (margin, margin))
                  both_tiles.paste(tile_raw, (margin, tile_whasa.size[1] + 3 * margin))
                  views_images.append(both_tiles)
  
          # Building the tiled image
          image_size = (max([im.size[0] for im in views_images]), max([im.size[1] for im in views_images]))
          grid_dim = {12 : (4,3), 14 : (7,2), 5 : (5,1), 10:(10,1), 7:(7,1), 1 : (1,1), 3: (3,1), 20 : (4,5)}[len(views_images)]
  
          tiled_image = Image.new('RGBA', (grid_dim[0] * image_size[0], grid_dim[1] * image_size[1]), 'black')
          positions = [[j*image_size[0], i*image_size[1]] for i in xrange(grid_dim[1]) for j in xrange(grid_dim[0])]
          for i, pos in zip(views_images, positions):
              pos = [pos[j] + (image_size[j] - min(image_size[j], i.size[j]))/2.0 for j in xrange(len(pos))]
              tiled_image.paste(i, (int(pos[0]), int(pos[1])))
          tiled_image.save(r_path, 'PNG')
          subject = att[2]
          #tiled_outpath = self.preferences['output_path'] + '/QCWHASA_label_%s_%s.png'%(subject, direction)
          #tiled_image.save(tiled_outpath, 'PNG')
          tiled_images_outpath.setdefault(subject, []).append(r_path)
      return tiled_images_outpath
          

    def create_png_whasa_report(self, images_by_subject):
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

      for subject in images_by_subject:
          print subject
          whasa = images_by_subject[subject]
  
          whasa_a_im = Image.open(whasa[0])
          whasa_b_im = Image.open(whasa[1])
          w_whasa_a, h_whasa_a = whasa_a_im.size
          w_whasa_b, h_whasa_b = whasa_b_im.size
  
          margin_h = 200
          margin_w = 100
 
          whole_image = Image.new('RGB', (max(w_whasa_a, w_whasa_b) + 2 * margin_w, 2 * max(h_whasa_a, h_whasa_b) + 3 * margin_h), 'white')
          whole_image.paste(whasa_a_im, (margin_w, margin_h) )
          whole_image.paste(whasa_b_im, (margin_w, 2*margin_h + h_whasa_a) )
  
          from PyQt4 import Qt
  
          font = Qt.QFont('Times', 100)
          data_left = whole_image.convert('RGBA').tostring('raw', 'BGRA')
          qim_left  = Qt.QImage(data_left, whole_image.size[0], whole_image.size[1], Qt.QImage.Format_ARGB32)
          pix_left  = Qt.QPixmap.fromImage(qim_left)
          pix_left  = __render_text(pix_left, 'subject : %s'%subject, font, (20, 120) )
          whole_image = qt_to_pil_image(pix_left)
  
          whole_image.save(self.preferences['output_path'] + '/QCWHASA_label_%s.png'%subject, 'PNG')



class WhasaLabelSnapBase(SnapBase):

    def __init__(self, output_path):
        SnapBase.__init__(self, output_path)
        self._do_slice_rendering = True

    def get_slices_of_interest(self, data):
        slices = {}
        directions = ['A']

        # Unpacking data
        whasa_seg, mri = data
        voxel_size = mri.header()['voxel_size']

        whasa_minmax = detect_slices_of_interest(whasa_seg, directions)

        count_pas = 0
        for d in directions :
            d_minmax = (whasa_minmax[d][0], whasa_minmax[d][1])
            slices_list = []
            slices_list_wmh  = []
            slices_list_vide = []
            nb_of_slices = {'A': 14}[d]

            # récupérer les coupes avec et sans segmentation
            ws = whasa_seg.arraydata()
            i  = d_minmax[0]
            j  = d_minmax[1]
            while i != j+1:
              if sum(sum(ws[0][i])) == 0:
                tampo_slices = []
                tampo_slices.append(i)
                tampo_slices.append(sum(sum(ws[0][i])))
                slices_list_vide.append(tampo_slices)
              else:
                tampo_slices = []
                tampo_slices.append(i)
                tampo_slices.append(sum(sum(ws[0][i])))
                slices_list_wmh.append(tampo_slices)
              i += 1

            import operator
            slices_list_wmh = sorted(slices_list_wmh, key=operator.itemgetter(1))
            print("###slices list wmh : ", slices_list_wmh)
            print("###slices list vide : ", slices_list_vide)

            # On choisir les coupes de manière intelligente :
              # 4 coupes sans wmh (si il y a)
              # 5 coupes avec les plus grosses lésions (si il y a)
              # 5 coupes avec wmh (si il y a)
            #from random import choice
            #random_slice = choice(slices_list_vide)
            #slices_list.append(random_slice)
            #slices_list_vide.remove(random_slice)
            n_vide = len(slices_list_vide)
            n_wmh  = len(slices_list_wmh)
            delta_vide = 0
            delta_wmh  = 0

            if n_vide < 4:
              # il va manquer des coupes sans wmh
              delta_vide = 4-n_vide
              for slice, vox in slices_list_vide:
                slices_list.append(slice)

            if n_wmh < 10:
              # il va manquer des coupes avec wmh
              delta_wmh = 10-n_wmh
              for slice, vox in slices_list_wmh:
                slices_list.append(slice)

            if n_vide >= 4:
              # il faut prendre des coupes aléatoires
              i=0

              while i < 4+delta_wmh:
                pas = n_vide / float(4+delta_wmh)
                slices_list.append(slices_list_vide[int(round(pas*i))][0])
                i += 1

            if n_wmh >= 10:
              # il faut prendre des coupes aléatoires
              i=0
              while i < 5:
                # On prend les 5 coupes avec le plus de wmh segmenté
                max_wmh_slice = slices_list_wmh[len(slices_list_wmh)-1]
                slices_list.append(max_wmh_slice[0])
                slices_list_wmh.remove(max_wmh_slice)
                i+=1
              i=0
              slices_list_wmh = sorted(slices_list_wmh, key=operator.itemgetter(0))
              n_wmh  = len(slices_list_wmh)
              while i < 5+delta_vide:
                pas = n_wmh / float(5+delta_vide)
                slices_list.append(slices_list_wmh[int(round(pas*i))][0])
                i += 1

            slices_list = sorted(slices_list)
            print("slices list : ", slices_list)
            slices[d] = [(i, self.__get_slice_position__(d, i, voxel_size)) for i in slices_list]

        return slices



    def get_list_diskitems(self, verbose=True):

            from brainvisa.snapbase.snapbase.diskItemBrowser import SnapBaseItemBrowser

            dictdata = []
            import neuroHierarchy, neuroProcesses
    
            id_type = 'WMH Lesion Mask'
            d = SnapBaseItemBrowser(neuroHierarchy.databases, required={'_type': id_type})
            res = d.exec_()
            if res == d.Accepted:
              for each in d.getValues():
                  rdi = neuroHierarchy.ReadDiskItem('SPM FLAIR MRI Bias Corrected', neuroProcesses.getAllFormats())
                  mri = rdi.findValue(each)
                  dictdata.append(((each.get('subject'), each.get('protocol')),
                     {'type' : 'Whasa Segmentation',
                      'mri' : mri,
                      'whasa_seg' : each}) )
            print dictdata
            return dictdata



    def read_data(self, diskitems):

        from soma import aims
        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        whasa_seg = aims.read(diskitems['whasa_seg'].fileName())
        mri       = aims.read(diskitems['mri'].fileName())
        return whasa_seg, mri


    def set_viewer(self, data, w):

        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        whasa_seg, mri = data

        ana_whasa = a.toAObject(whasa_seg)
        ana_mri   = a.toAObject(mri)
        for each in ana_whasa, ana_mri:
            each.releaseAppRef()

        # Fusion of the two masks
        palette = a.getPalette('RAINBOW')
        ana_whasa.setPalette( palette )
        self.aobjects['whasa_seg'] = a.fusionObjects( [ana_mri, ana_whasa], method='Fusion2DMethod' )
        a.execute("Fusion2DParams", object=self.aobjects['whasa_seg'], mode='linear', rate = 0.7,
                      reorder_objects = [ ana_mri, ana_whasa] )

        # Load in Anatomist window
        window = a.AWindow(a, w)
        window.assignReferential( a.centralReferential()  )
        a.addObjects( self.aobjects['whasa_seg'], [window] )

        return window



class WhasaRawSnapBase(WhasaLabelSnapBase):

    def __init__(self, output_path):
        WhasaLabelSnapBase.__init__(self, output_path)
        self._do_slice_rendering = False

    def set_viewer(self, data, w):

        import anatomist.direct.api as ana
        a = ana.Anatomist('-b')

        whasa_seg, mri = data

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
