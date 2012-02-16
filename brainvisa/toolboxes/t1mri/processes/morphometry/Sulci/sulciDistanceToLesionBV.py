from neuroProcesses import *
from brainvisa.data.labelSelection import LabelSelection
import registration

name = 'Sulci Distance to Lesion'
userLevel = 2


signature = Signature(
  'lgrey_white', ReadDiskItem( 'Left grey white mask',
    'Aims readable volume formats' ),
  'rgrey_white', ReadDiskItem( 'Right grey white mask',
    'Aims readable volume formats' ),
  'lesion_mask', ReadDiskItem( 'Lesion Mask', 'Aims readable volume formats' ),
  'distance_map', WriteDiskItem( 'Lesion distance map',
    'Aims readable volume formats' ),
  'lgraph', ReadDiskItem( 'Labelled Cortical Folds Graph',
    'Graph and data', requiredAttributes={ 'side' : 'left' } ),
  'rgraph', ReadDiskItem( 'Labelled Cortical Folds Graph',
    'Graph and data', requiredAttributes={ 'side' : 'right' } ),
  'output_csv', WriteDiskItem( 'CSV file', 'CSV file' ),
  'nomenclature', ReadDiskItem( 'Nomenclature', 'Hierarchy' ),
  'model', ReadDiskItem( 'Model graph', 'Graph' ),
  'region_selection', LabelSelection(),
  'label_attribute', Choice( 'auto', 'label', 'name' ),
  'reuse_existing_distancemap', Boolean(),
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
    if self.lgraph is not None and self.rgraph is None:
      return self.signature[ 'model' ].findValue( self.lgraph )
    elif self.lgraph is None and self.rgraph is not None:
      return self.signature[ 'model' ].findValue( self.rgraph )
    return None

  self.nomenclature = self.signature[ 'nomenclature' ].findValue( {} )
  self.setOptional( 'model', 'nomenclature', 'region_selection',
    'distance_map', 'lgraph', 'rgraph', 'lgrey_white', 'rgrey_white',
    'lesion_mask' )
  self.linkParameters( 'rgrey_white', 'lgrey_white' )
  self.linkParameters( 'lgraph', 'lgrey_white' )
  self.linkParameters( 'rgraph', 'lgraph' )
  self.linkParameters( 'lesion_mask', 'lgrey_white' )
  self.linkParameters( 'model', ( 'lgraph', 'rgraph' ), linkModel )
  self.linkParameters( 'region_selection', ( 'model', 'nomenclature' ),
    change_region )
  self.linkParameters( 'distance_map', 'lesion_mask' )
  self.reuse_existing_distancemap = False


def execution( self, context ):
  self.region_selection.writeSelection( context )
  if self.region_selection.isValid():
    sfile = self.region_selection.file
  else:
    sfile = None
  graphs = [ x for x in ( self.lgraph, self.rgraph ) if x is not None ]
  cmd = [ 'sulciDistanceToLesion.py', '-o', self.output_csv ]
  if self.lgrey_white is not None and self.rgrey_white is not None \
    and self.lesion_mask is not None:
    cmd += [ '-L', self.lgrey_white, '-R', self.rgrey_white,
      '-l', self.lesion_mask ]
  elif self.distance_map is None or not self.reuse_existing_distancemap:
    raise RuntimeError( 'either lgrey_white, rgrey_white and lesion_mask, ' \
      'or distance_map and reuse_existing_distancemap, should be specified.' )
  if self.distance_map is not None:
    if self.reuse_existing_distancemap \
      and os.path.exists( self.distance_map.fullPath() ):
      cmd += [ '--indistance', self.distance_map ]
    else:
      cmd += [ '-d', self.distance_map ]
  if sfile is not None:
    cmd += [ '-t', sfile ]
  elif self.nomenclature is not None and self.model is not None:
    cmd += [ '-t', self.nomenclature ]
    if self.model is not None:
      cmd += [ '--modeltrans', self.model ]
  if len( graphs ) != 0:
    g = graphs[0]
    subject = g.get( 'subject', None )
    if subject:
      cmd += [ '-s', subject ]
    if self.label_attribute == 'auto':
      if g.get( 'manually_labelled', 'No' ) == 'Yes':
        cmd += [ '-l', 'name' ]
      else:
        cmd += [ '--labelatt', 'label' ]
    else:
      cmd += [ '--labelatt', self.label_attribute ]
  for g in graphs:
    cmd += [ '-g', g ]
  context.system( *cmd )

