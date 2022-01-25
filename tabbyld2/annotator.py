import collections
from collections import Counter
import tabbyld2.utility as utl
import tabbyld2.cea_solver as cea
import tabbyld2.cta_solver as cta
import tabbyld2.column_classifier as cc
import tabbyld2.candidate_generation as cg
import os


# Типы данных XML-схемы для литеральных столбцов таблицы
DATE_DATATYPE = "xsd:date"
TIME_DATATYPE = "xsd:time"
NON_NEGATIVE_INTEGER_DATATYPE = "xsd:nonNegativeInteger"
POSITIVE_INTEGER_DATATYPE = "xsd:positiveInteger"
DECIMAL_DATATYPE = "xsd:decimal"
STRING_DATATYPE = "xsd:string"


def ranking_candidate_entities_by_ss(table_with_candidate_entities):
    """
    Ранжирование сущностей кандидатов для значений ячеек категориальных столбцов (включая сущностный столбец)
    по схоству строк.
    :param table_with_candidate_entities: очищенная исходная таблица с наборами сущностей кандидатов
    :return: таблица с наборами ранжированных сущностей кандидатов для ячеек
    """
    result = dict()
    for key, item in table_with_candidate_entities.items():
        # Обход ячеек с сущностями кандидатами
        for entity_mention, candidate_entities in item.items():
            # Вычисление оценок для сущностей из набора кандидатов по сходству строк
            result_item = cea.get_string_similarity(entity_mention, candidate_entities)
            # Формирование ранжированных сущностей кандидатов для ячеек
            if key not in result:
                result[key] = dict()
            result[key][entity_mention] = result_item

    return result


def ranking_candidate_entities_by_ns(table_with_candidate_entities, recognized_table):
    """
    Ранжирование сущностей кандидатов для значений ячеек категориальных столбцов (включая сущностный столбец)
    по сходству на основе NER-классов.
    :param table_with_candidate_entities: очищенная исходная таблица с наборами сущностей кандидатов
    :param recognized_table: словарь (таблица) с распознанными именованными сущностями: ключ и NER-класс
    :return: таблица с наборами ранжированных сущностей кандидатов для ячеек
    """
    result = dict()
    for key, item in table_with_candidate_entities.items():
        global_index = 1
        # Обход ячеек с сущностями кандидатами
        for entity_mention, candidate_entities in item.items():
            # Определение NER-класса (метки) для текущего значения ячейки
            ner_class = cc.NONE
            local_index = 1
            for recognized_row in recognized_table:
                if global_index == local_index:
                    for rd_key, recognized_named_entities in recognized_row.items():
                        if rd_key == key:
                            if isinstance(recognized_named_entities, list):
                                for recognized_named_entity in recognized_named_entities:
                                    if recognized_named_entity in cc.NAMED_ENTITY_TAGS:
                                        ner_class = recognized_named_entity
                            else:
                                ner_class = recognized_named_entities

                local_index += 1
            # Вычисление оценок для сущностей из набора кандидатов по сходству на основе NER-классов
            result_item = cea.get_ner_based_similarity(ner_class, candidate_entities)
            # Формирование ранжированных сущностей кандидатов для ячеек
            if key not in result:
                result[key] = dict()
            result[key][entity_mention] = result_item
            global_index += 1

    return result


def ranking_candidate_entities_by_hs(table_with_candidate_entities):
    """
    Ранжирование сущностей кандидатов для значений ячеек категориальных столбцов (включая сущностный столбец)
    по сходству на основе заголовка столбца.
    :param table_with_candidate_entities: очищенная исходная таблица с наборами сущностей кандидатов
    :return: таблица с наборами ранжированных сущностей кандидатов для ячеек
    """
    result = dict()
    for key, item in table_with_candidate_entities.items():
        # Обход ячеек с сущностями кандидатами
        for entity_mention, candidate_entities in item.items():
            # Вычисление оценок для сущностей из набора кандидатов по сходству на основе заголовка столбца
            result_item = cea.get_heading_based_similarity(key, candidate_entities)
            # Формирование ранжированных сущностей кандидатов для ячеек
            if key not in result:
                result[key] = dict()
            result[key][entity_mention] = result_item

    return result


