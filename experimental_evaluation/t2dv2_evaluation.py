import os
import json
import html
import urllib.parse

import pandas as pd
from pandas import DataFrame
import tabbyld2.parser as pr
import tabbyld2.utility as utl
import tabbyld2.pipeline as pl
from datetime import datetime
from experimental_evaluation.evaluation_model import DatasetEvaluationModel, TableEvaluationModel, \
    AbstractColumnsClassificationEvaluationModel, AbstractSubjectColumnIdentificationEvaluationModel, \
    AbstractCellEntityAnnotationEvaluationModel
from tabbyld2.config import ResultPath, EvaluationPath
from tabbyld2.column_classifier import ColumnType
from tabbyld2.tabular_data_model import TableModel


class T2Dv2ColumnsClassificationEvaluationModel(AbstractColumnsClassificationEvaluationModel, TableEvaluationModel):
    def evaluate_columns_classification(self, checked_data: DataFrame):
        """
        Evaluate columns classification for tables from T2Dv2 dataset.
        :param checked_data: checked tabular data
        """
        # Get total number of columns
        total_columns = len(self.table.columns)
        # Get number of classified columns
        classified_columns = 0
        for column in self.table.columns:
            if column.column_type is not None:
                classified_columns += 1
        # Get number of correctly classified columns
        categorical_column_number = 0
        literal_column_number = 0
        rows = []
        for key, items in checked_data.items():
            if key == 0:
                for i in range(len(items)):
                    if items[i] == self.table.table_name:
                        rows.append(i)
                literal_column_number = total_columns - len(rows)
            if key == 1:
                for i in range(len(items)):
                    for row_index in rows:
                        if i == row_index:
                            for k in range(len(self.table.columns)):
                                if k == int(items[i]):
                                    if self.table.columns[k].column_type == ColumnType.SUBJECT_COLUMN or \
                                            self.table.columns[k].column_type == ColumnType.CATEGORICAL_COLUMN:
                                        categorical_column_number += 1
        correctly_classified_columns = categorical_column_number + literal_column_number
        # Calculate precision
        self._precision = correctly_classified_columns / classified_columns if classified_columns != 0 else 0
        # Calculate recall
        self._recall = correctly_classified_columns / total_columns if total_columns != 0 else 0
        # Calculate F1 score
        self.calculate_f1_score()


class T2Dv2SubjectColumnIdentificationEvaluationModel(AbstractSubjectColumnIdentificationEvaluationModel,
                                                      TableEvaluationModel):
    def evaluate_subject_column_identification(self, checked_data: DataFrame):
        """
        Evaluate subject column identification among categorical columns for tables from T2Dv2 dataset.
        :param checked_data: checked tabular data
        """
        # Define precision
        exist_subject_column = False
        rows = []
        column_indices = dict()
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
        self._precision = 1.0 if exist_subject_column else 0.0
        # Define recall
        exist_subject_column = False
        for column in self.table.columns:
            if column.column_type == ColumnType.SUBJECT_COLUMN:
                exist_subject_column = True
        self._recall = 1.0 if exist_subject_column else 0.0
        # Calculate F1 score
        self.calculate_f1_score()


class T2Dv2CellEntityAnnotationEvaluationModel(AbstractCellEntityAnnotationEvaluationModel, TableEvaluationModel):
    def evaluate_cell_entity_annotation(self):
        """
        Evaluate cell entity annotation (CEA task).
        """
        for instance_root, instance_dirs, instance_files in os.walk(EvaluationPath.T2DV2_INSTANCE):
            for instance_file in instance_files:
                if utl.remove_suffix_in_filename(instance_file) == self.table.table_name:
                    # Get checked tabular data
                    instance_data = pd.DataFrame(pd.read_csv(EvaluationPath.T2DV2_INSTANCE + instance_file, sep=",",
                                                             header=None, index_col=False, encoding="unicode_escape"))
                    # Annotation comparison
                    correctly_annotated_cells = 0
                    annotated_cells = 0
                    cell_number = 0
                    instances = []
                    values = []
                    for key, items in instance_data.items():
                        if key == 0:
                            instances = items
                            cell_number = len(instances)
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
                                                                    column.cells[i].annotation.lower():
                                                                correctly_annotated_cells += 1
                                                            else:
                                                                print("INS: " + urllib.parse.unquote(instances[j]) +
                                                                      " != ANN: " + column.cells[i].annotation)
                                                        else:
                                                            print("INS: " + urllib.parse.unquote(instances[j]) +
                                                                  " != ANN: NULL")
                    # Calculate precision
                    self._precision = correctly_annotated_cells / annotated_cells if annotated_cells != 0 else 0
                    print("***************************************************")
                    print("Correctly annotated cells = " + str(correctly_annotated_cells))
                    print("Annotated cells = " + str(annotated_cells))
                    print("Cell number = " + str(cell_number))
                    # Calculate recall
                    self._recall = correctly_annotated_cells / cell_number if cell_number != 0 else 0
                    # Calculate F1 score
                    self.calculate_f1_score()


