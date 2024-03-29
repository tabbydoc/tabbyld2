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
    RANKED_CANDIDATE_CLASSES_BY_NS = "ranked_candidate_classes_by_ns.json"

    ANNOTATED_CELLS = "annotated_cells.json"
    ANNOTATED_COLUMNS = "annotated_columns.json"
    ANNOTATED_PROPERTIES = "annotated_properties.json"


class EvaluationPath:
    T2DV2 = str(Path(__file__).parent.parent) + "/datasets/T2Dv2/"  # Path to T2Dv2 dataset
    T2DV2_JSON = T2DV2 + "tables/"  # Path to source T2Dv2 tables in the JSON format
    T2DV2_POSITIVE_EXAMPLES = T2DV2 + "positive_examples/"  # Path to positive examples in CSV format from T2Dv2 dataset
    T2DV2_NEGATIVE_EXAMPLES = T2DV2 + "negative_examples/"  # Path to negative examples in CSV format from T2Dv2 dataset
    T2DV2_INSTANCE = T2DV2 + "instance/"  # Path to instances in CSV format from T2Dv2 dataset
    T2DV2_CLASS_CHECKED = "extend_col_class_checked_fg.csv"  # File of class checked for T2Dv2 dataset

    TOUGH_TABLES = str(Path(__file__).parent.parent) + "/datasets/Tough_Tables/"  # Path to Tough_Tables dataset
    TOUGH_TABLES_EXAMPLES = TOUGH_TABLES + "tables/"  # Path to source tables in CSV format from Tough_Tables dataset
    TOUGH_TABLES_GT = TOUGH_TABLES + "gt/"  # Path to checked files for Tough_Tables dataset
    TOUGH_TABLES_CEA = TOUGH_TABLES_GT + "CEA_2T_gt/"  # Path to checked CEA task files for Tough_Tables dataset
    TOUGH_TABLES_CLASS_CHECKED = "CTA_2T_gt.csv"  # File of class checked for Tough_Tables dataset

    GIT_TABLES_SEMTAB_2022 = str(Path(__file__).parent.parent) + "/datasets/GitTables_SemTab_2022/"  # Path to GitTables_SemTab_2022 dataset
    GIT_TABLES_SEMTAB_2022_EXAMPLES = GIT_TABLES_SEMTAB_2022 + "tables/"  # Path to source tables from GitTables_SemTab_2022 dataset
    GIT_TABLES_SEMTAB_2022_GT = GIT_TABLES_SEMTAB_2022 + "gt/"  # Path to checked files for GitTables_SemTab_2022 dataset
    GIT_TABLES_SEMTAB_2022_CLASS_CHECKED = "dbpedia_property_train.csv"  # File of class checked for GitTables_SemTab_2022 dataset

    EVALUATION_PATH = str(Path(__file__).parent.parent) + "/results/evaluation/"  # Path to save evaluations in the form json files

    # JSON files of table evaluations
    COLUMNS_CLASSIFICATION_EVALUATION = "columns_classification.json"
    SUBJECT_COLUMN_IDENTIFICATION_EVALUATION = "subject_column_identification.json"
    CELL_ENTITY_ANNOTATION_EVALUATION = "cell_entity_annotation.json"
    COLUMN_TYPE_ANNOTATION_EVALUATION = "column_type_annotation.json"
    COLUMNS_PROPERTY_ANNOTATION_EVALUATION = "columns_property_annotation.json"
    TOTAL_EVALUATION = "total_evaluation.json"  # JSON file of dataset evaluation
