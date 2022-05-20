import tabbyld2.utility as utl
from typing import Optional
from tabbyld2.annotator import SemanticTableAnnotator
from tabbyld2.column_classifier import TableColumnClassifier
from tabbyld2.config import ResultPath
from tabbyld2.knowledge_graph_model import EntityRankingMethod, ClassRankingMethod
from tabbyld2.tabular_data_model import TableModel


def pipeline_preprocessing(table_model: TableModel = None, file: str = None, include_serialization: bool = True) \
        -> Optional[TableModel]:
    """
    Pipeline for table preprocessing procedure, including named-entity recognition for cells, columns classification and
    subject column identification.
    :param table_model: table model
    :param file: full file name
    :param include_serialization: flag to include or exclude json serialization from result
    :return: new table model
    """
    # Tabular data cleaning
    table_model.clean(True)
    # Create column classifier object
    column_classifier = TableColumnClassifier(table_model)
    # Recognize named entities for table cells
    column_classifier.recognize_named_entities()
    # Classify table columns
    column_classifier.classify_columns()
    # Identify a subject column among categorical columns (named entity columns)
    column_classifier.define_subject_column()
    # Serialize results in json format
    if include_serialization:
        path = ResultPath.PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + "/"
        utl.write_json_file(path, ResultPath.CLEARED_DATA, table_model.serialize_cleared_table())
        utl.write_json_file(path, ResultPath.RECOGNIZED_DATA,
                            column_classifier.table_model.serialize_recognized_named_entities())
        utl.write_json_file(path, ResultPath.CLASSIFIED_DATA,
                            column_classifier.table_model.serialize_classified_columns())

    return column_classifier.table_model


def pipeline_cell_entity_annotation(table_model: TableModel = None, file: str = None,
                                    include_serialization: bool = True) -> Optional[TableModel]:
    """
    Pipeline for cell entity annotation (CEA) task.
    :param table_model: table model
    :param file: full file name
    :param include_serialization: flag to include or exclude json serialization from result
    :return: new table model
    """
    # Create semantic table annotator object
    annotator = SemanticTableAnnotator(table_model)
    # Find candidate entities for all cells of categorical columns including a subject column
    annotator.find_candidate_entities()
    # Rank candidate entities by string similarity
    annotator.rank_candidate_entities_by_string_similarity()
    # Rank candidate entities by NER based similarity
    # annotator.rank_candidate_entities_by_ner_based_similarity()
    # Rank candidate entities by heading based similarity
    annotator.rank_candidate_entities_by_heading_based_similarity()
    # Rank candidate entities by entity embeddings based similarity
    # annotator.rank_candidate_entities_by_entity_embeddings_based_similarity()
    # Rank candidate entities by context based similarity
    annotator.rank_candidate_entities_by_context_based_similarity()
    # Aggregate scores for candidate entities obtained based on five heuristics
    annotator.aggregate_ranked_candidate_entities()
    # Annotate cell values (mentions) based on ranked candidate entities
    annotator.annotate_cells()
    # Serialize results in json format
    if include_serialization:
        path = ResultPath.PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + "/"
        utl.write_json_file(path, ResultPath.CANDIDATE_ENTITIES,
                            annotator.table_model.serialize_candidate_entities_for_cells())
        utl.write_json_file(path, ResultPath.RANKED_CANDIDATE_ENTITIES_BY_SS,
                            annotator.table_model.serialize_ranked_candidate_entities(
                                EntityRankingMethod.STRING_SIMILARITY))
        utl.write_json_file(path, ResultPath.RANKED_CANDIDATE_ENTITIES_BY_NS,
                            annotator.table_model.serialize_ranked_candidate_entities(
                                EntityRankingMethod.NER_BASED_SIMILARITY))
        utl.write_json_file(path, ResultPath.RANKED_CANDIDATE_ENTITIES_BY_HS,
                            annotator.table_model.serialize_ranked_candidate_entities(
                                EntityRankingMethod.HEADING_BASED_SIMILARITY))
        utl.write_json_file(path, ResultPath.RANKED_CANDIDATE_ENTITIES_BY_ESS,
                            annotator.table_model.serialize_ranked_candidate_entities(
                                EntityRankingMethod.ENTITY_EMBEDDINGS_BASED_SIMILARITY))
        utl.write_json_file(path, ResultPath.RANKED_CANDIDATE_ENTITIES_BY_CS,
                            annotator.table_model.serialize_ranked_candidate_entities(
                                EntityRankingMethod.CONTEXT_BASED_SIMILARITY))
        utl.write_json_file(path, ResultPath.RANKED_CANDIDATE_ENTITIES,
                            annotator.table_model.serialize_ranked_candidate_entities(
                                EntityRankingMethod.SCORES_AGGREGATION))
        utl.write_json_file(path, ResultPath.ANNOTATED_CELLS, annotator.table_model.serialize_annotated_cells())

    return annotator.table_model


def pipeline_column_type_annotation(table_model: TableModel = None, file: str = None,
                                    include_serialization: bool = True) -> Optional[TableModel]:
    """
    Pipeline for column type annotation (CTA) task.
    :param table_model: table model
    :param file: full file name
    :param include_serialization: flag to include or exclude json serialization from result
    :return: new table model
    """
    # Create semantic table annotator object
    annotator = SemanticTableAnnotator(table_model)
    # Rank candidate classes for categorical columns by majority voting method
    annotator.rank_candidate_classes_by_majority_voting()
    # Rank candidate classes for categorical columns by heading similarity
    annotator.rank_candidate_classes_by_heading_similarity()
    # Rank candidate classes for categorical columns by column type prediction
    annotator.rank_candidate_classes_by_column_type_prediction()
    # Aggregate scores for candidate classes obtained based on three methods
    annotator.aggregate_ranked_candidate_classes()
    # Annotate categorical columns based on ranked candidate classes
    annotator.annotate_categorical_columns()
    # Annotate literal columns based on recognized named entities for cells
    annotator.annotate_literal_columns()
    # Serialize results in json format
    if include_serialization:
        path = ResultPath.PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + "/"
        utl.write_json_file(path, ResultPath.RANKED_CANDIDATE_CLASSES_BY_MV,
                            annotator.table_model.serialize_ranked_candidate_classes(
                                ClassRankingMethod.MAJORITY_VOTING))
        utl.write_json_file(path, ResultPath.RANKED_CANDIDATE_CLASSES_BY_HS,
                            annotator.table_model.serialize_ranked_candidate_classes(
                                ClassRankingMethod.HEADING_SIMILARITY))
        utl.write_json_file(path, ResultPath.RANKED_CANDIDATE_CLASSES_BY_CTP,
                            annotator.table_model.serialize_ranked_candidate_classes(
                                ClassRankingMethod.COLUMN_TYPE_PREDICTION))
        utl.write_json_file(path, ResultPath.RANKED_CANDIDATE_CLASSES,
                            annotator.table_model.serialize_ranked_candidate_classes(
                                ClassRankingMethod.SCORES_AGGREGATION))
        utl.write_json_file(path, ResultPath.ANNOTATED_COLUMNS,
                            annotator.table_model.serialize_annotated_columns())

    return annotator.table_model
