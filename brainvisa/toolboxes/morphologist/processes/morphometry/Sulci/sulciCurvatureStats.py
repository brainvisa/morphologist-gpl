# -*- coding: utf-8 -*-
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
import registration
from brainvisa.data.labelSelection import LabelSelection
try:
  import soma.workflow.client as sw
  import pickle
except:
  sw = None

name = 'Sulci Curvature Stats'
userLevel = 0

signature = Signature(
  'graphs', ListOf( ReadDiskItem( 'Labelled Cortical Folds Graph',
    'Graph and data' ) ),
  'output_csv', WriteDiskItem( 'CSV file', 'CSV file' ),
  'include_nodewise', Boolean(),
  'nomenclature', ReadDiskItem( 'Nomenclature', 'Hierarchy' ),
  'model', ReadDiskItem( 'Model graph', 'Graph' ),
  'region_selection', LabelSelection(),
  'label_attribute', Choice( 'auto', 'label', 'name' ),
  'mode', Choice( ( _t_( 'Run now' ), 0 ),
    ( _t_( 'build soma-workflow' ), 1 ) ),
  'workflow_file',  WriteDiskItem( 'Text file', 'Text file' ),
)


def initialization( self ):
  def change_region( self, proc ):
    if self.model:
      mod = self.model.fullPath()
    else:
      mod = None
    if self.nomenclature:
      nom = self.nomenclature.fullPath()
    else:
      nom = None
    sel = self.region_selection
    if sel is None:
      sel = LabelSelection( mod, nom )
    else:
      sel.value[ 'model' ] = mod
      sel.value[ 'nomenclature' ] = nom
    return sel

  def linkModel( self, proc ):
    if self.graphs is not None and len( self.graphs ) != 0:
      return self.signature[ 'model' ].findValue( self.graphs[0] )
    return None

  self.include_nodewise = False
  self.nomenclature = self.signature[ 'nomenclature' ].findValue( {} )
  self.setOptional( 'model', 'nomenclature', 'region_selection' )
  self.linkParameters( 'model', 'graphs', linkModel )
  self.linkParameters( 'region_selection', ( 'model', 'nomenclature' ),
    change_region )
  self.setOptional( 'workflow_file' )


def execution( self, context ):
  self.region_selection.writeSelection( context )
  if self.region_selection.isValid():
    sfile = self.region_selection.file
  else:
    sfile = None
  if self.mode == 1 and sw is None:
    context.write( 'sorry, soma-workflow is not working. Running locally.' )
    self.mode = 0
  if self.mode == 1:
    jobs = []
  ns = len( self.graphs )
  n = 0
  for g in self.graphs:
    subject = g.get( 'subject', None )
    cmd = [ 'sulciCurvature.py', '-i', g.fullPath(),
      '-o', self.output_csv.fullPath(), '-a' ]
    if subject:
      cmd += [ '-s', subject ]
    if self.label_attribute == 'auto':
      if g.get( 'manually_labelled', 'No' ) == 'Yes':
        cmd += [ '-l', 'name' ]
      else:
        cmd += [ '-l', 'label' ]
    else:
      cmd += [ '-l', self.label_attribute ]
    if self.include_nodewise:
      cmd.append( '-n' )
    if sfile is not None:
      cmd += [ '-t', sfile.fullPath() ]
    elif self.nomenclature is not None and self.model is not None:
      cmd += [ '-t', self.nomenclature.fullPath() ]
      if self.model is not None:
        cmd += [ '--modeltrans', self.model.fullPath() ]
    context.progress( n, ns, process=self )
    context.write( 'processing subject', n+1, '/', ns, ':', g, '...' )
    if self.mode == 0:
      context.system( *cmd )
    else:
      jobs.append( sw.Job( command=cmd, name='subject %d' %n ) )
    n += 1

    context.progress( ns, ns, process=self )

  if self.mode == 1:
    if self.workflow_file is None:
      raise ValueError( 'workflow_file is not specified' )
    wf = sw.Workflow( jobs=jobs, dependencies=[] )
    sw.Helper.serialize( self.workflow_file.fullPath(), wf )

