try:
  from traits.api import File, Float, Int
except ImportError:
  from enthought.traits.api import File, Float, Int

from soma.pipeline.process import Process
from soma.pipeline.pipeline import Pipeline

    
class SPMNormalization( Process ):
  def __init__( self, **kwargs ):
    super( SPMNormalization, self ).__init__( **kwargs )
    self.add_trait( 't1mri', File() )
    self.add_trait( 'commissure_coordinates', File( output=True) )
    self.add_trait( 'transformation', File( output=True) )
    self.add_trait( 'spm_transformation', File( output=True ) )
    self.add_trait( 'normalized_t1mri', File( output=True ) )
    self.add_trait( 'template', File() )
    self.add_trait( 'allow_flip_initial_MRI', Bool(False))
    self.add_trait( 'allow_retry_initialization', Bool(True))

    
class BiasCorrection( Process ):
  def __init__( self, **kwargs ):
    super( BiasCorrection, self ).__init__( **kwargs )
    self.add_trait( 't1mri', File() )
    self.add_trait( 'commissure_coordinates', File(optional=True) )
    self.add_trait( 'sampling', Float( 16.0 ) )
    self.add_trait( 'field_rigidity', Float( 20.0 ) )
    self.add_trait( 'zdir_multiply_regul', Float( 0.5 ) )
    self.add_trait( 'wridges_weight', Float( 20.0 ) )
    self.add_trait( 'ngrid', Int( 2 ) )
    self.add_trait( 'delete_last_n_slices', Enum( 'auto (AC/PC Points needed)', '0', '10', '20', '30' ) )
    self.add_trait( 't1mri_nobias', File( output=True ) )
    self.add_trait( 'mode', Enum( 'write_minimal','write_all','delete_useless','write_minimal without correction' ) )
    self.add_trait( 'write_field', Enum( 'no','yes' ) )
    self.add_trait( 'field', File ( output=True ) )
    self.add_trait( 'write_hfiltered', Enum( 'yes','no' ) )
    self.add_trait( 'hfiltered', File( output=True ) )
    self.add_trait( 'write_wridges', Enum( 'yes','no','read' ) )
    self.add_trait( 'white_ridges', File( output=True ) )
    self.add_trait( 'variance_fraction', Int( 75 ) )
    self.add_trait( 'write_variance', Enum( 'yes','no' ) )
    self.add_trait( 'variance', File( output=True ) )
    self.add_trait( 'edge_mask', Enum( 'yes','no' ) )
    self.add_trait( 'write_edges', Enum( 'yes','no' ) )
    self.add_trait( 'edges', File( output=True ) )
    self.add_trait( 'write_meancurvature', Enum( 'no','yes' ) )
    self.add_trait( 'meancurvature', File( output=True ) )
    self.add_trait( 'fix_random_seed', Bool( False ) )


class HistoAnalysis( Process ):
  def __init__( self, **kwargs ):
    super( HistoAnalysis, self ).__init__( **kwargs )
    self.add_trait( 't1mri_nobias', File() )
    self.add_trait( 'use_hfiltered', Bool( True ) )
    self.add_trait( 'hfiltered', File(optional=True) )
    self.add_trait( 'use_wridges', Bool( True ) )
    self.add_trait( 'white_ridges', File(optional=True) )
    self.add_trait( 'undersampling', Enum( 'iteration', 'auto', '32', '16', '8', '4', '2' ) )
    self.add_trait( 'histo_analysis', File( output=True ) )
    self.add_trait( 'histo', File( output=True) )
    self.add_trait( 'fix_random_seed', Bool( False ) )

    
