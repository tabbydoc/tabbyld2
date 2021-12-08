import tabbyld2.dbpedia_sparql_endpoint as dbs


# Весовые коэффициенты для балансировки важности оценок, полученных на основе применения 3 методов определения сходства
MV_WEIGHT_FACTOR = 1  # Метод голосования большинством
HS_WEIGHT_FACTOR = 1  # Метод на основе сходства по заголовку
CN_WEIGHT_FACTOR = 1  # Метод на основе прогнозирования класса


def get_majority_voting_similarity(annotated_cells):
    """
    Вычисление оценок для классов кандидатов на основе голосования большинством для категориального столбца.
    :param annotated_cells: словарь (таблица) с аннотированными ячейками
    :return: ранжированный список классов кандидатов
    """
    result = dict()
    # Обход аннотированных ячеек с сущностями
    for entity_mention, reference_entity in annotated_cells.items():
        # Получение набора классов для сущности из DBpedia
        dbpedia_classes = dbs.get_classes(reference_entity, False)
        # Определение оценки для классов на основе частоты их появления в наборе
        for dbpedia_class in dbpedia_classes:
            if dbpedia_class not in result:
                result[dbpedia_class] = 1
            else:
                result[dbpedia_class] += 1
    # Сортировка по оценкам
    result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))

    return result
