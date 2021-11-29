import os
import json
import tabbyld2.parser as pr
import tabbyld2.utility as utl
import tabbyld2.cleaner as cln
import tabbyld2.annotator as ant
import tabbyld2.column_classifier as cc
import tabbyld2.candidate_generation as cg
from flask import Flask, jsonify, abort, make_response, request
from werkzeug.utils import secure_filename


CSV_FILE_PATH = "C:/Users/79501/datasets/test/"
JSON_FILE_PATH = "C:/Users/79501/datasets/test/json/"
CLEARED_DATA_PATH = "C:/Users/79501/datasets/test/provenance/cleared_data/"
RECOGNIZED_DATA_PATH = "C:/Users/79501/datasets/test/provenance/recognized_data/"
CLASSIFIED_DATA_PATH = "C:/Users/79501/datasets/test/provenance/classified_data/"
CANDIDATE_ENTITIES_PATH = "C:/Users/79501/datasets/test/provenance/candidate_entities/"
CANDIDATE_CLASSES_PATH = "C:/Users/79501/datasets/test/provenance/candidate_classes/"
CANDIDATE_PROPERTIES_PATH = "C:/Users/79501/datasets/test/provenance/candidate_properties/"
ANNOTATED_CELL_DATA_PATH = "C:/Users/79501/datasets/test/provenance/annotated_cell_data/"
ANNOTATED_COLUMN_DATA_PATH = "C:/Users/79501/datasets/test/provenance/annotated_column_data/"
ANNOTATED_PROPERTY_DATA_PATH = "C:/Users/79501/datasets/test/provenance/annotated_property_data/"


app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.route("/tabbyld2/upload-csv-file", methods=["POST"])
def upload_csv_file():
    """
    Загрузка csv-файла исходной электронной таблицы, ее конвертация в формат json и очистка данных.
    :return: очищенная таблица представленная в формате json
    """
    if not request.files or "csv_file" not in request.files:
        abort(400)

    csv_file = request.files["csv_file"]
    # Проверка существования csv-файла и его расширения
    if csv_file and utl.allowed_file(csv_file.filename, {"csv"}):
        csv_filename = secure_filename(csv_file.filename)
        utl.check_directory(CSV_FILE_PATH)  # Проверка существования каталога для сохранения загруженного csv-файла
        csv_file.save(os.path.join(CSV_FILE_PATH, csv_filename))  # Сохранение csv-файла в каталог
        # Конвертация csv-файла электронной таблицы в формат json
        json_filename = pr.convert_csv_to_json(CSV_FILE_PATH, csv_filename, JSON_FILE_PATH)
        # Если есть результат конвертации и расширение файла json
        if json_filename is not None and utl.allowed_file(json_filename, {"json"}):
            cleared_data = cln.clean(JSON_FILE_PATH + json_filename)  # Очистка данных
            if cleared_data:
                # Проверка существования каталога для сохранения результатов очистки данных
                utl.check_directory(CLEARED_DATA_PATH)
                # Запись json-файлов c очищенными табличными данными
                with open(CLEARED_DATA_PATH + json_filename, "w") as outfile:
                    json.dump(cleared_data, outfile, indent=4)

                return jsonify(cleared_data), 200

    return jsonify({"error": "STL could not process data."}), 400


@app.route("/tabbyld2/upload-json-file", methods=["POST"])
def upload_json_file():
    """
    Загрузка json-файла представления электронной таблицы и очистка данных.
    :return: очищенная таблица представленная в формате json
    """
    if not request.files or "json_file" not in request.files:
        abort(400)

    json_file = request.files["json_file"]
    # Проверка существования json-файла и его расширения
    if json_file and utl.allowed_file(json_file.filename, {"json"}):
        json_filename = secure_filename(json_file.filename)
        utl.check_directory(JSON_FILE_PATH)  # Проверка существования каталога для сохранения загруженного json-файла
        json_file.save(os.path.join(JSON_FILE_PATH, json_filename))  # Сохранение json-файла в каталог
        cleared_data = cln.clean(JSON_FILE_PATH + json_filename)  # Очистка данных
        if cleared_data:
            # Проверка существования каталога для сохранения результатов очистки данных
            utl.check_directory(CLEARED_DATA_PATH)
            # Запись json-файлов c очищенными табличными данными
            with open(CLEARED_DATA_PATH + json_filename, "w") as outfile:
                json.dump(cleared_data, outfile, indent=4)

            return jsonify(cleared_data), 200

    return jsonify({"error": "STL could not process data."}), 400


