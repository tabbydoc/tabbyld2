import csv
import json
import os
from datetime import datetime

from ftfy import fix_encoding, fix_text
from tabbyld2.config import EvaluationPath, ResultPath
from tabbyld2.helpers.file import remove_suffix_in_filename
from tabbyld2.helpers.parser import save_json_dataset


if __name__ == "__main__":
    start_full_time = datetime.now()
    save_json_dataset(ResultPath.CSV_FILE_PATH, ResultPath.JSON_FILE_PATH)
    for _, _, files in os.walk(ResultPath.CSV_FILE_PATH):
        for file in files:
            provenance_path = ResultPath.PROVENANCE_PATH + remove_suffix_in_filename(file) + "/"
            instance = EvaluationPath.T2DV2_INSTANCE + file
            if not os.path.exists(provenance_path) or not os.path.exists(instance):
                continue
            with open(provenance_path + ResultPath.CLASSIFIED_DATA, "r", encoding="utf-8") as class_file:
                for key, value in json.loads(class_file.read()).items():
                    if value == "SUBJECT":
                        sub_col = fix_text(fix_encoding(str(key)))
            with open(provenance_path + ResultPath.CANDIDATE_ENTITIES, "r", encoding="utf-8") as candidate_entities_file:
                dictionary = json.loads(candidate_entities_file.read())[sub_col]
            k, length = 0, 0
            with open(instance, "r", newline="", encoding="utf-8") as csv_file:
                for (uri, cell_value, _) in csv.reader(csv_file):
                    length += 1
                    for key in dictionary.keys():
                        if fix_text(fix_encoding(str(key.lower().replace(" ", "")))) == \
                                fix_text(fix_encoding(str(cell_value.lower().replace(" ", "").replace(">", "")))):
                            if dictionary[key] is not None:
                                if dictionary[key].count(fix_text(fix_encoding(str(uri)))):
                                    k += 1
            print("Accuracy for " + str(file) + ": " + str(k / length))
    print("***************************************************")
    print("Full time: " + str(datetime.now() - start_full_time))
