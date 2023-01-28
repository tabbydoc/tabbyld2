import csv
import json
import os
from datetime import datetime

import stanza
from atomic_column_classifier import ColumnType
from dbpedia_sparql_endpoint import get_parent_classes
from duckling import DucklingWrapper
from experimental_evaluation.evaluation_model import TableEvaluation
from tabbyld2.config import EvaluationPath, ResultPath
from tabbyld2.helpers.file import allowed_file, remove_suffix_in_filename, write_json_file
from tabbyld2.helpers.parser import deserialize_table, save_json_dataset
from tabbyld2.pipeline import pipeline_cell_entity_annotation, pipeline_column_type_annotation, pipeline_preprocessing


class ToughTableEvaluation(TableEvaluation):
    """
    Experimental evaluations for table from Tough Tables dataset
    """
    def evaluate_cell_entity_annotation(self):
        """
        Evaluate cell entity annotation (CEA) task
        """
        correctly_annotated_cells, annotated_cells, cell_number = 0, 0, 0
        with open(EvaluationPath.TOUGH_TABLES_CEA + self.table.table_name + ".csv", "r", newline="", encoding="utf-8") as file:
            for text in csv.reader(file):
                cell_number += 1
                _, column_index, row_index, uris = str(text).split(',"')
                j = 0
                for column in self.table.columns:
                    if int(column_index[:-1]) == j and column.column_type != ColumnType.LITERAL_COLUMN:
                        i = int(row_index[:-1]) - 1
                        if column.cells[i].source_value is not None:
                            if column.cells[i].annotation is not None:
                                annotated_cells += 1
                                annotations = [column.cells[i].annotation.uri, *column.cells[i].annotation.redirects]
                                if list(set(annotations) & set(uris[:-3].split())):
                                    correctly_annotated_cells += 1
                                else:
                                    print("INS: " + str(uris[:-3].split()) + " != ANN: " + str(annotations))
                            else:
                                print("INS: " + str(uris[:-3].split()) + " != ANN: NULL")
                        else:
                            print("Cell value " + str(i) + " is NULL")
                    j += 1
        self.cell_entity_annotation_evaluation.set_precision(correctly_annotated_cells / annotated_cells if annotated_cells != 0 else 0)
        self.cell_entity_annotation_evaluation.set_recall(correctly_annotated_cells / cell_number if cell_number != 0 else 0)
        self.cell_entity_annotation_evaluation.calculate_f1_score()
        print("***************************************************")
        print("Correctly annotated cells = " + str(correctly_annotated_cells))
        print("Annotated cells = " + str(annotated_cells))
        print("Cell number = " + str(cell_number))

    def evaluate_column_type_annotation(self):
        """
        Evaluate column type annotation (CTA) task
        """
        target_columns, perfect, okay, wrong = 0, 0, 0, 0
        with open(EvaluationPath.TOUGH_TABLES_GT + EvaluationPath.TOUGH_TABLES_CLASS_CHECKED, "r", newline="", encoding="utf-8") as file:
            for (table_name, column_index, dbpedia_class) in csv.reader(file):
                if table_name == self.table.table_name:
                    target_columns += 1
                    j = 0
                    for column in self.table.columns:
                        if int(column_index) == j and column.annotation is not None:
                            if dbpedia_class == column.annotation:
                                perfect += 1
                            else:
                                if column.annotation in get_parent_classes(dbpedia_class):
                                    okay += 1
                                else:
                                    wrong += 1
                        j += 1
        print("***************************************************")
        print("target_columns = " + str(target_columns))
        print("perfect_annotations = " + str(perfect))
        print("okay_annotations = " + str(okay))
        print("wrong_annotations = " + str(wrong))
        all_annotations = perfect + okay + wrong
        print("all_annotations = " + str(all_annotations))
        print("***************************************************")
        average_hierarchical_score = (1 * perfect + 0.5 * okay - 1 * wrong) / target_columns if target_columns != 0 else 0
        self.column_type_annotation_evaluation.set_average_hierarchical_score(average_hierarchical_score)
        self.column_type_annotation_evaluation.set_average_perfect_score(perfect / all_annotations if all_annotations != 0 else 0)