@app.route("/tabbyld2/classify-column", methods=["POST"])
def classify_column():
    """
    Классификация столбцов таблицы по типам и определение сущностного (тематического) столбца.
    Ожидаются данные в json:
        request.json["column_ordinal"] - порядковый номер столбца в таблице
        request.json["cleared_data"] - очищенная таблица
        request.json["file_name"] - название файла исходной таблицы без расширения
    :return: словарь с типами столбцов в формате json
    """
    if not request.json or "cleared_data" not in request.json:
        abort(400)

    # Распознавание именованных сущностей в исходном словаре (таблице)
    recognized_data = cc.recognize_named_entities(request.json["cleared_data"])
    if recognized_data and "file_name" in request.json:
        # Проверка существования каталога для сохранения результатов распознавания именованных сущностей
        utl.check_directory(RECOGNIZED_DATA_PATH)
        # Запись json-файлов c результатами распознавания именованных сущностей
        with open(RECOGNIZED_DATA_PATH + request.json["file_name"] + ".json", "w") as outfile:
            json.dump(recognized_data, outfile, indent=4)

    # Классификация столбцов в исходном словаре (таблице) на основе распознанных именованных сущностей
    classified_data = cc.classify_recognized_named_entities(recognized_data)
    classified_data = cc.classify_columns(classified_data)
    # Определение сущностного (тематического) столбца
    classified_data = cc.define_subject_column(
        request.json["cleared_data"],
        classified_data,
        None if request.json["column_ordinal"] is "" else int(request.json["column_ordinal"])
    )
    if classified_data and "file_name" in request.json:
        # Проверка существования каталога для сохранения результатов классификации столбцов
        utl.check_directory(CLASSIFIED_DATA_PATH)
        # Запись json-файлов c результатами классификации столбцов
        with open(CLASSIFIED_DATA_PATH + request.json["file_name"] + ".json", "w") as outfile:
            json.dump(classified_data, outfile, indent=4)

    # Удаление предыдущего файла с результатами поиска сущностей кандидатов
    utl.remove_file(CANDIDATE_ENTITIES_PATH + request.json["file_name"] + ".json")
    # Удаление предыдущего файла с результатами аннотирования значений ячеек
    utl.remove_file(ANNOTATED_CELL_DATA_PATH + request.json["file_name"] + ".json")
    # Удаление предыдущего файла с результатами поиска классов кандидатов
    utl.remove_file(CANDIDATE_CLASSES_PATH + request.json["file_name"] + ".json")
    # Удаление предыдущего файла с результатами аннотирования столбцов
    utl.remove_file(ANNOTATED_COLUMN_DATA_PATH + request.json["file_name"] + ".json")
    # Удаление предыдущего файла с результатами поиска свойств кандидатов
    utl.remove_file(CANDIDATE_PROPERTIES_PATH + request.json["file_name"] + ".json")
    # Удаление предыдущего файла с результатами аннотирования отношений между парами столбцов
    utl.remove_file(ANNOTATED_PROPERTY_DATA_PATH + request.json["file_name"] + ".json")

    return jsonify({"recognized_data": recognized_data, "classified_data": classified_data}), 200


