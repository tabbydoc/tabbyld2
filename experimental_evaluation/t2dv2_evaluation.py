import csv
import json
import os
from datetime import datetime
from html import unescape
from urllib.parse import unquote

import pandas as pd
import stanza
from duckling import DucklingWrapper
from experimental_evaluation.evaluation_model import TableEvaluation
from tabbyld2.config import EvaluationPath, ResultPath
from tabbyld2.helpers.file import allowed_file, remove_suffix_in_filename, write_json_file
from tabbyld2.helpers.parser import deserialize_table, save_json_dataset
from tabbyld2.pipeline import pipeline_cell_entity_annotation, pipeline_column_type_annotation, pipeline_preprocessing
from tabbyld2.preprocessing.atomic_column_classifier import ColumnType


class T2Dv2TableEvaluation(TableEvaluation):

    def evaluate_subject_column_identification(self):
        """
        Evaluate subject column identification among categorical columns
        """
        checked_data = pd.DataFrame(pd.read_csv(EvaluationPath.T2DV2 + EvaluationPath.T2DV2_CLASS_CHECKED,
                                                sep=",", header=None, index_col=False))
        exist_subject_column = False
        for i in range(len(checked_data.get(0))):
            if checked_data.get(0)[i] == self.table.table_name:
                for j in range(len(self.table.columns)):
                    if self.table.columns[j].column_type == ColumnType.SUBJECT_COLUMN and j == int(checked_data.get(1)[i]) and \
                            checked_data.get(2)[i]:
                        exist_subject_column = True
        self.subject_column_identification_evaluation.set_precision(1.0 if exist_subject_column else 0.0)
        exist_subject_column = False
        for column in self.table.columns:
            if column.column_type == ColumnType.SUBJECT_COLUMN:
                exist_subject_column = True
        self.subject_column_identification_evaluation.set_recall(1.0 if exist_subject_column else 0.0)
        self.subject_column_identification_evaluation.calculate_f1_score()

    def evaluate_cell_entity_annotation(self):
        """
        Evaluate cell entity annotation (CEA) task
        """
        correctly_annotated_cells, annotated_cells, cell_number = 0, 0, 0
        with open(EvaluationPath.T2DV2_INSTANCE + self.table.table_name + ".csv", "r", newline="", encoding="utf-8") as file:
            for (uri, cell_value, cell_index) in csv.reader(file):
                cell_number += 1
                for column in self.table.columns:
                    if column.column_type == ColumnType.SUBJECT_COLUMN:
                        for i in range(len(column.cells)):
                            if column.cells[i].source_value is not None and int(cell_index) == (i + 1):
                                if unescape(cell_value.lower()) == column.cells[i].source_value.lower():
                                    if column.cells[i].annotation is not None:
                                        annotated_cells += 1
                                        annotations = [column.cells[i].annotation.uri, *column.cells[i].annotation.redirects]
                                        if unquote(uri) in annotations:
                                            correctly_annotated_cells += 1
                                        else:
                                            print("INS: " + unquote(uri) + " != ANN: " + column.cells[i].annotation.uri)
                                    else:
                                        print("INS: " + unquote(uri) + " != ANN: NULL")
                                else:
                                    print("CELL: " + unescape(cell_value.lower()) + " != CELL: " + column.cells[i].source_value.lower())
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
        # Get class checked data for tables from T2Dv2 dataset
        checked_data = pd.DataFrame(pd.read_csv(EvaluationPath.T2DV2 + EvaluationPath.T2DV2_CLASS_CHECKED,
                                                sep=",", header=None, index_col=False))
        perfect, okay, total, rows, column_indices = 0, 0, 0, [], {}
        for key, items in checked_data.items():
            if key == 0:
                for i in range(len(items)):
                    if items[i] == self.table.table_name:
                        rows.append(i)
            if key == 1:
                for i in range(len(items)):
                    for row_index in rows:
                        if i == row_index:
                            column_indices[row_index] = int(items[i])
            if key == 3:
                for i in range(len(items)):
                    for row_index in rows:
                        if i == row_index:
                            for row, column_index in column_indices.items():
                                for k in range(len(self.table.columns)):
                                    if i == row and column_index == k and self.table.columns[k].annotation is not None:
                                        total += 1
                                    if i == row and column_index == k and items[i] and str(items[i]) != "nan":
                                        if self.table.columns[k].column_type != ColumnType.LITERAL_COLUMN and \
                                                self.table.columns[k].annotation == items[i]:
                                            perfect += 1
            if key == 4:
                for i in range(len(items)):
                    for row_index in rows:
                        if i == row_index:
                            for row, column_index in column_indices.items():
                                for k in range(len(self.table.columns)):
                                    if i == row and column_index == k and items[i] and str(items[i]) != "nan":
                                        if self.table.columns[k].column_type != ColumnType.LITERAL_COLUMN and \
                                                self.table.columns[k].annotation in items[i].split(","):
                                            okay += 1
        print("***************************************************")
        print(column_indices)
        print("target_columns = " + str(len(column_indices)))
        print("perfect_annotations = " + str(perfect))
        print("okay_annotations = " + str(okay))
        print("all_annotations = " + str(total))
        wrong = total - (perfect + okay)
        print("wrong_annotations = " + str(wrong))
        print("***************************************************")
        self.column_type_annotation_evaluation.set_average_hierarchical_score(
            (1 * perfect + 0.5 * okay - 1 * wrong) / len(column_indices) if len(column_indices) != 0 else 0)
        self.column_type_annotation_evaluation.set_average_perfect_score(perfect / total if total != 0 else 0)


