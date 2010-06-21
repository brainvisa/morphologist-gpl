from neuroProcesses import *
import shfjGlobals
import numpy as np
from neuroHierarchy import databases
from soma import aims
# Yann: I cannot find anacheck module in t1mri sources. I added a comment because it raises an error when brainvisa starts.
#from brainvisa.wip.anacheck import neurostats as ns
#from brainvisa.wip.anacheck.CheckPipeline import DatabaseEnquirer


types = {}
types["raw"] = "Raw T1 MRI"
types["bias"] = "T1 MRI Bias Corrected"
types["histo"] = "Histo Analysis"
types["mask"] = "T1 Brain Mask"
types["voronoi"] = "Voronoi Diagram"
types["headmesh"] = "Head Mesh"
types["leftcsfgrey"] = "Left CSF+GREY Mask"
types["rightcsfgrey"] = "Right CSF+GREY Mask"
types["leftGWmask"] = "Left Grey White Mask"
types["rightGWmask"] = "Right Grey White Mask"
types["leftwhitemesh"] = "Left Hemisphere White Mesh"
types["rightwhitemesh"] = "Right Hemisphere White Mesh"
types["lefthemimesh"] = "Left Hemisphere Mesh"
types["righthemimesh"] = "Right Hemisphere Mesh"

global TYPES_NAMES
TYPES_NAMES = types


name = 'Ana Check if every step has given a file'
userLevel = 3

signature = Signature(
  'MRI', ListOf(ReadDiskItem("Raw T1 MRI", shfjGlobals.vipVolumeFormats )),
  'stats_file', WriteDiskItem("Text File", "Text File"),
  'mode', Choice("All", "Only Problems", "None"),
  'files_report', WriteDiskItem("Text File", "Text File"),
  'types', ListOf(Choice(*types.values() ) )

  )


def checkSubjectFiles( self, mri ):
    # Returns A Dictionary With Infos Related To The Subject MRI
  
    datainfo = {}
    datainfo["database"] = mri.get("_database") #"/volatile/operto/data/nmr"
    datainfo["protocol"] = mri.get("protocol") #"nmr"
    datainfo["acquisition"] = mri.get("acquisition") #"default_acquisition"
    datainfo["modality"] = mri.get("modality") #"t1mri"
    datainfo["subject"] =  mri.get("subject") #"sujet01"
    image = aims.read(mri.fullPath())
    voxel_size = image.header()['voxel_size']
    datainfo["voxel_size"] = voxel_size
    
    print ">>>>> LE SUJET ETUDIE EST LE SUIVANT :"
    print "%s (%s/%s) DU PROTOCOLE %s DE LA BASE %s "%(datainfo["subject"],
        datainfo["modality"], datainfo["acquisition"], datainfo["protocol"],
        datainfo["database"])

    return  datainfo, DatabaseEnquirer.getFiles(datainfo)