# @app.route("/tabbyld2/get-candidate-entities", methods=["POST"])
# def get_candidate_entities():
#     """
#     Получение сущностей кандадатов на основе текстового упоминания сущности в ячейке столбца.
#     Ожидаются данные в json:
#         request.json["cell_value"] - значение ячейки (текстовое упоминание сущности)
#         request.json["file_name"] - название файла исходной таблицы без расширения
#     :return: словарь с набором сущностей кандадатов для значения ячейки
#     """
#     if not request.json or "cell_value" not in request.json:
#         abort(400)
#
#     # Генерация сущностей кандидатов
#     candidate_entities = cg.generate_candidate_entities(request.json["cell_value"])
#     if candidate_entities and "file_name" in request.json:
#         # Проверка существования каталога для сохранения результатов поиска сущностей кандидатов
#         utl.check_directory(CANDIDATE_ENTITIES_PATH)
#         # Файл с очищенной таблицей в формате json
#         cleared_data_file = CLEARED_DATA_PATH + request.json["file_name"] + ".json"
#         # Файл с результатами поиска сущностей кандидатов
#         file_with_candidate_entities = CANDIDATE_ENTITIES_PATH + request.json["file_name"] + ".json"
#         # Создание файла с результатами поиска сущностей кандидатов на основе json-файла очищенной таблицы
#         utl.create_table_cells_file(cleared_data_file, file_with_candidate_entities)
#         # Запись в json-файл результата поиска сущностей кандидатов для определенного текстового упоминания сущности
#         utl.update_table_cells_file(file_with_candidate_entities, request.json["cell_value"],
#                                     candidate_entities[request.json["cell_value"]])
#
#     return jsonify(candidate_entities), 200


# @app.route("/tabbyld2/get-reference-entity", methods=["POST"])
# def get_reference_entity():
#     """
#     Получение наиболее подходящей (референтной) сущности из набора кандадатов для аннотирования значения ячейки.
#     Ожидаются данные в json:
#         request.json["cell_value"] - название заголовка столбца (текстовое упоминание класса)
#         request.json["candidate_entities"] - набор классов кандидатов
#         request.json["entity_name"] - название класса
#         request.json["file_name"] - название файла исходной таблицы без расширения
#     :return: словарь с референтной сущностью кандадатом для аннотирования значения ячейки
#     """
#     if not request.json or "cell_value" not in request.json or "candidate_entities" not in request.json or \
#             "entity_name" not in request.json:
#         abort(400)
#
#     # Связывание KG-сущности с ячейкой
#     reference_entity = ant.link_entity_to_cell(request.json["cell_value"], request.json["candidate_entities"],
#                                                request.json["entity_name"])
#     if reference_entity and "file_name" in request.json:
#         # Проверка существования каталога для сохранения результатов аннотирования значений ячеек
#         utl.check_directory(ANNOTATED_CELL_DATA_PATH)
#         # Файл с очищенной таблицей в формате json
#         cleared_data_file = CLEARED_DATA_PATH + request.json["file_name"] + ".json"
#         # Файл с результатами аннотирования заголовков столбцов
#         annotated_cell_data_file = ANNOTATED_CELL_DATA_PATH + request.json["file_name"] + ".json"
#         # Создание файла с результатами аннотирования значения ячейки на основе json-файла очищенной таблицы
#         utl.create_table_cells_file(cleared_data_file, annotated_cell_data_file)
#         # Запись в json-файл результата аннотирования значения ячейки
#         utl.update_table_cells_file(annotated_cell_data_file, request.json["cell_value"],
#                                     reference_entity[request.json["cell_value"]])
#
#     return jsonify(reference_entity), 200


# @app.route("/tabbyld2/get-candidate-classes", methods=["POST"])
# def get_candidate_classes():
#     """
#     Получение классов кандадатов на основе текстового упоминания класса в заголовке столбца.
#     Ожидаются данные в json:
#         request.json["column_name"] - название заголовка столбца (текстовое упоминание класса)
#         request.json["file_name"] - название файла исходной таблицы без расширения
#     :return: словарь с набором классов кандадатов для заголовка столбца
#     """
#     if not request.json or "column_name" not in request.json:
#         abort(400)
#
#     # Генерация классов кандидатов
#     candidate_classes = cg.generate_candidate_classes(request.json["column_name"])
#     if candidate_classes and "file_name" in request.json:
#         # Проверка существования каталога для сохранения результатов поиска классов кандидатов
#         utl.check_directory(CANDIDATE_CLASSES_PATH)
#         # Файл с результатами классификации столбцов
#         classified_data_file = CLASSIFIED_DATA_PATH + request.json["file_name"] + ".json"
#         # Файл с результатами поиска классов кандидатов
#         file_with_candidate_classes = CANDIDATE_CLASSES_PATH + request.json["file_name"] + ".json"
#         # Если файл с результатами классификации столбцов существует
#         if os.path.exists(classified_data_file):
#             # Создание основы файла с заголовками таблицы
#             utl.create_table_headings_file(classified_data_file, file_with_candidate_classes)
#             # Запись в json-файл результата поиска классов кандидатов для определенного текстового упоминания класса
#             utl.update_table_headings_file(file_with_candidate_classes, request.json["column_name"],
#                                            candidate_classes[request.json["column_name"]])
#
#     return jsonify(candidate_classes), 200


