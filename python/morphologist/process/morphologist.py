# -*- coding: utf-8 -*-
try:
  from traits.api import File, Float, Int, Bool, Enum
except ImportError:
  from enthought.traits.api import File, Float, Int, Bool, Enum

try:
  from capsul.process import Process
  from capsul.pipeline import Pipeline
  print '%s uses CAPSUL.' % __name__
except:
  from soma.process import Process
  from soma.pipeline import Pipeline
  print '%s uses Soma.' % __name__
import subprocess


from spm_normalization import SPMNormalization
from bias_correction import BiasCorrection
from histo_analysis import HistoAnalysis
from compute_brain_mask import ComputeBrainMask
from split_brain_mask import SplitBrainMask
from talairach_transformation import TalairachTransformation
from head_mesh import HeadMesh
    
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
    def __init__(self):  
        print '__initt'
        super(Morphologist, self).__init__() 
        self.name_process = 'Morphologist'

    def pipeline_definition( self ):
      
        #self.add_trait( 't1mri', File() )
        self.add_trait( 'fix_random_seed', Bool( False ) )
        
        self.add_process( 'SPMNormalization', SPMNormalization() )
    	self.export_parameter( 'SPMNormalization', 't1mri' )
        #self.add_link( 't1mri->SPMNormalization.t1mri' )
    	#self.add_link( 'SPMNormalization.t1mri->t1mri' )
        #self.add_switch( 'select_normalization', [ 'spm', 'none' ], 't1mri' )
        self.add_process( 'bias_correction', BiasCorrection() )
    
        #self.add_link( 'normalization.normalized->select_normalization.spm' )
        #self.add_link( 't1mri->select_normalization.none' )
        #self.add_link( 't1mri->normalization.image' )
    
        #Link between bias correction and others
        self.add_link( 't1mri->bias_correction.t1mri' )
        self.add_link( 'SPMNormalization.commissure_coordinates->bias_correction.commissure_coordinates' )
        self.add_link( 'fix_random_seed->bias_correction.fix_random_seed' )
        self.export_parameter( 'bias_correction', 't1mri_nobias' )
        
        
        #Link between histo_analysis and others
        self.add_process( 'histo_analysis', HistoAnalysis() )
        self.add_link( 'bias_correction.t1mri_nobias->histo_analysis.t1mri_nobias' )
        self.add_link( 'bias_correction.hfiltered->histo_analysis.hfiltered' )
        self.add_link( 'bias_correction.white_ridges->histo_analysis.white_ridges' )
        self.add_link( 'fix_random_seed->histo_analysis.fix_random_seed' )
    	self.export_parameter( 'histo_analysis', 'histo_analysis' )
  
        #Link between brain_mask and others
        self.add_process( 'brain_mask', ComputeBrainMask() )
        self.add_link( 't1mri->brain_mask.t1mri' )
        self.add_link( 'SPMNormalization.commissure_coordinates->brain_mask.commissure_coordinates' ) 
        self.add_link( 'histo_analysis.histo_analysis->brain_mask.histo_analysis' )
        self.add_link( 'bias_correction.variance->brain_mask.variance' )
        self.add_link( 'bias_correction.edges->brain_mask.edges' )
        self.add_link( 'bias_correction.white_ridges->brain_mask.white_ridges' )
        self.add_link( 'fix_random_seed->brain_mask.fix_random_seed' )
        self.export_parameter( 'brain_mask', 'brain_mask' )
      
        #Link between split_brain and others  
        self.add_process( 'split_brain', SplitBrainMask() )
        self.add_link( 'SPMNormalization.commissure_coordinates->split_brain.commissure_coordinates' ) 
        self.add_link( 'bias_correction.t1mri_nobias->split_brain.t1mri_nobias' )
        self.add_link( 'bias_correction.white_ridges->split_brain.white_ridges' )
        self.add_link( 'histo_analysis.histo_analysis->split_brain.histo_analysis' )
        self.add_link( 'brain_mask.brain_mask->split_brain.brain_mask' )
        self.add_link( 'fix_random_seed->split_brain.fix_random_seed' )
        
        #Link between talairach_transformation and others  
        self.add_process( 'talairach_transformation', TalairachTransformation() )
        self.add_link( 'SPMNormalization.commissure_coordinates->talairach_transformation.commissure_coordinates' ) 
        self.add_link( 'split_brain.split_brain->talairach_transformation.split_brain' ) 
        
        #Link between head_mesh and others  
        self.add_process( 'head_mesh', HeadMesh() )
        self.add_link( 'bias_correction.t1mri_nobias->head_mesh.t1mri_nobias' )
        self.add_link( 'histo_analysis.histo_analysis->head_mesh.histo_analysis' )
    
    
        
        #self.add_process( 'left_grey_white', GreyWhite(), label=1 )
        #self.export_parameter( 'left_grey_white', 'label', None )
        #self.add_link( 'select_normalization.t1mri->left_grey_white.t1mri' )
        #self.add_link( 'split_brain.split_brain->left_grey_white.label_image' )
        #self.export_parameter( 'left_grey_white', 'gw_classification', 'left_gw_classification' )
        #self.export_parameter( 'left_grey_white', 'hemi_cortex', 'left_hemi_cortex' )
        #self.export_parameter( 'left_grey_white', 'hemi_mesh', 'left_hemi_mesh' )
        #self.export_parameter( 'left_grey_white', 'white_mesh', 'left_white_mesh' )
        
        #self.add_process( 'right_grey_white', GreyWhite(), label=2 )
        #self.export_parameter( 'right_grey_white', 'label', None )
        #self.add_link( 'select_normalization.t1mri->right_grey_white.t1mri' )
        #self.add_link( 'split_brain.split_brain->right_grey_white.label_image' )
        #self.export_parameter( 'right_grey_white', 'gw_classification', 'right_gw_classification' )
        #self.export_parameter( 'right_grey_white', 'hemi_cortex', 'right_hemi_cortex' )
        #self.export_parameter( 'right_grey_white', 'hemi_mesh', 'right_hemi_mesh' )
        #self.export_parameter( 'right_grey_white', 'white_mesh', 'right_white_mesh' )
    
    
        #self.node_position = {'bias_correction': (620.0, 140.0),
                              #'brain_mask': (930.0, 139.0),
                              #'histo_analysis': (761.0, 190.0),
                              #'inputs': (50.0, 65.0),
                              #'left_grey_white': (1242.0, 55.0),
                              #'normalization': (278.0, 145.0),
                              #'outputs': (1457.0, 103.0),
                              #'right_grey_white': (1239.0, 330.0),
                              #'select_normalization': (442.0, 65.0),
                              #'split_brain': (1089.0, 163.0)}
                              
                              
    #def __call__( self ):
        #""" Function to call the execution """
        #print 'call pipeline morphologist'
	#for pro in self.list_process_in_pipeline:
	    #if 'BiasCorrection' in str(pro):
		#print 'OK BIASS'
		#pro()     
                              


