import os
import pandas as pd
import tabbyld2.utility as ut


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
            ut.check_directory(json_file_path)
            # Формирование названия для json-файла
            json_file_name = os.path.splitext(csv_file_name)[0] + ".json"
            # Сохранение json-файла с результатами конвертации электронной таблицы
            file_data.to_json(json_file_path + json_file_name, orient="records", date_format="epoch",
                              double_precision=10, force_ascii=True, date_unit="ms", default_handler=None, indent=4)
            print("Файл электронной таблицы в формате json успешно получен!")
        except pd.errors.EmptyDataError:
            print("Файл электронной таблицы пуст!")
    else:
        print("Файла электронной таблицы не существует!")

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
            ut.check_directory(csv_file_path)
            # Формирование названия для csv-файла
            csv_file_name = os.path.splitext(json_file_name)[0] + ".csv"
            # Сохранение csv-файла электронной таблицы
            file_data.to_csv(csv_file_path + csv_file_name, index=False)
            print("Файл электронной таблицы в формате csv успешно сохранен!")
        except pd.errors.EmptyDataError:
            print("JSON-файл представления электронной таблицы пуст!")
    else:
        print("JSON-файла представления электронной таблицы не существует!")

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
            if ut.allowed_file(file, {"csv"}):
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
            if ut.allowed_file(file, {"json"}):
                # Конвертация json-файла представления электронной таблицы в формат csv
                convert_json_to_csv(json_file_path, file, csv_file_path)
