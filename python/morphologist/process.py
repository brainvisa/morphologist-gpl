try:
  from traits.api import File, Float, Int
except ImportError:
  from enthought.traits.api import File, Float, Int

from soma.pipeline.process import Process
from soma.pipeline.pipeline import Pipeline

    
class SPMNormalization( Process ):
  def __init__( self, **kwargs ):
    super( SPMNormalization, self ).__init__( **kwargs )
    self.add_trait( 'image', File( exists=True ) )
    self.add_trait( 'template', File( exists=True ) )
    self.add_trait( 'normalized', File() )

    
class BiasCorrection( Process ):
  def __init__( self, **kwargs ):
    super( BiasCorrection, self ).__init__( **kwargs )
    self.add_trait( 't1mri', File( exists=True ) )
    self.add_trait( 'field_rigidity', Float() )
    self.add_trait( 'nobias', File() )

    
class HistoAnalysis( Process ):
  def __init__( self, **kwargs ):
    super( HistoAnalysis, self ).__init__( **kwargs )
    self.add_trait( 'image', File( exists=True ) )
    self.add_trait( 'histo_analysis', File() )

    
class BrainMask( Process ):
  def __init__( self, **kwargs ):
    super( BrainMask, self ).__init__( **kwargs )
    self.add_trait( 't1mri', File( exists=True ) )
    self.add_trait( 'histo_analysis', File( exists=True ) )
    self.add_trait( 'brain_mask', File() )

    
class SplitBrain( Process ):
  def __init__( self, **kwargs ):
    super( SplitBrain, self ).__init__( **kwargs )
    self.add_trait( 't1mri', File( exists=True ) )
    self.add_trait( 'histo_analysis', File( exists=True ) )
    self.add_trait( 'brain_mask', File( exists=True ) )
    self.add_trait( 'split_brain', File() )

    
class GreyWhiteClassification( Process ):
  def __init__( self, **kwargs ):
    super( GreyWhiteClassification, self ).__init__( **kwargs )
    self.add_trait( 't1mri', File( exists=True ) )
    self.add_trait( 'label_image', File( exists=True ) )
    self.add_trait( 'label', Int( optional=True ) )
    self.add_trait( 'gw_classification', File() )


class GreyWhiteSurface( Process ):
  def __init__( self, **kwargs ):
    super( GreyWhiteSurface, self ).__init__( **kwargs )
    self.add_trait( 't1mri', File( exists=True ) )
    self.add_trait( 'gw_classification', File( exists=True ) )
    self.add_trait( 'hemi_cortex', File() )
    self.add_trait( 'white_mesh', File() )

    
class SphericalHemisphereSurface( Process ):
  def __init__( self, **kwargs ):
    super( SphericalHemisphereSurface, self ).__init__( **kwargs )
    self.add_trait( 'gw_classification', File( exists=True ) )
    self.add_trait( 'hemi_cortex', File( exists=True ) )
    self.add_trait( 'hemi_mesh', File() )


class GreyWhite( Pipeline ):
  def pipeline_definition( self ):
    self.add_trait( 't1mri', File( exists=True ) )
    
    self.add_process( 'gw_classification', GreyWhiteClassification() )
    self.add_link( 't1mri->gw_classification.t1mri' )
    
    self.add_process( 'gw_surface', GreyWhiteSurface() )
    self.add_link( 't1mri->gw_surface.t1mri' )
    self.add_link( 'gw_classification.gw_classification->gw_surface.gw_classification' )
    self.export_parameter( 'gw_classification', 'gw_classification' )
    
    self.add_process( 'hemi_surface', SphericalHemisphereSurface() )
    self.add_link( 'gw_classification.gw_classification->hemi_surface.gw_classification' )
    self.add_link( 'gw_surface.hemi_cortex->hemi_surface.hemi_cortex' )
    self.export_parameter( 'gw_surface', 'hemi_cortex' )



