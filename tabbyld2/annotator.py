import collections
import tabbyld2.column_classifier as cc
from Levenshtein._levenshtein import distance


# Типы данных XML-схемы для литеральных столбцов таблицы
DATE_DATATYPE = "xsd:date"
TIME_DATATYPE = "xsd:time"
NON_NEGATIVE_INTEGER_DATATYPE = "xsd:nonNegativeInteger"
POSITIVE_INTEGER_DATATYPE = "xsd:positiveInteger"
DECIMAL_DATATYPE = "xsd:decimal"
STRING_DATATYPE = "xsd:string"


def get_levenshtein_distance(entity_mention, candidate_entity, underscore_replacement: bool = False):
    """
    Вычисление расстояния Левенштейна (редактирования) между двумя строками.
    :param entity_mention: текстовое упоминание сущности
    :param candidate_entity: сущность-кандидат
    :param underscore_replacement: режим замены символа нижнего подчеркивания на пробел
    :return: нормализованное расстояние Левенштейна в диапазоне [0, ..., 1]
    """
    # Замена символа нижнего подчеркивания на пробел
    if underscore_replacement:
        candidate_entity = candidate_entity.replace("_", " ")
    # Вычисление абсолютного расстояния Левенштейна
    levenshtein_distance = distance(entity_mention, candidate_entity)
    # Нижняя граница
    min_range = 0
    # Определение верхней границы
    if len(entity_mention) > len(candidate_entity):
        max_range = len(entity_mention)
    else:
        max_range = len(candidate_entity)
    # Нормализация абсолютного расстояния Левенштейна
    normalized_levenshtein_distance = 1 - ((levenshtein_distance - min_range) / (max_range - min_range))

    return normalized_levenshtein_distance


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


def define_datatype(recognized_table):
    """
    Определение типа данных для каждого столбца таблицы на основе распознанных именованных сущностей (NER-меток).
    :param recognized_table: словарь распознанных именнованых сущностей в таблице
    :return: словарь с типами данных XML-схемы для каждого столбца
    """
    # Определение соответствия типа данных на основе распознанной именованной сущности (NER-метки) для каждой ячейки
    typed_table = []
    for recognized_row in recognized_table:
        typed_item = dict()
        for key, recognized_named_entities in recognized_row.items():
            typed_value = STRING_DATATYPE
            if isinstance(recognized_named_entities, list):
                for recognized_named_entity in recognized_named_entities:
                    if recognized_named_entity in cc.NAMED_ENTITY_TAGS:
                        typed_value = STRING_DATATYPE
            else:
                if recognized_named_entities in cc.NAMED_ENTITY_TAGS:
                    typed_value = STRING_DATATYPE
                if recognized_named_entities == cc.DATE:
                    typed_value = DATE_DATATYPE
                if recognized_named_entities == cc.TIME:
                    typed_value = TIME_DATATYPE
                if recognized_named_entities == cc.PERCENT:
                    typed_value = NON_NEGATIVE_INTEGER_DATATYPE
                if recognized_named_entities == cc.MONEY:
                    typed_value = NON_NEGATIVE_INTEGER_DATATYPE
                if recognized_named_entities == cc.QUANTITY:
                    typed_value = NON_NEGATIVE_INTEGER_DATATYPE
                if recognized_named_entities == cc.ORDINAL:
                    typed_value = POSITIVE_INTEGER_DATATYPE
                if recognized_named_entities == cc.CARDINAL:
                    typed_value = DECIMAL_DATATYPE
                if recognized_named_entities == cc.EMPTY:
                    typed_value = POSITIVE_INTEGER_DATATYPE
            typed_item[key] = typed_value
        typed_table.append(typed_item)

    # Объединение всех типов данных для каждого столбца в один общий список
    merge_table = dict()
    for typed_row in typed_table:
        if not bool(merge_table):
            for key, value in typed_row.items():
                merge_table[key] = [value]
        else:
            merge_table = merge_dicts(typed_row, merge_table)

    # Определение наиболее распространенного типа данных в списке для каждого столбца
    result_list = dict()
    for key, datatype_list in merge_table.items():
        result_list[key] = max(set(datatype_list), key=datatype_list.count)

    return result_list


def link_datatype_to_column(recognized_table):
    """
    Связывание KG-типов данных с литеральными столбцами.
    :param recognized_table: словарь (таблица) с распознанными именнованными сущностями
    :return: словарь содержащий аннотированные литеральные столбцы
    """
    result_list = dict()
    typed_data = define_datatype(recognized_table)
    try:
        if isinstance(typed_data, dict):
            for key, value in typed_data.items():
                if value != STRING_DATATYPE:
                    result_list[key] = value
    except Exception as e:
        print(e)
    return result_list


def link_class_to_column(column_name, candidate_classes, reference_class=None):
    """
    Связывание KG-класса со столбцом.
    :param column_name: название заголовка столбца
    :param candidate_classes: набор классов кандидатов
    :param reference_class: референтный класс
    :return: словарь содержащий аннотированный столбец
    """
    result_list = dict()
    if reference_class is not None:
        result_list[column_name] = reference_class
    else:
        if isinstance(candidate_classes, collections.Mapping) and len(candidate_classes):
            pass
        else:
            pass

    return result_list


def link_entity_to_cell(cell_value, candidate_entities, reference_entity=None):
    """
    Связывание KG-сущности с ячейкой.
    :param cell_value: значение ячейки
    :param candidate_entities: набор сущностей кандидатов
    :param reference_entity: референтная сущность
    :return: словарь содержащий аннотированную ячейку
    """
    result_list = dict()
    if reference_entity is not None:
        result_list[cell_value] = reference_entity
    else:
        if isinstance(candidate_entities, collections.Mapping) and len(candidate_entities):
            pass
        else:
            pass

    return result_list


def link_property_to_column_pair(column_name, candidate_properties, reference_property=None):
    """
    Связывание KG-свойства (отношения) с парой столбцов.
    :param column_name: название заголовка столбца с которым связывается сущностный (тематический) столбец
    :param candidate_properties: набор свойств кандидатов
    :param reference_property: референтное свойство
    :return: словарь содержащий аннотированную связь между парой столбцов
    """
    result_list = dict()
    if reference_property is not None:
        result_list[column_name] = reference_property
    else:
        if isinstance(candidate_properties, collections.Mapping) and len(candidate_properties):
            pass
        else:
            pass

    return result_list