class ComputeBrainMask( Process ):
  def __init__( self, **kwargs ):
    super( BrainMask, self ).__init__( **kwargs )
    self.add_trait( 't1mri', File() )
    self.add_trait( 'histo_analysis', File() )
    self.add_trait( 'variance', File() )
    self.add_trait( 'edges', File() )
    self.add_trait( 'white_ridges', File(optional=True) )
    self.add_trait( 'commissure_coordinates', File(optional=True) )
    self.add_trait( 'lesion_mask', File(optional=True) )
    self.add_trait( 'variant',  Enum('2010',
                       '2005 based on white ridge',
                       'Standard + (iterative erosion)',
                       'Standard + (selected erosion)',
                       'Standard + (iterative erosion) without regularisation',
                       'Robust + (iterative erosion)',
                       'Robust + (selected erosion)',
                       'Robust + (iterative erosion) without regularisation',
                       'Fast (selected erosion)'
    self.add_trait( 'erosion_size', Enum( 1, 1.5, 1.8, 2, 2.5, 3, 3.5 ,4 ) )
    self.add_trait( 'visu', Enum('No', 'Yes') )
    self.add_trait( 'layer', Enum(0, 1, 2, 3, 4, 5) )
    self.add_trait( 'first_slice', Int(0) )
    self.add_trait( 'last_slice', Int(0) )
    self.add_trait( 'brain_mask', File( output=True ) )
    self.add_trait( 'fix_random_seed', Bool( False ) )

    
class SplitBrain( Process ):
  def __init__( self, **kwargs ):
    super( SplitBrain, self ).__init__( **kwargs )
    self.add_trait( 'brain_mask', File() )
    self.add_trait( 't1mri_nobias', File() )
    self.add_trait( 'histo_analysis', File() )
    self.add_trait( 'commissure_coordinates', File() )
    self.add_trait( 'use_ridges', Bool( True) )
    self.add_trait( 'white_ridges', File() )
    self.add_trait( 'use_template', Bool( True) )
    self.add_trait( 'split_template', File() )
    self.add_trait( 'mode', Enum( 'Watershed (2011)', 'Voronoi') )
    self.add_trait( 'variant', Enum( 'regularized', 'GW Barycentre', 'WM Standard Deviation') )
    self.add_trait( 'bary_factor', Enum( 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1) )
    self.add_trait( 'mult_factor', Enum( 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4) )
    self.add_trait( 'initial_erosion', Float(2.0) )
    self.add_trait( 'cc_min_size', Int(500) )
    self.add_trait( 'split_brain', File( output=True ) )
    self.add_trait( 'fix_random_seed', Bool( False ) )


class TalairachTransformation( Process ):
    self.add_trait( 'split_brain', File() )
    self.add_trait( 'commissure_coordinates', File() )
    self.add_trait( 'Talairach_transform', File( output=True) )


class HeadMesh( Process ):
    self.add_trait( 't1mri_nobias', File() )
    self.add_trait( 'histo_analysis', File(optional=True) )
    self.add_trait( 'head_mesh', File( output=True) )
    self.add_trait( 'head_mask', File( optional=True,output=True) )
    self.add_trait( 'keep_head_mask', Bool( False ) )
    self.add_trait( 'remove_mask', File( optional=True) )
    self.add_trait( 'first_slice', Int( optional=True) )
    self.add_trait( 'threshold', Int( optional=True) )
    self.add_trait( 'closing', Float( optional=True) )
    
#class GreyWhiteClassification( Process ):
  #def __init__( self, **kwargs ):
    #super( GreyWhiteClassification, self ).__init__( **kwargs )
    #self.add_trait( 't1mri', File() )
    #self.add_trait( 'label_image', File() )
    #self.add_trait( 'label', Int( optional=True ) )
    #self.add_trait( 'gw_classification', File( output=True ) )


#class GreyWhiteSurface( Process ):
  #def __init__( self, **kwargs ):
    #super( GreyWhiteSurface, self ).__init__( **kwargs )
    #self.add_trait( 't1mri', File() )
    #self.add_trait( 'gw_classification', File() )
    #self.add_trait( 'hemi_cortex', File( output=True ) )
    #self.add_trait( 'white_mesh', File( output=True ) )

    
#class SphericalHemisphereSurface( Process ):
  #def __init__( self, **kwargs ):
    #super( SphericalHemisphereSurface, self ).__init__( **kwargs )
    #self.add_trait( 'gw_classification', File() )
    #self.add_trait( 'hemi_cortex', File() )
    #self.add_trait( 'hemi_mesh', File( output=True ) )


#class GreyWhite( Pipeline ):
  #def pipeline_definition( self ):
    ##self.add_trait( 't1mri', File() )
    
    #self.add_process( 'gw_classification', GreyWhiteClassification() )
    #self.export_parameter( 'gw_classification', 't1mri' )
    ##self.add_link( 't1mri->gw_classification.t1mri' )
    
    #self.add_process( 'gw_surface', GreyWhiteSurface() )
    #self.add_link( 't1mri->gw_surface.t1mri' )
    #self.add_link( 'gw_classification.gw_classification->gw_surface.gw_classification' )
    #self.export_parameter( 'gw_classification', 'gw_classification' )
    
    #self.add_process( 'hemi_surface', SphericalHemisphereSurface() )
    #self.add_link( 'gw_classification.gw_classification->hemi_surface.gw_classification' )
    #self.add_link( 'gw_surface.hemi_cortex->hemi_surface.hemi_cortex' )
    #self.export_parameter( 'gw_surface', 'hemi_cortex' )



class Morphologist( Pipeline ):
  def pipeline_definition( self ):
    self.add_trait( 't1mri', File() )
    
    self.add_process( 'normalization', 'morphologist.process.SPMNormalization' )
    self.add_switch( 'select_normalization', [ 'spm', 'none' ], 't1mri' )
    self.add_process( 'bias_correction', BiasCorrection() )

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
  view2 = PipelineView( GreyWhite() )
  view2.show()

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

