import os
import json
import tabbyld2.parser as pr
import tabbyld2.utility as utl
import tabbyld2.cleaner as cln
import tabbyld2.annotator as ant
import tabbyld2.column_classifier as cc
import tabbyld2.candidate_generation as cg


CSV_FILE_PATH = str(utl.get_project_root()) + "/dataset/"  # root path for source tables in CSV format
JSON_FILE_PATH = CSV_FILE_PATH + "json/"  # path for json table files
PROVENANCE_PATH = CSV_FILE_PATH + "provenance/"  # path for results and their provenance

# Paths of result provenance
CLEARED_DATA_PATH = "/cleared_data/"
RECOGNIZED_DATA_PATH = "/recognized_data/"
CLASSIFIED_DATA_PATH = "/classified_data/"

CANDIDATE_ENTITIES_PATH = "/candidate_entities/"
CANDIDATE_CLASSES_PATH = "/candidate_classes/"
CANDIDATE_PROPERTIES_PATH = "/candidate_properties/"

RANKED_CANDIDATE_ENTITIES = "/ranked_candidate_entities/"
RANKED_CANDIDATE_ENTITIES_BY_SS = "/ranked_candidate_entities_by_ss/"
RANKED_CANDIDATE_ENTITIES_BY_NS = "/ranked_candidate_entities_by_ns/"
RANKED_CANDIDATE_ENTITIES_BY_HS = "/ranked_candidate_entities_by_hs/"
RANKED_CANDIDATE_ENTITIES_BY_ESS = "/ranked_candidate_entities_by_ess/"
RANKED_CANDIDATE_ENTITIES_BY_CS = "/ranked_candidate_entities_by_cs/"

ANNOTATED_CELL_DATA_PATH = "/annotated_cell_data/"
ANNOTATED_COLUMN_DATA_PATH = "/annotated_column_data/"
ANNOTATED_PROPERTY_DATA_PATH = "/annotated_property_data/"


# Сохранение набора электронных таблиц в формате json
pr.save_json_dataset(CSV_FILE_PATH, JSON_FILE_PATH)

