import stanza
import operator
import collections
from math import sqrt
from collections import defaultdict

# Named Entities from OntoNotes package:
PERSON = "PERSON"  # People, including fictional
NORP = "NORP"  # Nationalities or religious or political groups
FACILITY = "FACILITY"  # Buildings, airports, highways, bridges, etc.
ORGANIZATION = "ORG"  # Companies, agencies, institutions, etc.
GPE = "GPE"  # Countries, cities, states
LOCATION = "LOC"  # Non-GPE locations, mountain ranges, bodies of water
PRODUCT = "PRODUCT"  # Vehicles, weapons, foods, etc. (Not services)
EVENT = "EVENT"  # Named hurricanes, battles, wars, sports events, etc.
ART_WORK = "WORK OF ART"  # Titles of books, songs, etc.
LAW = "LAW"  # Named documents made into laws
NONE = "NONE"  # NER result is empty

# All named Entity tag list
NAMED_ENTITY_TAGS = [PERSON, NORP, FACILITY, ORGANIZATION, GPE, LOCATION, PRODUCT, EVENT, ART_WORK, LAW, NONE]

# Literal Types from OntoNotes package:
DATE = "DATE"  # Absolute or relative dates or periods
TIME = "TIME"  # Times smaller than a day
PERCENT = "PERCENT"  # Percentage (including "%")
MONEY = "MONEY"  # Monetary values, including unit
QUANTITY = "QUANTITY"  # Measurements, as of weight or distance
ORDINAL = "ORDINAL"  # "first", "second", etc.
CARDINAL = "CARDINAL"  # Numerals that do not fall under another type
EMPTY = "EMPTY"  # Empty value

CATEGORICAL_COLUMN = "CATEGORICAL"  # Categorical column type
LITERAL_COLUMN = "LITERAL"  # Literal column type
SUBJECT_COLUMN = "SUBJECT"  # Subject column type


def is_float(string):
    """
    Определение является ли строка числовым значением.
    :param string: исходная строка
    :return: True - если строка является числом, False - в противном случае
    """
    try:
        float(string.replace(",", "."))
        return True
    except ValueError:
        return False


def test_ner(text):
    """
    Функция для тестирвоания распознавания именованных сущностей в тексте.
    :param text: исходный текст
    """
    stanza.download("en")
    nlp = stanza.Pipeline(lang="en", processors="tokenize,ner")
    doc = nlp(text)
    print(*[f"entity: {ent.text}\ttype: {ent.type}" for ent in doc.ents], sep="\n")


def recognize_named_entities(source_table):
    """
    Распознавание именованных сущностей в исходном словаре (таблице)
    :param source_table: исходный словарь (таблица) состоящий из объектов: ключ и упоминание сущности (значение ячейки)
    :return: словарь распознанных именнованых сущностей в таблице
    """
    result_list = []
    # Подготовка нейронного конвейера
    stanza.download("en")
    nlp = stanza.Pipeline(lang="en", processors="tokenize,ner")
    # Обход строк в исходной таблице
    for row in source_table:
        result_item = dict()
        for key, mention_entity in row.items():
            # Распознавание именованной сущности
            doc = nlp(mention_entity + ".")
            # Формирование словаря с рузультатом распознавания именованных сущностей
            recognized_named_entities = []
            if len(doc.ents) > 1:
                for ent in doc.ents:
                    recognized_named_entities.append(ent.type)
            if len(doc.ents) == 1:
                recognized_named_entities = doc.ents[0].type
            if len(doc.ents) == 0:
                recognized_named_entities = NONE
            # Если упоминанию сущности присвоена неопределенная метка NONE
            if not isinstance(recognized_named_entities, list):
                if recognized_named_entities == NONE:
                    # Корректировка упоминания сущности, если оно является числовым значением
                    if is_float(mention_entity):
                        recognized_named_entities = CARDINAL
                    # Корректировка упоминания сущности, если оно является пустой строкой
                    if mention_entity == "":
                        recognized_named_entities = EMPTY
            result_item[key] = recognized_named_entities
        result_list.append(result_item)

    return result_list


