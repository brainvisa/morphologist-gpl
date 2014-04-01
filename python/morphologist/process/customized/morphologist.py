
import morpho.morphologist

class CustomMorphologist(morpho.morphologist.morphologist):

    def __init__(self, autoexport_nodes_parameters=True, **kwargs):
        super(CustomMorphologist, self).__init__(False, **kwargs)
        self.set_autoexport_parameters(autoexport_nodes_parameters)
        self.export_internal_parameters()


    def pipeline_definition(self):
        super(CustomMorphologist, self).pipeline_definition()

        self.add_switch('select_Talairach',
            ['StandardACPC', 'Normalization'],
            ['Talairach_transform'])

        # export output parameter
        self.export_parameter('select_Talairach', 'Talairach_transform',
            'Talairach_transform')
        self.add_link('PrepareSubject.TalairachFromNormalization_Talairach_transform->select_Talairach.StandardACPC_switch_Talairach_transform')
        self.add_link('TalairachTransformation.Talairach_transform->select_Talairach.Normalization_switch_Talairach_transform')
        #self.export_parameter('PrepareSubject', 'select_AC_PC_Or_Normalization', 'select_normalization')
        self.add_link('select_Talairach->PrepareSubject.select_AC_PC_Or_Normalization')


