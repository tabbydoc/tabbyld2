import os
import json
import tabbyld2.parser as pr
import tabbyld2.utility as utl
import tabbyld2.cleaner as cln
import tabbyld2.column_classifier as cc


CSV_FILE_PATH = "C:/Users/79501/datasets/test/"
JSON_FILE_PATH = "C:/Users/79501/datasets/test/json/"
CLEARED_DATA_PATH = "C:/Users/79501/datasets/test/provenance/cleared_data/"
RECOGNIZED_DATA_PATH = "C:/Users/79501/datasets/test/provenance/recognized_data/"
CLASSIFIED_DATA_PATH = "C:/Users/79501/datasets/test/provenance/classified_data/"
CANDIDATE_CLASSES_PATH = "C:/Users/79501/datasets/test/provenance/candidate_classes/"
CANDIDATE_ENTITIES_PATH = "C:/Users/79501/datasets/test/provenance/candidate_entities/"
ANNOTATED_HEADING_DATA_PATH = "C:/Users/79501/datasets/test/provenance/annotated_heading_data/"
ANNOTATED_CELL_DATA_PATH = "C:/Users/79501/datasets/test/provenance/annotated_cell_data/"


# Сохранение набора электронных таблиц в формате json
pr.save_json_dataset(CSV_FILE_PATH, JSON_FILE_PATH)

# Обход файлов json-файлов электронных таблиц в каталоге
for root, dirs, files in os.walk(JSON_FILE_PATH):
    for file in files:
        if utl.allowed_file(file, {"json"}):
            # Очистка данных
            cleared_data = cln.clean(JSON_FILE_PATH + file)
            if cleared_data:
                # Проверка существования каталога для сохранения результатов очистки данных
                utl.check_directory(CLEARED_DATA_PATH)
                # Запись json-файлов c очищенными табличными данными
                with open(CLEARED_DATA_PATH + file, "w") as outfile:
                    json.dump(cleared_data, outfile, indent=4)

                # Распознавание именованных сущностей в исходном словаре (таблице)
                recognized_data = cc.recognize_named_entities(cleared_data)
                if recognized_data:
                    # Проверка существования каталога для сохранения результатов распознавания именованных сущностей
                    utl.check_directory(RECOGNIZED_DATA_PATH)
                    # Запись json-файлов c результатами распознавания именованных сущностей
                    with open(RECOGNIZED_DATA_PATH + file, "w") as outfile:
                        json.dump(recognized_data, outfile, indent=4)

                # Классификация столбцов в исходном словаре (таблице) на основе распознанных именованных сущностей
                classified_data = cc.classify_recognized_named_entities(recognized_data)
                classified_data = cc.classify_columns(classified_data)
                # Определение сущностного (тематического) столбца
                classified_data = cc.define_subject_column(cleared_data, classified_data)
                if classified_data:
                    # Проверка существования каталога для сохранения результатов классификации столбцов
                    utl.check_directory(CLASSIFIED_DATA_PATH)
                    # Запись json-файлов c результатами классификации столбцов
                    with open(CLASSIFIED_DATA_PATH + file, "w") as outfile:
                        json.dump(classified_data, outfile, indent=4)
