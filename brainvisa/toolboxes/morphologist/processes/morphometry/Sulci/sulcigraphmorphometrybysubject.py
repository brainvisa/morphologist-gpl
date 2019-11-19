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

from __future__ import print_function

from brainvisa.processes import *
import os
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
        raise ValidationError('no soma.aims module')


name = 'Sulci graph morphometry by subject'
userLevel = 0

signature = Signature(
    'left_sulci_graph', ReadDiskItem('Labelled Cortical folds graph', 'Graph',
                                     requiredAttributes={'side': 'left'}),
    'right_sulci_graph', ReadDiskItem('Labelled Cortical folds graph', 'Graph',
                                      requiredAttributes={'side': 'right'}),
    'sulci_file', ReadDiskItem('Sulci groups list', 'JSON file'),
    'use_attribute', Choice('label', 'name'),
    'sulcal_morpho_measures', WriteDiskItem(
        'Sulcal morphometry measurements', 'CSV File'),
)


def initialization(self):
    def linkAttribute(proc, dummy):
        if proc.left_sulci_graph is not None:
            if proc.left_sulci_graph.get('automatically_labelled') == 'No':
                return 'name'
        return 'label'

    self.linkParameters('right_sulci_graph', 'left_sulci_graph')
    self.linkParameters('sulcal_morpho_measures', 'left_sulci_graph')
    self.use_attribute = 'label'
    self.sulci_file = self.signature['sulci_file'].findValue(
        {'version': 'default'})
    self.linkParameters('use_attribute', 'left_sulci_graph', linkAttribute)


def weightedAverage(mesureslist):
    product = 0.
    weightsum = 0.
    for mesure, weight in mesureslist:
        product += mesure*weight
        weightsum += weight
    if weightsum != 0.:
        result = product/weightsum
    else:
        result = float('NaN')
    return result


def divSum(mesureslist):
    sum1 = 0.
    sum2 = 0.
    for mes1, mes2 in mesureslist:
        sum1 += mes1
        sum2 += mes2
    if sum2 != 0.:
        result = 2.*sum1/sum2
    else:
        result = float('NaN')
    return result