def computeVolumesAndCreateCSV(self, MRI, stats_file, files_report_path):
  
    hashtypes = [ "raw", "bias", "histo", "mask", "voronoi", "leftcsfgrey",
        "rightcsfgrey", "leftGWmask", "rightGWmask", "leftwhitemesh",
        "rightwhitemesh", "lefthemimesh", "righthemimesh", "headmesh" ]
    symbols = {'RAW': 'Raw T1 MRI', 'BIAS' : 'T1 MRI Bias Corrected',
        'HIS' : 'Histo Analysis', 'MASK' : 'T1 Brain Mask',
        'VORO': 'Voronoi Diagram', 'HEAD': 'Head Mesh',
        'LCG' : 'Left CSF+GREY Mask', 'RCG' : 'Right CSF+GREY Mask',
        'LGW' : 'Left Grey White Mask', 'RGW' : 'Right Grey White Mask',
        'LW' : 'Left Hemisphere White Mesh', 'RW': 'Right Hemisphere White Mesh',
        'LH' : 'Left Hemisphere Mesh', 'RH' : 'Right Hemisphere Mesh'}
    #symbols = [ "RAW", "BIAS", "HIS", "MASK", "VORO", "LCG", "RCG", "LGW", "RGW",
        #"LW", "RW", "LH", "RH", "HEAD"]


    files_infos = []

    for mri in MRI:

        # files_infos Contains For Every Subject A Dictionary With Infos Related
        #   To Its MRI
        datainfo, files_subject = self.checkSubjectFiles ( mri )

        files_infos.append(files_subject)


    # Ecrire Un Compte Rendu Texte Dans Un Fichier De La Liste De Fichiers Crees
    files_report = []
    files_report.append(symbols)
    files_report.append( ["subject_name"] )
    files_report[0].extend( symbols.keys() )
    
    print "files_report_path:", files_report_path
    out_file = open(files_report_path.fullPath(), 'w')
    row = files_report[0]
    report_line = ""
    for each in row[:-1]:
        report_line = report_line +  each + "\t"
    report_line = report_line + "\n"
    out_file.write(report_line)
    out_file.close()


    # Computing Stats From The Different Images and Saving it

    stats = {}
    print "Stats_file :", stats_file
    
    out_file = open(stats_file.fullPath(), 'w')
    out_file.write("sujet, protocol, mask, gray_mean, gray_std, white_mean, white_std, vorL, vorR, vorC, corLG, corLW, corRG, corRW, leftGrey, rightGrey, leftWhite, rightWhite, est_csfgrey_G_mean, est_csfgrey_G_std, est_csfgrey_W_mean, est_csfgrey_W_std, est_GWmask_G_mean, est_GWmask_G_std, est_GWmask_W_mean, est_GWmask_W_std, est_csfgrey_G_mean_nobias, est_csfgrey_G_std_nobias, est_csfgrey_W_mean_nobias, est_csfgrey_W_std_nobias, est_GWmask_G_mean_nobias, est_GWmask_G_std_nobias, est_GWmask_W_mean_nobias, est_GWmask_W_std_nobias \n")
    out_file.close()

    
    report = []
    for num_sujet, mri in enumerate(MRI):
        subject = files_infos[num_sujet]['subject']
        protocol = files_infos[num_sujet]['protocol']
        vox_size = files_infos[num_sujet]['voxel_size']
        stats[num_sujet], subject_report = ns.getStatsFromSubjectImages( files_infos[num_sujet] )
        report.extend(subject_report)

        vox_vol = vox_size[0] * vox_size[1] * vox_size[2] * vox_size[3]

        sv = ns.getVariousVolumes( stats, num_sujet, vox_vol )

        stats_line = "%s, %s, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %i\n" \
            %( subject, protocol, sv["mask"], sv["gray_mean"], sv['gray_std'], sv["white_mean"], sv['white_std'], sv["vorL"], sv["vorR"],
            sv["vorC"], sv["corLG"], sv["corLW"], sv["corRG"], sv["corRW"],
            sv["leftGrey"], sv["rightGrey"], sv["leftWhite"], sv["rightWhite"], sv["estim_csfgrey_G_mean"], sv["estim_csfgrey_G_std"], sv["estim_csfgrey_W_mean"], sv["estim_csfgrey_W_std"], sv["estim_GWmask_G_mean"], sv["estim_GWmask_G_std"], sv["estim_GWmask_W_mean"], sv["estim_GWmask_W_std"],
            sv["estim_csfgrey_G_mean_nobias"], sv["estim_csfgrey_G_std_nobias"], sv["estim_csfgrey_W_mean_nobias"], sv["estim_csfgrey_W_std_nobias"], sv["estim_GWmask_G_mean_nobias"], sv["estim_GWmask_G_std_nobias"], sv["estim_GWmask_W_mean_nobias"], sv["estim_GWmask_W_std_nobias"] )
            
        print stats_line[:-1]
        
        out_file = open(stats_file.fullPath(), 'a')
        out_file.write(stats_line)
        out_file.close()

        # Updating the Files Report File
        
        files_report.append([])
        files_report[-1].append(files_infos[num_sujet]['subject'])
        for x, i in enumerate(hashtypes):

            if files_infos[num_sujet].has_key(str(i)) and (len(files_infos[num_sujet][str(i)])!=0) :
                files_report[-1].append("o")
            else :
                files_report[-1].append("x")

            
        row = files_report[-1]
        report_line = ""
        for each in row[:-1]:
            report_line = report_line +  each + "\t"
        report_line = report_line + "\n"
        print report_line[:-1]
        out_file = open(files_report_path.fullPath(), 'a')
        out_file.write(report_line)
        out_file.close()
        

    print "report:", report



    # Displaying The Results
    
    self.labels = []
    subjects_to_display = []
    if self.mode == 'All':
        subjects_to_display = np.arange(len(MRI)).tolist()
        
    elif self.mode == "Only Problems":
        for num_sujet, mri in enumerate( MRI ):
            for x, i in enumerate( hashtypes ):
                test = True
                if files_infos[num_sujet].has_key(str(i)) and (len(files_infos[num_sujet][str(i)])==0) :
                    test = False
            if not test:
                subjects_to_display.append(num_sujet)

    #if self.mode is not "None":
        
        ## Updating the layout
  
        #for x,i in enumerate( hashtypes ):

            #self.labels.append( qt.QLabel(str(symbols[x]), self.result.frame) )
            
            #self.labels[-1].show()
            #self.result.layout.addWidget(self.labels[-1], 0, x+1)

        #for num_sujet in subjects_to_display:

            #subject = files_infos[num_sujet]['subject']
            #self.labels.append(qt.QLabel( str(subject), self.result.frame ) )
            
            #self.labels[-1].show()
            #self.result.layout.addWidget(self.labels[-1], num_sujet+1, 0 )

        
            #for x, i in enumerate(hashtypes):
                
                #if files_infos[num_sujet].has_key(str(i)) and (len(files_infos[num_sujet][str(i)])!=0) :
                    #self.labels.append(qt.QLabel(self.result.frame))

                    #self.labels[-1].setPixmap(self.result.pixmaps["ok"])
                    #qt.QToolTip.add( self.labels[-1], str(files_infos[num_sujet][str(i)] ))
                    #self.labels[-1].show()
                    #self.result.layout.addWidget(self.labels[-1], num_sujet+1, x+1)
                #else :
                    #self.labels.append( qt.QLabel(self.result.frame) )

                    #self.labels[-1].setPixmap(self.result.pixmaps["no"])
                    #self.labels[-1].show()
                    #self.result.layout.addWidget(self.labels[-1], num_sujet+1, x+1)
                    

    return report