# @app.route("/tabbyld2/get-reference-class", methods=["POST"])
# def get_reference_class():
#     """
#     Получение наиболее подходящего (референтного) класса из набора кандадатов для
#     аннотирования сущностного или категориального столбца.
#     Ожидаются данные в json:
#         request.json["column_name"] - название заголовка столбца (текстовое упоминание класса)
#         request.json["candidate_classes"] - набор классов кандидатов
#         request.json["class_name"] - название класса
#         request.json["file_name"] - название файла исходной таблицы без расширения
#     :return: словарь с референтным классом кандадатом для аннотирования заголовка столбца
#     """
#     if not request.json or "column_name" not in request.json or "candidate_classes" not in request.json:
#         abort(400)
#
#     # Связывание KG-класса со столбцом
#     reference_class = ant.link_class_to_column(request.json["column_name"], request.json["candidate_classes"],
#                                                request.json["class_name"])
#     if reference_class and "file_name" in request.json:
#         # Проверка существования каталога для сохранения результатов аннотирования заголовков столбцов
#         utl.check_directory(ANNOTATED_COLUMN_DATA_PATH)
#         # Файл с результатами классификации столбцов
#         classified_data_file = CLASSIFIED_DATA_PATH + request.json["file_name"] + ".json"
#         # Файл с результатами аннотирования заголовков столбцов
#         annotated_heading_data_file = ANNOTATED_COLUMN_DATA_PATH + request.json["file_name"] + ".json"
#         # Если файл с результатами классификации столбцов существует
#         if os.path.exists(classified_data_file):
#             # Создание основы файла с заголовками таблицы
#             utl.create_table_headings_file(classified_data_file, annotated_heading_data_file)
#             # Запись в json-файл результата аннотирования заголовка столбца
#             utl.update_table_headings_file(annotated_heading_data_file, request.json["column_name"],
#                                            reference_class[request.json["column_name"]])
#
#     return jsonify(reference_class), 200


# @app.route("/tabbyld2/get-reference-datatype", methods=["POST"])
# def get_reference_datatype():
#     """
#     Получение наиболее подходящих (референтных) типов данных для аннотирования литеральных столбцов.
#     :return: словарь содержащий аннотированные литеральные столбцы
#     """
#     if not request.json or "recognized_data" not in request.json:
#         abort(400)
#
#     # Связывание KG-типов данных с литеральными столбцами
#     reference_datatype = ant.link_datatype_to_column(request.json["recognized_data"])
#     if reference_datatype and "file_name" in request.json:
#         # Проверка существования каталога для сохранения результатов аннотирования заголовков столбцов
#         utl.check_directory(ANNOTATED_COLUMN_DATA_PATH)
#         # Файл с результатами аннотирования заголовков столбцов
#         annotated_heading_data_file = ANNOTATED_COLUMN_DATA_PATH + request.json["file_name"] + ".json"
#         # Если файл с результатами аннотирования заголовков столбцов существует
#         if not os.path.exists(annotated_heading_data_file):
#             # Файл с результатами классификации столбцов
#             classified_data_file = CLASSIFIED_DATA_PATH + request.json["file_name"] + ".json"
#             # Если файл с результатами классификации столбцов существует
#             if os.path.exists(classified_data_file):
#                 # Создание основы файла с заголовками таблицы
#                 utl.create_table_headings_file(classified_data_file, annotated_heading_data_file)
#         # Запись в json-файл результата аннотирования заголовка столбца
#         if isinstance(reference_datatype, dict):
#             for key, value in reference_datatype.items():
#                 utl.update_table_headings_file(annotated_heading_data_file, key, value)
#
#     return jsonify(reference_datatype), 200


