# -*- coding: utf-8 -*-
#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
#
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the 
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info". 
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.


from brainvisa.processes import *
import shfjGlobals

name = 'Sulci Recognition (both hemispheres)'
userLevel = 0

ann_model = 'Abstract Neural Network (ANN)'
ann_model_2001 = 'ANN, older 2000-2001 labels'
spam_model = 'Statistical Parametric Anatomy Map (SPAM)'
desync_msg = 'desynchronized between left and right side'

signature = Signature(
    'side', Choice( 'left', 'right', 'both', 'none' ),
    'model', Choice( ann_model, ann_model_2001, spam_model, desync_msg),
    'left_data_graph', ReadDiskItem( 'Left Cortical Folds Graph',
      'Graph and Data' ),
    'left_output_graph', WriteDiskItem( 'Labelled Cortical Folds Graph',
      'Graph and Data', requiredAttributes={ 'side': 'left' } ),
    'right_data_graph', ReadDiskItem( 'Right Cortical Folds Graph',
      'Graph and Data' ),
    'right_output_graph', WriteDiskItem( 'Labelled Cortical Folds Graph',
      'Graph and Data', requiredAttributes={ 'side': 'right' } ),
)

#import neuroConfig
#import sys
#neuroConfig.debugParametersLinks = sys.stdout

class changeSide(object):
    def __init__( self, proc ):
        self.proc = weakref.proxy( proc )
    def __call__( self, node ):
        side = self.proc.side
        # must be called to avoid infinite recursion
        if (node.isSelected() and side in self.sel) \
            or (not node.isSelected() and side in self.unsel):
            return
        self.proc.side = self.map[side]


class changeSideLeft(changeSide):
    map = { 'left' : 'none', 'none' : 'left',
        'right' : 'both', 'both' : 'right'}
    sel = ['left', 'both']
    unsel = ['right', 'none']
    def __init__( self, proc ):
        changeSide.__init__(self, proc)

class changeSideRight(changeSide):
    map = { 'left' : 'both', 'both' : 'left',
        'right' : 'none', 'none' : 'right'}
    sel = ['right', 'both']
    unsel = ['left', 'none']
    def __init__( self, proc ):
        changeSide.__init__(self, proc)

class changeModel(object):
    def __init__( self, proc ):
        self.proc = weakref.proxy( proc )
    def __call__( self, node ):
        if not node.isSelected(): return
        if self.left().isSelected() and self.right().isSelected():
            self.proc.model = self.model
        else:    self.proc.model = desync_msg

class changeModelANN(changeModel):
    def __init__( self, proc ):
        changeModel.__init__(self, proc)
        self.model = ann_model
    def updateModel( self ):
        e = self.proc.executionNode()
        model_hint = e.LeftSulciRecognition.recognition2000.model_hint
        if model_hint == 1:
          self.model = ann_model_2001
        else:
          self.model = ann_model
    def left(self):
        self.updateModel()
        e = self.proc.executionNode()
        return e.LeftSulciRecognition.recognition2000
    def right(self):
        self.updateModel()
        e = self.proc.executionNode()
        return e.RightSulciRecognition.recognition2000

class changeModelSPAM(changeModel):
    def __init__( self, proc ):
        changeModel.__init__(self, proc)
        self.model = spam_model
    def left(self):
        e = self.proc.executionNode()
        return e.LeftSulciRecognition.SPAM_recognition09
    def right(self):
        e = self.proc.executionNode()
        return e.RightSulciRecognition.SPAM_recognition09

