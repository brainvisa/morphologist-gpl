from brainvisa.processes import *
import os
import shutil
import zipfile
import glob


name = 'Import volBrain results into a brainvisa database'
userLevel = 0

inputs = 'Inputs'
outputs_native = 'Outputs in native space'
outputs_mni = 'Outputs in MNI space'
report = 'VolBrain Reports'


signature = Signature(
    # Inputs
    'volBrain_zip', ReadDiskItem(
        'Any Type',
        'ZIP file',
        section=inputs),
    'volBrain_native_zip', ReadDiskItem(
        'Any Type',
        'ZIP file',
        section=inputs),
    'subject', ReadDiskItem(
        'Subject',
        'Directory',
        section=inputs),
    'acquisition', String(
        section=inputs),
    'check_subject_name_in_zipfile', Boolean(
        section=inputs),
    # Outputs reports
    'report_csv', WriteDiskItem(
        'Analysis Report',
        'CSV file',
        requiredAttributes={'modality': 'volBrain'},
        section=report),
    'report_pdf', WriteDiskItem(
        'Analysis Report',
        'PDF file',
        requiredAttributes={'modality': 'volBrain'},
        section=report),
    # MNI outputs
    'mni_lab', WriteDiskItem(
        'Subcortical labels',
        'gz compressed NIFTI-1 image',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'mni'},
        section=outputs_mni),
    'mni_hemi', WriteDiskItem(
        'Split Brain Mask',
        'gz compressed NIFTI-1 image',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'mni'},
        section=outputs_mni),
    'mni_crisp', WriteDiskItem(
        'Intracranial labels',
        'gz compressed NIFTI-1 image',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'mni'},
        section=outputs_mni),
    'mni_mask', WriteDiskItem(
        'Intracranial mask',
        'gz compressed NIFTI-1 image',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'mni'},
        section=outputs_mni),
    'mni_wm', WriteDiskItem(
        'tissue probability map',
        'gz compressed NIFTI-1 image',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'mni',
                            'tissue_class': 'white'},
        section=outputs_mni),
    'mni_gm', WriteDiskItem(
        'tissue probability map',
        'gz compressed NIFTI-1 image',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'mni',
                            'tissue_class': 'grey'},
        section=outputs_mni),
    'mni_csf', WriteDiskItem(
        'tissue probability map',
        'gz compressed NIFTI-1 image',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'mni',
                            'tissue_class': 'csf'},
        section=outputs_mni),
    'mni_normalised', WriteDiskItem(
        'T1 MRI Denoised and Bias Corrected',
        'gz compressed NIFTI-1 image',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'mni'},
        section=outputs_mni),
    'mni_readme', WriteDiskItem(
        'Text file',
        'PDF file',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'mni'},
        section=outputs_mni),
    'affine_transformation', WriteDiskItem(
        'Transformation',
        'Text file',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'mni'},
        section=outputs_mni),
    # Native outputs
    'native_lab', WriteDiskItem(
        'Subcortical labels',
        'gz compressed NIFTI-1 image',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'native'},
        section=outputs_native),
    'native_hemi', WriteDiskItem(
        'Split Brain Mask',
        'gz compressed NIFTI-1 image',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'native'},
        section=outputs_native),
    'native_crisp', WriteDiskItem(
        'Intracranial labels',
        'gz compressed NIFTI-1 image',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'native'},
        section=outputs_native),
    'native_mask', WriteDiskItem(
        'Intracranial mask',
        'gz compressed NIFTI-1 image',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'native'},
        section=outputs_native),
    'native_filtered', WriteDiskItem(
        'T1 MRI Denoised',
        'gz compressed NIFTI-1 image',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'native'},
        section=outputs_native),
    'native_normalised', WriteDiskItem(
        'T1 MRI Denoised and Bias Corrected',
        'gz compressed NIFTI-1 image',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'native'},
        section=outputs_native),
    'native_readme', WriteDiskItem(
        'Text file',
        'PDF file',
        requiredAttributes={'modality': 'volBrain',
                            'space': 'native'},
        section=outputs_native),
)