def classify_recognized_named_entities(recognized_table):
    """
    Определение типа значений в ячейке на основе распознанных именованных сущностей.
    :param recognized_table: словарь (таблица) с распознанными именованными сущностями: ключ и NER-тег
    :return: словарь классифицированных по типам значений ячеек в таблице
    """
    result_list = []
    for recognized_row in recognized_table:
        result_item = dict()
        for key, recognized_named_entities in recognized_row.items():
            typed_value = LITERAL_COLUMN
            if isinstance(recognized_named_entities, list):
                for recognized_named_entity in recognized_named_entities:
                    if recognized_named_entity in NAMED_ENTITY_TAGS:
                        typed_value = CATEGORICAL_COLUMN
            else:
                if recognized_named_entities in NAMED_ENTITY_TAGS:
                    typed_value = CATEGORICAL_COLUMN
            result_item[key] = typed_value
        result_list.append(result_item)

    return result_list


def classify_columns(typed_table):
    """
    Определение типов столбцов на основе классифицированных значений ячеек.
    :param typed_table: словарь (таблица) с квалифицированными значениями ячеек: ключ и тип ячейки
    :return: словарь с типами столбцов
    """
    # Подсчет количества категориальных и литеральных значений ячеек
    categorical_number = defaultdict(int)
    literal_number = defaultdict(int)
    for typed_row in typed_table:
        for key, value in typed_row.items():
            if categorical_number[key] == 0:
                categorical_number[key] = 0
            if literal_number[key] == 0:
                literal_number[key] = 0
            if value == CATEGORICAL_COLUMN:
                categorical_number[key] += 1
            if value == LITERAL_COLUMN:
                literal_number[key] += 1
    # Определение типов для столбцов
    result_list = dict()
    for key_c, value_c in categorical_number.items():
        for key_l, value_l in literal_number.items():
            if key_c == key_l:
                if value_c >= value_l:
                    result_list[key_c] = CATEGORICAL_COLUMN
                else:
                    result_list[key_c] = LITERAL_COLUMN

    return result_list


def get_empty_cell_fraction(source_table, classified_table):
    """
    Получение доли пустых ячеек для категориальных столбцов.
    :param source_table: исходный словарь (таблица) состоящий из объектов: ключ и упоминание сущности (значение ячейки)
    :param classified_table: словарь (таблица) с типизированными столбцами
    :return: словарь c оценкой для каждого столбца
    """
    result_list = dict()
    # Вычисление общего количества ячеек в столбце
    cell_number = len(source_table)
    # Обход типов столбцов
    for column_key, column_type in classified_table.items():
        if column_type == CATEGORICAL_COLUMN:
            # Вычисление количества пустых ячеек в столбце
            empty_cell_number = 0
            for row in source_table:
                for key, mention_entity in row.items():
                    if column_key == key and not mention_entity:
                        empty_cell_number += 1
            # Вычисление доли пустых ячеек в столбце
            result_list[column_key] = empty_cell_number / cell_number

    return result_list


def get_unique_content_cell_fraction(source_table, classified_table):
    """
    Получение доли ячеек с уникальным содержимым для категориальных столбцов.
    :param source_table: исходный словарь (таблица) состоящий из объектов: ключ и упоминание сущности (значение ячейки)
    :param classified_table: словарь (таблица) с типизированными столбцами
    :return: словарь c оценкой для каждого столбца
    """
    result_list = dict()
    # Вычисление общего количества ячеек в столбце
    cell_number = len(source_table)
    # Обход типов столбцов
    for column_key, column_type in classified_table.items():
        if column_type == CATEGORICAL_COLUMN:
            # Вычисление количества ячеек с уникальным содержимым
            col = collections.Counter()
            for row in source_table:
                for key, mention_entity in row.items():
                    if column_key == key:
                        col[mention_entity] += 1
            # Вычисление доли ячеек с уникальным содержимым в столбце
            result_list[column_key] = len(col) / cell_number

    return result_list


