
from morphologist.capsul.qc import database_qc_table
import json
import os.path as osp


class MorphologistQcTable(database_qc_table.DatabaseQcTable):

    @staticmethod
    def get_qc_status(proc, path):
        if not osp.exists(path):
            return proc.statuses.BAD
        with open(path) as f:
            report = json.load(f)
        stat = {
            'OK': proc.statuses.OK,
            'Warning': proc.statuses.WARNING,
            'Suspicious': proc.statuses.SUSPICIOUS,
            'Bad': proc.statuses.BAD,
        }
        status = report.get('status', 'Bad')
        return stat[status]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.status_for_type[
            'morphologist.capsul.morphologist.Morphologist.Report_report_json'
            ] = MorphologistQcTable.get_qc_status
        self.data_types = [
            'morphologist.capsul.morphologist.Morphologist.t1mri',
            'morphologist.capsul.morphologist.Morphologist.t1mri_nobias',
            'morphologist.capsul.morphologist.Morphologist.histo_analysis',

            'morphologist.capsul.morphologist.Morphologist.BrainSegmentation_brain_mask',
            'morphologist.capsul.morphologist.Morphologist.split_brain',
            'morphologist.capsul.morphologist.Morphologist.HeadMesh_head_mesh',
            'morphologist.capsul.morphologist.Morphologist.GreyWhiteClassification_grey_white',
            'morphologist.capsul.morphologist.Morphologist.GreyWhiteClassification_1_grey_white',
            'morphologist.capsul.morphologist.Morphologist.GreyWhiteTopology_hemi_cortex',
            'morphologist.capsul.morphologist.Morphologist.GreyWhiteTopology_1_hemi_cortex',
            'morphologist.capsul.morphologist.Morphologist.GreyWhiteMesh_white_mesh',
            'morphologist.capsul.morphologist.Morphologist.GreyWhiteMesh_1_white_mesh',
            'morphologist.capsul.morphologist.Morphologist.SulciSkeleton_skeleton',
            'morphologist.capsul.morphologist.Morphologist.SulciSkeleton_1_skeleton',

            'morphologist.capsul.morphologist.Morphologist.PialMesh_pial_mesh',
            'morphologist.capsul.morphologist.Morphologist.PialMesh_1_pial_mesh',
            'morphologist.capsul.morphologist.Morphologist.left_graph',
            'morphologist.capsul.morphologist.Morphologist.right_graph',
            'morphologist.capsul.morphologist.Morphologist.left_labelled_graph',
            'morphologist.capsul.morphologist.Morphologist.right_labelled_graph',

            'morphologist.capsul.morphologist.Morphologist.sulcal_morpho_measures',
            'morphologist.capsul.morphologist.Morphologist.GlobalMorphometry_brain_volumes_file',
            'morphologist.capsul.morphologist.Morphologist.Report_report',
            'morphologist.capsul.morphologist.Morphologist.Report_report_json']
        # self.data_filters = ["{'center': 'subjects'}"]
        self.keys = ['subject', 'acquisition', 'bids', 'sulci_recognition_session']
        self.type_labels = [
            'Raw T1 MRI', 'Bias Corrected', 'Histo Analysis', 'Brain Mask',
            'Hemispheres Split', 'Head Mesh',
            'Left Grey White Mask', 'Right Grey White Mask',
            'Left CSF+GREY Mask', 'Right CSF+GREY Mask',
            'Left Hemisphere White Mesh', 'Right Hemisphere White Mesh',
            'Left Cortex Skeleton', 'Right Cortex Skeleton',
            'Left Hemisphere Mesh', 'Right Hemisphere Mesh',
            'Left Cortical Sulci', 'Right Cortical Sulci',
            'Left Labelled Sulci', 'Right Labelled Sulci',
            'Sulcal morphometry measurements', 'Brain volumes',
            'Report', 'QC']


del database_qc_table  # just to avois ambiguity on the process in the module


if __name__ == '__main__':
    from capsul.api import capsul_engine
    from soma.qt_gui.qt_backend import Qt

    def get_qc_status(proc, path):
        if not osp.exists(path):
            return proc.statuses.BAD
        with open(path) as f:
            report = json.load(f)
        stat = {
            'OK': proc.statuses.OK,
            'Warning': proc.statuses.WARNING,
            'Suspicious': proc.statuses.SUSPICIOUS,
            'Bad': proc.statuses.BAD,
        }
        status = report.get('status', 'Bad')
        return stat[status]

    engine = capsul_engine()
    proc = MorphologistQcTable()
    proc.set_study_config(engine.study_config)
    proc.database = '/home/dr144257/data/baseessai'
    proc.fom = 'morphologist-auto-1.0'
    # proc.database = '/home/dr144257/data/morpho_bids/derivatives/morphologist-6.0'
    # proc.fom = 'morphologist-bids-2.0'
    # proc.output_file = '/tmp/qc_report.pdf'

    qapp = Qt.QApplication([])
    keep = proc()
    qapp.exec()
    del keep
