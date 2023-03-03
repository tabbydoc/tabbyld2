import os
from typing import Optional

import pandas as pd
from tabbyld2.config import EvaluationPath, ResultPath
from tabbyld2.datamodel.tabular_data_model import ColumnCellModel, TableColumnModel, TableModel
from tabbyld2.helpers.file import allowed_file, check_path


def deserialize_table(filename: str, source_json_data: dict) -> TableModel:
    """
    Deserialize a source table in JSON format and create table model object
    :param filename: a table file name
    :param source_json_data: a tabular data in JSON format
    :return: a TableModel object
    """
    dicts = {k: [d[k] for d in source_json_data] for k in source_json_data[0]}
    columns = [TableColumnModel(key, tuple([ColumnCellModel(item) for item in items])) for key, items in dicts.items()]
    return TableModel(filename, tuple(columns))


def convert_csv_to_json(csv_file_path: str, csv_filename: str, json_file_path: str) -> Optional[str]:
    """
    Convert CSV file with a source table to JSON format
    :param csv_file_path: path to CSV table file
    :param csv_filename: a file name in CSV format
    :param json_file_path: full path to a table file in JSON format
    :return: json_file_name - a file name in JSON format
    """
    if os.path.exists(csv_file_path + csv_filename):
        try:
            file_data = pd.DataFrame(pd.read_csv(csv_file_path + csv_filename, sep=",", header=0, index_col=False))
            check_path(json_file_path)
            json_filename = os.path.splitext(csv_filename)[0] + ".json"
            file_data.to_json(json_file_path + json_filename, orient="records", date_format="epoch", double_precision=10, force_ascii=True,
                              date_unit="ms", default_handler=None, indent=4)
            print("Source table file in JSON format has been successfully received!")
            return json_filename
        except pd.errors.EmptyDataError:
            print("Source table file is empty!")
    else:
        print("Source table file does not exist!")
    return None


def convert_json_to_csv(json_file_path: str, json_filename: str, csv_file_path: str) -> Optional[str]:
    """
    Convert table file in JSON format to a file in CSV format
    :param json_file_path: full path to a table file in JSON format
    :param json_filename: a file name in JSON format
    :param csv_file_path: full path to a table file in CSV format
    :return: csv_filename - a file name in CSV format
    """
    if os.path.exists(json_file_path + json_filename):
        try:
            file_data = pd.DataFrame(pd.read_json(json_file_path + json_filename))
            check_path(csv_file_path)
            csv_filename = os.path.splitext(json_filename)[0] + ".csv"
            file_data.to_csv(csv_file_path + csv_filename, index=False)
            print("Source table file in CSV format has been successfully received!")
            return csv_filename
        except pd.errors.EmptyDataError:
            print("Source table file is empty!")
    else:
        print("Source table file does not exist!")
    return None


def save_json_dataset(csv_file_path: str, json_file_path: str):
    """
    Save a set of tables in JSON format
    :param csv_file_path: full path to table files in CSV format
    :param json_file_path: full path to table files in JSON format
    """
    for _, _, files in os.walk(csv_file_path):
        for file in files:
            if allowed_file(file, {"csv"}):
                convert_csv_to_json(csv_file_path, file, json_file_path)


def save_csv_dataset(json_file_path: str, csv_file_path: str):
    """
    Save a set of JSON table views in CSV format
    :param json_file_path: full path to table files in JSON format
    :param csv_file_path: full path to table files in CSV format
    """
    for _, _, files in os.walk(json_file_path):
        for file in files:
            if allowed_file(file, {"json"}):
                convert_json_to_csv(json_file_path, file, csv_file_path)


def convert_t2dv2_tables_to_csv():
    """
    Convert JSON files of tables from T2Dv2 dataset to CSV format
    """
    for _, _, files in os.walk(EvaluationPath.T2DV2_JSON):
        for file in files:
            if allowed_file(file, {"json"}):
                print(file)
                source_json_data = pd.read_json(EvaluationPath.T2DV2_JSON + file, encoding="unicode_escape")
                table, index = {}, 0
                if "relation" in source_json_data.keys():
                    for item in source_json_data.get("relation"):
                        if item[0]:
                            table[item[0]] = item[1:]
                        else:
                            table[index] = item[1:]
                        index += 1
                csv_filename = os.path.splitext(file)[0] + ".csv"  # Form a CSV file name
                data_frame = pd.DataFrame(table)  # Save new CSV file or tabular data
                data_frame.to_csv(ResultPath.CSV_FILE_PATH + csv_filename, header=True, index=False)
                print("File '" + str(csv_filename) + "' is created successfully.")
