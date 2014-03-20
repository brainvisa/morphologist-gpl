# -*- coding: utf-8 -*-
try:
  from traits.api import File, Float, Int, Bool, Enum
except ImportError:
  from enthought.traits.api import File, Float, Int, Bool, Enum

try:
  from capsul.process import Process
  print '%s uses CAPSUL.' % __name__
except:
  from soma.process import Process
  print '%s uses Soma.' % __name__
import subprocess

class BiasCorrection( Process ):
    def __init__( self, **kwargs ):
        super( BiasCorrection, self ).__init__( **kwargs )
     	self.name_process = 'morphologistPipeline.BiasCorrection'
        self.add_trait( 't1mri', File() )
        self.add_trait( 'commissure_coordinates', File(optional=True) )
        self.add_trait( 'sampling', Float( 16.0 ) )
        self.add_trait( 'field_rigidity', Float( 20.0 ) )
        self.add_trait( 'zdir_multiply_regul', Float( 0.5 ) )
        self.add_trait( 'wridges_weight', Float( 20.0 ) )
        self.add_trait( 'ngrid', Int( 2 ) )
        self.add_trait( 'delete_last_n_slices', Enum( 'auto (AC/PC Points needed)', '0', '10', '20', '30' ) )
        self.add_trait( 't1mri_nobias', File( output=True ) )
        self.add_trait( 'bias_correction_mode', Enum( 'write_minimal','write_all','delete_useless','write_minimal without correction' ) )
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

    def __call__( self ):
        print 'call bias correction'
	print 'self t1mri',self.t1mri
	print 'getattre t1mri',getattr(self,'t1mri')
	print 'self',self
	for name, trait in self.user_traits().iteritems():
	    print name,trait
	    
	    
        if self.bias_correction_mode == 'write_all':
            self.write_wridges = 'yes'
            self.write_field = 'yes'
            self.write_hfiltered = 'yes'
            self.write_variance = 'yes'
            self.write_meancurvature = 'yes'
            self.write_edges = 'yes'
        if self.edge_mask == 'yes':
            edge = '3'
        else:
            edge = 'n'
        
        if self.bias_correction_mode in ('write_minimal', 'write_all', 'write_minimal without correction'):
            command = ['VipT1BiasCorrection', '-i', self.t1mri,
                '-o', self.t1mri_nobias,
                '-Fwrite', self.write_field,
                '-field', self.field,
                '-Wwrite', self.write_wridges,
                '-wridge', self.white_ridges,
                '-Kregul', self.field_rigidity,
                '-sampling', self.sampling,
                '-Kcrest', self.wridges_weight,
                '-Grid', self.ngrid,
                '-ZregulTuning', self.zdir_multiply_regul,
                '-vp', self.variance_fraction, '-e', edge,
                '-eWrite', self.write_edges,
                '-ename', self.edges,
                '-vWrite', self.write_variance,
                '-vname', self.variance,
                '-mWrite', self.write_meancurvature,
                '-mname', self.meancurvature,
                '-hWrite', self.write_hfiltered,
                '-hname', self.hfiltered,
                '-Last', self.delete_last_n_slices ]
            if self.commissure_coordinates is not None:
                command += ['-Points', self.commissure_coordinates]
            if self.bias_correction_mode == 'write_minimal without correction':
                command += ['-Dcorrect', 'n']
            if self.fix_random_seed:
                command += ['-srand', '10']
	
        #tm = registration.getTransformationManager()
        #tm.copyReferential(self.t1mri, self.t1mri_nobias)
        #if self.write_field:
            #tm.copyReferential( self.t1mri, self.field )
        #if self.write_hfiltered:
            #tm.copyReferential( self.t1mri, self.hfiltered )
        #if self.write_wridges:
            #tm.copyReferential( self.t1mri, self.white_ridges )
        #if self.write_variance:
            #tm.copyReferential( self.t1mri, self.variance )
        #if self.write_edges:
            #tm.copyReferential( self.t1mri, self.edges )
        #if self.write_meancurvature:
            #tm.copyReferential( self.t1mri, self.meancurvature )
            
        #elif self.bias_correction_mode == 'delete_useless':
            #if os.path.exists(self.field.fullName() + '.ima') or os.path.exists(self.field.fullName() + '.ima.gz'):
                #shelltools.rm( self.field.fullName() + '.*' )
            #if os.path.exists(self.variance.fullName() + '.ima') or os.path.exists(self.variance.fullName() + '.ima.gz'):
                #shelltools.rm( self.variance.fullName() + '.*' )
            #if os.path.exists(self.edges.fullName() + '.ima') or os.path.exists(self.edges.fullName() + '.ima.gz'):
                #shelltools.rm( self.edges.fullName() + '.*' )
            #if os.path.exists(self.meancurvature.fullName() + '.ima') or os.path.exists(self.meancurvature.fullName() + '.ima.gz'):
                #shelltools.rm( self.meancurvature.fullName() + '.*' )
         
        #print 'command biais correction',command        
        #args= ['python', '-m', 'brainvisa.axon.runprocess','morphologistProcess']    
       
       
          
        str_command=[str(x) for x in command]
        print 'strcommand',str_command
        subprocess.check_call( str_command )
