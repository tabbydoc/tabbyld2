import os
import json
from datetime import datetime

import stanza
from duckling import DucklingWrapper

from experimental_evaluation.evaluation_model import TableEvaluation
from tabbyld2.helpers.file import allowed_file, remove_suffix_in_filename, write_json_file
from tabbyld2.helpers.parser import deserialize_table, save_json_dataset
from tabbyld2.config import ResultPath, EvaluationPath
from tabbyld2.pipeline import pipeline_preprocessing


def evaluate_tough_tables_dataset():
    """
    Get experimental evaluation for tables from Tough_Tables dataset.
    """
    start_full_time = datetime.now()
    table_evaluations = []
    # Save source tables from Tough_Tables dataset in the json format
    save_json_dataset(ResultPath.CSV_FILE_PATH, ResultPath.JSON_FILE_PATH)
    stanza.download("en")  # Init Stanford NER annotator
    named_entity_recognition = stanza.Pipeline(lang="en", processors="tokenize,ner")  # Neural pipeline preparation
    duckling_wrapper = DucklingWrapper()  # Init DucklingWrapper object
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
                    table = pipeline_preprocessing(table, file, named_entity_recognition, duckling_wrapper)  # Preprocessing
                    # Get column classification evaluation
                    tough_tables_evaluation = TableEvaluation(table)
                    tough_tables_evaluation.evaluate_columns_classification(EvaluationPath.TOUGH_TABLES_GT +
                                                                            EvaluationPath.TOUGH_TABLES_CLASS_CHECKED)
                    # Save preprocessing evaluation results to json files
                    path = EvaluationPath.EVALUATION_PATH + remove_suffix_in_filename(file) + "/"
                    write_json_file(path, EvaluationPath.COLUMNS_CLASSIFICATION_EVALUATION,
                                    tough_tables_evaluation.column_classification_evaluation.serialize_evaluation())

                    table_evaluations.append(tough_tables_evaluation)

                    print("***************************************************")
                    print("Column classification evaluation:")
                    print("precision = " + str(tough_tables_evaluation.column_classification_evaluation.precision))
                    print("recall = " + str(tough_tables_evaluation.column_classification_evaluation.recall))
                    print("f1 = " + str(tough_tables_evaluation.column_classification_evaluation.f1_score))

    if table_evaluations:
        cc_precision, cc_recall, all_scores = 0, 0, 0
        for table_evaluation in table_evaluations:
            if table_evaluation.column_classification_evaluation is not None:
                cc_precision += table_evaluation.column_classification_evaluation.precision
                cc_recall += table_evaluation.column_classification_evaluation.recall
                all_scores += 1
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
        print("Full time: " + str(datetime.now() - start_full_time))


if __name__ == "__main__":
    evaluate_tough_tables_dataset()