def ranking_candidate_entities_by_ess(table_with_candidate_entities):
    """
    Ранжирование сущностей кандидатов для значений ячеек категориальных столбцов (включая сущностный столбец)
    по сходству на основе семантической близости между сущностями кандидатами.
    :param table_with_candidate_entities: очищенная исходная таблица с наборами сущностей кандидатов
    :return: таблица с наборами ранжированных сущностей кандидатов для ячеек
    """
    # Вычисление оценок для сущностей из набора кандидатов по сходству на основе
    # семантической близости между сущностями кандидатами
    result = cea.get_entity_embedding_based_semantic_similarity(table_with_candidate_entities)
    # Формирование ранжированных сущностей кандидатов для ячеек

    os.remove("rdf2vec.model")
    return result


def ranking_candidate_entities_by_cs(table_with_candidate_entities):
    """
    Ранжирование сущностей кандидатов для значений ячеек категориальных столбцов (включая сущностный столбец)
    по сходству на основе контекста.
    :param table_with_candidate_entities: очищенная исходная таблица с наборами сущностей кандидатов
    :return: таблица с наборами ранжированных сущностей кандидатов для ячеек
    """
    result = dict()
    for key, item in table_with_candidate_entities.items():
        # Обход ячеек с сущностями кандидатами
        for entity_mention, candidate_entities in item.items():
            # Вычисление оценок для сущностей из набора кандидатов по сходству на основе контекста
            result_item = cea.get_context_based_similarity(entity_mention, candidate_entities)
            # Формирование ранжированных сущностей кандидатов для ячеек
            if key not in result:
                result[key] = dict()
            result[key][entity_mention] = result_item

    return result


def get_counter_for_ranked_candidate_entities(cell_value, ranked_candidate_entities):
    """
    Получение ранжированных сущностей кандидатов в Counter
    :param cell_value: значение ячейки для которого необходимо сформировать ранжированный набор сущностей кандидатов
    :param ranked_candidate_entities: ранжированный набор сущностей кандидатов
    :return: ранжированный набор сущностей кандидатов в Counter
    """
    result = Counter()
    for key, item in ranked_candidate_entities.items():
        for entity_mention, candidate_entities in item.items():
            if cell_value == entity_mention:
                result = Counter(candidate_entities)

    return result


def aggregate_ranked_candidate_entities(ranked_candidate_entities_by_ss, ranked_candidate_entities_by_ns,
                                        ranked_candidate_entities_by_hs, ranked_candidate_entities_by_ess,
                                        ranked_candidate_entities_by_cs):
    """
    Агрегирование оценок (рангов) для сущностей кандидатов для значений ячеек, полученных на основе пяти эвристик.
    :param ranked_candidate_entities_by_ss: ранжированные сущности кандидаты по сходству строк
    :param ranked_candidate_entities_by_ns: ранжированные сущности кандидаты по сходству на основе NER-классов
    :param ranked_candidate_entities_by_hs: ранжированные сущности кандидаты по сходству на основе заголовка столбца
    :param ranked_candidate_entities_by_ess: ранжированные сущности кандидаты по сходству на основе
    семантической близости между сущностями кандидатами
    :param ranked_candidate_entities_by_cs: ранжированные сущности кандидаты по сходству на основе контекста
    :return: таблица с наборами агрегированных ранжированных сущностей кандидатов для ячеек
    """
    result = dict()
    for ss_key, ss_item in ranked_candidate_entities_by_ss.items():
        # Обход ячеек с сущностями кандидатами, полученных по сходству строк
        for ss_entity_mention, ss_candidate_entities in ss_item.items():
            # Преобразование ранжированных сущностей кандидатов по сходству строк в Counter
            ss = Counter(ss_candidate_entities)
            # Обход ячеек с сущностями кандидатами, полученных по сходству на основе NER-классов
            ns = get_counter_for_ranked_candidate_entities(ss_entity_mention, ranked_candidate_entities_by_ns)
            # Обход ячеек с сущностями кандидатами, полученных по сходству на основе заголовка столбца
            hs = get_counter_for_ranked_candidate_entities(ss_entity_mention, ranked_candidate_entities_by_hs)
            # Обход ячеек с сущностями кандидатами, полученных по сходству на основе
            # семантической близости между сущностями кандидатами
            ess = get_counter_for_ranked_candidate_entities(ss_entity_mention, ranked_candidate_entities_by_ess)
            # Обход ячеек с сущностями кандидатами, полученных по сходству на основе контекста
            cs = get_counter_for_ranked_candidate_entities(ss_entity_mention, ranked_candidate_entities_by_cs)
            # Объединение оценок (рангов)
            final_ranked_candidate_entities = ss + ns + hs + ess + cs
            result_item = dict(final_ranked_candidate_entities)
            # Сортировка по оценкам
            result_item = dict(sorted(result_item.items(), key=lambda item: item[1], reverse=True))
            # Формирование ранжированных сущностей кандидатов для ячеек
            if ss_key not in result:
                result[ss_key] = dict()
            result[ss_key][ss_entity_mention] = result_item

    return result


