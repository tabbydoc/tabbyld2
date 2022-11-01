import os
import json
import pandas as pd
import tabbyld2.parser as pr
import tabbyld2.utility as utl
import tabbyld2.pipeline as pl
from datetime import datetime
from experimental_evaluation.evaluation_model import TableEvaluation, BaseEvaluation
from tabbyld2.config import ResultPath, EvaluationPath
from tabbyld2.column_classifier import ColumnType
from tabbyld2.tabular_data_model import TableModel


class GitTablesSemTab2022Evaluation(TableEvaluation):
    """
    Experimental evaluations for table from GitTables_SemTab_2022 dataset.
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
        # Get class checked data for tables from GitTables_SemTab_2022 dataset
        checked_data = pd.DataFrame(pd.read_csv(EvaluationPath.GIT_TABLES_SEMTAB_2022_GT +
                                                EvaluationPath.GIT_TABLES_SEMTAB_2022_CLASS_CHECKED, sep=",", header=None, index_col=False))
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
                                    if self.table.columns[k].column_type == ColumnType.SUBJECT_COLUMN or \
                                            self.table.columns[k].column_type == ColumnType.CATEGORICAL_COLUMN:
                                        categorical_column_number += 1
        correctly_classified_columns = categorical_column_number + literal_column_number
        # Calculate evaluations
        self._column_classification_evaluation = BaseEvaluation()
        self._column_classification_evaluation._precision = correctly_classified_columns / classified_columns if classified_columns != 0 else 0
        self._column_classification_evaluation._recall = correctly_classified_columns / len(self.table.columns) if len(self.table.columns) != 0 else 0
        self._column_classification_evaluation.calculate_f1_score()


def evaluate_gittables_semtab_2022_dataset():
    """
    Get experimental evaluation for tables from GitTables_SemTab_2022 dataset.
    """
    start_full_time = datetime.now()
    table_evaluations = []
    # Save source tables from GitTables_SemTab_2022 dataset in the json format
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
                    # Get column classification evaluation
                    gittables_semtab_2022_evaluation = GitTablesSemTab2022Evaluation(table)
                    gittables_semtab_2022_evaluation.evaluate_columns_classification()
                    # Save preprocessing evaluation results to json files
                    path = EvaluationPath.EVALUATION_PATH + utl.remove_suffix_in_filename(file) + "/"
                    utl.write_json_file(path, EvaluationPath.COLUMNS_CLASSIFICATION_EVALUATION,
                                        gittables_semtab_2022_evaluation.column_classification_evaluation.serialize_evaluation())

                    table_evaluations.append(gittables_semtab_2022_evaluation)

                    print("***************************************************")
                    print("Column classification evaluation:")
                    print("precision = " + str(gittables_semtab_2022_evaluation.column_classification_evaluation.precision))
                    print("recall = " + str(gittables_semtab_2022_evaluation.column_classification_evaluation.recall))
                    print("f1 = " + str(gittables_semtab_2022_evaluation.column_classification_evaluation.f1_score))

    if table_evaluations:
        cc_precision, cc_recall = 0, 0
        for table_evaluation in table_evaluations:
            if table_evaluation.column_classification_evaluation is not None:
                cc_precision += table_evaluation.column_classification_evaluation.precision
                cc_recall += table_evaluation.column_classification_evaluation.recall
        # Get column classification evaluations for all tables from T2Dv2 dataset
        cc_precision = cc_precision / len(table_evaluations)
        cc_recall = cc_recall / len(table_evaluations)
        cc_f1_score = (2 * cc_precision * cc_recall) / (cc_precision + cc_recall) if cc_precision != 0 and cc_recall != 0 else 0
        print("***************************************************")
        print("Total evaluation for column classification:")
        print("precision = " + str(cc_precision))
        print("recall = " + str(cc_recall))
        print("f1 = " + str(cc_f1_score))
        print("***************************************************")
        print("Full time: " + str(datetime.now() - start_full_time))


if __name__ == "__main__":
    evaluate_gittables_semtab_2022_dataset()