# @app.route("/tabbyld2/get-candidate-properties", methods=["POST"])
# def get_candidate_properties():
#     """
#     Получение свойств кандадатов на основе текстового упоминания класса в заголовке столбца.
#     Ожидаются данные в json:
#         request.json["column_name"] - название заголовка столбца (текстовое упоминание класса)
#         request.json["file_name"] - название файла исходной таблицы без расширения
#     :return: словарь с набором свойств кандадатов
#     """
#     if not request.json or "column_name" not in request.json:
#         abort(400)
#
#     # Генерация свойств кандидатов
#     candidate_properties = cg.generate_candidate_properties(request.json["column_name"])
#     if candidate_properties and "file_name" in request.json:
#         # Проверка существования каталога для сохранения результатов поиска свойств кандидатов
#         utl.check_directory(CANDIDATE_PROPERTIES_PATH)
#         # Файл с результатами классификации столбцов
#         classified_data_file = CLASSIFIED_DATA_PATH + request.json["file_name"] + ".json"
#         # Файл с результатами поиска свойств кандидатов
#         file_with_candidate_properties = CANDIDATE_PROPERTIES_PATH + request.json["file_name"] + ".json"
#         # Если файл с результатами классификации столбцов существует
#         if os.path.exists(classified_data_file):
#             # Создание основы файла с заголовками таблицы
#             utl.create_table_headings_file(classified_data_file, file_with_candidate_properties)
#             # Запись в json-файл результата поиска свойств кандидатов для определенного текстового упоминания класса
#             utl.update_table_headings_file(file_with_candidate_properties, request.json["column_name"],
#                                            candidate_properties[request.json["column_name"]])
#
#     return jsonify(candidate_properties), 200


# @app.route("/tabbyld2/get-reference-property", methods=["POST"])
# def get_reference_property():
#     """
#     Получение наиболее подходящего (референтного) свойства из набора кандадатов для
#     аннотирования отношения между сущностным (тематическим) столбцом и другим столбцом.
#     Ожидаются данные в json:
#         request.json["column_name"] - название заголовка столбца (текстовое упоминание класса)
#         request.json["candidate_properties"] - набор свойств кандидатов
#         request.json["property_name"] - название своства
#         request.json["file_name"] - название файла исходной таблицы без расширения
#     :return: словарь с референтным свойством кандадатом для аннотирования отношения между парой столбцов
#     """
#     if not request.json or "column_name" not in request.json or "candidate_properties" not in request.json:
#         abort(400)
#
#     # Связывание KG-свойства с парой столбцов
#     reference_property = ant.link_property_to_column_pair(request.json["column_name"],
#                                                           request.json["candidate_properties"],
#                                                           request.json["property_name"])
#     if reference_property and "file_name" in request.json:
#         # Проверка существования каталога для сохранения результатов аннотирования отношения между парой столбцов
#         utl.check_directory(ANNOTATED_PROPERTY_DATA_PATH)
#         # Файл с результатами классификации столбцов
#         classified_data_file = CLASSIFIED_DATA_PATH + request.json["file_name"] + ".json"
#         # Файл с результатами аннотирования отношений между парами столбцов
#         annotated_relation_data_file = ANNOTATED_PROPERTY_DATA_PATH + request.json["file_name"] + ".json"
#         # Если файл с результатами классификации столбцов существует
#         if os.path.exists(classified_data_file):
#             # Создание основы файла с заголовками таблицы
#             utl.create_table_headings_file(classified_data_file, annotated_relation_data_file)
#             # Запись в json-файл результата аннотирования отношения между парой столбцов
#             utl.update_table_headings_file(annotated_relation_data_file, request.json["column_name"],
#                                            reference_property[request.json["column_name"]])
#
#     return jsonify(reference_property), 200


@app.errorhandler(404)
def not_found(error):
    """
    Обработка некорректных запросов.
    :param error: код ошибки
    :return: ошибка в формате json
    """
    return make_response(jsonify({"error": "Not found"}), 404)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
