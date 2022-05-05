
# The auto conversion from Axon pipeline to CAPSUL has been done using the
# following command:
#
# python -m brainvisa.processing.axon_to_capsul -c 3 -m morphologist.capsul3.axon -s -u TalairachTransformationFromNormalization:morphologist.capsul3.talairachtransformationfromnormalization.TalairachTransformationFromNormalization -u SPMnormalizationPipeline:morphologist.capsul3.spmnormalization.SPMNormalization -u FSLnormalizationPipeline:morphologist.capsul3.fslnormalization.FSLNormalization -p morphologist -o axonmorphologist.py -n morphologist:AxonMorphologist -n corticalfoldsgraph:SulciGraph -n acpcOrNormalization:BrainOrientation -n headMesh:ScalpMesh -n hemispheremesh:PialMesh -n NobiasHistoAnalysis:HistoAnalysis -n preparesubject:AcpcOrientation -n reorientAnatomy:ReorientAnatomy -n sulciskeleton:SulciSkeleton -n normalizationPipeline:Normalization -n recognition:SulciLabellingANN -n spam_recognition:SulciLabellingSPAM -n spam_recognitionglobal:SulciLabellingSPAMGlobal -n spam_recognitionlocal:SulciLabellingSPAMLocal -n recognitionGeneral:SulciLabelling -n spam_recognitionmarkov:SulciLabellingSPAMMarkov -n normalization_skullstripped:NormalizationSkullStripped -p AimsConverter -o aimsconverter.py -p ImportT1MRI -o importt1mri.py
#
# THEN a few edits are needed:
# in t1biascorrection.py:
# - self.add_field('field' -> self.add_field('b_field'
# - in execution():
#   add lines after if value is undefined: continue
#             # patch forbidden field name "field"
#             if name == 'b_field':
#                 name = 'field'



