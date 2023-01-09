# -*- coding: utf-8 -*-
from __future__ import print_function
from brainvisa.processes import *
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
    'volBrain_mni_zip', ReadDiskItem(
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
        if self.volBrain_mni_zip is not None:
            directory = os.path.dirname(self.volBrain_mni_zip.fullPath())
            basename = os.path.basename(self.volBrain_mni_zip.fullPath())
            zip_native = os.path.join(directory,
                                      'native_' + basename)
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
    self.linkParameters('volBrain_native_zip', 'volBrain_mni_zip', linkNativeZip)
    
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
    self.linkParameters('native_hemi','native_lab')
    self.linkParameters('native_mask','native_lab')
    self.linkParameters('native_crisp','native_lab')
    self.linkParameters('native_filtered','native_lab')
    self.linkParameters('native_normalised','native_lab')
    self.linkParameters('native_readme','native_lab')
    
    self.signature['volBrain_mni_zip'].mandatory = False
    self.signature['volBrain_native_zip'].mandatory = False
    

def execution(self, context):
    
    if self.check_subject_name_in_zipfile:
        if self.volBrain_mni_zip:
            p = self.volBrain_mni_zip.fullPath()
        elif self.volBrain_native_zip:
            p = self.volBrain_native_zip.fullPath()
        if p:
            if p.find(self.subject.get('subject')) < 0:
                context.write("The zip files path do not match with the subject's name, verify your file or disable the check.")
                return
    
    # MNI directoy
    if self.volBrain_mni_zip:
        dir_mni = context.temporary('Directory')
        with zipfile.ZipFile(self.volBrain_mni_zip.fullPath(), 'r') as zip_mni:
            zip_mni.extractall(dir_mni.fullPath())
    
        files_list = glob.glob(os.path.join(dir_mni.fullPath(), '*mni*'))
        for f in files_list:
            #print f
            p = os.path.basename(f).split('_')
            if p[0] != 'n':
                p_out = [x for x in self.signature.keys() if p[0] in x and 'mni' in x][0]
            else:
                p_out = 'mni_normalised'
            
            command_list = ['AimsFileConvert',
                            '-i', f,
                            '-o', self.__dict__[p_out]]
                            #'-o', self.signature[p_out],
            if p_out[4:] in ['lab', 'hemi', 'mask', 'crisp']:
                command_list += ['-t', 'S16']
            print(command_list)
            context.system(*command_list)
    
        native_filtered = glob.glob(os.path.join(dir_mni.fullPath(), 'fjob*'))[0]
        command_list = ['AimsFileConvert',
                        '-i', f,
                        '-o', self.native_filtered]
        context.system(*command_list)
        
        transfo = glob.glob(os.path.join(dir_mni.fullPath(), 'affine_mfjob*'))[0]
        shutil.copy(transfo, self.affine_transformation.fullPath())

        shutil.copy(os.path.join(dir_mni.fullPath(), 'README.pdf'),
                    self.mni_readme.fullPath())
        
        job_id = os.path.basename(glob.glob(os.path.join(dir_mni.fullPath(), 'job*'))[0])
        report = 'report_' + job_id
        shutil.copy(os.path.join(dir_mni.fullPath(), report.replace('.nii', '.csv')),
                    self.report_csv.fullPath())
        shutil.copy(os.path.join(dir_mni.fullPath(), report.replace('.nii', '.pdf')),
                    self.report_pdf.fullPath())
    
    # Native directory
    if self.volBrain_native_zip:
        dir_native = context.temporary('Directory')
        with zipfile.ZipFile(self.volBrain_native_zip.fullPath(), 'r') as zip_native:
            zip_native.extractall(dir_native.fullPath())
        
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
            print(command_list)
            context.system(*command_list)
            
        shutil.copy(os.path.join(dir_native.fullPath(), 'READMEnat.pdf'),
                    self.native_readme.fullPath())

    
    
