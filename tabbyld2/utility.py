import os
import json
import shutil
from pathlib import Path
from typing import Optional, Dict
from tabbyld2.config import ResultPath


def is_float(string):
    """
    Определение является ли строка числовым значением с плавающей точкой.
    :param string: исходная строка
    :return: True - если строка является числом с плавающей точкой, False - в противном случае
    """
    try:
        float(string.replace(",", "."))
        return True
    except ValueError:
        return False


def is_int(string):
    """
    Определение является ли строка целым числовым значением.
    :param string: исходная строка
    :return: True - если строка является целым числом, False - в противном случае
    """
    try:
        int(string)
        return True
    except ValueError:
        return False


def is_number(string):
    """
    Определение является ли строка каким-либо числовым занчением.
    :param string: исходная строка
    :return: True - если строка является числом, False - в противном случае
    """
    if is_int(string):
        return True
    else:
        if is_float(string):
            return True
        else:
            return False


def merge_dicts(dict1, dict2):
    """
    Объединение содержимого двух словарей.
    :param dict1: первый словарь
    :param dict2: второй словарь
    :return: результирующий (третий) словарь
    """
    dict3 = {**dict1, **dict2}
    for key, value in dict3.items():
        if key in dict1 and key in dict2:
            if isinstance(dict3[key], list):
                dict3[key].append(dict1[key])
    return dict3


def remove_suffix_in_filename(filename):
    """
    Удаление расширения файла из имени файла.
    :param filename: полное имя файла
    :return: имя файла без расширения
    """
    path = Path(filename)

    return path.stem


def allowed_file(filename, allowed_extensions):
    """
    Проверка разрешения файла.
    :param filename: полное имя файла
    :param allowed_extensions: список допустимых расширений файла
    :return: является ли файл допустимого разрешения
    """
    return "." in filename and filename.rsplit(".", 1)[1] in allowed_extensions


def check_directory(directory):
    """
    Проверка существования пути (каталога). Если такого пути нет, то он будет создан.
    :param directory: путь (каталог)
    """
    if os.path.exists(directory) is False:
        os.makedirs(directory)


def remove_file(file):
    """
    Удаление файла.
    :param file: полный путь до файла
    """
    if os.path.exists(file):
        path = os.path.join(os.path.abspath(file))
        os.remove(path)


def write_json_file(file: str = None, path: str = None, dicts: Optional[Dict] = None):
    check_directory(ResultPath.PROVENANCE_PATH + remove_suffix_in_filename(file) + path)
    with open(ResultPath.PROVENANCE_PATH + remove_suffix_in_filename(file) + path + file, "w") as outfile:
        json.dump(dicts, outfile, indent=4)


def create_table_headings_file(classified_data_file, table_headings_file):
    """
    Создание json-файла с заголовками столбцов на основе файла с классифицированными столбцами таблицы.
    :param classified_data_file: полный путь до json-файла с классифицированными столбцами таблицы
    :param table_headings_file: полный путь до json-файл с заголовками столбцов
    """
    if os.path.exists(table_headings_file) is False:
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
            # Формирование словаря с ключами
            result_list = dict()
            for row in cleared_data:
                for key, value in row.items():
                    result_list[key] = None
            # Формирование значений для ключений
            for column_name in result_list:
                result_item = dict()
                for row in cleared_data:
                    for key, value in row.items():
                        if column_name == key:
                            result_item[value] = None
                result_list[column_name] = result_item
        # Запись нового json-файла
        with open(table_cells_file, "w") as outfile:
            outfile.write(json.dumps(result_list, indent=4))


def update_table_cells_file(table_cells_file, key, value):
    """
    Запись в json-файл с заголовками столбцов и сгруппированными значениями ячеек определенного значения по ключу.
    :param table_cells_file: полный путь до json-файл с заголовками столбцов и сгруппированными значениями ячеек
    :param key: ключ (значение ячейки)
    :param value: новое значение для ячейки
    """
    if os.path.exists(table_cells_file):
        with open(table_cells_file, "r") as outfile:
            json_data = json.load(outfile)
            for column_name, item in json_data.items():
                for cell_value, candidate_entities in item.items():
                    if cell_value == key:
                        item[cell_value] = value
        with open(table_cells_file, "w") as outfile:
            outfile.write(json.dumps(json_data, indent=4))