# Обход файлов json-файлов электронных таблиц в каталоге
for root, dirs, files in os.walk(JSON_FILE_PATH):
    for file in files:
        if utl.allowed_file(file, {"json"}):
            # Очистка данных
            cleared_data = cln.clean(JSON_FILE_PATH + file)
            if cleared_data:
                # Формирование пути к файлу
                path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + CLEARED_DATA_PATH
                # Проверка существования каталога для сохранения результатов очистки данных
                utl.check_directory(path)
                # Запись json-файла c очищенными табличными данными
                with open(path + file, "w") as outfile:
                    json.dump(cleared_data, outfile, indent=4)

            # Распознавание именованных сущностей в исходном словаре (таблице)
            recognized_data = cc.recognize_named_entities(cleared_data)
            if recognized_data:
                # Формирование пути к файлу
                path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + RECOGNIZED_DATA_PATH
                # Проверка существования каталога для сохранения результатов распознавания именованных сущностей
                utl.check_directory(path)
                # Запись json-файла c результатами распознавания именованных сущностей
                with open(path + file, "w") as outfile:
                    json.dump(recognized_data, outfile, indent=4)

            # Классификация столбцов в исходном словаре (таблице) на основе распознанных именованных сущностей
            classified_data = cc.classify_recognized_named_entities(recognized_data)
            classified_data = cc.classify_columns(classified_data)
            # Определение сущностного (тематического) столбца
            classified_data = cc.define_subject_column(cleared_data, classified_data)
            if classified_data:
                # Формирование пути к файлу
                path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + CLASSIFIED_DATA_PATH
                # Проверка существования каталога для сохранения результатов классификации столбцов
                utl.check_directory(path)
                # Запись json-файла c результатами классификации столбцов
                with open(path + file, "w") as outfile:
                    json.dump(classified_data, outfile, indent=4)

            print("*********************************************************")
            # Поиск сущностей кандидатов для всех ячеек категорильных столбцов
            candidate_entity_data = cg.get_candidate_entities_for_table(cleared_data, classified_data)
            if candidate_entity_data:
                # Формирование пути к файлу
                path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + CANDIDATE_ENTITIES_PATH
                # Проверка существования каталога для сохранения результатов поиска сущностей кандидатов для таблицы
                utl.check_directory(path)
                # Запись json-файла c результатами поиска сущностей кандидатов
                with open(path + file, "w") as outfile:
                    json.dump(candidate_entity_data, outfile, indent=4)

            print("*********************************************************")
            # Ранжирование значений ячеек по схоству строк
            ranked_candidate_entities_by_ss = ant.ranking_cells_by_ss(candidate_entity_data)
            if ranked_candidate_entities_by_ss:
                # Формирование пути к файлу
                path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + RANKED_CANDIDATE_ENTITIES_BY_SS
                # Проверка существования каталога для сохранения результатов ранжирования сущностей кандидатов
                utl.check_directory(path)
                # Запись json-файла c результатами ранжирования сущностей кандидатов
                with open(path + file, "w") as outfile:
                    json.dump(ranked_candidate_entities_by_ss, outfile, indent=4)
            # Ранжирование значений ячеек по сходству на основе NER-классов
            ranked_candidate_entities_by_ns = ant.ranking_cells_by_ns(candidate_entity_data, recognized_data)
            if ranked_candidate_entities_by_ns:
                # Формирование пути к файлу
                path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + RANKED_CANDIDATE_ENTITIES_BY_NS
                # Проверка существования каталога для сохранения результатов ранжирования сущностей кандидатов
                utl.check_directory(path)
                # Запись json-файла c результатами ранжирования сущностей кандидатов
                with open(path + file, "w") as outfile:
                    json.dump(ranked_candidate_entities_by_ns, outfile, indent=4)
            # Ранжирование значений ячеек категориальных столбцов (включая сущностный столбец) по
            # сходству на основе заголовка столбца
            ranked_candidate_entities_by_hs = ant.ranking_cells_by_hs(candidate_entity_data)
            if ranked_candidate_entities_by_hs:
                # Формирование пути к файлу
                path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + RANKED_CANDIDATE_ENTITIES_BY_HS
                # Проверка существования каталога для сохранения результатов ранжирования сущностей кандидатов
                utl.check_directory(path)
                # Запись json-файла c результатами ранжирования сущностей кандидатов
                with open(path + file, "w") as outfile:
                    json.dump(ranked_candidate_entities_by_hs, outfile, indent=4)
            # Ранжирование значений ячеек по сходству на основе семантической близости между сущностями кандидатами
            ranked_candidate_entities_by_ess = ant.ranking_cells_by_ess(candidate_entity_data)
            if ranked_candidate_entities_by_ess:
                # Формирование пути к файлу
                path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + RANKED_CANDIDATE_ENTITIES_BY_ESS
                # Проверка существования каталога для сохранения результатов ранжирования сущностей кандидатов
                utl.check_directory(path)
                # Запись json-файла c результатами ранжирования сущностей кандидатов
                with open(path + file, "w") as outfile:
                    json.dump(ranked_candidate_entities_by_ess, outfile, indent=4)
            # Ранжирование значений ячеек по сходству на основе контекста
            ranked_candidate_entities_by_cs = ant.ranking_cells_by_cs(candidate_entity_data)
            if ranked_candidate_entities_by_cs:
                # Формирование пути к файлу
                path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + RANKED_CANDIDATE_ENTITIES_BY_CS
                # Проверка существования каталога для сохранения результатов ранжирования сущностей кандидатов
                utl.check_directory(path)
                # Запись json-файла c результатами ранжирования сущностей кандидатов
                with open(path + file, "w") as outfile:
                    json.dump(ranked_candidate_entities_by_cs, outfile, indent=4)
            # Агрегирование оценок (рангов) для значений ячеек, полученных на основе пяти эвристик
            final_ranked_candidate_entities = ant.aggregate_ranked_cells(ranked_candidate_entities_by_ss,
                                                                         ranked_candidate_entities_by_ns,
                                                                         ranked_candidate_entities_by_hs,
                                                                         ranked_candidate_entities_by_ess,
                                                                         ranked_candidate_entities_by_cs)
            if final_ranked_candidate_entities:
                # Формирование пути к файлу
                path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + RANKED_CANDIDATE_ENTITIES
                # Проверка существования каталога для сохранения результатов объединения рангов для сущностей кандидатов
                utl.check_directory(path)
                # Запись json-файла c результатами итогового ранжирования сущностей кандидатов
                with open(path + file, "w") as outfile:
                    json.dump(final_ranked_candidate_entities, outfile, indent=4)
            # Аннотирование значений ячеек на основе ранжированного списка сущностей кандидатов
            annotated_cell_data = ant.annotate_cells(final_ranked_candidate_entities)
            if annotated_cell_data:
                # Формирование пути к файлу
                path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + ANNOTATED_CELL_DATA_PATH
                # Проверка существования каталога для сохранения результатов аннотирования значений ячеек
                utl.check_directory(path)
                # Запись json-файла c результатами аннотирования значений ячеек
                with open(path + file, "w") as outfile:
                    json.dump(annotated_cell_data, outfile, indent=4)
