import os
import json
import html
import urllib.parse
import pandas as pd
import tabbyld2.parser as pr
import tabbyld2.utility as utl
import tabbyld2.pipeline as pl
from datetime import datetime
from experimental_evaluation.evaluation_model import TableEvaluation, BaseEvaluation
from tabbyld2.config import ResultPath, EvaluationPath
from tabbyld2.column_classifier import ColumnType
from tabbyld2.tabular_data_model import TableModel


class T2Dv2TableEvaluation(TableEvaluation):
    """
    Experimental evaluations for table from T2Dv2 dataset.
    """
    def evaluate_columns_classification(self):
        """
        Evaluate atomic classification of table columns (categorical or literal).
        """
        # Get number of classified columns
        classified_columns = 0
        for column in self.table.columns:
            if column.column_type is not None:
                classified_columns += 1
        # Get class checked data for tables from T2Dv2 dataset
        checked_data = pd.DataFrame(pd.read_csv(EvaluationPath.T2DV2 + EvaluationPath.T2DV2_CLASS_CHECKED,
                                                sep=",", header=None, index_col=False))
        # Get number of correctly classified columns
        categorical_column_number, literal_column_number, rows = 0, 0, []
        for key, items in checked_data.items():
            if key == 0:
                for i in range(len(items)):
                    if items[i] == self.table.table_name:
                        rows.append(i)
                literal_column_number = len(self.table.columns) - len(rows)
            if key == 1:
                for i in range(len(items)):
                    for row_index in rows:
                        if i == row_index:
                            for k in range(len(self.table.columns)):
                                if k == int(items[i]):
                                    if self.table.columns[k].column_type == ColumnType.SUBJECT_COLUMN or self.table.columns[k].column_type == ColumnType.CATEGORICAL_COLUMN:
                                        categorical_column_number += 1
        correctly_classified_columns = categorical_column_number + literal_column_number
        # Calculate evaluations
        self._column_classification_evaluation = BaseEvaluation()
        self._column_classification_evaluation._precision = correctly_classified_columns / classified_columns if classified_columns != 0 else 0
        self._column_classification_evaluation._recall = correctly_classified_columns / len(self.table.columns) if len(self.table.columns) != 0 else 0
        self._column_classification_evaluation.calculate_f1_score()

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
        self._subject_column_identification_evaluation = BaseEvaluation()
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
        for instance_root, instance_dirs, instance_files in os.walk(EvaluationPath.T2DV2_INSTANCE):
            for instance_file in instance_files:
                if utl.remove_suffix_in_filename(instance_file) == self.table.table_name:
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
                    self._cell_entity_annotation_evaluation = BaseEvaluation()
                    self._cell_entity_annotation_evaluation._precision = correctly_annotated_cells / annotated_cells if annotated_cells != 0 else 0
                    self._cell_entity_annotation_evaluation._recall = correctly_annotated_cells / cell_number if cell_number != 0 else 0
                    self._cell_entity_annotation_evaluation.calculate_f1_score()
                    print("***************************************************")
                    print("Correctly annotated cells = " + str(correctly_annotated_cells))
                    print("Annotated cells = " + str(annotated_cells))
                    print("Cell number = " + str(cell_number))