def annotate_cells(final_ranked_candidate_entities):
    """
    Аннотирование значений ячеек таблицы.
    :param final_ranked_candidate_entities: словарь (таблица) с наборами ранжированных сущностей кандидатов
    :return: словарь (таблица) с аннотированными значениями ячеек
    """
    result = dict()
    for key, item in final_ranked_candidate_entities.items():
        # Обход ячеек с сущностями кандидатами
        for entity_mention, candidate_entities in item.items():
            result_item = ""
            if bool(candidate_entities):
                # Получение первой сущности из набора кандидатов с максимальной оценкой
                result_item = list(candidate_entities.keys())[0]
            # Формирование ранжированных сущностей кандидатов для ячеек
            if key not in result:
                result[key] = dict()
            result[key][entity_mention] = result_item

    return result


def ranking_candidate_classes_by_mv(annotated_cells_table, classified_table):
    """
    Ранжирование классов кандидатов для категориальных столбцов (включая сущностный столбец)
    по сходству на голосования большинством.
    :param annotated_cells_table: словарь (таблица) с аннотированными ячейками
    :param classified_table: словарь (таблица) с типизированными столбцами
    :return: таблица с наборами ранжированных классов кандидатов для категориальных столбцов
    """
    result = dict()
    for key, item in annotated_cells_table.items():
        # Обход строк в данных с классификацией столбцов
        for col_key, type_column in classified_table.items():
            if key == col_key:
                if type_column == cc.SUBJECT_COLUMN or type_column == cc.CATEGORICAL_COLUMN:
                    # Вычисление оценок для классов кандидатов на основе голосования большинством
                    result[key] = cta.get_majority_voting_similarity(item)
                else:
                    result[key] = ""

    return result


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
            merge_table = utl.merge_dicts(typed_row, merge_table)

    # Определение наиболее распространенного типа данных в списке для каждого столбца
    result = dict()
    for key, datatype_list in merge_table.items():
        result[key] = max(set(datatype_list), key=datatype_list.count)

    return result


def link_datatype_to_column(recognized_table):
    """
    Связывание KG-типов данных с литеральными столбцами.
    :param recognized_table: словарь (таблица) с распознанными именнованными сущностями
    :return: словарь содержащий аннотированные литеральные столбцы
    """
    result = dict()
    typed_data = define_datatype(recognized_table)
    try:
        if isinstance(typed_data, dict):
            for key, value in typed_data.items():
                if value != STRING_DATATYPE:
                    result[key] = value
    except Exception as e:
        print(e)
    return result


def link_class_to_column(column_name, candidate_classes, reference_class=None):
    """
    Связывание KG-класса со столбцом.
    :param column_name: название заголовка столбца
    :param candidate_classes: набор классов кандидатов
    :param reference_class: референтный класс
    :return: словарь содержащий аннотированный столбец
    """
    result = dict()
    if reference_class is not None:
        result[column_name] = reference_class
    else:
        if isinstance(candidate_classes, collections.Mapping) and len(candidate_classes):
            pass
        else:
            pass

    return result


def link_entity_to_cell(cell_value, candidate_entities, reference_entity=None):
    """
    Связывание KG-сущности с ячейкой.
    :param cell_value: значение ячейки
    :param candidate_entities: набор сущностей кандидатов
    :param reference_entity: референтная сущность
    :return: словарь содержащий аннотированную ячейку
    """
    result = dict()
    if reference_entity is not None:
        result[cell_value] = reference_entity
    else:
        if isinstance(candidate_entities, collections.Mapping) and len(candidate_entities):
            pass
        else:
            pass

    return result


def link_property_to_column_pair(column_name, candidate_properties, reference_property=None):
    """
    Связывание KG-свойства (отношения) с парой столбцов.
    :param column_name: название заголовка столбца с которым связывается сущностный (тематический) столбец
    :param candidate_properties: набор свойств кандидатов
    :param reference_property: референтное свойство
    :return: словарь содержащий аннотированную связь между парой столбцов
    """
    result = dict()
    if reference_property is not None:
        result[column_name] = reference_property
    else:
        if isinstance(candidate_properties, collections.Mapping) and len(candidate_properties):
            pass
        else:
            pass

    return result