def initialization(self):
    #def linkSubject(self, proc):
        #if self.volBrain_mni_zip is not None:
            #subject = os.path.basename(self.volBrain_mni_zip.fullPath()).split('.nii.gz')[0]
        #return subject
    
    def linkNativeZip(self, proc):
        if self.volBrain_zip is not None:
            directory = os.path.dirname(self.volBrain_zip.fullPath())
            basename = os.path.basename(self.volBrain_zip.fullPath())
            zip_native = os.path.join(directory,
                                      'native_' + basename)
            if os.path.exists(zip_native):
                return zip_native
    
    def linkVolBrainOutput(self, proc):
        if self.subject and self.acquisition:
            d = {'_database': self.subject.get('_database'),
                 '_ontology': self.subject.get('_ontology'),
                 'center': self.subject.get('center'),
                 'subject': self.subject.get('subject'),
                 'acquisition': self.acquisition}
            #return self.signature['mni_lab'].findValue(d)
            return self.signature['report_csv'].findValue(d)
    
    #self.linkParameters('subject', 'volBrain_mni_zip', linkSubject)
    self.linkParameters('volBrain_native_zip', 'volBrain_zip', linkNativeZip)
    
    #self.linkParameters('mni_lab', ('subject', 'acquisition'), linkVolBrainOutput)
    self.linkParameters('report_csv', ('subject', 'acquisition'), linkVolBrainOutput)
    
    #self.linkParameters('report_csv', 'mni_lab')
    self.linkParameters('report_pdf', 'report_csv')
    self.linkParameters('mni_lab', 'report_csv')
    
    self.linkParameters('mni_hemi', 'mni_lab')
    self.linkParameters('mni_mask', 'mni_lab')
    self.linkParameters('mni_crisp', 'mni_lab')
    self.linkParameters('mni_gm', 'mni_lab')
    self.linkParameters('mni_wm', 'mni_lab')
    self.linkParameters('mni_csf', 'mni_lab')
    self.linkParameters('mni_normalised', 'mni_lab')
    self.linkParameters('mni_readme', 'mni_lab')
    self.linkParameters('affine_transformation', 'mni_lab')
    
    self.linkParameters('native_lab', 'mni_lab')
    self.linkParameters('native_hemi', 'native_lab')
    self.linkParameters('native_mask', 'native_lab')
    self.linkParameters('native_crisp', 'native_lab')
    self.linkParameters('native_filtered', 'native_lab')
    self.linkParameters('native_normalised', 'native_lab')
    self.linkParameters('native_readme', 'native_lab')
    
    self.setOptional('volBrain_native_zip', 'native_filtered', 'native_normalised', 'native_readme')
    

def execution(self, context):
    if (self.check_subject_name_in_zipfile and self.volBrain_zip and
            self.volBrain_zip.fullPath().find(self.subject.get('subject')) < 0):
        context.write("The zip files path do not match with the subject's name, verify your file or disable the check.")
        return

    if self.volBrain_native_zip:
        # Old way
        self.extract_volbrain_in_space_zip(context)
    elif self.get_volbrain_zip_version(self.volBrain_zip.fullPath()) == 'space':
        # Old way
        self.extract_volbrain_in_space_zip(context)
    else:
        # New way
        self.extract_volbrain_all_in_zip(context)
    
    
