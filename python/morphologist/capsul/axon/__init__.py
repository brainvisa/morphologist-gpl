
# The auto conversion from Axon pipeline to CAPSUL has been done using the
# following command:
#
# python -m brainvisa.processing.axon_to_capsul -m morphologist.capsul.axon -s -u TalairachTransformationFromNormalization:morphologist.capsul.talairachtransformationfromnormalization.TalairachTransformationFromNormalization -u SPMnormalizationPipeline:morphologist.capsul.spmnormalization.SPMNormalization -u FSLnormalizationPipeline:morphologist.capsul.fslnormalization.FSLNormalization -p morphologist -o axonmorphologist.py -n morphologist:AxonMorphologist -n corticalfoldsgraph:SulciGraph -n acpcOrNormalization:BrainOrientation -n headMesh:ScalpMesh -n hemispheremesh:PialMesh -n NobiasHistoAnalysis:HistoAnalysis -n preparesubject:AcpcOrientation -n reorientAnatomy:ReorientAnatomy -n sulciskeleton:SulciSkeleton -n normalizationPipeline:Normalization -n recognition:SulciLabellingANN -n spam_recognition:SulciLabellingSPAM -n spam_recognitionglobal:SulciLabellingSPAMGlobal -n spam_recognitionlocal:SulciLabellingSPAMLocal -n recognitionGeneral:SulciLabelling -n spam_recognitionmarkov:SulciLabellingSPAMMarkov -n normalization_skullstripped:NormalizationSkullStripped -p AimsConverter -o aimsconverter.py -p ImportT1MRI -o importt1mri.py  -p morphologistProcess -o morphologistprocess.py -p CorticalFoldsGraphUpgradeFromOld -o corticalfoldsgraphupgradefromold.py
#
#
