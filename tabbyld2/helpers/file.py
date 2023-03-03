import json
import os
import shutil
from pathlib import Path
from typing import List, Set


def remove_suffix_in_filename(filename: str) -> str:
    """
    Remove a file extension from a file name
    :param filename: a file name
    :return: a file name without extension
    """
    return Path(filename).stem


def allowed_file(filename: str, allowed_extensions: Set[str]) -> bool:
    """
    Check a file extension
    :param filename: a file name
    :param allowed_extensions: a list of valid file extensions
    :return: an allowed file extension flag
    """
    return "." in filename and filename.rsplit(".", 1)[1] in allowed_extensions


def check_path(path: str):
    """
    Check a path exists. If there is no such path, it will be created
    :param path: a path
    """
    if not os.path.exists(path):
        os.makedirs(path)


def remove_file(file_path: str):
    """
    Remove a file
    :param file_path: full path to a file
    """
    if os.path.exists(file_path):
        os.remove(os.path.join(os.path.abspath(file_path)))


def write_json_file(path: str, filename: str, dicts: List[dict]):
    """
    Write a JSON file with serialized data represented as a dict
    :param path: full path to a file
    :param filename: a file name
    :param dicts: a dictionary data
    """
    check_path(path)
    with open(path + filename, "w", encoding="utf-8") as outfile:
        json.dump(dicts, outfile, indent=4, ensure_ascii=False)


def create_table_headings_file(classified_data_file: str, table_headings_file: str):
    """
    Создание json-файла с заголовками столбцов на основе файла с классифицированными столбцами таблицы.
    :param classified_data_file: полный путь до json-файла с классифицированными столбцами таблицы
    :param table_headings_file: полный путь до json-файл с заголовками столбцов
    """
    if not os.path.exists(table_headings_file):
        shutil.copy(classified_data_file, table_headings_file)
        with open(table_headings_file, "r") as outfile:
            json_data = json.load(outfile)
            for key in json_data.keys():
                json_data[key] = None
        with open(table_headings_file, "w") as outfile:
            outfile.write(json.dumps(json_data, indent=4))


def update_table_headings_file(table_headings_file, key, value):
    """
    Запись в json-файл с заголовками столбцов определенного значения по ключу.
    :param table_headings_file: полный путь до json-файл с заголовками столбцов
    :param key: ключ (заголовок столбца)
    :param value: новое значение для заголовка столбца
    """
    if os.path.exists(table_headings_file):
        with open(table_headings_file, "r") as outfile:
            json_data = json.load(outfile)
            json_data[key] = value
        with open(table_headings_file, "w") as outfile:
            outfile.write(json.dumps(json_data, indent=4))


def create_table_cells_file(cleared_data_file, table_cells_file):
    """
    Создание json-файла с заголовками столбцов и сгруппированными значениями ячеек.
    :param cleared_data_file: полный путь до json-файла с представлением очищенной таблицы
    :param table_cells_file: полный путь до json-файл с заголовками столбцов и сгруппированными значениями ячеек
    """
    if os.path.exists(cleared_data_file) and not os.path.exists(table_cells_file):
        with open(cleared_data_file, "r") as outfile:
            cleared_data = json.load(outfile)
            result_list = {key: None for row in cleared_data for key in row.keys()}  # Формирование словаря с ключами
            # Формирование значений для ключений
            for column_name in result_list:
                result_item = {}
                for row in cleared_data:
                    if column_name in row.keys():
                        result_item[row.get(column_name)] = None
                result_list[column_name] = result_item
        # Запись нового json-файла
        with open(table_cells_file, "w") as outfile:
            outfile.write(json.dumps(result_list, indent=4))


def update_table_cells_file(table_cells_file, key, new_cell_value):
    """
    Запись в json-файл с заголовками столбцов и сгруппированными значениями ячеек определенного значения по ключу.
    :param table_cells_file: полный путь до json-файл с заголовками столбцов и сгруппированными значениями ячеек
    :param key: ключ (значение ячейки)
    :param new_cell_value: новое значение для ячейки
    """
    if os.path.exists(table_cells_file):
        with open(table_cells_file, "r") as outfile:
            json_data = json.load(outfile)
            for item in json_data.values():
                item[key] = new_cell_value
        with open(table_cells_file, "w") as outfile:
            outfile.write(json.dumps(json_data, indent=4))