def evaluate_tough_tables_dataset():
    """
    Get experimental evaluation for tables from Tough_Tables dataset
    """
    start_full_time = datetime.now()
    table_evaluations = []
    # Save source tables from Tough_Tables dataset in the json format
    save_json_dataset(ResultPath.CSV_FILE_PATH, ResultPath.JSON_FILE_PATH)
    stanza.download("en")  # Init Stanford NER annotator
    named_entity_recognition = stanza.Pipeline(lang="en", processors="tokenize,ner")  # Neural pipeline preparation
    duckling_wrapper = DucklingWrapper()  # Init DucklingWrapper object
    # Cycle through table files
    for _, _, files in os.walk(ResultPath.JSON_FILE_PATH):
        for file in files:
            if allowed_file(file, {"json"}):
                print("File '" + str(file) + "' processing started!")
                try:
                    with open(ResultPath.JSON_FILE_PATH + file, "r", encoding="utf-8") as fp:
                        # Deserialize a source table in the json format (create a table model)
                        table = deserialize_table(remove_suffix_in_filename(file), json.load(fp))
                except json.decoder.JSONDecodeError:
                    print("Error decoding json table file!")
                if table is not None:
                    table = pipeline_preprocessing(table, file, named_entity_recognition, duckling_wrapper)  # Preprocessing
                    table = pipeline_cell_entity_annotation(table, file)  # Solve CEA task
                    table = pipeline_column_type_annotation(table, file)  # Solve CTA task

                    # Get column classification evaluation
                    tough_tables_evaluation = ToughTableEvaluation(table)
                    tough_tables_evaluation.evaluate_columns_classification(
                        EvaluationPath.TOUGH_TABLES_GT + EvaluationPath.TOUGH_TABLES_CLASS_CHECKED)
                    # Save preprocessing evaluation results to json files
                    path = EvaluationPath.EVALUATION_PATH + remove_suffix_in_filename(file) + "/"
                    write_json_file(path, EvaluationPath.COLUMNS_CLASSIFICATION_EVALUATION,
                                    tough_tables_evaluation.column_classification_evaluation.serialize_evaluation())
                    print("***************************************************")
                    print("Column classification evaluation:")
                    print("precision = " + str(tough_tables_evaluation.column_classification_evaluation.precision))
                    print("recall = " + str(tough_tables_evaluation.column_classification_evaluation.recall))
                    print("f1 = " + str(tough_tables_evaluation.column_classification_evaluation.f1_score))

                    # Get CEA task evaluation
                    tough_tables_evaluation.evaluate_cell_entity_annotation()
                    # Save CEA evaluation results to json files
                    write_json_file(path, EvaluationPath.CELL_ENTITY_ANNOTATION_EVALUATION,
                                    tough_tables_evaluation.cell_entity_annotation_evaluation.serialize_evaluation())
                    print("***************************************************")
                    print("CEA evaluation:")
                    print("precision = " + str(tough_tables_evaluation.cell_entity_annotation_evaluation.precision))
                    print("recall = " + str(tough_tables_evaluation.cell_entity_annotation_evaluation.recall))
                    print("f1 = " + str(tough_tables_evaluation.cell_entity_annotation_evaluation.f1_score))

                    # Get CTA task evaluation
                    tough_tables_evaluation.evaluate_column_type_annotation()
                    # Save CTA evaluation results to json files
                    write_json_file(path, EvaluationPath.COLUMN_TYPE_ANNOTATION_EVALUATION,
                                    tough_tables_evaluation.column_type_annotation_evaluation.serialize_evaluation())
                    print("***************************************************")
                    print("CTA evaluation:")
                    print("ah score = " + str(tough_tables_evaluation.column_type_annotation_evaluation.average_hierarchical_score))
                    print("ap score = " + str(tough_tables_evaluation.column_type_annotation_evaluation.average_perfect_score))

                    table_evaluations.append(tough_tables_evaluation)

    if table_evaluations:
        cc_precision, cc_recall, all_scores, cea_precision, cea_recall, cta_ah_score, cta_ap_score = 0, 0, 0, 0, 0, 0, 0
        for table_evaluation in table_evaluations:
            if table_evaluation.column_classification_evaluation is not None:
                cc_precision += table_evaluation.column_classification_evaluation.precision
                cc_recall += table_evaluation.column_classification_evaluation.recall
                all_scores += 1
            if table_evaluation.cell_entity_annotation_evaluation is not None:
                cea_precision += table_evaluation.cell_entity_annotation_evaluation.precision
                cea_recall += table_evaluation.cell_entity_annotation_evaluation.recall
            if table_evaluation.column_type_annotation_evaluation is not None:
                cta_ah_score += table_evaluation.column_type_annotation_evaluation.average_hierarchical_score
                cta_ap_score += table_evaluation.column_type_annotation_evaluation.average_perfect_score
        # Get column classification scores for all tables from Tough_Tables dataset
        total_cc_p = cc_precision / all_scores
        total_cc_r = cc_recall / all_scores
        total_cc_f1 = (2 * total_cc_p * total_cc_r) / (total_cc_p + total_cc_r) if total_cc_p != 0 and total_cc_r != 0 else 0
        print("***************************************************")
        print("Total evaluation for atomic column classification:")
        print("precision = " + str(total_cc_p))
        print("recall = " + str(total_cc_r))
        print("f1 = " + str(total_cc_f1))
        print("***************************************************")

        # Get cell entity annotation evaluations for all tables from Tough_Tables dataset
        cea_precision = cea_precision / len(table_evaluations)
        cea_recall = cea_recall / len(table_evaluations)
        cea_f1_score = (2 * cea_precision * cea_recall) / (cea_precision + cea_recall) if cea_precision != 0 and cea_recall != 0 else 0
        print("***************************************************")
        print("Total evaluation for cell entity annotation:")
        print("precision = " + str(cea_precision))
        print("recall = " + str(cea_recall))
        print("f1 = " + str(cea_f1_score))
        # Get column type annotation evaluations for all tables from Tough_Tables dataset
        cta_ah_score = cta_ah_score / len(table_evaluations)
        cta_ap_score = cta_ap_score / len(table_evaluations)
        print("***************************************************")
        print("Total evaluation for column type annotation:")
        print("average hierarchical score = " + str(cta_ah_score))
        print("average perfect score = " + str(cta_ap_score))
        # Save evaluation results for Tough_Tables dataset to json file
        evaluations = {"column classification": {"precision": total_cc_p, "recall": total_cc_r, "f1_score": total_cc_f1},
                       "cell entity annotation": {"precision": cea_precision, "recall": cea_recall, "f1_score": cea_f1_score},
                       "column type annotation": {"ah_score": cta_ah_score, "ap_score": cta_ap_score}}
        write_json_file(EvaluationPath.EVALUATION_PATH, EvaluationPath.TOTAL_EVALUATION, [evaluations])
        print("***************************************************")
        print("Full time: " + str(datetime.now() - start_full_time))


if __name__ == "__main__":
    evaluate_tough_tables_dataset()
