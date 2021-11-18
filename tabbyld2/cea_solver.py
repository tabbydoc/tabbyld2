from Levenshtein._levenshtein import distance


def get_levenshtein_distance(entity_mention, candidate_entity, underscore_replacement: bool = False,
                             short_name: bool = False):
    """
    Вычисление расстояния Левенштейна (редактирования) между двумя строками.
    :param entity_mention: текстовое упоминание сущности
    :param candidate_entity: сущность-кандидат
    :param underscore_replacement: режим замены символа нижнего подчеркивания на пробел
    :param short_name: режим отображения короткого наименования сущности (без полного URI)
    :return: нормализованное расстояние Левенштейна в диапазоне [0, ..., 1]
    """
    # Замена символа нижнего подчеркивания на пробел
    if underscore_replacement:
        candidate_entity = candidate_entity.replace("_", " ")
    # Удаление URI-адреса в имени сущности
    if short_name:
        candidate_entity = candidate_entity.replace("http://dbpedia.org/resource/", "")
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


def get_string_similarity(entity_mention, candidate_entities):
    """
    Вычисление оценок для сущностей из набора кандидатов по сходству строк.
    :param entity_mention: текстовое упоминание сущности
    :param candidate_entities: набор сущностей-кандидатов
    :return: ранжированный список сущностей-кандидатов
    """
    result = []
    for candidate_entity in candidate_entities:
        result.append([candidate_entity, get_levenshtein_distance(entity_mention, candidate_entity, True, False)])

    return result
