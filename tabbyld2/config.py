from pathlib import Path


class ResultPath:
    # Path for source tables in CSV format
    CSV_FILE_PATH = str(Path(__file__).parent.parent) + "/source_tables/"
    # Path to save source tables in the form json files
    JSON_FILE_PATH = str(Path(__file__).parent.parent) + "/results/json/"
    # Path to save processing results and their provenance in the form json files
    PROVENANCE_PATH = str(Path(__file__).parent.parent) + "/results/provenance/"

    # JSON files of result provenance
    CLEARED_DATA = "cleared_data.json"
    RECOGNIZED_DATA = "recognized_data.json"
    CLASSIFIED_DATA = "classified_data.json"

    CANDIDATE_ENTITIES = "candidate_entities.json"
    CANDIDATE_CLASSES = "candidate_classes.json"
    CANDIDATE_PROPERTIES = "candidate_properties.json"

    RANKED_CANDIDATE_ENTITIES = "ranked_candidate_entities.json"
    RANKED_CANDIDATE_ENTITIES_BY_SS = "ranked_candidate_entities_by_ss.json"
    RANKED_CANDIDATE_ENTITIES_BY_NS = "ranked_candidate_entities_by_ns.json"
    RANKED_CANDIDATE_ENTITIES_BY_HS = "ranked_candidate_entities_by_hs.json"
    RANKED_CANDIDATE_ENTITIES_BY_ESS = "ranked_candidate_entities_by_ess.json"
    RANKED_CANDIDATE_ENTITIES_BY_CS = "ranked_candidate_entities_by_cs.json"

    RANKED_CANDIDATE_CLASSES = "ranked_candidate_classes.json"
    RANKED_CANDIDATE_CLASSES_BY_MV = "ranked_candidate_classes_by_mv.json"
    RANKED_CANDIDATE_CLASSES_BY_HS = "ranked_candidate_classes_by_hs.json"
    RANKED_CANDIDATE_CLASSES_BY_CTP = "ranked_candidate_classes_by_ctp.json"

    ANNOTATED_CELLS = "annotated_cells.json"
    ANNOTATED_COLUMNS = "annotated_columns.json"
    ANNOTATED_PROPERTIES = "annotated_properties.json"


class EvaluationPath:
    # Path to T2Dv2 dataset
    T2DV2 = str(Path(__file__).parent.parent) + "/datasets/T2Dv2/"
    # Path to positive examples in CSV format from T2Dv2 dataset
    T2DV2_POSITIVE_EXAMPLES = str(Path(__file__).parent.parent) + "/datasets/T2Dv2/positive_examples/"
    # Path to negative examples in CSV format from T2Dv2 dataset
    T2DV2_NEGATIVE_EXAMPLES = str(Path(__file__).parent.parent) + "/datasets/T2Dv2/negative_examples/"
    # Path to instances in CSV format from T2Dv2 dataset
    T2DV2_INSTANCE = str(Path(__file__).parent.parent) + "/datasets/T2Dv2/instance/"
    # File of class checked for T2Dv2 dataset
    T2DV2_CLASS_CHECKED = "col_class_checked_fg.csv"

    # Path to save evaluations in the form json files
    EVALUATION_PATH = str(Path(__file__).parent.parent) + "/results/evaluation/"

    # JSON files of table evaluations
    COLUMNS_CLASSIFICATION_EVALUATION = "columns_classification.json"
    SUBJECT_COLUMN_IDENTIFICATION_EVALUATION = "subject_column_identification.json"
    # JSON file of dataset evaluation
    TOTAL_EVALUATION = "total_evaluation.json"