def extract_volbrain_in_space_zip(self, context):
    """Extract files from volBrain result zip.
    It follows old zip hierarchy with mni and native results in separated zip.
    """
    # MNI directory
    if self.volBrain_zip:
        dir_mni = self.extract_zip(context, self.volBrain_zip)
    
        files_list = glob.glob(os.path.join(dir_mni.fullPath(), '*mni*'))
        for f in files_list:
            p = os.path.basename(f).split('_')
            if p[0] != 'n':
                p_out = [x for x in self.signature.keys() if p[0] in x and 'mni' in x][0]
            else:
                p_out = 'mni_normalised'
            
            command_list = ['AimsFileConvert',
                            '-i', f,
                            '-o', self.__dict__[p_out]]
            if p_out[4:] in ['lab', 'hemi', 'mask', 'crisp']:
                command_list += ['-t', 'S16']
            context.system(*command_list)
    
        native_filtered = glob.glob(os.path.join(dir_mni.fullPath(), 'fjob*'))[0]
        command_list = ['AimsFileConvert',
                        '-i', native_filtered,
                        '-o', self.native_filtered]
        context.system(*command_list)
        
        other_files = [
            ('affine_mfjob*', self.affine_transformation),
            ('README.pdf', self.mni_readme),
            ('report_job*csv', self.report_csv),
            ('report_job*pdf', self.report_pdf)
        ]
        for pattern, output_file in other_files:
            input_file = glob.glob(os.path.join(dir_mni.fullPath(), pattern))[0]
            shutil.copy(input_file, output_file.fullPath())
    
    # Native directory
    if self.volBrain_native_zip:
        dir_native = self.extract_zip(context, self.volBrain_native_zip)
        
        files_list = glob.glob(os.path.join(dir_native.fullPath(), '*native*'))
        for f in files_list:
            p = os.path.basename(f).split('_')
            if p[1] == 'n':
                p_out = 'native_normalised'
                command_list = ['AimsFileConvert',
                                '-i', f,
                                '-o', self.__dict__[p_out]]
            else:
                p_out = p[0] + '_' + p[1]
                command_list = ['AimsFileConvert',
                                '-i', f,
                                '-o', self.__dict__[p_out],
                                '-t', 'S16']
            context.system(*command_list)
            
        shutil.copy(os.path.join(dir_native.fullPath(), 'READMEnat.pdf'),
                    self.native_readme.fullPath())


def extract_volbrain_all_in_zip(self, context):
    """Extract files from volBrain result zip.
    It follows recent zip hierarchy.
    """
    dir_zip = self.extract_zip(context, self.volBrain_zip)
    
    file_correspondance = {
        'mni_structures': 'mni_lab',
        'native_structures': 'native_lab',
        'mni_t1': 'mni_normalised',
        'mni_tissues': 'mni_crisp',
        'native_tissues': 'native_crisp'
    }
    files_list = glob.glob(os.path.join(dir_zip.fullPath(), '*nii.gz'))
    for f in files_list:
        file_type = '_'.join(os.path.basename(f).split('_')[:2])
        p_out = file_correspondance.get(file_type, file_type)
            
        command_list = ['AimsFileConvert',
                        '-i', f,
                        '-o', self.__dict__[p_out]]
        if p_out[4:] in ['lab', 'hemi', 'mask', 'crisp']:
            command_list += ['-t', 'S16']
        context.system(*command_list)
    
    other_files = [
        ('matrix_affine*', self.affine_transformation),
        ('README.pdf', self.mni_readme),
        ('report_job*csv', self.report_csv),
        ('report_job*pdf', self.report_pdf)
    ]
    for pattern, output_file in other_files:
        input_file = glob.glob(os.path.join(dir_zip.fullPath(), pattern))[0]
        shutil.copy(input_file, output_file.fullPath())


def extract_zip(self, context, zip_path):
    if zip_path:
        dir_mni = context.temporary('Directory')
        with zipfile.ZipFile(zip_path.fullPath(), 'r') as zip_file:
            zip_file.extractall(dir_mni.fullPath())
        return dir_mni


def get_volbrain_zip_version(self, zip_path):
    """Read files in zip_path to know which volbrain zip is:
    - 'all': recent volbrain zip version, which native and mni space results
    - 'space': old volbrain zip version, which contain only native or only mni space results
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        if [i for i in zip_file.namelist() if i.startswith('native_')]:
            return 'all'
        else:
            return 'space'