def evaluation():
    """
    Get experimental evaluation for tables from T2Dv2 dataset.
    """
    start_full_time = datetime.now()
    cc_evaluations = ()
    sci_evaluations = ()
    cea_evaluations = ()
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
                    # Get class checked data for tables from T2Dv2 dataset
                    class_checked_data = pd.DataFrame(pd.read_csv(EvaluationPath.T2DV2 +
                                                                  EvaluationPath.T2DV2_CLASS_CHECKED, sep=",",
                                                                  header=None, index_col=False))
                    # Evaluate columns classification
                    cc_evaluation_model = T2Dv2ColumnsClassificationEvaluationModel(table)
                    cc_evaluation_model.evaluate_columns_classification(class_checked_data)
                    cc_evaluations += (cc_evaluation_model,)
                    # Evaluate subject column identification
                    sci_evaluation_model = T2Dv2SubjectColumnIdentificationEvaluationModel(table)
                    sci_evaluation_model.evaluate_subject_column_identification(class_checked_data)
                    sci_evaluations += (sci_evaluation_model,)
                    # Save evaluation results to json files
                    path = EvaluationPath.EVALUATION_PATH + utl.remove_suffix_in_filename(file) + "/"
                    utl.write_json_file(path, EvaluationPath.COLUMNS_CLASSIFICATION_EVALUATION,
                                        cc_evaluation_model.serialize_evaluation())
                    utl.write_json_file(path, EvaluationPath.SUBJECT_COLUMN_IDENTIFICATION_EVALUATION,
                                        sci_evaluation_model.serialize_evaluation())
                    print("***************************************************")
                    print("Columns classification evaluation:")
                    print(cc_evaluation_model.precision)
                    print(cc_evaluation_model.recall)
                    print(cc_evaluation_model.f1_score)
                    print("***************************************************")
                    print("Subject column identification evaluation:")
                    print(sci_evaluation_model.precision)
                    print(sci_evaluation_model.recall)
                    print(sci_evaluation_model.f1_score)

                    # Solve CEA task
                    table = pl.pipeline_cell_entity_annotation(table, file)
                    # Evaluate CEA task
                    cea_evaluation_model = T2Dv2CellEntityAnnotationEvaluationModel(table)
                    cea_evaluation_model.evaluate_cell_entity_annotation()
                    cea_evaluations += (cea_evaluation_model,)
                    # Save evaluation results to json files
                    utl.write_json_file(path, EvaluationPath.CELL_ENTITY_ANNOTATION_EVALUATION,
                                        cea_evaluation_model.serialize_evaluation())
                    print("***************************************************")
                    print("CEA evaluation:")
                    print(cea_evaluation_model.precision)
                    print(cea_evaluation_model.recall)
                    print(cea_evaluation_model.f1_score)

    print("***************************************************")
    print("Total evaluation for columns classification:")
    # Evaluate columns classification for all tables from T2Dv2 dataset
    cc_evaluation_dataset = DatasetEvaluationModel(cc_evaluations)
    cc_evaluation_dataset.calculate_precision()
    cc_evaluation_dataset.calculate_recall()
    cc_evaluation_dataset.calculate_f1_score()
    print(cc_evaluation_dataset.precision)
    print(cc_evaluation_dataset.recall)
    print(cc_evaluation_dataset.f1_score)
    print("***************************************************")
    print("Total evaluation for subject column identification:")
    # Evaluate subject column identification for all tables from T2Dv2 dataset
    sci_evaluation_dataset = DatasetEvaluationModel(sci_evaluations)
    sci_evaluation_dataset.calculate_precision()
    sci_evaluation_dataset.calculate_recall()
    sci_evaluation_dataset.calculate_f1_score()
    print(sci_evaluation_dataset.precision)
    print(sci_evaluation_dataset.recall)
    print(sci_evaluation_dataset.f1_score)
    print("***************************************************")
    print("Total evaluation for cell entity annotation:")
    # Evaluate cell entity annotation for all tables from T2Dv2 dataset
    cea_evaluation_dataset = DatasetEvaluationModel(cea_evaluations)
    cea_evaluation_dataset.calculate_precision()
    cea_evaluation_dataset.calculate_recall()
    cea_evaluation_dataset.calculate_f1_score()
    print(cea_evaluation_dataset.precision)
    print(cea_evaluation_dataset.recall)
    print(cea_evaluation_dataset.f1_score)
    # Save evaluation result for dataset to json file
    total_evaluation = dict()
    total_evaluation["columns classification"] = cc_evaluation_dataset.serialize_evaluation()
    total_evaluation["subject column identification"] = sci_evaluation_dataset.serialize_evaluation()
    total_evaluation["cell entity annotation"] = cea_evaluation_dataset.serialize_evaluation()
    utl.write_json_file(EvaluationPath.EVALUATION_PATH, EvaluationPath.TOTAL_EVALUATION, total_evaluation)
    print("***************************************************")
    print("Full time: " + str(datetime.now() - start_full_time))


evaluation()
