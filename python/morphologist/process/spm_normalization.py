# -*- coding: utf-8 -*-
try:
  from traits.api import File, Float, Int, Bool, Enum
except ImportError:
  from enthought.traits.api import File, Float, Int, Bool, Enum

from capsul.process import Process

class SPMNormalization( Process ):
    def __init__( self, **kwargs ):
        super( SPMNormalization, self ).__init__( **kwargs )
        self.name_process = 'morphologistPipeline.SPMNormalization'
        self.add_trait( 't1mri', File() )
        self.add_trait( 'commissure_coordinates', File( output=True) )
        self.add_trait( 'transformation', File( output=True) )
        self.add_trait( 'spm_transformation', File( output=True ) )
        self.add_trait( 'normalized_t1mri', File( output=True ) )
        self.add_trait( 'template', File() )
        self.add_trait( 'allow_flip_initial_MRI', Bool(False))
        self.add_trait( 'allow_retry_initialization', Bool(True))
    
