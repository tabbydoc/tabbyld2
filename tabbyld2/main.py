import os
import json
import tabbyld2.parser as pr
import tabbyld2.utility as utl
from tabbyld2.config import ResultPath
from tabbyld2.knowledge_graph_model import EntityRankingMethod, ClassRankingMethod
from tabbyld2.annotator import SemanticTableAnnotator
from tabbyld2.column_classifier import TableColumnClassifier
from tabbyld2.tabular_data_model import ColumnCellModel, TableColumnModel, TableModel


if __name__ == '__main__':
    # Save a set of source tables in the json format
    pr.save_json_dataset(ResultPath.CSV_FILE_PATH, ResultPath.JSON_FILE_PATH)
    # Cycle through table files
    for root, dirs, files in os.walk(ResultPath.JSON_FILE_PATH):
        for file in files:
            if utl.allowed_file(file, {"json"}):
                try:
                    with open(ResultPath.JSON_FILE_PATH + file, "r", encoding="utf-8") as fp:
                        print("File '" + str(file) + "' processing started!")
                        # Deserialize a source table in the json format (create a table model)
                        source_json_data = json.load(fp)
                        columns = tuple()
                        dicts = {k: [d[k] for d in source_json_data] for k in source_json_data[0]}
                        for key, items in dicts.items():
                            cells = tuple()
                            for item in items:
                                cells += (ColumnCellModel(item),)
                            columns += (TableColumnModel(key, cells),)
                        table = TableModel(file, columns)

                        # Tabular data cleaning
                        table.clean(True)
                        utl.write_json_file(file, ResultPath.CLEARED_DATA_PATH, table.serialize_cleared_table())

                        column_classifier = TableColumnClassifier(table)
                        # Recognize named entities for table cells
                        column_classifier.recognize_named_entities()
                        # Classify table columns
                        column_classifier.classify_columns()
                        # Identify a subject column among categorical columns (named entity columns)
                        column_classifier.define_subject_column()
                        table = column_classifier.table_model
                        utl.write_json_file(file, ResultPath.RECOGNIZED_DATA_PATH,
                                            table.serialize_recognized_named_entities())
                        utl.write_json_file(file, ResultPath.CLASSIFIED_DATA_PATH, table.serialize_classified_columns())

                        annotator = SemanticTableAnnotator(table)
                        # Find candidate entities for all cells of categorical columns including a subject column
                        annotator.find_candidate_entities()
                        utl.write_json_file(file, ResultPath.CANDIDATE_ENTITIES_PATH,
                                            annotator.table_model.serialize_candidate_entities_for_cells())
                        # Rank candidate entities by string similarity
                        annotator.rank_candidate_entities_by_string_similarity()
                        utl.write_json_file(file, ResultPath.RANKED_CANDIDATE_ENTITIES_BY_SS,
                                            annotator.table_model.serialize_ranked_candidate_entities(
                                                EntityRankingMethod.STRING_SIMILARITY))
                        # Rank candidate entities by NER based similarity
                        annotator.rank_candidate_entities_by_ner_based_similarity()
                        utl.write_json_file(file, ResultPath.RANKED_CANDIDATE_ENTITIES_BY_NS,
                                            annotator.table_model.serialize_ranked_candidate_entities(
                                                EntityRankingMethod.NER_BASED_SIMILARITY))
                        # Rank candidate entities by heading based similarity
                        annotator.rank_candidate_entities_by_heading_based_similarity()
                        utl.write_json_file(file, ResultPath.RANKED_CANDIDATE_ENTITIES_BY_HS,
                                            annotator.table_model.serialize_ranked_candidate_entities(
                                                EntityRankingMethod.HEADING_BASED_SIMILARITY))
                        # Rank candidate entities by entity embeddings based similarity
                        annotator.rank_candidate_entities_by_entity_embeddings_based_similarity()
                        utl.write_json_file(file, ResultPath.RANKED_CANDIDATE_ENTITIES_BY_ESS,
                                            annotator.table_model.serialize_ranked_candidate_entities(
                                                EntityRankingMethod.ENTITY_EMBEDDINGS_BASED_SIMILARITY))
                        # Rank candidate entities by context based similarity
                        annotator.rank_candidate_entities_by_context_based_similarity()
                        utl.write_json_file(file, ResultPath.RANKED_CANDIDATE_ENTITIES_BY_CS,
                                            annotator.table_model.serialize_ranked_candidate_entities(
                                                EntityRankingMethod.CONTEXT_BASED_SIMILARITY))
                        # Aggregate scores for candidate entities obtained based on five heuristics
                        annotator.aggregate_ranked_candidate_entities()
                        utl.write_json_file(file, ResultPath.RANKED_CANDIDATE_ENTITIES,
                                            annotator.table_model.serialize_ranked_candidate_entities(
                                                EntityRankingMethod.SCORES_AGGREGATION))
                        # Annotate cell values (mentions) based on ranked candidate entities
                        annotator.annotate_cells()
                        utl.write_json_file(file, ResultPath.ANNOTATED_CELLS_PATH,
                                            annotator.table_model.serialize_annotated_cells())

                        # Rank candidate classes for categorical columns by majority voting method
                        annotator.rank_candidate_classes_by_majority_voting()
                        utl.write_json_file(file, ResultPath.RANKED_CANDIDATE_CLASSES_BY_MV,
                                            annotator.table_model.serialize_ranked_candidate_classes(
                                                ClassRankingMethod.MAJORITY_VOTING))
                        # Rank candidate classes for categorical columns by heading similarity
                        annotator.rank_candidate_classes_by_heading_similarity()
                        utl.write_json_file(file, ResultPath.RANKED_CANDIDATE_CLASSES_BY_HS,
                                            annotator.table_model.serialize_ranked_candidate_classes(
                                                ClassRankingMethod.HEADING_SIMILARITY))
                        # Rank candidate classes for categorical columns by column type prediction
                        annotator.rank_candidate_classes_by_column_type_prediction()
                        utl.write_json_file(file, ResultPath.RANKED_CANDIDATE_CLASSES_BY_CTP,
                                            annotator.table_model.serialize_ranked_candidate_classes(
                                                ClassRankingMethod.COLUMN_TYPE_PREDICTION))
                        # Aggregate scores for candidate classes obtained based on three methods
                        annotator.aggregate_ranked_candidate_classes()
                        utl.write_json_file(file, ResultPath.RANKED_CANDIDATE_CLASSES,
                                            annotator.table_model.serialize_ranked_candidate_classes(
                                                ClassRankingMethod.SCORES_AGGREGATION))
                        # Annotate categorical columns based on ranked candidate classes
                        annotator.annotate_categorical_columns()
                        utl.write_json_file(file, ResultPath.ANNOTATED_COLUMNS_PATH,
                                            annotator.table_model.serialize_annotated_columns())
                except json.decoder.JSONDecodeError:
                    print("Error decoding json table file!")