def execution(self, context):

    json_sulci = open(self.sulci_file.fullPath())
    sulci_sel = json.load(json_sulci)

    dict_morpho = {}
    list_sulci = []
    dict_sulci_inv = {}

    for sulcus in sulci_sel[next(iter(sulci_sel.keys()))]:
        for ss_sulcus in sulci_sel[next(iter(sulci_sel.keys()))][sulcus]:
            list_sulci.append(ss_sulcus)
            dict_sulci_inv[ss_sulcus] = sulcus

    lgraph = aims.read(self.left_sulci_graph.fullPath())
    rgraph = aims.read(self.right_sulci_graph.fullPath())

    for sulcus in (list(lgraph.vertices())+list(rgraph.vertices())):
        if (sulcus.getSyntax() == 'fold') and (sulcus[self.use_attribute] in list_sulci):
            surface_tal = 0.
            surface_nat = 0.
            maxdepth_tal = 0.
            maxdepth_nat = 0.
            bottom_point_number = 0.
            meandepth_tal = 0.
            meandepth_nat = 0.
            hj_length_tal = 0.
            hj_length_nat = 0.
            mid_interface_voxels = 0.
            thickness_mean = 0.
            CSF_volume = 0.

            # SURFACE
            if 'refsurface_area' in sulcus.keys():
                surface_tal = sulcus['refsurface_area']
            if 'surface_area' in sulcus.keys():
                surface_nat = sulcus['surface_area']
            # MAX_DEPTH
            if 'refmaxdepth' in sulcus.keys():
                maxdepth_tal = sulcus['refmaxdepth']
            if 'maxdepth' in sulcus.keys():
                maxdepth_nat = sulcus['maxdepth']
            # MEAN_DEPTH
            # Si les sillons sont trop petits, ils peuvent ne pas avoir de profondeur moyenne.
            if 'bottom_point_number' in sulcus.keys():
                bottom_point_number = sulcus['bottom_point_number']
            if 'refmean_depth' in sulcus.keys():
                meandepth_tal = sulcus['refmean_depth']
            if 'mean_depth' in sulcus.keys():
                meandepth_nat = sulcus['mean_depth']
            # LENGTH
            for rel in sulcus.edges():
                if rel.getSyntax() == 'hull_junction':
                    if 'reflength' not in rel:
                        context.write('no reflength in rel', rel)
                        context.write('vertex:', sulcus.get('name'), sulcus.get('index'))
                    else:
                        hj_length_tal = rel['reflength']
                        hj_length_nat = rel['length']
            # THICKNESS
            # Si la MG est trop fine, il peut ne pas y avoir d'epaisseur moyenne.
            if 'mid_interface_voxels' in sulcus.keys():
                mid_interface_voxels = sulcus['mid_interface_voxels']
            if 'thickness_mean' in sulcus.keys():
                thickness_mean = sulcus['thickness_mean']
            # OPENING
            if 'CSF_volume' in sulcus.keys():
                CSF_volume = sulcus['CSF_volume']

            # On ecrit les valeurs dans un dictionnaire, en rangeant par sillon principal.
            mainlabel = dict_sulci_inv[sulcus[self.use_attribute]]
            if mainlabel in dict_morpho:
                # Si le sillon existe deja on ajoute les mesures.
                dict_morpho[mainlabel]['surface_tal'].append(surface_tal)
                dict_morpho[mainlabel]['surface_nat'].append(surface_nat)
                dict_morpho[mainlabel]['maxdepth_tal'].append(maxdepth_tal)
                dict_morpho[mainlabel]['maxdepth_nat'].append(maxdepth_nat)
                dict_morpho[mainlabel]['meandepth_tal'].append(
                    (meandepth_tal, bottom_point_number))
                dict_morpho[mainlabel]['meandepth_nat'].append(
                    (meandepth_nat, bottom_point_number))
                dict_morpho[mainlabel]['hj_length_tal'].append(hj_length_tal)
                dict_morpho[mainlabel]['hj_length_nat'].append(hj_length_nat)
                dict_morpho[mainlabel]['thickness'].append(
                    (thickness_mean, mid_interface_voxels))
                dict_morpho[mainlabel]['opening'].append(
                    (CSF_volume, surface_nat))
            else:
                # Si le sillon n'existe pas encore, on le cree.
                dict_morpho[mainlabel] = {
                    'surface_tal': [surface_tal],
                    'surface_nat': [surface_nat],
                    'maxdepth_tal': [maxdepth_tal],
                    'maxdepth_nat': [maxdepth_nat],
                    'meandepth_tal': [(meandepth_tal, bottom_point_number)],
                    'meandepth_nat': [(meandepth_nat, bottom_point_number)],
                    'hj_length_tal': [hj_length_tal],
                    'hj_length_nat': [hj_length_nat],
                    'thickness': [(thickness_mean, mid_interface_voxels)],
                    'opening': [(CSF_volume, surface_nat)]}

    f = open(self.sulcal_morpho_measures.fullPath(), 'w')
    f.write('sulcus;label;side;surface_talairach;surface_native;maxdepth_talairach;maxdepth_native;meandepth_talairach;meandepth_native;hull_junction_length_talairach;hull_junction_length_native;GM_thickness;opening')

    for sulcus in sorted(sulci_sel[next(iter(sulci_sel.keys()))].keys()):
        # for sulcus in sorted(dict_morpho.keys()):
        if sulcus in dict_morpho.keys():
            # SURFACE
            surface_tal = round(sum(dict_morpho[sulcus]['surface_tal']), 2)
            surface_nat = round(sum(dict_morpho[sulcus]['surface_nat']), 2)
            # MAX_DEPTH
            maxdepth_tal = round(max(dict_morpho[sulcus]['maxdepth_tal']), 2)
            maxdepth_nat = round(max(dict_morpho[sulcus]['maxdepth_nat']), 2)
            # MEAN_DEPTH
            meandepth_tal = round(weightedAverage(
                dict_morpho[sulcus]['meandepth_tal']), 2)
            meandepth_nat = round(weightedAverage(
                dict_morpho[sulcus]['meandepth_nat']), 2)
            # LENGTH
            hj_length_tal = round(sum(dict_morpho[sulcus]['hj_length_tal']), 2)
            hj_length_nat = round(sum(dict_morpho[sulcus]['hj_length_nat']), 2)
            # THICKNESS
            thickness = round(weightedAverage(
                dict_morpho[sulcus]['thickness']), 2)
            # OPENING
            opening = round(divSum(dict_morpho[sulcus]['opening']), 2)
        else:
            surface_tal = float('NaN')
            surface_nat = float('NaN')
            maxdepth_tal = float('NaN')
            maxdepth_nat = float('NaN')
            meandepth_tal = float('NaN')
            meandepth_nat = float('NaN')
            hj_length_tal = float('NaN')
            hj_length_nat = float('NaN')
            thickness = float('NaN')
            opening = float('NaN')

        f.write('\n' + sulcus + ';' + sulcus.split('_')[0] + ';' + sulcus.split('_')[1] + ';' +
                str(surface_tal) + ';' + str(surface_nat) + ';' +
                str(maxdepth_tal) + ';' + str(maxdepth_nat) + ';' +
                str(meandepth_tal) + ';' + str(meandepth_nat) + ';' +
                str(hj_length_tal) + ';' + str(hj_length_nat) + ';' +
                str(thickness) + ';' + str(opening))
    f.close()
