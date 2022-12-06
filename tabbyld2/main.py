import json
import os
from datetime import datetime

import stanza
from duckling import DucklingWrapper
from tabbyld2.config import ResultPath
from tabbyld2.helpers.file import allowed_file, remove_suffix_in_filename
from tabbyld2.helpers.parser import deserialize_table, save_json_dataset
from tabbyld2.pipeline import pipeline_cell_entity_annotation, pipeline_column_type_annotation, pipeline_preprocessing


if __name__ == '__main__':
    start_full_time = datetime.now()
    save_json_dataset(ResultPath.CSV_FILE_PATH, ResultPath.JSON_FILE_PATH)  # Save a set of source tables in the json format
    stanza.download("en")  # Init Stanford NER annotator
    named_entity_recognition = stanza.Pipeline(lang="en", processors="tokenize,ner")  # Neural pipeline preparation
    duckling_wrapper = DucklingWrapper()  # Init DucklingWrapper object
    for _, _, files in os.walk(ResultPath.JSON_FILE_PATH):
        for file in files:
            if allowed_file(file, {"json"}):
                print("File '" + str(file) + "' processing started!")
                try:
                    with open(ResultPath.JSON_FILE_PATH + file, "r", encoding="utf-8") as fp:
                        # Deserialize a source table in the json format (create a table model)
                        table = deserialize_table(remove_suffix_in_filename(file), json.load(fp))
                except json.decoder.JSONDecodeError:
                    print("Error decoding json table file!")
                if table is not None:
                    table = pipeline_preprocessing(table, file, named_entity_recognition, duckling_wrapper)  # Preprocessing
                    table = pipeline_cell_entity_annotation(table, file)  # Solve CEA task
                    table = pipeline_column_type_annotation(table, file)  # Solve CTA task
    print("***************************************************")
    print("Full time: " + str(datetime.now() - start_full_time))
