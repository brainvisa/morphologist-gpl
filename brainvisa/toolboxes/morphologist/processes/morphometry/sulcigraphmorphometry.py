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
import os, re
import sys
import json

try:
  from soma import aims
except:
  pass

def validation():
  try:
    from soma import aims
  except:
    raise ValidationError( 'no soma.aims module' )

name = 'Sulci Graph Morphometry'
userLevel = 2

signature = Signature(
    'sulci_graphs', ListOf(ReadDiskItem('Cortical folds graph', 'Graph',
                           requiredAttributes = {'graph_version' : '3.1'})),
    'sulci_file', ReadDiskItem('Text File', 'Text file'),
    'use_attribute', Choice('label', 'name'),
    'output_dir', ReadDiskItem('Directory', 'Directory'),
    'output_prefix', String(),
)


def initialization( self ):
    self.use_attribute = 'label'
    self.output_prefix = 'morpho_'
    self.setOptional('output_prefix')


def weightedAverage(mesureslist):
    product=0.
    weightsum=0.
    for mesure, weight in mesureslist:
        product += mesure*weight
        weightsum += weight
    if weightsum!=0.:
        result = product/weightsum
    else:
        result = 0.
    return result
    

def divSum(mesureslist):
    sum1=0.
    sum2=0.
    for mes1, mes2 in mesureslist:
        sum1 += mes1
        sum2 += mes2
    if sum2!=0.:
        result = 2.*sum1/sum2
    else:
        result = 0.
    return result

   