class changeSpamMethod(object):
    def __init__(self, proc):
        self.proc = weakref.proxy( proc )
    def __call__( self, node=None): #ignore node
        # NOTE: can't be moved to __init__, since executionNode
        # does not exist yet
        e = self.proc.executionNode()
        self.nodeL = e.LeftSulciRecognition.SPAM_recognition09
        self.nodeR = e.RightSulciRecognition.SPAM_recognition09

        nodesL = self.nodeL.global_recognition, \
            self.nodeL.local_or_markovian, \
            self.nodeL.local_or_markovian.local_recognition, \
            self.nodeL.local_or_markovian.markovian_recognition
        NodesR = self.nodeR.global_recognition, \
            self.nodeR.local_or_markovian, \
            self.nodeR.local_or_markovian.local_recognition, \
            self.nodeR.local_or_markovian.markovian_recognition

        # 1) Desynchronized
        for (l, r) in zip(nodesL, NodesR):
            if l.isSelected() != r.isSelected():
                self.proc.spam_method = desync_msg
                return
        if self.nodeL.global_recognition.model_type != \
            self.nodeR.global_recognition.model_type:
                self.proc.spam_method = desync_msg
                return

        # 2) special cases
        node1 = self.globalSpam()
        node2 = self.localOrMarkovianSpam()
        if not node1.isSelected():
            # a) LocalOrMarkovian should be preceded
            #    by "Global SPAM"
            if node2.isSelected():
                self.proc.spam_method = "unknown"
            # b) Nothing selected
            else:    self.proc.spam_method = "none"
            return
        # 4) known methods :
        # Talairach, global, global+Markov, global+local
        # Other methods are not named ("unknown" is used)
        if not node2.isSelected(): # here: node 1 is selected
            if node1.model_type == 'Global registration':
                self.proc.spam_method = "global"
            elif node1.model_type == 'Talairach':
                self.proc.spam_method = "Talairach"
            else:    self.proc.spam_method = "unknown"
            return
        if node1.model_type == 'Global registration':
            if node2.local_recognition.isSelected():
                self.proc.spam_method = "global+local"
            elif node2.markovian_recognition.isSelected():
                self.proc.spam_method = "global+Markov"
            else:    self.proc.spam_method = "unknown"
        else:    self.proc.spam_method = "unknown"

    def globalSpam(self):
        return self.mainNode().global_recognition
    def localOrMarkovianSpam(self):
        return self.mainNode().local_or_markovian


class changeSpamMethodLeft(changeSpamMethod):
    def __init__( self, proc ):
        changeSpamMethod.__init__(self, proc)
    def mainNode(self):
        return self.nodeL

class changeSpamMethodRight(changeSpamMethod):
    def __init__( self, proc ):
        changeSpamMethod.__init__(self, proc)
    def mainNode(self):
        return self.nodeR