#def clearLayout(self):

    #for i in self.labels:
        #self.result.layout.remove(i)
        #self.result.frame.removeChild(i)
        #del i
    



def initialization( self ):

    self.labels = []
    self.stats_file = "/volatile/operto/temp/stats_csv.txt"
    self.files_report = "/volatile/operto/temp/files_report.txt"

def execution( self, context ):
    #self.result.btnExecute.setText("Interrupt")
    #self.result.btnExecute.disconnect( self.result.btnExecute, qt.SIGNAL( 'clicked()' ), context._runButton )
    #self.result.btnExecute.connect( self.result.btnExecute, qt.SIGNAL( 'clicked()' ), context._interruptStepButton )

    if (len(self.MRI) is not 0):
        #self.clearLayout()
        report = self.computeVolumesAndCreateCSV( self.MRI, self.stats_file, self.files_report )
        context.write('error report : ', report)
        
    #self.result.btnExecute.setText("Execute")
    #self.result.btnExecute.disconnect( self.result.btnExecute, qt.SIGNAL( 'clicked()' ), context._interruptStepButton )
    #self.result.btnExecute.connect( self.result.btnExecute, qt.SIGNAL( 'clicked()' ), context._runButton )



#class PipelineFilesChecker (qt.QWidget):

    #def resetLayout(self, parent):

        #self.frame = qt.QFrame(parent )
        #self.frame.setMargin(15)
        #self.frame.setFrameStyle( qt.QFrame.Panel | qt.QFrame.Raised )
        #self.layout = qt.QGridLayout(self.frame, len( TYPES_NAMES.keys() ),1)
        #self.btnExecute = qt.QPushButton("Execute", parent )

    #def __init__(self, parent) :

        #super( PipelineFilesChecker , self ).__init__( parent)

        #self.resetLayout(parent)
        #self.parent = parent
        #self.pixmaps = {}
        #self.pixmaps["ok"] = qt.QPixmap(os.path.expandvars( '$BRAINVISA_SHARE/brainvisa-4.0/icons/ok.png'))
        #self.pixmaps["no"] = qt.QPixmap(os.path.expandvars( '$BRAINVISA_SHARE/brainvisa-4.0/icons/abort.png'))


#def inlineGUI( self, values, context, parent, externalRunButton=False ):

    #self.result = PipelineFilesChecker(parent)
    #self.result.btnExecute.connect( self.result.btnExecute, qt.SIGNAL( 'clicked()' ), context._runButton )
    #return self.result
  