def execution( self, context ):
    
    json_sulci = open(self.sulci_file.fullPath())
    sulci_sel = json.load(json_sulci)
    
    dict_morpho = {}
    list_sulci = []
    dict_sulci_inv = {}
    
    for sulcus in sulci_sel[sulci_sel.keys()[0]]:
        for ss_sulcus in sulci_sel[sulci_sel.keys()[0]][sulcus]:
            list_sulci.append(ss_sulcus)
            dict_sulci_inv[ss_sulcus] = sulcus
    
    for sulci_graph in self.sulci_graphs:
        subject = sulci_graph.get('subject')
        graph = aims.read(sulci_graph.fullPath())      
        
        for sulcus in graph.vertices():
            if (sulcus.getSyntax()=='fold') and (sulcus[self.use_attribute] in list_sulci):                                                     
                ##SURFACE
                surface_tal = sulcus['refsurface_area']
                surface_nat = sulcus['surface_area']
                ##MAX_DEPTH
                maxdepth_tal = sulcus['refmaxdepth']
                maxdepth_nat = sulcus['maxdepth']
                ##MEAN_DEPTH
                #Si les sillons sont trop petits, ils peuvent ne pas avoir de profondeur moyenne.
                if 'refmean_depth' in sulcus.keys():
                    meandepth_tal = sulcus['refmean_depth']
                else:
                    meandepth_tal = 0.
                if 'mean_depth' in sulcus.keys():
                    meandepth_nat = sulcus['mean_depth']
                else:
                    meandepth_nat = 0.
                bottom_point_number = sulcus['bottom_point_number']
                ##LENGTH
                length_tal = 0.
                length_nat = 0.
                for rel in sulcus.edges():
                    if rel.getSyntax()=='hull_junction':
                        length_tal = rel['reflength']
                        length_nat = rel['length']
                ##THICKNESS
                #Si la MG est trop fine, il peut ne pas y avoir d'epaisseur moyenne.
                if 'thickness_mean' in sulcus.keys():
                    thickness_mean = sulcus['thickness_mean']
                    mid_interface_voxels = sulcus['mid_interface_voxels']
                else:
                    thickness_mean = 0.
                    mid_interface_voxels = 0.
                ##OPENING
                CSF_volume = sulcus['CSF_volume']
                surface_nat = sulcus['surface_area']
                
                #On ecrit les valeurs dans un dictionnaire, en rangeant par sillon principal puis par sujet.
                mainlabel = dict_sulci_inv[sulcus[self.use_attribute]]
                if dict_morpho.has_key(mainlabel):
                    if dict_morpho[mainlabel].has_key(subject):
                        #Si le sillon et le sujet existent deja on ajoute les mesures.
                        dict_morpho[mainlabel][subject]['surface_tal'].append(surface_tal)
                        dict_morpho[mainlabel][subject]['surface_nat'].append(surface_nat)
                        dict_morpho[mainlabel][subject]['maxdepth_tal'].append(maxdepth_tal)
                        dict_morpho[mainlabel][subject]['maxdepth_nat'].append(maxdepth_nat)
                        dict_morpho[mainlabel][subject]['meandepth_tal'].append((meandepth_tal, bottom_point_number))
                        dict_morpho[mainlabel][subject]['meandepth_nat'].append((meandepth_nat, bottom_point_number))
                        dict_morpho[mainlabel][subject]['length_tal'].append(length_tal)
                        dict_morpho[mainlabel][subject]['length_nat'].append(length_nat)
                        dict_morpho[mainlabel][subject]['thickness'].append((thickness_mean, mid_interface_voxels))
                        dict_morpho[mainlabel][subject]['opening'].append((CSF_volume, surface_nat))
                    else:
                        #Si le sujet n'existe pas encore, on le cree.
                        dict_morpho[mainlabel][subject] = {
                            'surface_tal': [surface_tal],
                            'surface_nat': [surface_nat],
                            'maxdepth_tal': [maxdepth_tal],
                            'maxdepth_nat': [maxdepth_nat],
                            'meandepth_tal': [(meandepth_tal, bottom_point_number)],
                            'meandepth_nat': [(meandepth_nat, bottom_point_number)],
                            'length_tal': [length_tal],
                            'length_nat': [length_nat],
                            'thickness': [(thickness_mean, mid_interface_voxels)],
                            'opening': [(CSF_volume, surface_nat)]}
                else:
                    #Si le sillon n'existe pas encore, on le cree.
                    dict_morpho[mainlabel] = {subject: {
                        'surface_tal': [surface_tal],
                        'surface_nat': [surface_nat],
                        'maxdepth_tal': [maxdepth_tal],
                        'maxdepth_nat': [maxdepth_nat],
                        'meandepth_tal': [(meandepth_tal, bottom_point_number)],
                        'meandepth_nat': [(meandepth_nat, bottom_point_number)],
                        'length_tal': [length_tal],
                        'length_nat': [length_nat],
                        'thickness': [(thickness_mean, mid_interface_voxels)],
                        'opening': [(CSF_volume, surface_nat)]}}
    
    for sulcus in dict_morpho.keys():
        output_file = os.path.join(self.output_dir.fullPath(), self.output_prefix+sulcus+'.dat')
        f = open( output_file, 'w' )
        f.write('subject;label;surface_talairach;surface_native;maxdepth_talairach;maxdepth_native;meandepth_talairach;meandepth_native;length_talairach;length_native;GM_thickness;opening\n')
        
        for sub in sorted(dict_morpho[sulcus].keys()):
            ##SURFACE
            surface_tal = round(sum(dict_morpho[sulcus][sub]['surface_tal']), 2)
            surface_nat = round(sum(dict_morpho[sulcus][sub]['surface_nat']), 2)
            ##MAX_DEPTH
            maxdepth_tal = round(max(dict_morpho[sulcus][sub]['maxdepth_tal']), 2)
            maxdepth_nat = round(max(dict_morpho[sulcus][sub]['maxdepth_nat']), 2)
            ##MEAN_DEPTH
            meandepth_tal = round(weightedAverage(dict_morpho[sulcus][sub]['meandepth_tal']), 2)
            meandepth_nat = round(weightedAverage(dict_morpho[sulcus][sub]['meandepth_nat']), 2)
            ##LENGTH
            length_tal = round(sum(dict_morpho[sulcus][sub]['length_tal']), 2)
            length_nat = round(sum(dict_morpho[sulcus][sub]['length_nat']), 2)
            ##THICKNESS
            thickness = round(weightedAverage(dict_morpho[sulcus][sub]['thickness']), 2)          
            ##OPENING
            opening = round(divSum(dict_morpho[sulcus][sub]['opening']), 2)
            
            f.write(sub + ';' + sulcus + ';' + 
                    str(surface_tal) + ';' + str(surface_nat) + ';' + 
                    str(maxdepth_tal) + ';' + str(maxdepth_nat) + ';' + 
                    str(meandepth_tal) + ';' + str(meandepth_nat) + ';' +
                    str(length_tal) + ';' + str(length_nat) + ';' +
                    str(thickness) + ';' + str(opening) + '\n')
        f.close()

    
    
    
    
    
    
    
    
    
