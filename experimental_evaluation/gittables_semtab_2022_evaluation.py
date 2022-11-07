import os
import json
from datetime import datetime

from experimental_evaluation.evaluation_model import TableEvaluation
from tabbyld2.helpers.file import allowed_file, remove_suffix_in_filename, write_json_file
from tabbyld2.helpers.parser import save_json_dataset
from tabbyld2.config import ResultPath, EvaluationPath
from tabbyld2.datamodel.tabular_data_model import TableModel
from tabbyld2.pipeline import pipeline_preprocessing


def evaluate_gittables_semtab_2022_dataset():
    """
    Get experimental evaluation for tables from GitTables_SemTab_2022 dataset.
    """
    start_full_time = datetime.now()
    table_evaluations = []
    # Save source tables from GitTables_SemTab_2022 dataset in the json format
    save_json_dataset(ResultPath.CSV_FILE_PATH, ResultPath.JSON_FILE_PATH)
    # Cycle through table files
    for root, dirs, files in os.walk(ResultPath.JSON_FILE_PATH):
        for file in files:
            if allowed_file(file, {"json"}):
                print("File '" + str(file) + "' processing started!")
                try:
                    with open(ResultPath.JSON_FILE_PATH + file, "r", encoding="utf-8") as fp:
                        # Deserialize a source table in the json format (create a table model)
                        table = TableModel.deserialize_source_table(remove_suffix_in_filename(file), json.load(fp))
                except json.decoder.JSONDecodeError:
                    print("Error decoding json table file!")
                if table is not None:
                    table = pipeline_preprocessing(table, file)  # Preprocessing
                    # Get column classification evaluation
                    gittables_semtab_2022_evaluation = TableEvaluation(table)
                    gittables_semtab_2022_evaluation.evaluate_columns_classification(EvaluationPath.GIT_TABLES_SEMTAB_2022_GT +
                                                                                     EvaluationPath.GIT_TABLES_SEMTAB_2022_CLASS_CHECKED)
                    # Save preprocessing evaluation results to json files
                    path = EvaluationPath.EVALUATION_PATH + remove_suffix_in_filename(file) + "/"
                    write_json_file(path, EvaluationPath.COLUMNS_CLASSIFICATION_EVALUATION,
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
