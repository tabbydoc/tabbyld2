import csv
import json
import os
from datetime import datetime
from html import unescape
from urllib.parse import unquote

import cleaner as cl
from dbpedia_sparql_endpoint import get_redirects
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
                all_candidate_entities = {}
                for cell_value, entities in json.loads(candidate_entities_file.read())[sub_col].items():
                    if entities:
                        string = ""
                        for entity in entities:
                            string += ", <" + entity + ">" if string else "<" + entity + ">"
                        all_candidate_entities[cell_value.lower()] = list({*get_redirects(string), *entities})
            k, length = 0, 0
            with open(instance, "r", newline="", encoding="utf-8") as csv_file:
                for (uri, cell_value, _) in csv.reader(csv_file):
                    length += 1
                    cv = cl.remove_multiple_spaces(cl.remove_garbage_characters(cl.fix_text(cell_value.lower())))
                    candidate_entities = all_candidate_entities.get(unescape(cv))
                    if candidate_entities:
                        if unquote(uri) in candidate_entities:
                            k += 1
                        else:
                            print("No entity: " + uri + " for '" + unescape(cell_value) + "'")
                    else:
                        print("For cell: '" + unescape(cell_value) + "' - " + str(candidate_entities))
            print("Accuracy for " + str(file) + ": " + str(k / length) + "\n")
    print("***************************************************")
    print("Full time: " + str(datetime.now() - start_full_time))
