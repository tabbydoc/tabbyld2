from typing import Optional

from tabbyld2.config import ResultPath
from tabbyld2.datamodel.knowledge_graph_model import ClassRankingMethod, EntityRankingMethod
from tabbyld2.datamodel.tabular_data_model import TableModel
from tabbyld2.helpers.file import remove_suffix_in_filename, write_json_file
from tabbyld2.preprocessing.atomic_column_classifier import AtomicColumnClassifier
from tabbyld2.preprocessing.subject_column_identifier import SubjectColumnIdentifier
from tabbyld2.table_annotation.annotator import SemanticTableAnnotator


def pipeline_preprocessing(table_model: TableModel, file: str, include_serialization: bool = True) -> Optional[TableModel]:
    """
    Pipeline for table preprocessing procedure, including named-entity recognition for cells, columns classification and
    subject column identification
    :param table_model: a table model
    :param file: a file name with extension
    :param include_serialization: a flag to include or exclude JSON serialization from result
    :return: a new table model
    """
    table_model.clean(True)  # Tabular data cleaning
    column_classifier = AtomicColumnClassifier(table_model)
    column_classifier.classify_columns()  # Classify table columns on atomic types
    subject_column_identifier = SubjectColumnIdentifier(column_classifier.table_model)
    subject_column_identifier.identify_subject_column()  # Identify a subject column among categorical columns (named entity columns)
    # Serialize results in json format
    if include_serialization:
        path = ResultPath.PROVENANCE_PATH + remove_suffix_in_filename(file) + "/"
        write_json_file(path, ResultPath.CLEARED_DATA, table_model.serialize_cleared_table())
        write_json_file(path, ResultPath.RECOGNIZED_DATA, subject_column_identifier.table_model.serialize_recognized_named_entities())
        write_json_file(path, ResultPath.CLASSIFIED_DATA, subject_column_identifier.table_model.serialize_classified_columns())
    return subject_column_identifier.table_model


def pipeline_cell_entity_annotation(table_model: TableModel, file: str, include_serialization: bool = True) -> Optional[TableModel]:
    """
    Pipeline for cell entity annotation (CEA) task
    :param table_model: a table model
    :param file: a file name with extension
    :param include_serialization: a flag to include or exclude json serialization from result
    :return: a new table model
    """
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
        path = ResultPath.PROVENANCE_PATH + remove_suffix_in_filename(file) + "/"
        write_json_file(path, ResultPath.CANDIDATE_ENTITIES, annotator.table_model.serialize_candidate_entities_for_cells())
        write_json_file(path, ResultPath.RANKED_CANDIDATE_ENTITIES_BY_SS, annotator.table_model.serialize_ranked_candidate_entities(
            EntityRankingMethod.STRING_SIMILARITY))
        write_json_file(path, ResultPath.RANKED_CANDIDATE_ENTITIES_BY_NS, annotator.table_model.serialize_ranked_candidate_entities(
            EntityRankingMethod.NER_BASED_SIMILARITY))
        write_json_file(path, ResultPath.RANKED_CANDIDATE_ENTITIES_BY_HS, annotator.table_model.serialize_ranked_candidate_entities(
            EntityRankingMethod.HEADING_BASED_SIMILARITY))
        write_json_file(path, ResultPath.RANKED_CANDIDATE_ENTITIES_BY_ESS, annotator.table_model.serialize_ranked_candidate_entities(
            EntityRankingMethod.ENTITY_EMBEDDINGS_BASED_SIMILARITY))
        write_json_file(path, ResultPath.RANKED_CANDIDATE_ENTITIES_BY_CS, annotator.table_model.serialize_ranked_candidate_entities(
            EntityRankingMethod.CONTEXT_BASED_SIMILARITY))
        write_json_file(path, ResultPath.RANKED_CANDIDATE_ENTITIES, annotator.table_model.serialize_ranked_candidate_entities(
            EntityRankingMethod.SCORES_AGGREGATION))
        write_json_file(path, ResultPath.ANNOTATED_CELLS, annotator.table_model.serialize_annotated_cells())
    return annotator.table_model


def pipeline_column_type_annotation(table_model: TableModel, file: str, include_serialization: bool = True) -> Optional[TableModel]:
    """
    Pipeline for column type annotation (CTA) task
    :param table_model: a table model
    :param file: a file name with extension
    :param include_serialization: a flag to include or exclude json serialization from result
    :return: a new table model
    """
    # Define path
    path = ResultPath.PROVENANCE_PATH + remove_suffix_in_filename(file) + "/" if include_serialization and file is not None else None
    annotator = SemanticTableAnnotator(table_model)  # Create semantic table annotator object
    # Rank candidate classes for categorical columns by majority voting method
    annotator.rank_candidate_classes_by_majority_voting()
    if path is not None:
        # Serialize majority voting results in json format
        write_json_file(path, ResultPath.RANKED_CANDIDATE_CLASSES_BY_MV,
                        annotator.table_model.serialize_ranked_candidate_classes(ClassRankingMethod.MAJORITY_VOTING))
    # Rank candidate classes for categorical columns by heading similarity
    annotator.rank_candidate_classes_by_heading_similarity()
    if path is not None:
        # Serialize heading similarity results in json format
        write_json_file(path, ResultPath.RANKED_CANDIDATE_CLASSES_BY_HS,
                        annotator.table_model.serialize_ranked_candidate_classes(ClassRankingMethod.HEADING_SIMILARITY))
    # Rank candidate classes for categorical columns by column type prediction
    annotator.rank_candidate_classes_by_column_type_prediction()
    if path is not None:
        # Serialize column type prediction results in json format
        write_json_file(path, ResultPath.RANKED_CANDIDATE_CLASSES_BY_CTP,
                        annotator.table_model.serialize_ranked_candidate_classes(ClassRankingMethod.COLUMN_TYPE_PREDICTION))
    annotator.aggregate_ranked_candidate_classes()  # Aggregate scores for candidate classes obtained based on three methods
    if path is not None:
        # Serialize score aggregation results in json format
        write_json_file(path, ResultPath.RANKED_CANDIDATE_CLASSES,
                        annotator.table_model.serialize_ranked_candidate_classes(ClassRankingMethod.SCORES_AGGREGATION))
    annotator.annotate_categorical_columns()  # Annotate categorical columns based on ranked candidate classes
    annotator.annotate_literal_columns()  # Annotate literal columns based on recognized named entities for cells
    if path is not None:
        # Serialize column annotation results in json format
        write_json_file(path, ResultPath.ANNOTATED_COLUMNS, annotator.table_model.serialize_annotated_columns())
    return annotator.table_model