class Morphologist( Pipeline ):
  def pipeline_definition( self ):
    self.add_trait( 't1mri', File(  exists=True ) )
    
    self.add_process( 'normalization', 'morphologist.process.SPMNormalization' )
    self.add_switch( 'select_normalization', [ 'spm', 'none' ], 't1mri' )
    self.add_process( 'bias_correction', BiasCorrection() )
    #self.export_parameter( 'bias_correction', 't1mri' )
    #self.export_parameter( 'normalization', 'image' )
    #self.add_link( 't1mri->normalization.image' )

    self.add_link( 'normalization.normalized->select_normalization.spm' )
    self.add_link( 't1mri->select_normalization.none' )
    self.add_link( 't1mri->normalization.image' )

    self.add_link( 'select_normalization.t1mri->bias_correction.t1mri' )
    self.export_parameter( 'bias_correction', 'nobias' )
    
    self.add_process( 'histo_analysis', HistoAnalysis() )
    self.add_link( 'bias_correction.nobias->histo_analysis.image' )
    
    self.add_process( 'brain_mask', BrainMask() )
    self.add_link( 'select_normalization.t1mri->brain_mask.t1mri' )
    self.add_link( 'histo_analysis.histo_analysis->brain_mask.histo_analysis' )
    self.export_parameter( 'brain_mask', 'brain_mask' )
    
    self.add_process( 'split_brain', SplitBrain() )
    self.add_link( 'select_normalization.t1mri->split_brain.t1mri' )
    self.add_link( 'histo_analysis.histo_analysis->split_brain.histo_analysis' )
    self.add_link( 'brain_mask.brain_mask->split_brain.brain_mask' )
    
    self.add_process( 'left_grey_white', GreyWhite(), label=1 )
    self.export_parameter( 'left_grey_white', 'label', None )
    self.add_link( 'select_normalization.t1mri->left_grey_white.t1mri' )
    self.add_link( 'split_brain.split_brain->left_grey_white.label_image' )
    self.export_parameter( 'left_grey_white', 'gw_classification', 'left_gw_classification' )
    self.export_parameter( 'left_grey_white', 'hemi_cortex', 'left_hemi_cortex' )
    self.export_parameter( 'left_grey_white', 'hemi_mesh', 'left_hemi_mesh' )
    self.export_parameter( 'left_grey_white', 'white_mesh', 'left_white_mesh' )
    
    self.add_process( 'right_grey_white', GreyWhite(), label=2 )
    self.export_parameter( 'right_grey_white', 'label', None )
    self.add_link( 'select_normalization.t1mri->right_grey_white.t1mri' )
    self.add_link( 'split_brain.split_brain->right_grey_white.label_image' )
    self.export_parameter( 'right_grey_white', 'gw_classification', 'right_gw_classification' )
    self.export_parameter( 'right_grey_white', 'hemi_cortex', 'right_hemi_cortex' )
    self.export_parameter( 'right_grey_white', 'hemi_mesh', 'right_hemi_mesh' )
    self.export_parameter( 'right_grey_white', 'white_mesh', 'right_white_mesh' )

    self.node_position = {'bias_correction': (620.0, 140.0),
                          'brain_mask': (930.0, 139.0),
                          'histo_analysis': (761.0, 190.0),
                          'inputs': (50.0, 65.0),
                          'left_grey_white': (1242.0, 55.0),
                          'normalization': (278.0, 145.0),
                          'outputs': (1457.0, 103.0),
                          'right_grey_white': (1239.0, 330.0),
                          'select_normalization': (442.0, 65.0),
                          'split_brain': (1089.0, 163.0)}


if __name__ == '__main__':
  import sys
  from PyQt4 import QtGui
  from soma.gui.widget_controller_creation import ControllerWidget
  from soma.functiontools import SomaPartial as partial
  from soma.gui.pipeline.pipeline_gui import PipelineView
  
  app = QtGui.QApplication( sys.argv )

  morphologist = Morphologist()
  morphologist.select_normalization = 'none'
  #morphologist.nodes[ 'left_grey_white' ].enabled = False
  view1 = PipelineView( morphologist )
  view1.show()
  def set_morphologist_pipeline():
    view1.set_pipeline( morphologist )
  #morphologist.nodes_activation.on_trait_change( set_morphologist_pipeline )
  morphologist.on_trait_change( set_morphologist_pipeline, 'selection_changed' )
  morphologist.on_trait_change( partial( view1.set_pipeline, morphologist ), 'select_normalization' )
  #view2 = PipelineView( GreyWhite() )
  #view2.show()

  cw = ControllerWidget( morphologist, live=True )
  cw.show()
  
  #morphologist.trait( 'nobias' ).hidden = True
  #cw.controller.user_traits_changed = True
  #printer = QtGui.QPrinter( QtGui.QPrinter.HighResolution )
  #printer.setOutputFormat( QtGui.QPrinter.PostScriptFormat )
  #printer.setOutputFileName( sys.argv[ 1 ] )
  #painter = QtGui.QPainter()
  #painter.begin( printer )

  #scale = QtGui.QTransform.fromScale( .5, .5 )
  #painter.setTransform( scale )
  #view1.scene.render( painter )
  #painter.end()
  
  app.exec_()
  morphologist.workflow().write( sys.stdout )
  del view1
  #del view2

