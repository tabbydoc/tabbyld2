import html
import json
import os
import urllib.parse
import pandas as pd

from datetime import datetime

import tabbyld2.pipeline as pl
from experimental_evaluation.evaluation_model import AdditionalEvaluation, MainEvaluation, TableEvaluation

from tabbyld2.helpers.file import allowed_file, remove_suffix_in_filename, write_json_file
from tabbyld2.helpers.parser import deserialize_table, save_json_dataset
from tabbyld2.config import EvaluationPath, ResultPath
from tabbyld2.preprocessing.atomic_column_classifier import ColumnType


class T2Dv2TableEvaluation(TableEvaluation):
    """
    Experimental evaluations for table from T2Dv2 dataset.
    """

    def evaluate_subject_column_identification(self):
        """
        Evaluate subject column identification among categorical columns.
        """
        # Get class checked data for tables from T2Dv2 dataset
        checked_data = pd.DataFrame(pd.read_csv(EvaluationPath.T2DV2 + EvaluationPath.T2DV2_CLASS_CHECKED,
                                                sep=",", header=None, index_col=False))
        exist_subject_column, rows, column_indices = False, [], {}
        for key, items in checked_data.items():
            if key == 0:
                for i in range(len(items)):
                    if items[i] == self.table.table_name:
                        rows.append(i)
            if key == 1:
                for i in range(len(items)):
                    for row_index in rows:
                        if i == row_index:
                            column_indices[row_index] = items[i]
            if key == 2:
                for i in range(len(items)):
                    for row_index in rows:
                        if i == row_index:
                            for row, column_index in column_indices.items():
                                for k in range(len(self.table.columns)):
                                    if i == row and int(column_index) == k:
                                        if items[i] and self.table.columns[k].column_type == ColumnType.SUBJECT_COLUMN:
                                            exist_subject_column = True
        # Calculate evaluations
        self._subject_column_identification_evaluation = MainEvaluation()
        self._subject_column_identification_evaluation._precision = 1.0 if exist_subject_column else 0.0
        exist_subject_column = False
        for column in self.table.columns:
            if column.column_type == ColumnType.SUBJECT_COLUMN:
                exist_subject_column = True
        self._subject_column_identification_evaluation._recall = 1.0 if exist_subject_column else 0.0
        self._subject_column_identification_evaluation.calculate_f1_score()

    def evaluate_cell_entity_annotation(self):
        """
        Evaluate cell entity annotation (CEA) task.
        """
        for _, _, instance_files in os.walk(EvaluationPath.T2DV2_INSTANCE):
            for instance_file in instance_files:
                if remove_suffix_in_filename(instance_file) == self.table.table_name:
                    # Get checked tabular data
                    instance_data = pd.DataFrame(pd.read_csv(EvaluationPath.T2DV2_INSTANCE + instance_file, sep=",",
                                                             header=None, index_col=False, encoding="unicode_escape"))
                    # Annotation comparison
                    correctly_annotated_cells, annotated_cells, cell_number, instances, values = 0, 0, 0, [], []
                    for key, items in instance_data.items():
                        if key == 0:
                            instances, cell_number = items, len(items)
                        if key == 1:
                            values = items
                        if key == 2:
                            for column in self.table.columns:
                                if column.column_type == ColumnType.SUBJECT_COLUMN:
                                    for i in range(len(column.cells)):
                                        if column.cells[i].source_value is not None:
                                            for j in range(len(items)):
                                                if (i + 1) == int(items[j]):
                                                    if html.unescape(values[j].lower()) == \
                                                            column.cells[i].source_value.lower():
                                                        if column.cells[i].annotation is not None:
                                                            annotated_cells += 1
                                                            if urllib.parse.unquote(instances[j].lower()) == \
                                                                    column.cells[i].annotation.lower() or instances[j].encode("raw_unicode_escape").decode("utf-8").lower() == column.cells[i].annotation.lower():
                                                                correctly_annotated_cells += 1
                                                            else:
                                                                print("INS: " + urllib.parse.unquote(instances[j]) +
                                                                      " != ANN: " + column.cells[i].annotation)
                                                        else:
                                                            print("INS: " + urllib.parse.unquote(instances[j]) +
                                                                  " != ANN: NULL")
                    # Calculate evaluations
                    self._cell_entity_annotation_evaluation = MainEvaluation()
                    self._cell_entity_annotation_evaluation._precision = correctly_annotated_cells / annotated_cells if annotated_cells != 0 else 0
                    self._cell_entity_annotation_evaluation._recall = correctly_annotated_cells / cell_number if cell_number != 0 else 0
                    self._cell_entity_annotation_evaluation.calculate_f1_score()
                    print("***************************************************")
                    print("Correctly annotated cells = " + str(correctly_annotated_cells))
                    print("Annotated cells = " + str(annotated_cells))
                    print("Cell number = " + str(cell_number))

    def evaluate_column_type_annotation(self):
        """
        Evaluate column type annotation (CTA) task.
        """
        # Get class checked data for tables from T2Dv2 dataset
        checked_data = pd.DataFrame(pd.read_csv(EvaluationPath.T2DV2 + EvaluationPath.T2DV2_CLASS_CHECKED,
                                                sep=",", header=None, index_col=False))
        perfect_annotations, okay_annotations, wrong_annotations, all_annotations, rows, column_indices = 0, 0, 0, 0, [], {}
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
                                        all_annotations += 1
                                    if i == row and column_index == k and items[i] and str(items[i]) != "nan":
                                        if self.table.columns[k].column_type != ColumnType.LITERAL_COLUMN and self.table.columns[k].annotation == items[i]:
                                            perfect_annotations += 1
            if key == 4:
                for i in range(len(items)):
                    for row_index in rows:
                        if i == row_index:
                            for row, column_index in column_indices.items():
                                for k in range(len(self.table.columns)):
                                    if i == row and column_index == k and items[i] and str(items[i]) != "nan":
                                        if self.table.columns[k].column_type != ColumnType.LITERAL_COLUMN and self.table.columns[k].annotation in items[i].split(","):
                                            okay_annotations += 1
        print("***************************************************")
        print(column_indices)
        print("target_columns = " + str(len(column_indices)))
        print("perfect_annotations = " + str(perfect_annotations))
        print("okay_annotations = " + str(okay_annotations))
        print("all_annotations = " + str(all_annotations))
        wrong_annotations = all_annotations - (perfect_annotations + okay_annotations)
        print("wrong_annotations = " + str(wrong_annotations))
        print("***************************************************")
        # Calculate evaluations
        self._column_type_annotation_evaluation = AdditionalEvaluation()
        self._column_type_annotation_evaluation._average_hierarchical_score = (1 * perfect_annotations + 0.5 * okay_annotations - 1 * wrong_annotations) / len(column_indices)
        self._column_type_annotation_evaluation._average_perfect_score = perfect_annotations / all_annotations if all_annotations != 0 else 0