if __name__ == '__main__':
    import sys
    from PyQt4 import QtGui
    from soma.gui.widget_controller_creation import ControllerWidget
    from soma.functiontools import SomaPartial as partial
    from soma.gui.pipeline.pipeline_gui import PipelineView
    
    from soma.pipeline.process import Process
    
    app = QtGui.QApplication( sys.argv )
    
    morphologist = Process.get_instance( 'morphologist.process.morphologist' )
    
    for node_name, node in morphologist.nodes.iteritems():
      print 'Node:', node_name
      process = getattr( node, 'process', None )
      if process:
        for trait_name in process.user_traits():
          trait = process.trait( trait_name )
          print '  %s: %s %s' % ( trait_name, repr( getattr( trait, 'output', False ) ), repr( getattr( trait, 'connected_output', False ) ) )

    #morphologist.nodes[ 'left_grey_white' ].enabled = False
    #view1 = PipelineView( morphologist )
    #view1.show()
    #def set_morphologist_pipeline():
        #view1.set_pipeline( morphologist )
    #morphologist.nodes_activation.on_trait_change( set_morphologist_pipeline )
    #morphologist.on_trait_change( set_morphologist_pipeline, 'selection_changed' )
    #morphologist.on_trait_change( partial( view1.set_pipeline, morphologist ), 'select_normalization' )
    #view2 = PipelineView( GreyWhite() )
    #view2.show()
    
    #cw = ControllerWidget( morphologist, live=True )
    #cw.show()
    
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
    
    #app.exec_()
    morphologist.workflow().write( sys.stdout )
    #del view1
    #del view2
    
    