# Default values
def initialization( self ):
    # values = (left side selected, right side selected)
    side_select_map = {'left': (True, False), 'right' : (False, True),
                'both': (True, True), 'none' : (False, False)}
    # values = (Global/Talairach selected, mode,
    #           Local/Markov     selected, mode)
    spam_select_map = {'Talairach' : (True, "Talairach", False, None),
        'global' : (True, "Global registration", False, None),
        'global+local' : (True, "Global registration", True, "local"),
        'global+Markov' : (True, "Global registration", True, "Markov"),
        'none' : (False, None, False, None) }

    # create nodes
    eNode = ParallelExecutionNode( self.name, parameterized = self, optional=1)
    eNodeL = ProcessExecutionNode( 'recognitionGeneral',
            optional=1, selected=1)
    eNodeL._process.name = 'Sulci Recognition (left side)'
    eNode.addChild("LeftSulciRecognition", eNodeL)
    eNodeR = ProcessExecutionNode( 'recognitionGeneral',
            optional=1, selected=1)
    eNodeR._process.name = 'Sulci Recognition (right side)'
    eNode.addChild("RightSulciRecognition", eNodeR)
    eNodeLspam = eNodeL.SPAM_recognition09
    eNodeRspam = eNodeR.SPAM_recognition09

    # callbacks
    cL = changeSpamMethodLeft(self)
    cR = changeSpamMethodRight(self)

    def linkSpamMethod(method, names, parameterized):
        eNode = parameterized[0].executionNode()
        if method in [desync_msg, 'unknown'] :
            return

        select_step1, type_step1, select_step2, type_step2 = \
                        spam_select_map[method]


        # step 1
        Lstep1 = eNodeLspam.global_recognition
        Rstep1 = eNodeRspam.global_recognition
        Lstep1.setSelected(select_step1)
        Rstep1.setSelected(select_step1)
        if type_step1 is not None:
            Lstep1.model_type = type_step1
            Rstep1.model_type = type_step1

        # step 2
        Lstep2 = eNodeLspam.local_or_markovian
        Rstep2 = eNodeRspam.local_or_markovian
        Lstep2.setSelected(select_step2)
        Rstep2.setSelected(select_step2)
        if type_step2 == 'local' :
            Lstep2.local_recognition.setSelected(True)
            Rstep2.local_recognition.setSelected(True)
        elif type_step2 == 'Markov' :
            Lstep2.markovian_recognition.setSelected(True)
            Rstep2.markovian_recognition.setSelected(True)
        return method


    def linkModel(model, names, parameterized):
        process = parameterized[0]
        signature = process.signature
        eNode = process.executionNode()
        if model == spam_model:
            signature['spam_method'] = Choice('Talairach',
                'global', 'global+local', 'global+Markov',
                desync_msg, 'unknown', 'none')
            cL()
            cR()
            eNode.LeftSulciRecognition.SPAM_recognition09.setSelected(True)
            eNode.RightSulciRecognition.SPAM_recognition09.setSelected(True)
            eNode.addLink(None, 'spam_method', linkSpamMethod)
        elif model in ( ann_model, ann_model_2001 ):
            if model == ann_model:
              eNode.LeftSulciRecognition.recognition2000.model_hint = 0
              eNode.RightSulciRecognition.recognition2000.model_hint = 0
            else:
              eNode.LeftSulciRecognition.recognition2000.model_hint = 1
              eNode.RightSulciRecognition.recognition2000.model_hint = 1
            eNode.LeftSulciRecognition.recognition2000.setSelected(True)
            eNode.RightSulciRecognition.recognition2000.setSelected(True)
        if model != spam_model:
            if signature.has_key('spam_method'):
                del signature['spam_method']
        process.changeSignature(signature)

    def linkSide(side, names, parameterized):
        eNode = parameterized[0].executionNode()
        selectLeft, selectRight = side_select_map[side]
        eNode.LeftSulciRecognition.setSelected(selectLeft)
        eNode.RightSulciRecognition.setSelected(selectRight)


    # default
    self.side = 'both'
    # detect if SPAM models are here. If not, ANN is the default method
    # otherwise use SPAMs by default
    spammodels = ReadDiskItem( 'Sulci Segments Model', 'Text Data Table' \
      )._findValues( selection = { 'sulci_segments_model_type' : \
        'global_registered_spam' },
        requiredAttributes = None, write = False )
    try:
      spammodels.next()
      self.model = spam_model
    except StopIteration:
      self.model = ann_model

    eNode.addLink(None, 'side', linkSide)
    eNode.addLink(None, 'model', linkModel)

    # Side
    eNodeL._selectionChange.add(changeSideLeft(self))
    eNodeR._selectionChange.add(changeSideRight(self))

    # Model
    eNodeL.recognition2000._selectionChange.add(changeModelANN(self))
    eNodeL.SPAM_recognition09._selectionChange.add(changeModelSPAM(self))
    eNodeR.recognition2000._selectionChange.add(changeModelANN(self))
    eNodeR.SPAM_recognition09._selectionChange.add(changeModelSPAM(self))

    # SPAM Methods
    eNode.addLink(None, 'LeftSulciRecognition.SPAM_recognition09.' + \
                    'global_recognition.model_type', cL)
    eNodeLspam.global_recognition._selectionChange.add(cL)
    eNodeLspam.local_or_markovian._selectionChange.add(cL)
    eNodeLspam.local_or_markovian.local_recognition._selectionChange.add(cL)
    eNodeLspam.local_or_markovian.markovian_recognition._selectionChange.add(cL)
    eNode.addLink(None, 'RightSulciRecognition.SPAM_recognition09.' + \
                    'global_recognition.model_type', cR)
    eNodeRspam.global_recognition._selectionChange.add(cR)
    eNodeRspam.local_or_markovian._selectionChange.add(cR)
    eNodeRspam.local_or_markovian.local_recognition._selectionChange.add(cR)
    eNodeRspam.local_or_markovian.markovian_recognition._selectionChange.add(cR)

    self.setExecutionNode( eNode )

    self.addLink( 'LeftSulciRecognition.data_graph', 'left_data_graph' )
    self.addLink( 'left_data_graph', 'LeftSulciRecognition.data_graph' )
    self.addLink( 'LeftSulciRecognition.output_graph', 'left_output_graph' )
    self.addLink( 'left_output_graph', 'LeftSulciRecognition.output_graph' )
    self.addLink( 'RightSulciRecognition.data_graph', 'right_data_graph' )
    self.addLink( 'right_data_graph', 'RightSulciRecognition.data_graph' )
    self.addLink( 'RightSulciRecognition.output_graph', 'right_output_graph' )
    self.addLink( 'right_output_graph', 'RightSulciRecognition.output_graph' )
    self.linkParameters( 'right_data_graph', 'left_data_graph' )