def evaluate_t2dv2_dataset():
    """
    Get experimental evaluation for tables from T2Dv2 dataset.
    """
    start_full_time = datetime.now()
    table_evaluations = []
    # Save positive examples of tables from T2Dv2 dataset in the json format
    save_json_dataset(ResultPath.CSV_FILE_PATH, ResultPath.JSON_FILE_PATH)
    # Cycle through table files
    for root, dirs, files in os.walk(ResultPath.JSON_FILE_PATH):
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
                    table = pl.pipeline_preprocessing(table, file)  # Preprocessing
                    table = pl.pipeline_cell_entity_annotation(table, file)  # Solve CEA task
                    table = pl.pipeline_column_type_annotation(table, file)  # Solve CTA task

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
        for table_evaluation in table_evaluations:
            if table_evaluation.column_classification_evaluation is not None:
                cc_precision += table_evaluation.column_classification_evaluation.precision
                cc_recall += table_evaluation.column_classification_evaluation.recall
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
        cc_precision = cc_precision / len(table_evaluations)
        cc_recall = cc_recall / len(table_evaluations)
        cc_f1_score = (2 * cc_precision * cc_recall) / (cc_precision + cc_recall) if cc_precision != 0 and cc_recall != 0 else 0
        print("***************************************************")
        print("Total evaluation for column classification:")
        print("precision = " + str(cc_precision))
        print("recall = " + str(cc_recall))
        print("f1 = " + str(cc_f1_score))
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
        evaluations = dict()
        evaluations["column classification"] = {"precision": cc_precision, "recall": cc_recall, "f1_score": cc_f1_score}
        evaluations["subject column identification"] = {"precision": sci_precision, "recall": sci_recall, "f1_score": sci_f1_score}
        evaluations["cell entity annotation"] = {"precision": cea_precision, "recall": cea_recall, "f1_score": cea_f1_score}
        evaluations["column type annotation"] = {"ah_score": cta_ah_score, "ap_score": cta_ap_score}
        write_json_file(EvaluationPath.EVALUATION_PATH, EvaluationPath.TOTAL_EVALUATION, evaluations)
        print("***************************************************")
        print("Full time: " + str(datetime.now() - start_full_time))


if __name__ == "__main__":
    evaluate_t2dv2_dataset()