def evaluate_t2dv2_dataset():
    """
    Get experimental evaluation for tables from T2Dv2 dataset
    """
    start_full_time = datetime.now()
    table_evaluations = []
    # Save positive examples of tables from T2Dv2 dataset in the json format
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
                    t2dv2_table_evaluation = T2Dv2TableEvaluation(table)
                    t2dv2_table_evaluation.evaluate_columns_classification(EvaluationPath.T2DV2 + EvaluationPath.T2DV2_CLASS_CHECKED)
                    # Get subject column identification evaluation
                    t2dv2_table_evaluation.evaluate_subject_column_identification()
                    # Save preprocessing evaluation results to json files
                    path = EvaluationPath.EVALUATION_PATH + remove_suffix_in_filename(file) + "/"
                    write_json_file(path, EvaluationPath.COLUMNS_CLASSIFICATION_EVALUATION,
                                    t2dv2_table_evaluation.column_classification_evaluation.serialize_evaluation())
                    write_json_file(path, EvaluationPath.SUBJECT_COLUMN_IDENTIFICATION_EVALUATION,
                                    t2dv2_table_evaluation.subject_column_identification_evaluation.serialize_evaluation())
                    print("***************************************************")
                    print("Column classification evaluation:")
                    print("precision = " + str(t2dv2_table_evaluation.column_classification_evaluation.precision))
                    print("recall = " + str(t2dv2_table_evaluation.column_classification_evaluation.recall))
                    print("f1 = " + str(t2dv2_table_evaluation.column_classification_evaluation.f1_score))
                    print("***************************************************")
                    print("Subject column identification evaluation:")
                    print("precision = " + str(t2dv2_table_evaluation.subject_column_identification_evaluation.precision))
                    print("recall = " + str(t2dv2_table_evaluation.subject_column_identification_evaluation.recall))
                    print("f1 = " + str(t2dv2_table_evaluation.subject_column_identification_evaluation.f1_score))

                    # Get CEA task evaluation
                    t2dv2_table_evaluation.evaluate_cell_entity_annotation()
                    # Save CEA evaluation results to json files
                    write_json_file(path, EvaluationPath.CELL_ENTITY_ANNOTATION_EVALUATION,
                                    t2dv2_table_evaluation.cell_entity_annotation_evaluation.serialize_evaluation())
                    print("***************************************************")
                    print("CEA evaluation:")
                    print("precision = " + str(t2dv2_table_evaluation.cell_entity_annotation_evaluation.precision))
                    print("recall = " + str(t2dv2_table_evaluation.cell_entity_annotation_evaluation.recall))
                    print("f1 = " + str(t2dv2_table_evaluation.cell_entity_annotation_evaluation.f1_score))

                    # Get CTA task evaluation
                    t2dv2_table_evaluation.evaluate_column_type_annotation()
                    # Save CTA evaluation results to json files
                    write_json_file(path, EvaluationPath.COLUMN_TYPE_ANNOTATION_EVALUATION,
                                    t2dv2_table_evaluation.column_type_annotation_evaluation.serialize_evaluation())
                    print("***************************************************")
                    print("CTA evaluation:")
                    print("ah score = " + str(t2dv2_table_evaluation.column_type_annotation_evaluation.average_hierarchical_score))
                    print("ap score = " + str(t2dv2_table_evaluation.column_type_annotation_evaluation.average_perfect_score))

                    table_evaluations.append(t2dv2_table_evaluation)

    if table_evaluations:
        cc_precision, cc_recall, sci_precision, sci_recall, cea_precision, cea_recall, cta_ah_score, cta_ap_score = 0, 0, 0, 0, 0, 0, 0, 0
        all_cc_scores = 0
        for table_evaluation in table_evaluations:
            if table_evaluation.column_classification_evaluation is not None:
                cc_precision += table_evaluation.column_classification_evaluation.precision
                cc_recall += table_evaluation.column_classification_evaluation.recall
                all_cc_scores += 1
            if table_evaluation.subject_column_identification_evaluation is not None:
                sci_precision += table_evaluation.subject_column_identification_evaluation.precision
                sci_recall += table_evaluation.subject_column_identification_evaluation.recall
            if table_evaluation.cell_entity_annotation_evaluation is not None:
                cea_precision += table_evaluation.cell_entity_annotation_evaluation.precision
                cea_recall += table_evaluation.cell_entity_annotation_evaluation.recall
            if table_evaluation.column_type_annotation_evaluation is not None:
                cta_ah_score += table_evaluation.column_type_annotation_evaluation.average_hierarchical_score
                cta_ap_score += table_evaluation.column_type_annotation_evaluation.average_perfect_score

        # Get column classification evaluations for all tables from T2Dv2 dataset
        total_cc_p = cc_precision / all_cc_scores
        total_cc_r = cc_recall / all_cc_scores
        total_cc_f1 = (2 * total_cc_p * total_cc_r) / (total_cc_p + total_cc_r) if total_cc_p != 0 and total_cc_r != 0 else 0
        print("***************************************************")
        print("Total evaluation for atomic column classification:")
        print("precision = " + str(total_cc_p))
        print("recall = " + str(total_cc_r))
        print("f1 = " + str(total_cc_f1))
        # Get subject column identification evaluations for all tables from T2Dv2 dataset
        sci_precision = sci_precision / len(table_evaluations)
        sci_recall = sci_recall / len(table_evaluations)
        sci_f1_score = (2 * sci_precision * sci_recall) / (sci_precision + sci_recall) if sci_precision != 0 and sci_recall != 0 else 0
        print("***************************************************")
        print("Total evaluation for subject column identification:")
        print("precision = " + str(sci_precision))
        print("recall = " + str(sci_recall))
        print("f1 = " + str(sci_f1_score))
        # Get cell entity annotation evaluations for all tables from T2Dv2 dataset
        cea_precision = cea_precision / len(table_evaluations)
        cea_recall = cea_recall / len(table_evaluations)
        cea_f1_score = (2 * cea_precision * cea_recall) / (cea_precision + cea_recall) if cea_precision != 0 and cea_recall != 0 else 0
        print("***************************************************")
        print("Total evaluation for cell entity annotation:")
        print("precision = " + str(cea_precision))
        print("recall = " + str(cea_recall))
        print("f1 = " + str(cea_f1_score))
        # Get column type annotation evaluations for all tables from T2Dv2 dataset
        cta_ah_score = cta_ah_score / len(table_evaluations)
        cta_ap_score = cta_ap_score / len(table_evaluations)
        print("***************************************************")
        print("Total evaluation for column type annotation:")
        print("average hierarchical score = " + str(cta_ah_score))
        print("average perfect score = " + str(cta_ap_score))
        # Save evaluation results for T2Dv2 dataset to json file
        evaluations = {"column classification": {"precision": total_cc_p, "recall": total_cc_r, "f1_score": total_cc_f1},
                       "subject column identification": {"precision": sci_precision, "recall": sci_recall, "f1_score": sci_f1_score},
                       "cell entity annotation": {"precision": cea_precision, "recall": cea_recall, "f1_score": cea_f1_score},
                       "column type annotation": {"ah_score": cta_ah_score, "ap_score": cta_ap_score}}
        write_json_file(EvaluationPath.EVALUATION_PATH, EvaluationPath.TOTAL_EVALUATION, [evaluations])
        print("***************************************************")
        print("Full time: " + str(datetime.now() - start_full_time))


if __name__ == "__main__":
    evaluate_t2dv2_dataset()