def evaluate_t2dv2_dataset():
    """
    Get experimental evaluation for tables from T2Dv2 dataset.
    """
    start_full_time = datetime.now()
    table_evaluations = []
    # Save positive examples of tables from T2Dv2 dataset in the json format
    pr.save_json_dataset(ResultPath.CSV_FILE_PATH, ResultPath.JSON_FILE_PATH)
    # Cycle through table files
    for root, dirs, files in os.walk(ResultPath.JSON_FILE_PATH):
        for file in files:
            if utl.allowed_file(file, {"json"}):
                print("File '" + str(file) + "' processing started!")
                try:
                    with open(ResultPath.JSON_FILE_PATH + file, "r", encoding="utf-8") as fp:
                        # Deserialize a source table in the json format (create a table model)
                        table = TableModel.deserialize_source_table(utl.remove_suffix_in_filename(file), json.load(fp))
                except json.decoder.JSONDecodeError:
                    print("Error decoding json table file!")
                if table is not None:
                    # Preprocessing table
                    table = pl.pipeline_preprocessing(table, file)
                    # Solve CEA task
                    table = pl.pipeline_cell_entity_annotation(table, file)

                    # Get column classification evaluation
                    t2dv2_table_evaluation = T2Dv2TableEvaluation(table)
                    t2dv2_table_evaluation.evaluate_columns_classification()
                    # Get subject column identification evaluation
                    t2dv2_table_evaluation.evaluate_subject_column_identification()
                    # Save preprocessing evaluation results to json files
                    path = EvaluationPath.EVALUATION_PATH + utl.remove_suffix_in_filename(file) + "/"
                    utl.write_json_file(path, EvaluationPath.COLUMNS_CLASSIFICATION_EVALUATION,
                                        t2dv2_table_evaluation.column_classification_evaluation.serialize_evaluation())
                    utl.write_json_file(path, EvaluationPath.SUBJECT_COLUMN_IDENTIFICATION_EVALUATION,
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
                    utl.write_json_file(path, EvaluationPath.CELL_ENTITY_ANNOTATION_EVALUATION,
                                        t2dv2_table_evaluation.cell_entity_annotation_evaluation.serialize_evaluation())
                    print("***************************************************")
                    print("CEA evaluation:")
                    print("precision = " + str(t2dv2_table_evaluation.cell_entity_annotation_evaluation.precision))
                    print("recall = " + str(t2dv2_table_evaluation.cell_entity_annotation_evaluation.recall))
                    print("f1 = " + str(t2dv2_table_evaluation.cell_entity_annotation_evaluation.f1_score))

                    table_evaluations.append(t2dv2_table_evaluation)

    if table_evaluations:
        cc_precision, cc_recall, sci_precision, sci_recall, cea_precision, cea_recall, cta_precision, cta_recall = 0, 0, 0, 0, 0, 0, 0, 0
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
                cta_precision += table_evaluation.column_type_annotation_evaluation.precision
                cta_recall += table_evaluation.column_type_annotation_evaluation.recall
        # Get column classification evaluations for all tables from T2Dv2 dataset
        cc_precision = cc_precision / len(table_evaluations)
        cc_recall = cc_recall / len(table_evaluations)
        cc_f1_score = (2 * cc_precision * cc_recall) / (cc_precision + cc_recall)
        print("***************************************************")
        print("Total evaluation for column classification:")
        print("precision = " + str(cc_precision))
        print("recall = " + str(cc_recall))
        print("f1 = " + str(cc_f1_score))
        # Get subject column identification evaluations for all tables from T2Dv2 dataset
        sci_precision = sci_precision / len(table_evaluations)
        sci_recall = sci_recall / len(table_evaluations)
        sci_f1_score = (2 * sci_precision * sci_recall) / (sci_precision + sci_recall)
        print("***************************************************")
        print("Total evaluation for subject column identification:")
        print("precision = " + str(sci_precision))
        print("recall = " + str(sci_recall))
        print("f1 = " + str(sci_f1_score))
        # Get cell entity annotation evaluations for all tables from T2Dv2 dataset
        cea_precision = cea_precision / len(table_evaluations)
        cea_recall = cea_recall / len(table_evaluations)
        cea_f1_score = (2 * cea_precision * cea_recall) / (cea_precision + cea_recall)
        print("***************************************************")
        print("Total evaluation for cell entity annotation:")
        print("precision = " + str(cea_precision))
        print("recall = " + str(cea_recall))
        print("f1 = " + str(cea_f1_score))
        # Get column type annotation evaluations for all tables from T2Dv2 dataset
        cta_precision = cta_precision / len(table_evaluations)
        cta_recall = cta_recall / len(table_evaluations)
        cta_f1_score = (2 * cta_precision * cta_recall) / (cta_precision + cta_recall)
        print("***************************************************")
        print("Total evaluation for column type annotation:")
        print("precision = " + str(cta_precision))
        print("recall = " + str(cta_recall))
        print("f1 = " + str(cta_f1_score))
        # Save evaluation results for T2Dv2 dataset to json file
        evaluations = dict()
        evaluations["column classification"] = {"precision": cc_precision, "recall": cc_recall, "f1_score": cc_f1_score}
        evaluations["subject column identification"] = {"precision": sci_precision, "recall": sci_recall, "f1_score": sci_f1_score}
        evaluations["cell entity annotation"] = {"precision": cea_precision, "recall": cea_recall, "f1_score": cea_f1_score}
        evaluations["column type annotation"] = {"precision": cta_precision, "recall": cta_recall, "f1_score": cta_f1_score}
        utl.write_json_file(EvaluationPath.EVALUATION_PATH, EvaluationPath.TOTAL_EVALUATION, evaluations)
        print("***************************************************")
        print("Full time: " + str(datetime.now() - start_full_time))


if __name__ == "__main__":
    evaluate_t2dv2_dataset()
