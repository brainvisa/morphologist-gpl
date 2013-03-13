#!/usr/bin/python
import pyinotify
import sys, os
from brainvisa import checkbase as c
from brainvisa.checkbase.report import HTMLReportGenerator

global html_pathname, template_pathname, read_modules, cbdir

def process_module(c):
   global read_modules
   html = ''
   from inspect import getmembers, isfunction, getdoc, ismethod, isclass, ismodule
   import imp, sys
   imp.reload(c)
   print c.__name__

   functions_html = '<h3>%s</h3><br/>'%c.__name__
   for each in getmembers(c, isfunction):
      doc = getdoc(each[1])
      if doc: doc = '<br/>'.join(doc.split('\n'))
      functions_html += '<b>%s</b><br/>'%each[0]# : <div>%s</div><br/>'%(each[0], doc)


   classes = getmembers(c, isclass)
   classes_html = ''
   for each_class in classes:
    if not each_class[0] in read_modules:
      print each_class[0], read_modules
      read_modules.append(each_class[0])
      methods = {}
      classes_html += '<h3>%s</h3><br/>'%each_class[0]
      for each in getmembers(each_class[1], ismethod):
         methods[each[0]] = getdoc(each[1])
         doc = getdoc(each[1])
         if doc: doc = '<br/>'.join(doc.split('\n'))
         classes_html += '&nbsp;&nbsp;<b>%s</b><br/>'%each[0] # : <div>%s</div><br/>'%(each[0], doc)
      classes_html += '<br/>'

   html += functions_html + '<br>' + classes_html #g.generate_from_template(template_pathname, conversion_hashtable)

   modules = getmembers(c, ismodule)

   for m in modules:
      if not m[0] in ['os', 'sys'] and not m[0] in read_modules:
         read_modules.append(m[0])
         html += process_module(m[1]) + '<br><hr><br>'
   return html

def update(ev):
   print ev
   global html_pathname, template_pathname, read_modules
   read_modules = []

   from brainvisa import checkbase as c
   import imp, time, sys
   time.sleep(1)
   imp.reload(c)

   html = ''
   html = process_module(c)
   ht = {'$BODY' : html}
   g = HTMLReportGenerator()
   html = g.generate_from_template(template_pathname, ht)

   with open(html_pathname, 'wb') as f:
      f.write(html)

   import os
   old_dir = os.path.realpath(os.curdir)
   os.chdir('/tmp')

   import pdf
   p = pdf.PDFReportPrinter('/tmp/report_tmp.pdf', html=html)
   p.print_()

   os.system('pdftk /tmp/report_tmp.pdf dump_data output /tmp/report.txt')
   with open('/tmp/report.txt', 'rb') as f:
      t=f.readlines()
      nb_pages = int(t[-1].rstrip('\n').split(' ')[1])
      print nb_pages, 'pages'

   import math
   p = pdf.PDFReportPrinter('/tmp/report_tmp.pdf', html=html, doc_height = math.exp(-1/float(nb_pages)) * 70.0 / 0.24)
   p.print_()

   os.system('rm -rf /tmp/pg*.pdf')
   os.system('rm -rf /tmp/pg*.jpg')

   os.system('pdftk /tmp/report_tmp.pdf burst output /tmp/pg_%05d.pdf')
   from glob import glob
   for each in glob('/tmp/pg_*.pdf'):
      os.system("convert -verbose -colorspace RGB -resize 800 -interlace none -density 300 -quality 80 %s `echo %s | sed 's/\.pdf$/\.jpg/'`"%(each,each))
   os.system("montage /tmp/pg*.jpg -geometry +0+0 -tile x1 /tmp/report.pdf")
   os.chdir(old_dir)

   print 'done'


if __name__ == '__main__':
   global template_pathname, html_pathname, cbdir
   if len(sys.argv) < 4:
      print "usage : monitor.py checkbase_directory template_file html_file [loop]"
      exit(0)
   cbdir = sys.argv[1]
   template_pathname = sys.argv[2]
   html_pathname = sys.argv[3]
   assert(os.path.exists(cbdir))
   assert(os.path.exists(template_pathname))
   directories = []
   import string, sys
   from PyQt4 import Qt
   qt_app = Qt.QApplication(sys.argv)

   for root, dirs, files in os.walk(cbdir):
      if '.svn' in string.split(root, os.path.sep): continue
      directories.append(root)
   print directories

   update(None)

   if len(sys.argv) == 5 and sys.argv[4] == 'loop':
      wm = pyinotify.WatchManager()
      notifier = pyinotify.Notifier(wm)
      wdd = wm.add_watch(directories, pyinotify.IN_MODIFY, update)
      notifier.loop()
