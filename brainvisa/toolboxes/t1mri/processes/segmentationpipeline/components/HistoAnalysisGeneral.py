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

from neuroProcesses import *

name = 'Histogram analysis'
userLevel = 2
 
signature = Signature(
  'mri_corrected', ReadDiskItem( 'T1 MRI Bias Corrected',
      'Aims readable volume formats' ),
  'histo_analysis', WriteDiskItem( 'Histo Analysis', 'Histo Analysis' ),
  'hfiltered', ReadDiskItem( "T1 MRI Filtered For Histo",
      'Aims readable volume formats' ),
  'white_ridges', ReadDiskItem( "T1 MRI White Matter Ridges",
      'Aims readable volume formats' )
)


def selected( self, subproc ):
  if subproc._selected:
    self.signature[ 'hfiltered' ].mandatory = True
    self.signature[ 'white_ridges' ].mandatory = True
  else:
    self.setOptional( 'hfiltered' )
    self.setOptional( 'white_ridges' )


def initialization( self ):
  self.setOptional( 'hfiltered' )
  self.setOptional( 'white_ridges' )

  eNode = SelectionExecutionNode( self.name, parameterized = self )
  eNode.addChild( 'HistoAnalysis05',
                  ProcessExecutionNode( 'NobiasHistoAnalysis', selected = 0 ) )
  eNode.addChild( 'HistoAnalysis04',
                  ProcessExecutionNode( 'VipHistoAnalysis', selected = 1 ) )

  # break internal links

  # this doesn't work because weakref.proxy is a bullshit
  # eNode.HistoAnalysis05.removeLink( 'histo_analysis', 'mri_corrected' )
  # eNode.HistoAnalysis05.removeLink( 'hfiltered', 'mri_corrected' )
  # eNode.HistoAnalysis05.removeLink( 'white_ridges', 'mri_corrected' )
  # eNode.HistoAnalysis04.removeLink( 'histo_analysis', 'mri_corrected' )
  # so we do this dirty things
  eNode.HistoAnalysis05.clearLinksFrom( 'mri_corrected' )
  eNode.HistoAnalysis04.clearLinksFrom( 'mri_corrected' )

  # links for 2005 version

  eNode.addLink( 'HistoAnalysis05.mri_corrected', 'mri_corrected' )
  eNode.addLink( 'mri_corrected', 'HistoAnalysis05.mri_corrected' )
  eNode.addLink( 'HistoAnalysis05.histo_analysis', 'histo_analysis' )
  eNode.addLink( 'histo_analysis', 'HistoAnalysis05.histo_analysis' )
  eNode.addLink( 'HistoAnalysis05.hfiltered', 'hfiltered' )
  eNode.addLink( 'hfiltered', 'HistoAnalysis05.hfiltered' )
  eNode.addLink( 'HistoAnalysis05.white_ridges', 'white_ridges' )
  eNode.addLink( 'white_ridges', 'HistoAnalysis05.white_ridges' )

  # links for 2004 version

  eNode.addLink( 'HistoAnalysis04.mri_corrected', 'mri_corrected' )
  eNode.addLink( 'mri_corrected', 'HistoAnalysis04.mri_corrected' )
  eNode.addLink( 'HistoAnalysis04.histo_analysis', 'histo_analysis' )
  eNode.addLink( 'histo_analysis', 'HistoAnalysis04.histo_analysis' )

  # self links

  eNode.addLink( 'histo_analysis', 'mri_corrected' )
  eNode.addLink( 'hfiltered', 'mri_corrected' )
  eNode.addLink( 'white_ridges', 'mri_corrected' )

  # callback to handle 2005-specific parameters

  eNode.HistoAnalysis05._selectionChange.add( self.selected )

  self.setExecutionNode( eNode )

