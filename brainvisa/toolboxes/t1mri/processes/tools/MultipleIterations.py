from neuroProcesses import *
from neuroProcessesGUI import *
import shfjGlobals     
import qt, os
from neuroProcesses import getProcessInstance

name = 'Run Multiple Iterations'
userLevel = 3


def getProcessesList( processesIDlist ):
    processesList = []
    for proc in processesIDlist:
        try:
            process = getProcessInstance(proc)
            processesList.append( (process.name, proc) )
        except KeyError, e:
            print "keyError"
            print e
            pass
    return processesList


processesList = ['threshold', 'T1BiasCorrection', 'VipHistoAnalysis', 'VipGetBrain', 'SplitBrain' ]

signature = Signature(
  'process', Choice( *getProcessesList( processesList ) ),
  'parameter', Choice( )
  )

def getSelectedProcess( self ):
    selected_process = self.process
    if selected_process is None:
        selected_process = self.signature['process'].values[0][1]
    print 'selected_process', selected_process, self.signature['process'].values[0][0]
    process = getProcessInstance(selected_process)
    return selected_process, process

def updateParameters(self, data):
    print 'UPDATEPARAMETERS'
    selected_process, process = self.getSelectedProcess()
    keys = process.signature.keys()
    filtered_keys = []
    for key in keys:
        print process.signature[key].__class__
        if process.signature[key].__class__ in [Float, Integer, Boolean, Choice]: #, ReadDiskItem, WriteDiskItem]:
            filtered_keys.append( ('%s (%s)'%(key, process.signature[key].__class__.__name__), key ) )

    self.signature['parameter'].setChoices(*filtered_keys)

    # A REGLER
    #self.updateOtherParameters( data)
    print 'END_UPDATEPARAMETERS'
    return self.process
    

def updateOtherParameters(self, data):
    print 'UPDATEOTHERPARAMETERS'
    paramSignature  =  [ 'process', Choice(*getProcessesList( processesList ) ),
        'parameter', Choice( )]
    
    iterable_parameters = self.signature['parameter'].values
    selected_parameter = self.parameter
    if selected_parameter is None:
        selected_parameter = iterable_parameters[0][1]
    print "selected_parameter", selected_parameter

    signature = Signature( *paramSignature )

    selected_process, process = self.getSelectedProcess()
    keys = process.signature.keys()

    iterable_parameters = []
    others = []
    writeitems = []
    
    # ON RECUPERE LA LISTE DES PARAMETRES A AJOUTER A LA SIGNATURE
    # AINSI QUE LA LISTE DES WRITEDISKITEMS
    # AINSI QUE LA LISTE DES PARAMETRES SELECTIONNABLES POUR L'ITERATION
    # PARCOURS DES ELEMENTS DE LA SIGNATURE DU PROCESS SELECTIONNE
    for each in keys:
        class_key = process.signature[each].__class__
        if class_key in [Float, Integer, Boolean, ReadDiskItem, Choice]:
            if class_key not in [ReadDiskItem]:
                iterable_parameters.append( ('%s (%s)'%(each, process.signature[each].__class__.__name__), each ))
            # SI L'ELEMENT DIFFERE DU PARAMETRE SELECTIONNE
            if each != selected_parameter:
                others.append(each)
        elif class_key in [WriteDiskItem]:
            writeitems.append(each)
            print 'writediskitem', each

    # OTHERS CONTIENT LES AUTRES PARAMETRES A SPECIFIER
    # WRITEITEMS CONTIENT LES WRITEDISKITEMS DU TRAITEMENT QU'IL FAUDRA DECLINER
    #  EN AUTANT DE VALEURS QUE LEN(SELF.VALUES)
    # iterable_parameters CONTIENT TOUS LES PARAMETRES SELECTIONNABLES

    class_param = process.signature[selected_parameter].__class__

    if class_param in [Choice, Boolean]:
        paramSignature.extend( ['values', ListOf( Choice(*process.signature[selected_parameter].values) ) ] )
    else:
        paramSignature.extend( ['values', ListOf(class_param.__new__(class_param) ) ] )
    
        

    # ON PREPARE LA LISTE DES OTHERS PARAMETRES A LA SIGNATURE
    # PARCOURS DES ELEMENTS DE LA SIGNATURE DU PROCESS SELECTIONNE
    for key in keys:
        # ON VERIFIE QU'ON NE RAJOUTE PAS UN ELEMENT FIGURANT DEJA DANS LA
        #   SIGNATURE DE BASE (GENRE PROCESS PARAMETER OU VALUES)
        if not signature.has_key(key):
            # SI L'ELEMENT FIGURE DANS LES OTHERS
            if key in others:
                process.signature[key].mandatory = 0
                paramSignature.extend( [ key, process.signature[key] ] )
        else:
            assert(False)

    #CREATION DE LA NOUVELLE SIGNATURE
    print 'paramSignature', paramSignature
    signature = Signature( *paramSignature )
    print "others", others
    self.others = others
    self.writeitems = writeitems
    print "iterable_parameters", iterable_parameters
    signature['parameter'] = Choice(*iterable_parameters)
    

    if self.signature.has_key('values'):
        if class_param in [Choice, Boolean]:
            signature['values'] = ListOf( Choice(*process.signature[selected_parameter].values) )
        else:
            signature['values'] = ListOf(class_param.__new__(class_param) )
    new_iterable_parameters = self.signature['parameter'].values
    print "new_iterable_parameters", new_iterable_parameters
    print "newsig", signature['parameter'].values
    
    self.changeSignature( signature )
    print 'END_UPDATEOTHERPARAMETERS'
    