def get_distance_from_first_ne_column(classified_table):
    """
    Получение расстояния от первого сущностного столбца для категориальных столбцов.
    :param classified_table: словарь (таблица) с типизированными столбцами
    :return: словарь c оценкой для каждого столбца
    """
    result_list = dict()
    column_number = 0
    for column_key, column_type in classified_table.items():
        if column_type == CATEGORICAL_COLUMN:
            result_list[column_key] = column_number
        column_number += 1

    return result_list


def get_average_word_number(source_table, classified_table):
    """
    Получение среднего количества слов для категориальных столбцов.
    :param source_table: исходный словарь (таблица) состоящий из объектов: ключ и упоминание сущности (значение ячейки)
    :param classified_table: словарь (таблица) с типизированными столбцами
    :return: словарь c оценкой для каждого столбца
    """
    result_list = dict()
    # Вычисление общего количества ячеек в столбце
    cell_number = len(source_table)
    # Обход типов столбцов
    for column_key, column_type in classified_table.items():
        if column_type == CATEGORICAL_COLUMN:
            # Подсчет количества слов в ячейках
            total_word_number = 0
            for row in source_table:
                for key, mention_entity in row.items():
                    if column_key == key and mention_entity:
                        total_word_number += len(mention_entity.split())
            # Вычисление среднего количества слов в ячейках столбца
            result_list[column_key] = total_word_number / cell_number

    return result_list


def define_subject_column(source_table, classified_table, index=None):
    """
    Определение сущностного (тематического) столбца на основе эвристических оценок.
    :param source_table: исходный словарь (таблица) состоящий из объектов: ключ и упоминание сущности (значение ячейки)
    :param classified_table: словарь (таблица) с типизированными столбцами
    :param index: явное указание на номер сущностного (тематического) столбца
    :return: словарь (таблица) с отмеченным сущностным (тематическим) столбцом
    """
    result_list = dict()
    # Если явно указан номер столбца, то данный столбец назначается сущностным (тематическим)
    if is_float(str(index)) and 0 <= index <= len(classified_table):
        i = 0
        for key, type_column in classified_table.items():
            if i == index:
                result_list[key] = SUBJECT_COLUMN
            else:
                result_list[key] = type_column
            i += 1
    else:
        sub_col = dict()
        # Получение доли пустых ячеек
        empty_cell_fraction = get_empty_cell_fraction(source_table, classified_table)
        # Получение доли ячеек с уникальным содержимым
        unique_content_cell_fraction = get_unique_content_cell_fraction(source_table, classified_table)
        # Получение расстояния от первого сущностного столбца
        distance_from_first_ne_column = get_distance_from_first_ne_column(classified_table)
        # Получение среднего количества слов
        average_word_number = get_average_word_number(source_table, classified_table)
        # Агрегация оценки
        for key, type_column in classified_table.items():
            if type_column == CATEGORICAL_COLUMN:
                print(average_word_number[key])
                awn = average_word_number[key]
                if awn > 15:
                    awn = 100 / awn
                sub_col[key] = (2 * unique_content_cell_fraction[key] + awn -
                                empty_cell_fraction[key]) / sqrt(distance_from_first_ne_column[key] + 1)
                print("TOTAL = " + str(sub_col[key]))
        # Определение ключа столбца с максимальной оценкой
        subject_key = max(sub_col.items(), key=operator.itemgetter(1))[0]
        # Формирование словаря с определенным сущностным (тематическим) столбцом
        for key, type_column in classified_table.items():
            if key == subject_key:
                result_list[key] = SUBJECT_COLUMN
            else:
                result_list[key] = type_column

    return result_list
