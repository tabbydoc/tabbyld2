from pathlib import Path


class ResultPath:
    # Path for source tables in CSV format
    CSV_FILE_PATH = str(Path(__file__).parent.parent) + "/source_tables/"
    # Path to save source tables in the form json files
    JSON_FILE_PATH = str(Path(__file__).parent.parent) + "/results/json/"
    # Path to save processing results and their provenance in the form json files
    PROVENANCE_PATH = str(Path(__file__).parent.parent) + "/results/provenance/"
    # Path for T2Dv2 dataset tables in JSON format
    T2DV2_JSON_PATH = str(Path(__file__).parent.parent) + "/datasets/T2Dv2/tables/"

    # Paths of result provenance
    CLEARED_DATA_PATH = "/cleared_data/"
    RECOGNIZED_DATA_PATH = "/recognized_data/"
    CLASSIFIED_DATA_PATH = "/classified_data/"

    CANDIDATE_ENTITIES_PATH = "/candidate_entities/"
    CANDIDATE_CLASSES_PATH = "/candidate_classes/"
    CANDIDATE_PROPERTIES_PATH = "/candidate_properties/"

    RANKED_CANDIDATE_ENTITIES = "/ranked_candidate_entities/"
    RANKED_CANDIDATE_ENTITIES_BY_SS = "/ranked_candidate_entities_by_ss/"
    RANKED_CANDIDATE_ENTITIES_BY_NS = "/ranked_candidate_entities_by_ns/"
    RANKED_CANDIDATE_ENTITIES_BY_HS = "/ranked_candidate_entities_by_hs/"
    RANKED_CANDIDATE_ENTITIES_BY_ESS = "/ranked_candidate_entities_by_ess/"
    RANKED_CANDIDATE_ENTITIES_BY_CS = "/ranked_candidate_entities_by_cs/"

    RANKED_CANDIDATE_CLASSES = "/ranked_candidate_classes/"
    RANKED_CANDIDATE_CLASSES_BY_MV = "/ranked_candidate_classes_by_mv/"
    RANKED_CANDIDATE_CLASSES_BY_HS = "/ranked_candidate_classes_by_hs/"
    RANKED_CANDIDATE_CLASSES_BY_CTP = "/ranked_candidate_classes_by_ctp/"

    ANNOTATED_CELLS_PATH = "/annotated_cells/"
    ANNOTATED_COLUMNS_PATH = "/annotated_columns/"
    ANNOTATED_PROPERTIES_PATH = "/annotated_relationships_between_columns/"