def initialization( self ):
    
    print 'INITIALIZATION'
    self.signature['process'].setChoices(*getProcessesList(processesList) )
    self.addLink("process", "process", self.updateParameters)
    self.addLink(None, "parameter", self.updateOtherParameters)
    print 'END_INITIALIZATION'
    

def execution( self, context ):
    print 'EXECUTION'
    selected_process, process = self.getSelectedProcess()
    print selected_process
    keys = process.signature.keys()
    print "values", self.values
    print "writeitems", self.writeitems
    output_list = {}
    for value in self.values:
        output_list[value] = {}
        for each in self.writeitems:
            
            print "formats", process.signature[each].formats
            favorite_formats = ['GIS image']
            found = 0
            for format in favorite_formats:
                if format in process.signature[each].formats :
                    output_list[value][each] = context.temporary( format )
                    found = 1
                    break
            if found == 0:
                output_list[value][each] = context.temporary( process.signature[each].formats[0] )            
            print output_list[value][each]
    context.write(output_list)
    context.write(self.process)
    context.write(self.parameter)

    

    print "keys", keys
    print "others", self.others
    print "param", self.parameter
    processes = []
    for value in self.values:
        selected_process, process = self.getSelectedProcess()        
        process.setValue(self.parameter, value)        
        for other in self.others:
            print self.__getattribute__(other)
            if self.__getattribute__(other) != None :
                process.setValue( other, self.__getattribute__(other) )
        for each in self.writeitems:
            process.setValue( each, output_list[value][each] )
        processes.append(process)
        
        #for key in self.others:
            #context.write(key)
            #context.write(self.__getattribute__(key))
            #process.setValue(key, self.__getattribute__(key))
        #for each in self.writeitems:
            #context.write(each)
            #context.write(output_list[value][each])
            #process.setValue(each, output_list[value][each])
    
        #context.write("Parameter %s fixed to %i"%(self.parameter, value))
        #context.write(output_list[value])
        #context.runProcess(process)
    
    iterationProcess = IterationProcess("test", processes)
    showProcess(iterationProcess)

    #while 1:
        #selected_output = self.writeitems[0]
        #dial = context.dialog( 1, 'Choose the output to check',
                                #Signature( 'choice', Choice(*(self.writeitems)) ),
                                #_t_( 'OK' ), _t_( 'Stop' ) )
        #r = dial.call()
        #if r != 0:
            #context.write(selected_output)
            #context.write(r)
            ## EVENTUELLEMENT PROPOSER DE PRENDRE UNE DECISION SUR LE RESULTAT
            
            #while 1:
                #process = getProcessInstance(self.process)
                #decision = context.dialog( 1, 'Do you want to save one version of the results',
                        #Signature( 'value', Choice(*(self.values)),
                            #'output', process.signature[selected_output]),
                            #_t_( 'OK' ), _t_( 'Stop' ))
                #s = decision.call()
                #if s != 0:
                    #context.write("pas de sauvegarde")
                    #break
                #else:
                    #selected_value = decision.getValue('value')
                    #final_output = decision.getValue('output')
                    #if final_output != None:
                        #os.system("echo %s %s"%(output_list[selected_value][selected_output], final_output))
                        #context.write( "echo %s %s"%(output_list[selected_value][selected_output], final_output) )
                        #break
                
            #break
        #selected_output = dial.getValue( 'choice' )
        #context.write("selected_output : %s"%selected_output)

        #temporary = []
        #for value in self.values:
           #temporary.append(output_list[value][selected_output])
        #context.write(temporary)
        #showProcess("AnaControlMultipleIterations", temporary)
        

    






    

