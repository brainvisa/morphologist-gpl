#!/usr/bin/python
import pyinotify
import sys, os
from brainvisa import checkbase as c
from brainvisa.checkbase.report import HTMLReportGenerator

global html_pathname, template_pathname, read_modules

def process_module(c):
   global read_modules
   html = ''
   from inspect import getmembers, isfunction, getdoc, ismethod, isclass, ismodule
   print c.__name__

   functions_html = '<h3>%s</h3><br/>'%c.__name__
   for each in getmembers(c, isfunction):
      doc = getdoc(each[1])
      if doc: doc = '<br/>'.join(doc.split('\n'))
      functions_html += '<b>%s</b><br/>'%each[0]# : <div>%s</div><br/>'%(each[0], doc)


   classes = getmembers(c, isclass)
   classes_html = ''
   for each_class in classes:
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
      if m[0] not in ['os', 'sys'] and m[0] not in read_modules:
         read_modules.append(m[0])
         html += process_module(m[1]) + '<br><hr><br>'
   print html
   return html

def echototo(ev):
   global html_pathname, template_pathname, read_modules
   read_modules = []
   from brainvisa import checkbase as c
   html = ''
   html = process_module(c)
   ht = {'$BODY' : html}
   g = HTMLReportGenerator()
   html = g.generate_from_template(template_pathname, ht)

#   from brainvisa.checkbase import check as c
#   html += process_module(ch)

   with open(html_pathname, 'wb') as f:
      #html =
      f.write(html)

   print 'done'


if __name__ == '__main__':
   global template_pathname, html_pathname
   if len(sys.argv) < 4:
      print "usage : monitor.py checkbase_directory template_file html_file"
      exit(0)
   cbdir = sys.argv[1]
   template_pathname = sys.argv[2]
   html_pathname = sys.argv[3]
   assert(os.path.exists(cbdir))
   assert(os.path.exists(template_pathname))
   assert(os.path.exists(html_pathname))
#   python_files = []
#   for root, dirs, files in os.walk(cbdir):
#      for f in files:
#         name, ext = os.path.splitext(f)
#         if ext == '.py':
#            python_files.append(os.path.join(root, f))
   wm = pyinotify.WatchManager()
   notifier = pyinotify.Notifier(wm)
   directories = []
   import string
   for root, dirs, files in os.walk(cbdir):
      if '.svn' in string.split(root, os.path.sep): continue
      directories.append(root)
   print directories
   wdd = wm.add_watch(directories, pyinotify.IN_MODIFY, echototo)
   notifier.loop()
