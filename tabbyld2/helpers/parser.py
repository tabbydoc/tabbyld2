import os
import pandas as pd
from tabbyld2.config import ResultPath, EvaluationPath
from tabbyld2.helpers.file import allowed_file, check_directory
from tabbyld2.datamodel.tabular_data_model import TableModel, TableColumnModel, ColumnCellModel


def deserialize_table(file_name: str = None, source_json_data: dict = None) -> TableModel:
    """
    Deserialize a source table in the JSON format and create table model object.
    :param file_name: table file name
    :param source_json_data: tabular data in JSON format
    :return: TableModel object
    """
    dicts = {k: [d[k] for d in source_json_data] for k in source_json_data[0]}
    columns = [TableColumnModel(key, tuple([ColumnCellModel(item) for item in items])) for key, items in dicts.items()]
    return TableModel(file_name, tuple(columns))


def convert_csv_to_json(csv_file_path, csv_file_name, json_file_path):
    """
    Конвертация csv-файла электронной таблицы в формат json.
    :param csv_file_path: путь к csv-файлу электронной таблицы
    :param csv_file_name: название csv-файла
    :param json_file_path: путь к json-файлу представления электронной таблицы
    :return: json_file_name - название json-файла
    """
    json_file_name = None
    check_file = os.path.exists(csv_file_path + csv_file_name)
    if check_file:
        try:
            # Получение данных из csv-файла электронной таблицы
            file_data = pd.DataFrame(pd.read_csv(csv_file_path + csv_file_name, sep=",", header=0, index_col=False))
            # Проверка существования каталога для сохранения результатов
            check_directory(json_file_path)
            # Формирование названия для json-файла
            json_file_name = os.path.splitext(csv_file_name)[0] + ".json"
            # Сохранение json-файла с результатами конвертации электронной таблицы
            file_data.to_json(json_file_path + json_file_name, orient="records", date_format="epoch",
                              double_precision=10, force_ascii=True, date_unit="ms", default_handler=None, indent=4)
            print("Source table file in JSON format has been successfully received!")
        except pd.errors.EmptyDataError:
            print("Source table file is empty!")
    else:
        print("Source table file does not exist!")

    return json_file_name


def convert_json_to_csv(json_file_path, json_file_name, csv_file_path):
    """
    Конвертация json-файла представления электронной таблицы в формат csv.
    :param json_file_path: путь к json-файлу представления электронной таблицы
    :param json_file_name: название json-файла
    :param csv_file_path: путь к csv-файлу электронной таблицы
    :return: csv_file_name - название csv-файла электронной таблицы
    """
    csv_file_name = None
    check_file = os.path.exists(json_file_path + json_file_name)
    if check_file:
        try:
            # Получение данных из json-файла представления электронной таблицы
            file_data = pd.DataFrame(pd.read_json(json_file_path + json_file_name))
            # Проверка существования каталога для сохранения результатов
            check_directory(csv_file_path)
            # Формирование названия для csv-файла
            csv_file_name = os.path.splitext(json_file_name)[0] + ".csv"
            # Сохранение csv-файла электронной таблицы
            file_data.to_csv(csv_file_path + csv_file_name, index=False)
            print("Source table file in CSV format has been successfully received!")
        except pd.errors.EmptyDataError:
            print("Source table file is empty!")
    else:
        print("Source table file does not exist!")

    return csv_file_name


def save_json_dataset(csv_file_path, json_file_path):
    """
    Сохранение набора электронных таблиц в формате json.
    :param csv_file_path: путь к csv-файлам электронных таблиц
    :param json_file_path: путь к json-файлам представления электронных таблиц
    """
    # Обход файлов электронных таблиц в каталоге
    for root, dirs, files in os.walk(csv_file_path):
        for file in files:
            if allowed_file(file, {"csv"}):
                # Конвертация csv-файла электронной таблицы в формат json
                convert_csv_to_json(csv_file_path, file, json_file_path)


def save_csv_dataset(json_file_path, csv_file_path):
    """
    Сохранение набора json-файлов представлений электронных таблиц в формате csv.
    :param json_file_path: путь к json-файлам представления электронных таблиц
    :param csv_file_path: путь к csv-файлам электронных таблиц
    """
    # Обход json-файлов представлений электронных таблиц в каталоге
    for root, dirs, files in os.walk(json_file_path):
        for file in files:
            if allowed_file(file, {"json"}):
                # Конвертация json-файла представления электронной таблицы в формат csv
                convert_json_to_csv(json_file_path, file, csv_file_path)


def convert_t2dv2_tables_to_csv():
    """
    Конвертация json-файлов представления электронных таблиц из набора данных T2Dv2 в формат csv.
    """
    # Cycle through table files
    for root, dirs, files in os.walk(EvaluationPath.T2DV2_JSON):
        for file in files:
            if allowed_file(file, {"json"}):
                print(file)
                # Extract table from source json file
                source_json_data = pd.read_json(EvaluationPath.T2DV2_JSON + file, encoding="unicode_escape")
                table = dict()
                for key, items in source_json_data.items():
                    if key == "relation":
                        index = 0
                        for item in items:
                            if item[0]:
                                table[item[0]] = item[1:]
                            else:
                                table[index] = item[1:]
                            index += 1
                # Form name for new csv file
                csv_file_name = os.path.splitext(file)[0] + ".csv"
                # Save new csv file for tabular data
                data_frame = pd.DataFrame(table)
                data_frame.to_csv(ResultPath.CSV_FILE_PATH + csv_file_name, header=True, index=False)
                print("File '" + str(csv_file_name) + "' is created successfully.")
