import csv
import json
import os
import ftfy
from tabbyld2.config import EvaluationPath, ResultPath

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    subj_col = ''
    file_name = ''
    if os.path.exists(ResultPath.PROVENANCE_PATH):
        for root, dirs, file in os.walk(ResultPath.CSV_FILE_PATH):
            for files in file:
                print(files[:-4])
                file_name = files[:-4] + '/'
                path = ResultPath.PROVENANCE_PATH + file_name
                path_csv = EvaluationPath.T2DV2_INSTANCE + file_name[:-1] + ".csv"
                if not os.path.exists(path):
                    continue
                if not os.path.exists(path_csv):
                    continue

                with open(path + ResultPath.CLASSIFIED_DATA, "r", encoding='utf-8') as class_file:
                    dictionary = class_file.read()
                    cd_dict = json.loads(dictionary)
                    for keys, values in cd_dict.items():
                        if values == 'SUBJECT':
                            subj_col = ftfy.fix_text(ftfy.fix_encoding(str(keys)))
                with open(path + ResultPath.CANDIDATE_ENTITIES, "r", encoding='utf-8') as file1:
                    dictionary = file1.read()
                    cd_dict = json.loads(dictionary)
                    dictionary = cd_dict[subj_col]
                k = 0
                length = 0
                with open(path_csv, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        length += 1
                        for keys in dictionary.keys():
                            if ftfy.fix_text(ftfy.fix_encoding(str(keys.lower().replace(' ', '')))) == \
                                    ftfy.fix_text(
                                        ftfy.fix_encoding(str(row[1].lower().replace(' ', '').replace('>', '')))):
                                if dictionary[keys] is not None:
                                    if dictionary[keys].count(ftfy.fix_text(ftfy.fix_encoding(str(row[0])))):
                                        k += 1
                accuracy = k / length
                print("Accuracy:")
                print(accuracy)
                print()
